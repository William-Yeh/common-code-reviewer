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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skill"
FIXTURE_GLOB = "*/*.fixture.yaml"
FINDING = re.compile(
    r"^###\s+\[(?P<severity>BLOCKER|MAJOR|MINOR|NIT)\].*?"
    r"^\*\*File:\*\*\s*`?(?P<file>[^`\n]+?)`?\s*$.*?"
    r"^\*\*Rule:\*\*\s*`?(?P<rule>[a-z0-9]+/[a-z0-9-]+)`?\s*$",
    re.MULTILINE | re.DOTALL,
)
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
    values: set[int] = set()
    for part in re.split(r",\s*", location):
        ends = [int(value) for value in part.split("-")]
        values.update(range(ends[0], ends[-1] + 1))
    return values


def parse_findings(markdown: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in FINDING.finditer(markdown):
        file_match = FILE_LOCATION.fullmatch(match.group("file").strip())
        if file_match is None:
            continue
        findings.append(
            Finding(
                rule=match.group("rule"),
                severity=match.group("severity"),
                file=file_match.group("file"),
                location=file_match.group("location"),
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
        for match in re.finditer(
            r"^\|\s*`(?P<rule>[a-z0-9]+/[a-z0-9-]+)`\s*\|\s*"
            r"(?P<severity>BLOCKER|MAJOR|MINOR|NIT)\s*\|",
            path.read_text(),
            re.MULTILINE,
        ):
            severities[match.group("rule")] = match.group("severity")
    return severities


def prompt_for(fixture_path: Path, fixture: dict[str, object]) -> str:
    source = fixture_path.parent / str(fixture["source"])
    return (
        "Read skill/SKILL.md and follow it as the common-code-reviewer skill. "
        f"Load the Language Reference for {fixture['language']}. "
        f"Review only {source.relative_to(REPO_ROOT)} in --thorough mode. "
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
