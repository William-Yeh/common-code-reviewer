#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Tests for the deterministic structure validator."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import validate_structure

from validate_structure import (
    SCORING_PROFILE_SLOTS,
    Rule,
    covers_source,
    decision_categories,
    detection_ambiguities,
    duplicate_ids,
    expectation_lists,
    expectation_problems,
    fixture_coverage_problem,
    fixture_fatal_problem,
    fixture_header_problems,
    language_entry_problems,
    load_fixture,
    location_parts,
    location_problem,
    missing_fixture_dirs,
    non_code_parts,
    profile_gaps,
    register_language,
    registry_languages,
    uncovered_rules,
)

CATEGORIES = ["Branch", "Loop"]

FULL_PROFILE = """\
# Python Review Rules

## Change Risk

### Scored Units
text

### Decision Points

| Category | Python |
|---|---|
| Branch | `if` |
| Loop | `for` |

### Test Files
text

### Coverage Evidence
text

### Oracle Deviations
text
"""


class ScoringProfileTests(unittest.TestCase):
    def test_scored_language_with_every_slot_and_category_has_no_gaps(self) -> None:
        self.assertEqual(profile_gaps(FULL_PROFILE, scored=True, categories=CATEGORIES), [])

    def test_scored_language_missing_one_slot_names_it(self) -> None:
        text = FULL_PROFILE.replace("### Test Files\ntext\n\n", "")
        self.assertEqual(profile_gaps(text, scored=True, categories=CATEGORIES), ["### Test Files"])

    def test_scored_language_without_change_risk_section_reports_everything(self) -> None:
        text = "# Go Review Rules\n\n## Style Standard\n"
        gaps = profile_gaps(text, scored=True, categories=CATEGORIES)
        self.assertEqual(gaps[:6], ["## Change Risk", *SCORING_PROFILE_SLOTS])
        self.assertEqual(gaps[6:], ["Decision Points row: Branch", "Decision Points row: Loop"])

    def test_missing_decision_point_category_is_named(self) -> None:
        text = FULL_PROFILE.replace("| Loop | `for` |\n", "")
        self.assertEqual(
            profile_gaps(text, scored=True, categories=CATEGORIES), ["Decision Points row: Loop"]
        )

    def test_unscored_language_needs_nothing(self) -> None:
        self.assertEqual(profile_gaps("# Dockerfile Review Rules\n", scored=False, categories=CATEGORIES), [])

    def test_categories_come_from_the_shared_table_in_skill_md(self) -> None:
        skill = "text\n\n| Category | Counts | Never counts |\n|---|---|---|\n| Branch | `if` | `else` |\n| Loop | headers | |\n\nmore\n"
        self.assertEqual(decision_categories(skill), ["Branch", "Loop"])


SOURCE = [
    "import os",                      # 1
    "",                               # 2
    "# [ISSUE: shell out with user input]",  # 3
    "os.system(cmd)",                 # 4
    "    // trailing comment",        # 5
    "    /* block */",                # 6
    "*count++",                       # 7
]
C_LIKE = ["//", "/*"]


class LocationPointsAtCodeTests(unittest.TestCase):
    def test_single_line_of_code_is_fine(self) -> None:
        self.assertEqual(non_code_parts("4", SOURCE, ["#"]), [])

    def test_blank_line_is_reported(self) -> None:
        self.assertEqual(non_code_parts("2", SOURCE, ["#"]), ["2"])

    def test_comment_only_line_is_reported_per_language_prefix(self) -> None:
        self.assertEqual(non_code_parts("3", SOURCE, ["#"]), ["3"])
        self.assertEqual(non_code_parts("3", SOURCE, C_LIKE), [])
        self.assertEqual(non_code_parts("5-6", SOURCE, C_LIKE), ["5-6"])

    def test_pointer_dereference_is_code_not_a_comment(self) -> None:
        self.assertEqual(non_code_parts("7", SOURCE, C_LIKE), [])

    def test_range_needs_only_one_code_line(self) -> None:
        self.assertEqual(non_code_parts("2-4", SOURCE, ["#"]), [])

    def test_each_comma_part_is_judged_on_its_own(self) -> None:
        self.assertEqual(non_code_parts("2, 4, 3", SOURCE, ["#"]), ["2", "3"])


class LocationGrammarTests(unittest.TestCase):
    def test_parts_become_inclusive_ranges(self) -> None:
        self.assertEqual(
            [list(part) for part in location_parts("2-4, 8, 10-9")],
            [[2, 3, 4], [8], [9, 10]],
        )


class CoverageEvidenceTests(unittest.TestCase):
    def test_lcov_record_covers_source(self) -> None:
        self.assertTrue(covers_source("SF:tests/python/a.py\nDA:1,1\n", "a.py"))

    def test_cobertura_and_coverprofile_records_cover_source(self) -> None:
        self.assertTrue(covers_source('<class name="a" filename="tests/python/a.py">', "a.py"))
        self.assertTrue(covers_source("example.com/m/pkg/a.go:3.10,5.2 1 1\n", "a.go"))

    def test_a_longer_name_sharing_the_suffix_does_not_count(self) -> None:
        self.assertFalse(covers_source("SF:tests/python/test_a.py\n", "a.py"))
        self.assertFalse(covers_source("<coverage/>", "a.py"))


def language(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": "python",
        "reference": "references/python.md",
        "extensions": [".py"],
        "filenames": [],
        "scored": True,
        "comment_prefixes": ["#"],
    }
    entry.update(overrides)
    return entry


class RegistryEntryTests(unittest.TestCase):
    def test_well_formed_entry_has_no_problems(self) -> None:
        self.assertEqual(language_entry_problems(language()), [])

    def test_each_malformed_field_is_named(self) -> None:
        problems = language_entry_problems(
            language(id="Py thon", extensions=[], scored="yes", comment_prefixes="#")
        )
        self.assertEqual(
            problems,
            [
                "invalid language id: 'Py thon'",
                "Py thon: no detection patterns",
                "Py thon: 'scored' must be true or false",
                "Py thon: 'comment_prefixes' must be a list",
            ],
        )


class DetectionAmbiguityTests(unittest.TestCase):
    def test_distinct_patterns_are_unambiguous(self) -> None:
        languages = [language(), language(id="go", extensions=[".go"])]
        self.assertEqual(detection_ambiguities(languages), [])

    def test_shared_extension_is_reported_for_both_languages(self) -> None:
        languages = [language(), language(id="stub", extensions=[".py"])]
        self.assertEqual(
            detection_ambiguities(languages),
            [
                "python: detection example 'example.py' matched ['python', 'stub']",
                "stub: detection example 'example.py' matched ['python', 'stub']",
            ],
        )


RULES = {"common/dead-code": Rule("common/dead-code", "MINOR", None), "rust/x": Rule("rust/x", "NIT", None)}
PY_LINES = ["import os", "", "os.system(cmd)"]


class ExpectationTests(unittest.TestCase):
    def check(self, expectations: list[dict[str, object]]) -> tuple[list[str], list[tuple[str, object]]]:
        return expectation_problems(
            "required",
            expectations,
            rules=RULES,
            language_id="python",
            source_lines=PY_LINES,
            comment_prefixes=["#"],
        )

    def test_valid_expectation_yields_no_problems_and_its_evidence(self) -> None:
        problems, evidence = self.check([{"rule": "common/dead-code", "location": "3", "rationale": "r"}])
        self.assertEqual(problems, [])
        self.assertEqual(evidence, [("common/dead-code", "3")])

    def test_absence_expectation_has_no_location(self) -> None:
        _, evidence = self.check([{"rule": "common/dead-code", "rationale": "r"}])
        self.assertEqual(evidence, [("common/dead-code", None)])

    def test_unknown_rule_stops_further_checks_for_that_expectation(self) -> None:
        problems, evidence = self.check([{"rule": "common/nope", "location": "99"}])
        self.assertEqual(problems, ["required[1] uses unknown rule 'common/nope'"])
        self.assertEqual(evidence, [])

    def test_every_other_problem_is_reported_with_its_index(self) -> None:
        problems, _ = self.check(
            [
                {"rule": "rust/x", "location": "2", "rationale": 3},
                {"rule": "common/dead-code", "location": "9", "rationale": "r"},
                {"rule": "common/dead-code", "location": "3", "rationale": "r"},
                {"rule": "common/dead-code", "location": "3", "rationale": "r"},
            ]
        )
        self.assertEqual(
            problems,
            [
                "required[1] uses rust rule for python input",
                "required[1] location 2 points at no code (rust/x)",
                "required[1] requires a rationale",
                "required[2] has invalid location '9' for 3 lines",
                "duplicate required expectation ('common/dead-code', '3')",
            ],
        )


class RepositoryTests(unittest.TestCase):
    def test_this_repository_passes_structural_validation(self) -> None:
        """The repository is its own fixture: the full validator must pass on it."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            problems = validate_structure.run()
        self.assertEqual(problems, [])
        self.assertIn("PASSED", output.getvalue())


class ErrorPathTests(unittest.TestCase):
    """The shells' failure branches, exercised through their pure or file-scoped parts."""

    def setUp(self) -> None:
        validate_structure.errors.clear()
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_registry_file_problems_are_reported_and_yield_none(self) -> None:
        missing = self.tmp / "none.yaml"
        self.assertIsNone(registry_languages(missing))
        empty = self.tmp / "empty.yaml"
        empty.write_text("languages: []\n")
        self.assertIsNone(registry_languages(empty))
        self.assertEqual(len(validate_structure.errors), 2)

    def test_register_language_skips_non_string_ids(self) -> None:
        self.assertIsNone(register_language(language(id=7)))
        self.assertEqual(validate_structure.errors, ["invalid language id: 7"])

    def test_duplicate_ids_are_reported_once_each(self) -> None:
        self.assertEqual(
            duplicate_ids([language(), language(), language(id="go")]),
            ["duplicate language id: python"],
        )

    def test_location_problem_distinguishes_out_of_range_from_dead_lines(self) -> None:
        self.assertIn("invalid location", location_problem("9", PY_LINES, ["#"], "r") or "")
        self.assertIn("points at no code", location_problem("2", PY_LINES, ["#"], "r") or "")
        self.assertIsNone(location_problem("1", PY_LINES, ["#"], "r"))

    def test_expectation_lists_reject_bad_shapes(self) -> None:
        self.assertEqual(expectation_lists({"required": []}), ([], [], ["required must be a non-empty list"]))
        self.assertEqual(
            expectation_lists({"required": [{}], "forbidden": "x"}),
            ([{}], [], ["forbidden must be a list"]),
        )

    def test_fixture_fatal_problems(self) -> None:
        by_id = {"python": language()}
        self.assertEqual(fixture_fatal_problem({"language": "cobol"}, self.tmp / "f", by_id), "unknown language 'cobol'")
        self.assertEqual(
            fixture_fatal_problem({"language": "python", "source": "gone.py"}, self.tmp / "f", by_id),
            "source does not exist: gone.py",
        )

    def test_fixture_header_problems_name_each_mismatch(self) -> None:
        self.assertEqual(
            fixture_header_problems({"version": 2}, language(), "wrong.yaml", "a.go"),
            ["unsupported fixture version", "'a.go' does not match python detection patterns", "expected filename a.go.fixture.yaml"],
        )

    def test_fixture_coverage_problem_is_none_without_a_declaration(self) -> None:
        self.assertIsNone(fixture_coverage_problem({}, self.tmp / "f", "a.py"))
        self.assertEqual(
            fixture_coverage_problem({"coverage": "lcov.info"}, self.tmp / "f", "a.py"),
            "Coverage Evidence does not exist: lcov.info",
        )

    def test_load_fixture_reports_invalid_yaml(self) -> None:
        bad = self.tmp / "bad.fixture.yaml"
        bad.write_text("required: [\n")
        self.assertIsNone(load_fixture(bad, "bad"))
        self.assertTrue(validate_structure.errors[0].startswith("bad: invalid YAML"))

    def test_missing_fixture_dirs_and_uncovered_rules(self) -> None:
        self.assertEqual(missing_fixture_dirs({"cobol": language(id="cobol")}), ["cobol: requires at least one Conformance Fixture"])
        self.assertEqual(uncovered_rules({"a/x": [], "a/y": ["e"]}), ["1 Review Rules lack fixture coverage: a/x"])
        self.assertEqual(uncovered_rules({"a/y": ["e"]}), [])


if __name__ == "__main__":
    unittest.main()
