# ADR-0004: Accepted agent-skill-linter semantic deviations

Date: 2026-07-27

## Status

Accepted

## Context

`agent-skill-linter` passes cleanly on all mechanical rules (zero errors, zero
warnings) against `skill/`. Its semantic review steps — which require agent
judgment rather than pattern matching — surface two items that are technically
non-conforming but whose fixes carry costs exceeding their benefit.

Recording them here prevents rediscovery and re-litigation on every subsequent
lint run.

## Decision

### 1. Skill name retained as `common-code-reviewer` (Rule 12)

Rule 12 prefers action-oriented names (gerunds) over noun phrases, and its
reference material lists `code-reviewer` explicitly as flag-worthy. The
conforming form would be `reviewing-code`.

The name is retained unchanged because it is load-bearing across published
surfaces:

- the git remote, `William-Yeh/common-code-reviewer`
- the documented install path, `npx skills add William-Yeh/common-code-reviewer`
- the CI badge URL in README
- the invocation surface, `/common-code-reviewer`
- a reference in ADR-0001

Renaming a published v1.2.0 skill breaks every existing install. The routing
signal that agents actually match on is `description`, which already conforms
to Rule 11/18 as a single trigger clause.

### 2. Review Rule Catalog kept inline in SKILL.md (Rule 16)

Rule 16 flags dense, reactively-consulted sections for extraction to
`references/`. The Review Rule Catalog qualifies on density: 63 lines and 54
table rows, roughly 22% of the SKILL.md body.

It is kept inline because progressive disclosure optimizes for *conditionally*
needed content. The language references in `references/` are loaded only when
the corresponding language is detected in the diff. The common rule catalog has
no such skip path — Review Process step 6 requires resolving every finding
against it on every invocation, so extraction would trade always-present context
for a mandatory extra file read with no offsetting benefit.

SKILL.md is 286 lines, well inside the 500-line Rule 9 threshold, so there is no
body-length pressure forcing the split.

## Consequences

- Future lint runs will re-surface both items. They are accepted, not
  outstanding — treat this ADR as the resolution.
- The `description` field carries the full routing burden for this skill. It
  must remain a precise trigger clause; degrading it would remove the
  justification for deviation 1.
- Revisit deviation 1 only alongside a deliberate breaking release, where the
  install-path churn is already being absorbed for other reasons.
- Revisit deviation 2 if SKILL.md approaches the Rule 9 500-line threshold, or
  if the catalog itself grows enough that always-loaded cost exceeds the cost of
  one extra read. A partial extraction — BLOCKER rules inline, the rest in
  `references/` — was considered and remains the preferred fallback.
