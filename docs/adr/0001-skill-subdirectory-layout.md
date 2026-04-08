# ADR-0001: Move skill artifact into skill/ subdirectory

Date: 2026-04-02

## Status

Accepted

## Context

SKILL.md and `references/` originally lived at the repo root alongside test fixtures,
CI configuration, and other non-skill artifacts. The Agent Skills spec (via
`agent-skill-linter` Rule 17) recommends isolating the installable skill artifact so
that `npx skills add` copies only what agents need — not the entire repo including
hundreds of lines of test samples and CI scripts.

## Decision

Move `SKILL.md` and `references/` into a `skill/` subdirectory. The repo root retains
`tests/`, `.github/`, `LICENSE`, and `README.md`. The `skill/` directory is the unit
that gets installed by `npx skills add William-Yeh/common-code-reviewer`.

`tests/scripts/validate_structure.py` was updated to distinguish `REPO_ROOT` (repo
root, used for `tests/`) from `SKILL_DIR` (`skill/`, used for SKILL.md and references).

## Consequences

- `npx skills add` installs a leaner artifact — only SKILL.md + references.
- Manual installation instructions updated: copy `skill/` not the repo root.
- The `version` field was simultaneously removed from SKILL.md frontmatter — it is not
  in the Agent Skills spec allowed fields (`name`, `description`, `license`, `metadata`,
  `allowed-tools`, `compatibility`). Version tracking is done via git tags only.
- Versioning going forward: bump the git tag; no in-file version to keep in sync.

## Amendment

Date: 2026-04-08

The `version` field was re-added to SKILL.md frontmatter in v1.1.0. The
`pre-publish-checklist` skill requires a `version` field to perform version-sync
checks (comparing SKILL.md against the latest git tag). The `agent-skill-linter`
passes with the field present, so the practical constraint is the tooling requirement,
not spec prohibition. Going forward, both the `version` field in SKILL.md and the git
tag must be kept in sync when publishing.
