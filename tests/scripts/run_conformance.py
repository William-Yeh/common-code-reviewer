#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Run semantic Conformance Fixtures against Claude Code."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from validate_structure import RULE_ROW, location_parts

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skill"
FIXTURE_GLOB = "*/*.fixture.yaml"
# Lazy gaps never cross into the next finding's heading.
WITHIN_FINDING = r"(?:(?!^###\s).)*?"
FINDING = re.compile(
    r"^###\s+\[(?P<severity>BLOCKER|MAJOR|MINOR|NIT)\]" + WITHIN_FINDING
    + r"^\*\*File:\*\*[ \t]*(?P<file>[^\n]*?)[ \t]*$" + WITHIN_FINDING
    + r"^\*\*Rule:\*\*\s*`?(?P<rule>[a-z0-9]+/[a-z0-9-]+)`?\s*$",
    re.MULTILINE | re.DOTALL,
)
CODE_SPAN = re.compile(r"`([^`]+)`")
EXTRA_SITE = re.compile(r":(?P<location>\d+(?:-\d+)?)")
FILE_LOCATION = re.compile(r"^(?P<file>.+?)(?::(?P<location>\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*))?$")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    file: str
    location: str | None


def line_numbers(location: str | None) -> set[int]:
    if location is None:
        return set()
    return {number for span in location_parts(location) for number in span}


def extra_sites(spans: list[str]) -> list[str]:
    """Locations of the `:N` / `:N-M` code spans that follow the primary path."""
    matches = (EXTRA_SITE.fullmatch(span.strip()) for span in spans)
    return [match.group("location") for match in matches if match]


def primary_index(spans: list[str]) -> int:
    """Index of the first `path:line` span; the first span when none carries a line."""
    located = (
        index
        for index, span in enumerate(spans)
        if (match := FILE_LOCATION.fullmatch(span.strip())) and match.group("location")
    )
    return next(located, 0)


def file_and_location(file_line: str) -> tuple[str, str | None] | None:
    """Split a File line into path and location, merging extra `:N` sites the reviewer appends."""
    spans = CODE_SPAN.findall(file_line) or [file_line]
    start = primary_index(spans)
    primary = FILE_LOCATION.fullmatch(spans[start].strip())
    if primary is None:
        return None
    parts = [primary.group("location"), *extra_sites(spans[start + 1 :])]
    return primary.group("file"), ", ".join(filter(None, parts)) or None


def parse_findings(markdown: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in FINDING.finditer(markdown):
        parsed = file_and_location(match.group("file"))
        if parsed is None:
            continue
        findings.append(
            Finding(
                rule=match.group("rule"),
                severity=match.group("severity"),
                file=parsed[0],
                location=parsed[1],
            )
        )
    return findings


def matches(
    expectation: dict[str, object],
    finding: Finding,
    source: str,
    severities: dict[str, str] | None = None,
) -> bool:
    if expectation["rule"] != finding.rule:
        return False
    if severities is not None and severities.get(finding.rule) != finding.severity:
        return False
    if Path(finding.file).name != Path(source).name:
        return False
    expected_location = expectation.get("location")
    if expected_location is None:
        return True
    return bool(line_numbers(str(expected_location)) & line_numbers(finding.location))


def evaluate(
    fixture: dict[str, object],
    findings: list[Finding],
    severities: dict[str, str] | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    source = str(fixture["source"])
    missing = [
        expectation
        for expectation in fixture["required"]
        if not any(
            matches(expectation, finding, source, severities) for finding in findings
        )
    ]
    forbidden = [
        expectation
        for expectation in fixture["forbidden"]
        if any(matches(expectation, finding, source, severities) for finding in findings)
    ]
    return missing, forbidden


def load_severities() -> dict[str, str]:
    severities: dict[str, str] = {}
    for path in [SKILL_DIR / "SKILL.md", *(SKILL_DIR / "references").glob("*.md")]:
        for line in path.read_text().splitlines():
            if match := RULE_ROW.match(line):
                severities[match.group("id")] = match.group("severity")
    return severities


def prompt_for(fixture_path: Path, fixture: dict[str, object]) -> str:
    source = fixture_path.parent / str(fixture["source"])
    coverage = fixture.get("coverage")
    if coverage:
        evidence_path = (fixture_path.parent / str(coverage)).relative_to(REPO_ROOT)
        evidence = (
            f"Coverage Evidence is at {evidence_path}; read it before scoring change risk. "
        )
    else:
        evidence = "No Coverage Evidence exists for this file. "
    return (
        "Read skill/SKILL.md and follow it as the common-code-reviewer skill. "
        f"Load the Language Reference for {fixture['language']}. "
        f"Review only {source.relative_to(REPO_ROOT)} in --thorough mode. "
        f"{source.parent.relative_to(REPO_ROOT)}/ is this harness's fixture directory, not part "
        "of the reviewed project: decide whether the file is a test file from its own name and "
        "content, as the Scoring Profile's naming rules describe, never from that directory. "
        f"{evidence}"
        "Use the skill's normal Markdown output interface, including the visible "
        "Rule field for every finding. Do not edit or execute any reviewed file."
    )


def claude_version() -> str:
    result = subprocess.run(
        ["claude", "--version"], text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def invoke_claude(
    fixture_path: Path,
    fixture: dict[str, object],
    *,
    model: str,
    budget: float,
    transport_retries: int,
) -> tuple[str, dict[str, object]]:
    command = [
        "claude",
        "--print",
        "--bare",
        "--model",
        model,
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--tools",
        "Read",
        "--max-budget-usd",
        str(budget),
        "--output-format",
        "json",
        prompt_for(fixture_path, fixture),
    ]
    last_error = ""
    for _ in range(transport_retries + 1):
        result = subprocess.run(
            command, cwd=REPO_ROOT, text=True, capture_output=True, check=False
        )
        if result.returncode == 0:
            envelope = json.loads(result.stdout)
            return str(envelope["result"]), envelope
        last_error = result.stderr.strip() or result.stdout.strip()
    raise RuntimeError(last_error or "Claude Code exited without an error message")


def select_fixtures(patterns: list[str]) -> list[Path]:
    fixtures = sorted((REPO_ROOT / "tests").glob(FIXTURE_GLOB))
    if not patterns:
        return fixtures
    return [
        path
        for path in fixtures
        if any(fnmatch in str(path.relative_to(REPO_ROOT)) for fnmatch in patterns)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--max-budget-usd", type=float, default=0.50)
    parser.add_argument("--transport-retries", type=int, default=1)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--report", type=Path, default=Path("conformance-report.json"))
    args = parser.parse_args()

    fixtures = select_fixtures(args.fixture)
    if not fixtures:
        parser.error("no Conformance Fixtures matched")

    report: dict[str, object] = {
        "started_at": datetime.now(UTC).isoformat(),
        "runtime": "Claude Code",
        "runtime_version": claude_version(),
        "requested_model": args.model,
        "fixtures": [],
    }
    severities = load_severities()
    passed = True
    for path in fixtures:
        fixture = yaml.safe_load(path.read_text())
        print(f"running {path.relative_to(REPO_ROOT)}", flush=True)
        try:
            markdown, envelope = invoke_claude(
                path,
                fixture,
                model=args.model,
                budget=args.max_budget_usd,
                transport_retries=args.transport_retries,
            )
            findings = parse_findings(markdown)
            missing, forbidden = evaluate(fixture, findings, severities)
            interface_errors = [
                asdict(finding)
                for finding in findings
                if severities.get(finding.rule) != finding.severity
            ]
            result = {
                "fixture": str(path.relative_to(REPO_ROOT)),
                "passed": not missing and not forbidden and not interface_errors,
                "missing": missing,
                "forbidden": forbidden,
                "interface_errors": interface_errors,
                "findings": [asdict(finding) for finding in findings],
                "model_usage": envelope.get("modelUsage", {}),
                "cost_usd": envelope.get("total_cost_usd"),
                "markdown": markdown,
            }
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            result = {
                "fixture": str(path.relative_to(REPO_ROOT)),
                "passed": False,
                "runtime_error": str(exc),
            }
        passed = passed and bool(result["passed"])
        report["fixtures"].append(result)

    report["finished_at"] = datetime.now(UTC).isoformat()
    report["passed"] = passed
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {args.report}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
