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
from collections import Counter
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
CHANGE_RISK_SECTION = "## Change Risk"
SCORING_PROFILE_SLOTS = (
    "### Scored Units",
    "### Decision Points",
    "### Test Files",
    "### Coverage Evidence",
    "### Oracle Deviations",
)

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


def language_entry_problems(language: dict[str, object]) -> list[str]:
    """Field-level problems of one registry entry, independent of the filesystem."""
    problems: list[str] = []
    language_id = language.get("id")
    if not isinstance(language_id, str) or not re.fullmatch("[a-z0-9-]+", language_id):
        problems.append(f"invalid language id: {language_id!r}")
    patterns = list(language.get("extensions", [])) + list(language.get("filenames", []))
    if not patterns:
        problems.append(f"{language_id}: no detection patterns")
    if not isinstance(language.get("scored"), bool):
        problems.append(f"{language_id}: 'scored' must be true or false")
    if not isinstance(language.get("comment_prefixes"), list):
        problems.append(f"{language_id}: 'comment_prefixes' must be a list")
    return problems


def detection_examples(language: dict[str, object]) -> list[str]:
    examples = [f"example{extension}" for extension in language["extensions"]]
    examples.extend(
        str(pattern).replace("*", "example") for pattern in language["filenames"]
    )
    return examples


def languages_matching(languages: list[dict[str, object]], example: str) -> list[str]:
    return [str(candidate["id"]) for candidate in languages if source_matches(candidate, example)]


def detection_ambiguities(languages: list[dict[str, object]]) -> list[str]:
    """Detection examples that match zero or several registered languages."""
    problems: list[str] = []
    for language in languages:
        for example in detection_examples(language):
            matches = languages_matching(languages, example)
            if matches != [language["id"]]:
                problems.append(
                    f"{language['id']}: detection example {example!r} matched {matches}"
                )
    return problems


def unregistered_references(registered: set[Path]) -> list[str]:
    actual = set((SKILL_DIR / "references").glob("*.md"))
    return [
        f"unregistered Language Reference: {path.relative_to(REPO_ROOT)}"
        for path in sorted(actual - registered)
    ]


def unregistered_test_dirs(languages: list[dict[str, object]]) -> list[str]:
    registered = {str(language["id"]) for language in languages}
    actual = {
        path.name for path in TESTS_DIR.iterdir() if path.is_dir() and path.name != "scripts"
    }
    return [
        f"unregistered language test directory: tests/{language_id}"
        for language_id in sorted(actual - registered)
    ]


def report(label: str | None, problems: list[str]) -> None:
    """Record each problem as an error, prefixed with the file label when given."""
    for problem in problems:
        error(f"{label}: {problem}" if label else problem)


def registry_languages(path: Path = REGISTRY) -> list[dict[str, object]] | None:
    """The registry's language list, or None after reporting why it is unusable."""
    try:
        data = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as exc:
        error(f"cannot load skill/languages.yaml: {exc}")
        return None
    languages = data.get("languages") if isinstance(data, dict) else None
    if not isinstance(languages, list) or not languages:
        error("skill/languages.yaml must contain a non-empty languages list")
        return None
    return languages


def register_language(language: dict[str, object]) -> Path | None:
    """Report an entry's problems; return its reference path when the id is usable."""
    report(None, language_entry_problems(language))
    language_id = language.get("id")
    if not isinstance(language_id, str):
        return None
    reference = SKILL_DIR / str(language.get("reference", ""))
    if not reference.is_file():
        error(f"{language_id}: missing reference {reference.relative_to(REPO_ROOT)}")
    return reference


def duplicate_ids(languages: list[dict[str, object]]) -> list[str]:
    counts = Counter(str(language.get("id")) for language in languages)
    return [
        f"duplicate language id: {language_id}"
        for language_id, seen in sorted(counts.items())
        if seen > 1
    ]


def load_registry() -> list[dict[str, object]]:
    print("\n--- Validating language registry ---")
    languages = registry_languages()
    if languages is None:
        return []
    references = {
        reference
        for language in languages
        if (reference := register_language(language)) is not None
    }
    report(
        None,
        [
            *duplicate_ids(languages),
            *unregistered_references(references),
            *unregistered_test_dirs(languages),
            *detection_ambiguities(languages),
        ],
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


def location_parts(location: str) -> list[range]:
    """Parse the fixture location grammar into inclusive line ranges.

    ``"2-4, 8"`` becomes ``[range(2, 5), range(8, 9)]``. This is the single
    parser for the grammar; the live runner imports it too.
    """
    parts: list[range] = []
    for part in re.split(r",\s*", location):
        values = [int(value) for value in part.split("-")]
        parts.append(range(min(values), max(values) + 1))
    return parts


def location_in_source(location: str, line_count: int) -> bool:
    if not LOCATION.fullmatch(location):
        return False
    return all(
        span.start >= 1 and span[-1] <= line_count for span in location_parts(location)
    )


def covers_source(report_text: str, source_name: str) -> bool:
    """Whether a coverage report names the source file, whatever its format.

    LCOV, Cobertura, JaCoCo XML, and Go coverprofiles all spell the file path
    somewhere; only the basename is compared so import-path-based formats match.
    """
    pattern = r"(?<![\w.-])" + re.escape(source_name) + r"(?![\w])"
    return re.search(pattern, report_text) is not None


def non_code_parts(location: str, lines: list[str], comment_prefixes: list[str]) -> list[str]:
    """Return the comma-separated parts of a location that point at no code.

    A part is a single line or a range. It passes when at least one of its lines
    is neither blank nor a comment-only line for the language.
    """

    def is_code(line: str) -> bool:
        stripped = line.strip()
        return bool(stripped) and not any(
            stripped.startswith(prefix) for prefix in comment_prefixes
        )

    offending: list[str] = []
    for span in location_parts(location):
        if not any(is_code(lines[number - 1]) for number in span if number <= len(lines)):
            offending.append(f"{span.start}-{span[-1]}" if len(span) > 1 else str(span.start))
    return offending


def table_first_column(text: str, header_prefix: str) -> list[str]:
    """Return the first-column cells of the Markdown table whose header starts so."""
    cells: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith(header_prefix):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        first = line.split("|")[1].strip()
        if not first.startswith("-"):
            cells.append(first)
    return cells


def decision_categories(skill_text: str) -> list[str]:
    """The decision-point categories every Scoring Profile must spell."""
    return table_first_column(skill_text, "| Category | Counts |")


def missing_headings(reference_text: str) -> list[str]:
    headings = {line.strip() for line in reference_text.splitlines()}
    return [
        heading
        for heading in (CHANGE_RISK_SECTION, *SCORING_PROFILE_SLOTS)
        if heading not in headings
    ]


def missing_categories(reference_text: str, categories: list[str]) -> list[str]:
    section = reference_text.split("### Decision Points", 1)[-1]
    rows = table_first_column(section, "| Category |")
    return [f"Decision Points row: {name}" for name in categories if name not in rows]


def profile_gaps(reference_text: str, scored: bool, categories: list[str]) -> list[str]:
    """What a scored language's Scoring Profile is missing; nothing for unscored ones."""
    if not scored:
        return []
    return [*missing_headings(reference_text), *missing_categories(reference_text, categories)]


def scoring_profile_problems(
    scored_languages: list[dict[str, object]], categories: list[str]
) -> list[str]:
    problems: list[str] = []
    for language in scored_languages:
        reference = SKILL_DIR / str(language["reference"])
        gaps = profile_gaps(reference.read_text(), scored=True, categories=categories)
        if gaps:
            problems.append(
                f"{reference.relative_to(REPO_ROOT)} Scoring Profile lacks: {', '.join(gaps)}"
            )
    return problems


def validate_scoring_profiles(languages: list[dict[str, object]]) -> None:
    print("\n--- Validating Scoring Profiles ---")
    categories = decision_categories(SKILL_MD.read_text())
    if not categories:
        error("SKILL.md has no shared decision-point table")
    scored = [language for language in languages if language.get("scored")]
    problems = scoring_profile_problems(scored, categories)
    report(None, problems)
    if not problems:
        ok(f"{len(scored)} scored languages carry a complete Scoring Profile")


def location_problem(
    location: object, source_lines: list[str], comment_prefixes: list[str], rule_id: object
) -> str | None:
    if not location_in_source(str(location), len(source_lines)):
        return f"has invalid location {location!r} for {len(source_lines)} lines"
    dead = non_code_parts(str(location), source_lines, comment_prefixes)
    if dead:
        return f"location {', '.join(dead)} points at no code ({rule_id})"
    return None


def single_expectation_problems(
    expectation: dict[str, object],
    *,
    language_id: str,
    source_lines: list[str],
    comment_prefixes: list[str],
) -> list[str]:
    """Problems of one expectation whose rule exists. Messages carry no index."""
    rule_id = expectation["rule"]
    problems: list[str] = []
    owner = str(rule_id).split("/", 1)[0]
    if owner not in {"common", language_id}:
        problems.append(f"uses {owner} rule for {language_id} input")
    location = expectation.get("location")
    if location is not None and (
        problem := location_problem(location, source_lines, comment_prefixes, rule_id)
    ):
        problems.append(problem)
    if not isinstance(expectation.get("rationale"), str):
        problems.append("requires a rationale")
    return problems


def expectation_problems(
    expectation_type: str,
    expectations: list[dict[str, object]],
    *,
    rules: dict[str, Rule],
    language_id: str,
    source_lines: list[str],
    comment_prefixes: list[str],
) -> tuple[list[str], list[tuple[str, object]]]:
    """Problems in one expectation list, plus (rule, location) evidence per known rule.

    Messages carry no file prefix; the caller adds it.
    """
    problems: list[str] = []
    evidence: list[tuple[str, object]] = []
    seen: set[tuple[object, object]] = set()
    for index, expectation in enumerate(expectations, 1):
        rule_id = expectation.get("rule")
        prefix = f"{expectation_type}[{index}]"
        if rule_id not in rules:
            problems.append(f"{prefix} uses unknown rule {rule_id!r}")
            continue
        problems.extend(
            f"{prefix} {problem}"
            for problem in single_expectation_problems(
                expectation,
                language_id=language_id,
                source_lines=source_lines,
                comment_prefixes=comment_prefixes,
            )
        )
        identity = (rule_id, expectation.get("location"))
        if identity in seen:
            problems.append(f"duplicate {expectation_type} expectation {identity}")
        seen.add(identity)
        evidence.append((str(rule_id), identity[1]))
    return problems, evidence


def fixture_header_problems(
    fixture: dict[str, object], language: dict[str, object], path_name: str, source_name: str
) -> list[str]:
    problems: list[str] = []
    if fixture.get("version") != 1:
        problems.append("unsupported fixture version")
    if not source_matches(language, source_name):
        problems.append(
            f"{source_name!r} does not match {language['id']} detection patterns"
        )
    if path_name != f"{source_name}.fixture.yaml":
        problems.append(f"expected filename {source_name}.fixture.yaml")
    return problems


def coverage_evidence_problem(evidence: Path, coverage_name: str, source_name: str) -> str | None:
    if not evidence.is_file():
        return f"Coverage Evidence does not exist: {coverage_name}"
    if not covers_source(evidence.read_text(), source_name):
        return f"{coverage_name} never names {source_name}"
    return None


def fixture_coverage_problem(fixture: dict[str, object], path: Path, source_name: str) -> str | None:
    coverage_name = fixture.get("coverage")
    if coverage_name is None:
        return None
    return coverage_evidence_problem(path.parent / str(coverage_name), str(coverage_name), source_name)


def load_fixture(path: Path, label: str) -> dict[str, object] | None:
    try:
        return yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        error(f"{label}: invalid YAML: {exc}")
        return None


def fixture_fatal_problem(
    fixture: dict[str, object], path: Path, by_id: dict[str, dict[str, object]]
) -> str | None:
    """The one problem that makes a fixture unreviewable, if any."""
    language_id = fixture.get("language")
    if language_id not in by_id:
        return f"unknown language {language_id!r}"
    source_name = fixture.get("source")
    if not (path.parent / str(source_name)).is_file():
        return f"source does not exist: {source_name}"
    return None


def expectation_lists(
    fixture: dict[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str]]:
    """(required, forbidden, problems); required is empty when the fixture is unusable."""
    required = fixture.get("required")
    forbidden = fixture.get("forbidden")
    if not isinstance(required, list) or not required:
        return [], [], ["required must be a non-empty list"]
    if not isinstance(forbidden, list):
        return required, [], ["forbidden must be a list"]
    return required, forbidden, []


def check_expectations(
    label: str,
    *,
    required: list[dict[str, object]],
    forbidden: list[dict[str, object]],
    rules: dict[str, Rule],
    language: dict[str, object],
    source: Path,
    coverage: dict[str, list[str]],
) -> None:
    source_lines = source.read_text().splitlines()
    comment_prefixes = [str(prefix) for prefix in language.get("comment_prefixes", [])]
    for expectation_type, expectations in (("required", required), ("forbidden", forbidden)):
        problems, evidence = expectation_problems(
            expectation_type,
            expectations,
            rules=rules,
            language_id=str(language["id"]),
            source_lines=source_lines,
            comment_prefixes=comment_prefixes,
        )
        report(label, problems)
        if expectation_type == "required":
            for rule_id, location in evidence:
                coverage[rule_id].append(f"{source.parent.name}/{source.name}:{location or 'absent'}")


def validate_fixture(
    path: Path,
    by_id: dict[str, dict[str, object]],
    rules: dict[str, Rule],
    coverage: dict[str, list[str]],
) -> None:
    label = str(path.relative_to(REPO_ROOT))
    fixture = load_fixture(path, label)
    if fixture is None:
        return
    if fatal := fixture_fatal_problem(fixture, path, by_id):
        error(f"{label}: {fatal}")
        return
    language = by_id[str(fixture["language"])]
    source = path.parent / str(fixture["source"])
    problems = fixture_header_problems(fixture, language, path.name, source.name)
    if coverage_problem := fixture_coverage_problem(fixture, path, source.name):
        problems.append(coverage_problem)
    required, forbidden, list_problems = expectation_lists(fixture)
    report(label, [*problems, *list_problems])
    if not required:
        return
    check_expectations(
        label,
        required=required,
        forbidden=forbidden,
        rules=rules,
        language=language,
        source=source,
        coverage=coverage,
    )
    ok(label)


def legacy_expected_files() -> list[str]:
    return [
        f"legacy expected-finding file remains: {path.relative_to(REPO_ROOT)}"
        for path in sorted(TESTS_DIR.glob("*/expected-*.md"))
    ]


def missing_fixture_dirs(by_id: dict[str, dict[str, object]]) -> list[str]:
    return [
        f"{language_id}: requires at least one Conformance Fixture"
        for language_id in by_id
        if not list((TESTS_DIR / language_id).glob("*.fixture.yaml"))
    ]


def uncovered_rules(coverage: dict[str, list[str]]) -> list[str]:
    uncovered = sorted(rule_id for rule_id, evidence in coverage.items() if not evidence)
    if not uncovered:
        return []
    return [f"{len(uncovered)} Review Rules lack fixture coverage: {', '.join(uncovered)}"]


def validate_fixtures(
    languages: list[dict[str, object]], rules: dict[str, Rule]
) -> dict[str, list[str]]:
    print("\n--- Validating Conformance Fixtures ---")
    by_id = {str(language["id"]): language for language in languages}
    coverage: dict[str, list[str]] = {rule_id: [] for rule_id in rules}
    report(None, legacy_expected_files())
    fixtures = sorted(TESTS_DIR.glob("*/*.fixture.yaml"))
    for path in fixtures:
        validate_fixture(path, by_id, rules, coverage)
    report(None, [*missing_fixture_dirs(by_id), *uncovered_rules(coverage)])
    ok(f"{len(fixtures)} Conformance Fixtures")
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


def run() -> list[str]:
    """Run every check, print the report, and return the errors found."""
    errors.clear()
    warnings.clear()
    print("=== Skill and Conformance Validation ===")
    print(f"Root: {REPO_ROOT}")
    languages = load_registry()
    validate_skill()
    rules = load_catalog(languages)
    validate_scoring_profiles(languages)
    validate_fixtures(languages, rules)
    validate_generated()

    print("\n=== Summary ===")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    if errors:
        print("\nFAILED")
    else:
        print("\nPASSED" if not warnings else "\nPASSED with warnings")
    return list(errors)


def main() -> None:
    sys.exit(1 if run() else 0)


if __name__ == "__main__":
    main()
