#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Validate the installable skill and its deterministic conformance evidence."""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skill"
SKILL_MD = SKILL_DIR / "SKILL.md"
REGISTRY = SKILL_DIR / "languages.yaml"
TESTS_DIR = REPO_ROOT / "tests"
MAX_SKILL_LINES = 500
RULE_ROW = re.compile(
    r"^\|\s*`(?P<id>[a-z0-9]+/[a-z0-9-]+)`\s*\|"
    r"\s*(?P<severity>BLOCKER|MAJOR|MINOR|NIT)\s*\|"
)
LOCATION = re.compile(r"^\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*$")

errors: list[str] = []
warnings: list[str] = []


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    source: Path


def error(message: str) -> None:
    errors.append(message)
    print(f"  ERROR: {message}")


def warn(message: str) -> None:
    warnings.append(message)
    print(f"  WARN:  {message}")


def ok(message: str) -> None:
    print(f"  OK:    {message}")


def load_registry() -> list[dict[str, object]]:
    print("\n--- Validating language registry ---")
    try:
        data = yaml.safe_load(REGISTRY.read_text())
    except (OSError, yaml.YAMLError) as exc:
        error(f"cannot load skill/languages.yaml: {exc}")
        return []
    languages = data.get("languages") if isinstance(data, dict) else None
    if not isinstance(languages, list) or not languages:
        error("skill/languages.yaml must contain a non-empty languages list")
        return []

    seen: set[str] = set()
    registered_references: set[Path] = set()
    for language in languages:
        language_id = language.get("id")
        if not isinstance(language_id, str) or not re.fullmatch("[a-z0-9-]+", language_id):
            error(f"invalid language id: {language_id!r}")
            continue
        if language_id in seen:
            error(f"duplicate language id: {language_id}")
        seen.add(language_id)
        reference = SKILL_DIR / str(language.get("reference", ""))
        registered_references.add(reference)
        if not reference.is_file():
            error(f"{language_id}: missing reference {reference.relative_to(REPO_ROOT)}")
        patterns = list(language.get("extensions", [])) + list(language.get("filenames", []))
        if not patterns:
            error(f"{language_id}: no detection patterns")
    actual_references = set((SKILL_DIR / "references").glob("*.md"))
    for path in sorted(actual_references - registered_references):
        error(f"unregistered Language Reference: {path.relative_to(REPO_ROOT)}")
    registered_tests = {str(language["id"]) for language in languages}
    actual_tests = {
        path.name
        for path in TESTS_DIR.iterdir()
        if path.is_dir() and path.name != "scripts"
    }
    for language_id in sorted(actual_tests - registered_tests):
        error(f"unregistered language test directory: tests/{language_id}")

    for language in languages:
        examples = [
            f"example{extension}" for extension in language["extensions"]
        ]
        examples.extend(
            str(pattern).replace("*", "example") for pattern in language["filenames"]
        )
        for example in examples:
            matches = [
                str(candidate["id"])
                for candidate in languages
                if source_matches(candidate, example)
            ]
            if matches != [language["id"]]:
                error(
                    f"{language['id']}: detection example {example!r} "
                    f"matched {matches}"
                )
    if not errors:
        ok(f"{len(languages)} canonical language entries")
    return languages


def validate_skill() -> None:
    print("\n--- Validating SKILL.md ---")
    content = SKILL_MD.read_text()
    if not content.startswith("---"):
        error("skill/SKILL.md must start with YAML frontmatter")
        return
    try:
        _, frontmatter, body = content.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
    except (ValueError, yaml.YAMLError) as exc:
        error(f"invalid SKILL.md frontmatter: {exc}")
        return
    name = metadata.get("name")
    if name != REPO_ROOT.name:
        error(f"name {name!r} does not match repository {REPO_ROOT.name!r}")
    if not isinstance(name, str) or not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", name
    ):
        error(f"invalid skill name: {name!r}")
    elif len(name) > 64 or "--" in name:
        error(f"invalid skill name: {name!r}")
    if not metadata.get("description"):
        error("missing required frontmatter description")
    body_lines = len(body.splitlines())
    if body_lines > MAX_SKILL_LINES:
        error(f"SKILL.md body is {body_lines} lines (max {MAX_SKILL_LINES})")
    else:
        ok(f"SKILL.md body: {body_lines} lines")

    for link in re.findall(r"\[[^\]]+\]\(((?!https?://)[^)]+)\)", content):
        if not (SKILL_DIR / link).exists():
            error(f"broken local link in SKILL.md: {link}")


def load_catalog(languages: list[dict[str, object]]) -> dict[str, Rule]:
    print("\n--- Validating Review Rule catalog ---")
    paths = [SKILL_MD]
    paths.extend(SKILL_DIR / str(language["reference"]) for language in languages)
    rules: dict[str, Rule] = {}
    for path in paths:
        for line in path.read_text().splitlines():
            match = RULE_ROW.match(line)
            if not match:
                continue
            rule_id = match.group("id")
            owner = "common" if path == SKILL_MD else path.stem
            if rule_id.split("/", 1)[0] != owner:
                error(
                    f"{path.relative_to(REPO_ROOT)} owns {owner!r} but declares {rule_id!r}"
                )
            if rule_id in rules:
                error(f"duplicate Review Rule ID: {rule_id}")
                continue
            rules[rule_id] = Rule(rule_id, match.group("severity"), path)
    if not rules:
        error("no Review Rules found")
    else:
        ok(f"{len(rules)} unique Review Rules")
    return rules


def source_matches(language: dict[str, object], source: str) -> bool:
    if any(source.endswith(str(extension)) for extension in language["extensions"]):
        return True
    return any(fnmatch.fnmatch(source, str(pattern)) for pattern in language["filenames"])


def location_in_source(location: str, line_count: int) -> bool:
    if not LOCATION.fullmatch(location):
        return False
    for part in re.split(r",\s*", location):
        values = [int(value) for value in part.split("-")]
        if min(values) < 1 or max(values) > line_count:
            return False
    return True


def validate_fixtures(
    languages: list[dict[str, object]], rules: dict[str, Rule]
) -> dict[str, list[str]]:
    print("\n--- Validating Conformance Fixtures ---")
    by_id = {str(language["id"]): language for language in languages}
    coverage: dict[str, list[str]] = {rule_id: [] for rule_id in rules}
    fixture_count = 0

    stale = sorted(TESTS_DIR.glob("*/expected-*.md"))
    for path in stale:
        error(f"legacy expected-finding file remains: {path.relative_to(REPO_ROOT)}")

    for path in sorted(TESTS_DIR.glob("*/*.fixture.yaml")):
        fixture_count += 1
        try:
            fixture = yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            error(f"{path.relative_to(REPO_ROOT)}: invalid YAML: {exc}")
            continue
        language_id = fixture.get("language")
        language = by_id.get(language_id)
        if language is None:
            error(f"{path.relative_to(REPO_ROOT)}: unknown language {language_id!r}")
            continue
        source_name = fixture.get("source")
        if fixture.get("version") != 1:
            error(f"{path.relative_to(REPO_ROOT)}: unsupported fixture version")
        source = path.parent / str(source_name)
        if not source.is_file():
            error(f"{path.relative_to(REPO_ROOT)}: source does not exist: {source_name}")
            continue
        if not source_matches(language, source.name):
            error(
                f"{path.relative_to(REPO_ROOT)}: {source.name!r} does not match "
                f"{language_id} detection patterns"
            )
        if path.name != f"{source.name}.fixture.yaml":
            error(
                f"{path.relative_to(REPO_ROOT)}: expected filename "
                f"{source.name}.fixture.yaml"
            )

        line_count = len(source.read_text().splitlines())
        required = fixture.get("required")
        forbidden = fixture.get("forbidden")
        if not isinstance(required, list) or not required:
            error(f"{path.relative_to(REPO_ROOT)}: required must be a non-empty list")
            continue
        if not isinstance(forbidden, list):
            error(f"{path.relative_to(REPO_ROOT)}: forbidden must be a list")
            forbidden = []

        for expectation_type, expectations in (
            ("required", required),
            ("forbidden", forbidden),
        ):
            seen_expectations: set[tuple[object, object]] = set()
            for index, expectation in enumerate(expectations, 1):
                rule_id = expectation.get("rule")
                if rule_id not in rules:
                    error(
                        f"{path.relative_to(REPO_ROOT)}: {expectation_type}[{index}] "
                        f"uses unknown rule {rule_id!r}"
                    )
                    continue
                owner = str(rule_id).split("/", 1)[0]
                if owner not in {"common", language_id}:
                    error(
                        f"{path.relative_to(REPO_ROOT)}: {expectation_type}[{index}] "
                        f"uses {owner} rule for {language_id} input"
                    )
                location = expectation.get("location")
                if location is not None and not location_in_source(str(location), line_count):
                    error(
                        f"{path.relative_to(REPO_ROOT)}: {expectation_type}[{index}] "
                        f"has invalid location {location!r} for {line_count} lines"
                    )
                identity = (rule_id, location)
                if identity in seen_expectations:
                    error(
                        f"{path.relative_to(REPO_ROOT)}: duplicate "
                        f"{expectation_type} expectation {identity}"
                    )
                seen_expectations.add(identity)
                if not isinstance(expectation.get("rationale"), str):
                    error(
                        f"{path.relative_to(REPO_ROOT)}: {expectation_type}[{index}] "
                        "requires a rationale"
                    )
                if expectation_type == "required":
                    coverage[rule_id].append(
                        f"{path.parent.name}/{source.name}:{location or 'absent'}"
                    )
        ok(f"{path.relative_to(REPO_ROOT)}")

    for language_id in by_id:
        if not list((TESTS_DIR / language_id).glob("*.fixture.yaml")):
            error(f"{language_id}: requires at least one Conformance Fixture")

    uncovered = sorted(rule_id for rule_id, evidence in coverage.items() if not evidence)
    if uncovered:
        error(f"{len(uncovered)} Review Rules lack fixture coverage: {', '.join(uncovered)}")
    ok(f"{fixture_count} Conformance Fixtures")
    return coverage


def validate_generated() -> None:
    print("\n--- Validating generated documentation ---")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("sync_generated.py")), "--check"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        error(result.stdout.strip() or result.stderr.strip())
    else:
        ok("generated language tables are current")


def main() -> None:
    print("=== Skill and Conformance Validation ===")
    print(f"Root: {REPO_ROOT}")
    languages = load_registry()
    validate_skill()
    rules = load_catalog(languages)
    validate_fixtures(languages, rules)
    validate_generated()

    print("\n=== Summary ===")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    if errors:
        print("\nFAILED")
        sys.exit(1)
    print("\nPASSED" if not warnings else "\nPASSED with warnings")


if __name__ == "__main__":
    main()
