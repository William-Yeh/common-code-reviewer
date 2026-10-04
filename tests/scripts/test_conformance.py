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
    score_report,
    score_result,
    summarize_runs,
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

    def test_prompt_discounts_the_harness_tests_directory(self) -> None:
        # Scoring Profiles treat paths under tests/ as test files, and every fixture lives there;
        # the reviewer must judge from the file's own name and content (some fixtures are tests).
        prompt = prompt_for(self.FIXTURE_PATH, {"language": "python", "source": "pricing_engine.py"})
        self.assertIn("tests/python/ is this harness's fixture directory", prompt)
        self.assertIn("own name and content", prompt)


class FindingParserTests(unittest.TestCase):
    def finding_at(self, file_line: str) -> list[Finding]:
        return parse_findings(
            f"### [MAJOR] Issue\n**File:** {file_line}\n**Rule:** `common/god-module`\n"
        )

    def test_extra_sites_after_the_primary_location_are_merged(self) -> None:
        # Shapes the reviewer produced in the 2026-10-02 live run.
        cases = {
            "`tests/x.go:5`, also `:12`": "5, 12",
            "`tests/x.go:19` (also `:24`, `:25`)": "19, 24, 25",
            "`tests/x.go:54` (also `:61`, `:88-91`)": "54, 61, 88-91",
            "`tests/x.go:9` (same pattern at `:17`)": "9, 17",
        }
        for file_line, location in cases.items():
            with self.subTest(file_line=file_line):
                self.assertEqual(
                    self.finding_at(file_line),
                    [Finding("common/god-module", "MAJOR", "tests/x.go", location)],
                )

    def test_primary_location_is_the_first_span_that_carries_a_line(self) -> None:
        # Verbatim from the 2026-10-03 live run: the reviewer corrected its own path mid-line.
        file_line = (
            "`src/order_service.py` is not the path. "
            "The file is `tests/python/order_service.py:29-31, 54, 68`"
        )
        self.assertEqual(
            self.finding_at(file_line),
            [Finding("common/god-module", "MAJOR", "tests/python/order_service.py", "29-31, 54, 68")],
        )

    def test_unparseable_file_line_never_borrows_the_next_finding(self) -> None:
        markdown = (
            "### [BLOCKER] First\n**File:** see below\n**Rule:** `common/sql-injection`\n\n"
            "### [NIT] Second\n**File:** `tests/x.go:3`\n**Rule:** `common/style-naming`\n"
        )
        self.assertEqual(
            parse_findings(markdown),
            [
                Finding("common/sql-injection", "BLOCKER", "see below", None),
                Finding("common/style-naming", "NIT", "tests/x.go", "3"),
            ],
        )

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



FIXTURE = {
    "source": "svc.go",
    "required": [
        {"rule": "common/ignored-error", "location": "10"},
        {"rule": "common/god-module", "location": "3"},
    ],
    "forbidden": [],
}
HIT_ONLY_IGNORED = (
    "### [BLOCKER] Ignored error\n**File:** `tests/go/svc.go:10`\n**Rule:** `common/ignored-error`\n"
)


def run_report(markdown: str) -> dict[str, object]:
    return {"fixtures": [{"fixture": "tests/go/svc.go.fixture.yaml", "markdown": markdown}]}


class RecallTests(unittest.TestCase):
    SEVERITIES = {"common/ignored-error": "BLOCKER", "common/god-module": "MAJOR"}

    def score(self, report: dict[str, object]) -> list[tuple[str, int, str, bool]]:
        return score_report(report, lambda _path: FIXTURE, self.SEVERITIES)

    def test_each_required_expectation_becomes_a_hit_or_miss_row(self) -> None:
        self.assertEqual(
            self.score(run_report(HIT_ONLY_IGNORED)),
            [
                ("tests/go/svc.go.fixture.yaml", 0, "common/ignored-error", True),
                ("tests/go/svc.go.fixture.yaml", 1, "common/god-module", False),
            ],
        )

    def test_runtime_errors_are_excluded_rather_than_counted_as_misses(self) -> None:
        report = {"fixtures": [{"fixture": "tests/go/svc.go.fixture.yaml", "runtime_error": "Not logged in"}]}
        self.assertEqual(self.score(report), [])

    def test_summary_reports_recall_per_rule_and_expectation_stability(self) -> None:
        both = (
            HIT_ONLY_IGNORED
            + "\n### [MAJOR] God module\n**File:** `tests/go/svc.go:3`\n**Rule:** `common/god-module`\n"
        )
        runs = [self.score(run_report(m)) for m in (HIT_ONLY_IGNORED, both, HIT_ONLY_IGNORED)]
        summary = summarize_runs(runs)
        self.assertEqual(summary.recall, (4, 6))
        self.assertEqual(summary.per_rule, {"common/ignored-error": (3, 3), "common/god-module": (1, 3)})
        self.assertEqual(summary.flaky, [("tests/go/svc.go.fixture.yaml", 1, "common/god-module")])
        self.assertEqual(summary.systematic, [])

    def test_an_expectation_missed_in_every_run_is_systematic(self) -> None:
        runs = [self.score(run_report(HIT_ONLY_IGNORED)) for _ in range(3)]
        self.assertEqual(
            summarize_runs(runs).systematic, [("tests/go/svc.go.fixture.yaml", 1, "common/god-module")]
        )


class ScoreResultTests(unittest.TestCase):
    def test_result_records_misses_drift_cost_and_pass_state(self) -> None:
        drifted = HIT_ONLY_IGNORED.replace("[BLOCKER]", "[MINOR]")
        result = score_result(
            "tests/go/svc.go.fixture.yaml",
            drifted,
            {"total_cost_usd": 0.07, "modelUsage": {"m": {}}},
            FIXTURE,
            RecallTests.SEVERITIES,
        )
        self.assertFalse(result["passed"])
        # A finding at the wrong catalog severity satisfies nothing, so both expectations miss.
        self.assertEqual(result["missing"], FIXTURE["required"])
        self.assertEqual(
            result["interface_errors"],
            [{"rule": "common/ignored-error", "severity": "MINOR", "file": "tests/go/svc.go", "location": "10"}],
        )
        self.assertEqual((result["cost_usd"], result["markdown"]), (0.07, drifted))


if __name__ == "__main__":
    unittest.main()
