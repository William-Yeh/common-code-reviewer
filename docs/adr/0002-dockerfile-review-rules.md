# ADR-0002: Add Dockerfile review rules as a language reference

Date: 2026-04-08

## Status

Accepted

## Context

The skill supported four language references (TypeScript, Python, Java, Go), all
detected by file extension. Dockerfiles are a common source of security and
operational issues — unpinned base images, secrets baked into layers, containers
running as root — that are distinct from application code quality and not covered
by existing references.

Two characteristics make Dockerfile review rules different from the existing set:
1. Detection is by **filename** (`Dockerfile`, `Dockerfile.*`, `*.dockerfile`), not
   by extension. The language detection table needed to document this explicitly.
2. The rule categories do not map cleanly to SOLID/FP/Clean Code. Dockerfile review
   centers on image provenance, layer hygiene, multi-stage build discipline, and
   supply chain security — a separate concern axis.

## Decision

Add `skill/references/dockerfile.md` with 15 rules covering:
- Base image hygiene (pinned digests, minimal bases, `FROM latest` prohibition, non-root USER)
- Multi-stage builds (separation of build/runtime stages, named stages, precise `COPY --from`)
- Layer and cache optimization (instruction ordering, combined `RUN` with cleanup, `COPY` vs `ADD`)
- Security (no baked-in secrets, TLS verification, artifact checksum, `HEALTHCHECK`)

Add two test fixtures (`tests/dockerfile/Dockerfile-app`, `tests/dockerfile/Dockerfile-builder`)
covering all 15 rules, paired with expected-findings files. Update `validate_structure.py`
to include `dockerfile.md` in `REQUIRED_REFERENCES` and `dockerfile` in the test languages list.

## Consequences

- Coverage increases from 82% (36/44 rules) to 86% (51/59 rules).
- The language detection section of SKILL.md now mixes extension-based and
  filename-based patterns in the same table — reviewers must handle both.
- All 15 Dockerfile rules are covered by test fixtures (100% for this reference),
  compared to ~82% average for existing language references.
- SKILL.md body remains well within the 500-line limit (207 lines after the addition).
