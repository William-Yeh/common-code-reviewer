#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Generate language documentation from skill/languages.yaml."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skill"
REGISTRY = SKILL_DIR / "languages.yaml"
SKILL_MD = SKILL_DIR / "SKILL.md"
README_MD = REPO_ROOT / "README.md"
COVERAGE_MD = REPO_ROOT / "tests" / "COVERAGE.md"

START = "<!-- BEGIN GENERATED LANGUAGES -->"
END = "<!-- END GENERATED LANGUAGES -->"
COVERAGE_START = "<!-- BEGIN GENERATED COVERAGE -->"
COVERAGE_END = "<!-- END GENERATED COVERAGE -->"
RULE_ROW = re.compile(
    r"^\|\s*`(?P<id>[a-z0-9]+/[a-z0-9-]+)`\s*\|"
    r"\s*(?P<severity>BLOCKER|MAJOR|MINOR|NIT)\s*\|"
)


def load_languages() -> list[dict[str, object]]:
    data = yaml.safe_load(REGISTRY.read_text())
    return data["languages"]


def patterns(language: dict[str, object]) -> str:
    values = [f"`{value}`" for value in language["extensions"]]
    values.extend(f"`{value}`" for value in language["filenames"])
    return ", ".join(values)


def skill_table(languages: list[dict[str, object]]) -> str:
    rows = [
        "| Patterns | Language | Reference |",
        "|---|---|---|",
    ]
    rows.extend(
        f"| {patterns(language)} | {language['name']} | "
        f"[{language['reference']}]({language['reference']}) |"
        for language in languages
    )
    return "\n".join(rows)


def readme_table(languages: list[dict[str, object]]) -> str:
    rows = [
        "| Language | Frameworks | Style Standard |",
        "|---|---|---|",
    ]
    rows.extend(
        f"| {language['name']} | {', '.join(language['frameworks'])} | "
        f"{language['style']} |"
        for language in languages
    )
    return "\n".join(rows)


def coverage_document(languages: list[dict[str, object]]) -> str:
    catalog: dict[str, str] = {}
    paths = [SKILL_MD]
    paths.extend(SKILL_DIR / str(language["reference"]) for language in languages)
    for path in paths:
        for line in path.read_text().splitlines():
            match = RULE_ROW.match(line)
            if match:
                catalog[match.group("id")] = match.group("severity")

    evidence: dict[str, list[str]] = {rule_id: [] for rule_id in catalog}
    for path in sorted((REPO_ROOT / "tests").glob("*/*.fixture.yaml")):
        fixture = yaml.safe_load(path.read_text())
        source = fixture["source"]
        for expectation in fixture["required"]:
            location = expectation.get("location", "absent")
            evidence.setdefault(expectation["rule"], []).append(
                f"`{path.parent.name}/{source}:{location}`"
            )

    lines = [
        "# Review Rule Coverage",
        "",
        "Generated from the inline Review Rule catalogs and Conformance Fixtures.",
        "Run `uv run tests/scripts/sync_generated.py` after changing either.",
        "",
    ]
    for owner in sorted({rule_id.split("/", 1)[0] for rule_id in catalog}):
        lines.extend(
            [
                f"## {owner}",
                "",
                "| Review Rule | Severity | Required evidence |",
                "|---|---|---|",
            ]
        )
        for rule_id in sorted(rule for rule in catalog if rule.startswith(f"{owner}/")):
            refs = "<br>".join(evidence.get(rule_id, [])) or "—"
            lines.append(f"| `{rule_id}` | {catalog[rule_id]} | {refs} |")
        lines.append("")

    covered = sum(bool(refs) for refs in evidence.values())
    lines.extend(
        [
            "## Summary",
            "",
            f"**Coverage: {covered}/{len(catalog)} Review Rules "
            f"({covered / len(catalog):.0%})**",
            "",
        ]
    )
    return "\n".join(lines)


def coverage_summary(document: str) -> str:
    match = re.search(
        r"\*\*Coverage: (\d+)/(\d+) Review Rules \((\d+)%\)\*\*", document
    )
    if match is None:
        raise ValueError("generated coverage summary is missing")
    covered, total, percent = match.groups()
    return (
        f"The Conformance Fixtures cover **{covered}/{total} Review Rules "
        f"({percent}%)**. See\n`tests/COVERAGE.md` for the derived evidence."
    )


def replace_block(
    path: Path, start_marker: str, end_marker: str, body: str, *, check: bool
) -> bool:
    content = path.read_text()
    start = content.index(start_marker) + len(start_marker)
    end = content.index(end_marker, start)
    updated = content[:start] + f"\n{body}\n" + content[end:]
    if updated == content:
        return True
    if check:
        print(f"generated block is stale: {path.relative_to(REPO_ROOT)}")
        return False
    path.write_text(updated)
    print(f"updated {path.relative_to(REPO_ROOT)}")
    return True


def replace_generated(path: Path, table: str, *, check: bool) -> bool:
    content = path.read_text()
    start = content.index(START) + len(START)
    end = content.index(END, start)
    generated = f"\n{table}\n"
    updated = content[:start] + generated + content[end:]
    if updated == content:
        return True
    if check:
        print(f"generated language table is stale: {path.relative_to(REPO_ROOT)}")
        return False
    path.write_text(updated)
    print(f"updated {path.relative_to(REPO_ROOT)}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    languages = load_languages()
    results = [
        replace_generated(SKILL_MD, skill_table(languages), check=args.check),
        replace_generated(README_MD, readme_table(languages), check=args.check),
    ]
    coverage = coverage_document(languages)
    current_coverage = COVERAGE_MD.read_text() if COVERAGE_MD.exists() else ""
    if coverage != current_coverage:
        if args.check:
            print("generated rule coverage is stale: tests/COVERAGE.md")
            results.append(False)
        else:
            COVERAGE_MD.write_text(coverage)
            print("updated tests/COVERAGE.md")
            results.append(True)
    results.append(
        replace_block(
            README_MD,
            COVERAGE_START,
            COVERAGE_END,
            coverage_summary(coverage),
            check=args.check,
        )
    )
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
