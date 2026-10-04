#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
#   "hypothesis==6.140.2",
# ]
# ///

"""Tests for semantic Conformance Finding matching."""

import contextlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st

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
    Summary,
    format_summary,
    main,
    verdict,
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


def clean_result(passed: bool) -> dict[str, object]:
    return {"passed": passed, "missing": [] if passed else [{}], "forbidden": [], "interface_errors": []}


RESULTS = st.lists(st.booleans().map(clean_result), min_size=1, max_size=20)
RECALL = st.integers(min_value=1, max_value=700).flatmap(
    lambda total: st.tuples(st.integers(min_value=0, max_value=total), st.just(total))
)
THRESHOLD = st.floats(min_value=0.0, max_value=1.0)


class VerdictProperties(unittest.TestCase):
    @given(RESULTS, RECALL)
    def test_without_a_threshold_every_fixture_must_pass(self, results, recall) -> None:
        self.assertEqual(verdict(results, recall, None), all(r["passed"] for r in results))

    @given(RESULTS, RECALL, THRESHOLD)
    def test_with_a_threshold_clean_runs_pass_exactly_when_recall_reaches_it(self, results, recall, threshold) -> None:
        found, total = recall
        self.assertEqual(verdict(results, recall, threshold), found / total >= threshold)

    @given(RESULTS, RECALL, THRESHOLD, st.sampled_from(["runtime_error", "forbidden", "interface_errors"]))
    def test_a_runtime_error_forbidden_finding_or_drift_always_fails(self, results, recall, threshold, defect) -> None:
        broken = {"runtime_error": "Not logged in", "passed": False} if defect == "runtime_error" else {
            **clean_result(True), defect: [{"rule": "common/x"}], "passed": False}
        self.assertFalse(verdict([*results, broken], recall, threshold))
        self.assertFalse(verdict([*results, broken], recall, None))

    @given(RESULTS, THRESHOLD)
    def test_a_run_with_no_scored_expectations_never_passes_a_threshold(self, results, threshold) -> None:
        self.assertFalse(verdict(results, (0, 0), threshold))


RULE_IDS = st.sampled_from([f"common/rule-{n}" for n in range(8)])
KEYS = st.tuples(st.just("tests/go/svc.go.fixture.yaml"), st.integers(0, 30), RULE_IDS)
SUMMARIES = st.builds(
    Summary,
    recall=RECALL,
    per_rule=st.dictionaries(
        RULE_IDS, st.integers(1, 9).flatmap(lambda t: st.tuples(st.integers(0, t), st.just(t)))
    ),
    systematic=st.lists(KEYS, max_size=5),
    flaky=st.lists(KEYS, max_size=5),
)


class FormatSummaryProperties(unittest.TestCase):
    @given(SUMMARIES, st.integers(1, 9))
    def test_header_states_recall_and_run_count(self, summary, runs) -> None:
        found, total = summary.recall
        header = format_summary(summary, runs).split("\n")[0]
        self.assertTrue(header.startswith(f"recall {found}/{total} ("))
        self.assertTrue(header.endswith(f"over {runs} run(s)"))

    @given(SUMMARIES)
    def test_exactly_the_rules_found_less_than_fully_are_listed(self, summary) -> None:
        lines = format_summary(summary, 1).split("\n")
        listed = {line.split()[0] for line in lines if line.startswith("common/")}
        self.assertEqual(listed, {rule for rule, (f, t) in summary.per_rule.items() if f < t})

    @given(SUMMARIES)
    def test_section_counts_match_their_lists(self, summary) -> None:
        text = format_summary(summary, 1)
        self.assertIn(f"systematic misses (never found): {len(summary.systematic)}", text)
        self.assertIn(f"flaky expectations (found in some runs): {len(summary.flaky)}", text)
        self.assertEqual(sum(line.startswith("  tests/") for line in text.split("\n")),
                         len(summary.systematic) + len(summary.flaky))


FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
if "--version" in sys.argv:
    print("fake-claude 1.0")
    sys.exit(0)
if os.environ.get("FAKE_CLAUDE_FAIL"):
    print("Not logged in", file=sys.stderr)
    sys.exit(1)
markdown = open(os.environ["FAKE_CLAUDE_MARKDOWN"]).read()
print(json.dumps({"result": markdown, "total_cost_usd": 0.01, "modelUsage": {"fake-model": {}}}))
"""


class MainEndToEnd(unittest.TestCase):
    """Runs main() in-process against a fake claude executable on PATH."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        fake = self.tmp / "claude"
        fake.write_text(FAKE_CLAUDE.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        fixture = REPO_ROOT / "tests/go/edge_proxy.go.fixture.yaml"
        import yaml
        required = yaml.safe_load(fixture.read_text())["required"]
        severities = load_severities()
        self.markdown = self.tmp / "review.md"
        self.markdown.write_text("".join(
            f"### [{severities[e['rule']]}] finding\n**File:** `tests/go/edge_proxy.go:{e['location']}`\n"
            f"**Rule:** `{e['rule']}`\n\n" for e in required))
        self.report = self.tmp / "report.json"
        self.env = {"PATH": f"{self.tmp}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_CLAUDE_MARKDOWN": str(self.markdown)}

    def run_main(self, *argv: str, **env: str) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.dict(os.environ, {**self.env, **env}), mock.patch.object(
            sys, "argv", ["run_conformance.py", *argv]
        ), contextlib.redirect_stdout(out):
            try:
                main()
                code = 0
            except SystemExit as exit_:
                code = int(exit_.code or 0)
        return code, out.getvalue()

    def test_live_run_that_finds_everything_passes_and_records_recall(self) -> None:
        code, out = self.run_main("--fixture", "edge_proxy", "--report", str(self.report), "--min-recall", "1.0")
        report = json.loads(self.report.read_text())
        self.assertEqual(code, 0)
        self.assertEqual((report["recall"], report["runtime_version"], report["passed"]), ([3, 3], "fake-claude 1.0", True))
        self.assertIn("recall 3/3 (100.0%) over 1 run(s)", out)

    def test_cli_failure_is_recorded_as_a_runtime_error_and_fails_the_run(self) -> None:
        code, _ = self.run_main("--fixture", "edge_proxy", "--report", str(self.report), "--min-recall", "0.5",
                                FAKE_CLAUDE_FAIL="1")
        result = json.loads(self.report.read_text())["fixtures"][0]
        self.assertEqual((code, result["runtime_error"]), (1, "Not logged in"))

    def test_summarize_reads_saved_reports_without_calling_the_cli(self) -> None:
        self.run_main("--fixture", "edge_proxy", "--report", str(self.report))
        code, out = self.run_main("--summarize", str(self.report), FAKE_CLAUDE_FAIL="1")
        self.assertEqual((code, out.splitlines()[0]), (0, "recall 3/3 (100.0%) over 1 run(s)"))


if __name__ == "__main__":
    unittest.main()
