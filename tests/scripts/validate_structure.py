"""Validate Agent Skill structure against the agentskills.io spec."""

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"
MAX_SKILL_LINES = 500

REQUIRED_REFERENCES = ["typescript.md", "python.md", "java.md", "go.md"]

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"  WARN:  {msg}")


def ok(msg: str) -> None:
    print(f"  OK:    {msg}")


def validate_skill_md() -> None:
    print("\n--- Validating SKILL.md ---")

    if not SKILL_MD.exists():
        error("SKILL.md not found at repository root")
        return

    content = SKILL_MD.read_text()
    lines = content.splitlines()

    # Check frontmatter exists
    if not content.startswith("---"):
        error("SKILL.md must start with YAML frontmatter (---)")
        return

    # Extract frontmatter
    second_fence = content.index("---", 3)
    frontmatter = content[3:second_fence].strip()

    # Check required fields
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match:
        error("Missing required field: name")
    else:
        name = name_match.group(1).strip()
        validate_name(name)

    desc_match = re.search(r"^description:", frontmatter, re.MULTILINE)
    if not desc_match:
        error("Missing required field: description")
    else:
        ok("description field present")

    # Check line count
    body_lines = len(lines) - frontmatter.count("\n") - 3  # exclude frontmatter
    if body_lines > MAX_SKILL_LINES:
        error(f"SKILL.md body is {body_lines} lines (max {MAX_SKILL_LINES})")
    else:
        ok(f"SKILL.md body: {body_lines} lines (max {MAX_SKILL_LINES})")


def validate_name(name: str) -> None:
    # Spec constraints
    if len(name) > 64:
        error(f"name exceeds 64 chars: {len(name)}")
    if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", name):
        error(f"name '{name}' must be lowercase alphanumeric + hyphens, no leading/trailing hyphens")
    if "--" in name:
        error(f"name '{name}' contains consecutive hyphens")

    # Check name matches parent directory
    parent_dir = SKILL_ROOT.name
    if name != parent_dir:
        error(f"name '{name}' does not match parent directory '{parent_dir}'")
    else:
        ok(f"name '{name}' matches parent directory")


def validate_references() -> None:
    print("\n--- Validating references/ ---")

    if not REFERENCES_DIR.exists():
        error("references/ directory not found")
        return

    for ref_file in REQUIRED_REFERENCES:
        ref_path = REFERENCES_DIR / ref_file
        if not ref_path.exists():
            error(f"Missing reference: references/{ref_file}")
        else:
            line_count = len(ref_path.read_text().splitlines())
            ok(f"references/{ref_file} ({line_count} lines)")

    # Check no nested directories (spec: one level deep)
    for item in REFERENCES_DIR.iterdir():
        if item.is_dir():
            error(f"references/ should not contain subdirectories: {item.name}")


def validate_internal_links() -> None:
    print("\n--- Validating internal links ---")

    content = SKILL_MD.read_text()
    # Find markdown links to local files
    links = re.findall(r"\[.*?\]\(((?!https?://).*?)\)", content)

    for link in links:
        target = SKILL_ROOT / link
        if not target.exists():
            error(f"Broken link in SKILL.md: {link}")
        else:
            ok(f"Link valid: {link}")


def validate_test_samples() -> None:
    print("\n--- Validating test samples ---")

    tests_dir = SKILL_ROOT / "tests"
    if not tests_dir.exists():
        warn("tests/ directory not found")
        return

    languages = ["typescript", "python", "java", "go"]
    for lang in languages:
        lang_dir = tests_dir / lang
        if not lang_dir.exists():
            warn(f"No test directory for {lang}")
            continue

        samples = [f for f in lang_dir.iterdir() if not f.name.startswith("expected")]
        expecteds = [f for f in lang_dir.iterdir() if f.name.startswith("expected")]

        if not samples:
            warn(f"No test samples in tests/{lang}/")
        if not expecteds:
            warn(f"No expected findings in tests/{lang}/")

        for sample in samples:
            expected_name = f"expected-{sample.stem}.md"
            expected_path = lang_dir / expected_name
            if not expected_path.exists():
                warn(f"Sample {sample.name} missing expected findings: {expected_name}")
            else:
                ok(f"tests/{lang}/{sample.name} ↔ {expected_name}")


def main() -> None:
    print("=== Agent Skill Structure Validation ===")
    print(f"Root: {SKILL_ROOT}")

    validate_skill_md()
    validate_references()
    validate_internal_links()
    validate_test_samples()

    print("\n=== Summary ===")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\nFAILED — fix errors above")
        sys.exit(1)
    elif warnings:
        print("\nPASSED with warnings")
    else:
        print("\nPASSED")


if __name__ == "__main__":
    main()
