# ADR-0009: The review model is the user's choice; Sonnet is the measured default

Date: 2026-10-04

## Status

Accepted

## Decision

The skill does not pin a model. It runs on whatever model the agent session
uses. The README recommends a model per kind of review, using conformance
measurements taken on the same fixtures (ADR-0008):

| Model | Recall | Cost of one 25-fixture run |
|---|---|---|
| Sonnet 5.5 | 94.5% (six runs) | about $2 |
| Opus 5.5 | 96.7% (three runs) | about $6 |
| Fable 5.1 | 97.2% (three runs) | about $33 |

Sonnet is the recommendation for routine diffs, and it is the model the
weekly CI conformance run uses. Opus is the recommendation for
architecture-heavy changes, large refactors, and reviews before a release,
because it judges whole units better (`god-module` 80% against Sonnet's
57%). Fable is not recommended. Its lead over Opus is inside the noise
threshold, and it costs about five times as much.

## Considered Options

- A `model:` field in the `SKILL.md` frontmatter was rejected. It is a Claude
  Code extension that agent-skill-linter flags as non-portable. It would also
  take the choice away from the person who knows whether a diff is routine.
- Opus as the general recommendation was rejected. On these fixtures it finds
  2.2 points more than Sonnet at about three times the cost. That lead
  matters for architectural judgment but rarely changes the verdict on a
  routine diff.
- Fable for maximum recall was rejected. On these fixtures the extra cost
  bought no measurable recall over Opus.

## Consequences

The recommendation rests on fixtures written to be full of defects. It
compares the models with each other; it does not predict recall on an
ordinary diff. Repeat the comparison with three-run sets when a new model
generation ships, and update the README table and this record. The CI run
stays on Sonnet, so `--min-recall 0.89` holds for the model most users have.
