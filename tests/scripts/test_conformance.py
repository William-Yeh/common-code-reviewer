#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Tests for semantic Conformance Finding matching."""

import unittest

from run_conformance import (
    REPO_ROOT,
    Finding,
    evaluate,
    line_numbers,
    load_severities,
    parse_findings,
    prompt_for,
)


class PromptTests(unittest.TestCase):
    FIXTURE_PATH = REPO_ROOT / "tests/python/pricing_engine.py.fixture.yaml"

    def test_prompt_without_coverage_evidence_says_none_exists(self) -> None:
        prompt = prompt_for(self.FIXTURE_PATH, {"language": "python", "source": "pricing_engine.py"})
        self.assertIn("Review only tests/python/pricing_engine.py", prompt)
        self.assertIn("No Coverage Evidence exists", prompt)

    def test_prompt_names_coverage_evidence_when_fixture_declares_it(self) -> None:
        prompt = prompt_for(
            self.FIXTURE_PATH,
            {"language": "python", "source": "pricing_engine.py", "coverage": "lcov.info"},
        )
        self.assertIn("Coverage Evidence is at tests/python/lcov.info", prompt)
        self.assertNotIn("No Coverage Evidence", prompt)


class FindingParserTests(unittest.TestCase):
    def test_parses_normal_markdown_interface(self) -> None:
        markdown = """\
### [BLOCKER] SQL injection
**File:** `tests/python/order.py:10-12`
**Rule:** `common/sql-injection`
**Category:** Security | **Principle:** Injection

Explanation.
"""
        self.assertEqual(
            parse_findings(markdown),
            [
                Finding(
                    rule="common/sql-injection",
                    severity="BLOCKER",
                    file="tests/python/order.py",
                    location="10-12",
                )
            ],
        )

    def test_expands_ranges_and_lists(self) -> None:
        self.assertEqual(line_numbers("2-4, 8"), {2, 3, 4, 8})

    def test_allows_additional_findings(self) -> None:
        fixture = {
            "source": "order.py",
            "required": [{"rule": "common/sql-injection", "location": "10-12"}],
            "forbidden": [],
        }
        findings = [
            Finding("common/sql-injection", "BLOCKER", "order.py", "11"),
            Finding("common/dead-code", "MINOR", "order.py", "20"),
        ]
        self.assertEqual(evaluate(fixture, findings), ([], []))

    def test_detects_forbidden_overlap(self) -> None:
        fixture = {
            "source": "order.py",
            "required": [],
            "forbidden": [{"rule": "common/sql-injection", "location": "10-12"}],
        }
        finding = Finding("common/sql-injection", "BLOCKER", "order.py", "12-14")
        _, forbidden = evaluate(fixture, [finding])
        self.assertEqual(len(forbidden), 1)

    def test_wrong_catalog_severity_does_not_satisfy_required_finding(self) -> None:
        fixture = {
            "source": "order.py",
            "required": [{"rule": "common/sql-injection", "location": "10"}],
            "forbidden": [],
        }
        finding = Finding("common/sql-injection", "MAJOR", "order.py", "10")
        missing, _ = evaluate(
            fixture, [finding], {"common/sql-injection": "BLOCKER"}
        )
        self.assertEqual(len(missing), 1)

    def test_catalog_loader_includes_shared_and_language_rules(self) -> None:
        severities = load_severities()
        self.assertEqual(severities["common/sql-injection"], "BLOCKER")
        self.assertEqual(severities["rust/lock-across-await"], "BLOCKER")

    def test_absence_finding_needs_no_location(self) -> None:
        fixture = {
            "source": "Dockerfile",
            "required": [{"rule": "dockerfile/missing-healthcheck"}],
            "forbidden": [],
        }
        finding = Finding(
            "dockerfile/missing-healthcheck", "MINOR", "Dockerfile", None
        )
        self.assertEqual(evaluate(fixture, [finding]), ([], []))


if __name__ == "__main__":
    unittest.main()
