# ADR-0005: Change risk scoring without executable tooling

Date: 2026-09-05

## Status

Accepted

## Decision

The skill scores every named function a change touches with the CRAP formula,
`CC² × (1 − cov)³ + CC`, and reports the result in two ways: a Risk Report that
ranks every scored unit worst-first, and three catalog rules that fire at fixed
lines. The lines are 30 (`common/critical-change-risk`, MAJOR), 8
(`common/elevated-change-risk`, MINOR), and a CC line of 6
(`common/excess-complexity`, MINOR). At most one of the three fires per
function: the CC rule applies only where coverage already keeps the CRAP Score
at or under 8, so it reports complexity that tests cannot hide. The 30 line is the classic threshold from
Savoia and Evans; the 8 line and the CC line follow Robert C. Martin's practice
for agent-written code, where `crap4java` fails above 8.0 and his agent
constraints hold CC to "4 or so". Both sources are cited in the README.

The skill runs no tools. Cyclomatic complexity is counted from source by the
reviewer using one shared calculation, instantiated per language by a Scoring
Profile with five fixed slots. Coverage comes only from Coverage Evidence that
already exists in the workspace (LCOV, Cobertura, JaCoCo XML, Go coverprofile).
When no evidence exists the score is computed at 0% coverage and labelled
"worst case". `lizard` is the reference oracle for CC across all languages;
each profile records where it, or the team's usual gate, deviates.

## Considered Options

- Running coverage and complexity tools from the skill was rejected. ADR-0003
  forbids installation dependencies, and live conformance runs read-only, so a
  tool-driven rule could never be certified.
- Reporting `N/A` when coverage is absent, as Martin's tools do, was rejected
  for a reviewer. A ranked risk signal with no coverage is still the signal the
  reviewer exists to give; hiding it would silence the metric on most diffs.
  The label keeps the number honest.
- A single line at 8 or at 30 was rejected. One rule has one severity, and the
  two lines carry different merge impact.
- Per-language mainstream tools as the CC oracle were rejected because their
  counting rules disagree (ruff omits boolean operators, ESLint adds optional
  chaining, Rust has no mainstream cyclomatic tool). `lizard` covers every
  supported language with one rule that counts boolean operators, matching
  Martin's own implementations.
- Excluding constructors, as `crap4java` does, was rejected. That exclusion is
  a JaCoCo reporting artefact; a constructor with branches is exactly the risk
  the skill already hunts under `common/complex-construction`.

## Consequences

`skill/languages.yaml` declares `scored` per language and the generated
Language Detection table shows it, so the skill prose names no language. Every
scored reference must carry a Change Risk section with all five Scoring Profile
slots and a Decision Points row per shared category; the validator enforces it. The Risk Report is evidence,
not a Review Finding, so it prints in full under `--relaxed`. Test files are
never scored. The measured-coverage path has fixture evidence via a committed
LCOV report beside a Python fixture, which the live runner is told about.
