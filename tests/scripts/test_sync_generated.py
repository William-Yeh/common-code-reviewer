#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML==6.0.2",
# ]
# ///

"""Tests for the generated-table builders."""

import unittest

from sync_generated import patterns, readme_table, skill_table

LANGUAGES = [
    {
        "id": "go",
        "name": "Go",
        "reference": "references/go.md",
        "extensions": [".go"],
        "filenames": [],
        "frameworks": ["stdlib"],
        "style": "Effective Go",
        "scored": True,
    },
    {
        "id": "dockerfile",
        "name": "Dockerfile",
        "reference": "references/dockerfile.md",
        "extensions": [],
        "filenames": ["Dockerfile", "*.dockerfile"],
        "frameworks": ["Docker"],
        "style": "Docker best practices",
        "scored": False,
    },
]


class TableTests(unittest.TestCase):
    def test_patterns_list_extensions_then_filenames(self) -> None:
        self.assertEqual(patterns(LANGUAGES[1]), "`Dockerfile`, `*.dockerfile`")

    def test_skill_table_shows_the_scored_flag_per_language(self) -> None:
        rows = skill_table(LANGUAGES).splitlines()
        self.assertEqual(rows[0], "| Patterns | Language | Reference | Change Risk |")
        self.assertEqual(rows[2], "| `.go` | Go | [references/go.md](references/go.md) | scored |")
        self.assertTrue(rows[3].endswith("| not scored |"))

    def test_readme_table_lists_frameworks_and_style(self) -> None:
        self.assertEqual(readme_table(LANGUAGES).splitlines()[2], "| Go | stdlib | Effective Go |")


if __name__ == "__main__":
    unittest.main()
