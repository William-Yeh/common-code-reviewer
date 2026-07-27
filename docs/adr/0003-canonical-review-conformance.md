# ADR-0003: Canonical review rules and runtime-specific conformance

Date: 2026-07-27

## Status

Accepted

## Decision

The installable `skill/` artifact owns every Review Rule, its immutable
ownership-based identity, its severity, and the canonical language registry.
Repository-only tooling consumes that knowledge to generate documentation and
verify Conformance Fixtures; it must not become an installation dependency.

Conformance is semantic and recall-oriented: required findings match by rule
identity, file, and overlapping location where applicable; additional findings
are allowed unless a fixture explicitly forbids them. A rule has one severity,
so cases with different merge impact use different identities. Live evidence is
runtime-specific, beginning with read-only Claude Code `sonnet` runs, and does
not imply conformance for other Agent Skills-compatible runtimes.

## Considered Options

- A repository-level rule manifest was rejected because it would split rule
  identity from meaning and make the installed skill depend on repository
  artifacts.
- Exact prose or exact-set matching was rejected because model wording and
  ordering are nondeterministic and useful additional findings should remain
  possible.
- A required live-model pull-request check was deferred until scheduled runs
  demonstrate enough stability to justify blocking merges.

## Consequences

Every instruction capable of producing a finding must carry a visible rule
identity and severity. Language tables are generated from
`skill/languages.yaml`; fixtures use canonical YAML; deterministic validation is
required in pull requests, while live Claude Code conformance initially runs
manually and on a schedule.
