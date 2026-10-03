# ADR-0006: Reference severities resolve through the catalog

Date: 2026-10-02

## Status

Accepted

## Decision

A Language Reference never assigns a severity of its own. Every instruction
that can produce a finding names the catalogued rule it resolves to, written
inline as the rule ID, and takes that rule's severity. A "Prefer Modern
Features" table resolves to `common/language-idiom` unless a row's pattern
also matches a more specific rule in the same reference or the catalog; the
specific rule's ID and severity win.

Where reference prose disagreed with the catalog, each case was settled one of
two ways, following ADR-0003's rule that different merge impact means a
different identity:

- Align the prose to the existing rule (mutable default arguments, goroutines
  without cancellation, double type assertions, server and `EXPOSE` defaults).
- Add a rule with its own identity and severity, and a fixture that requires
  it: `common/n-plus-one-hot-path` (BLOCKER), `common/assertion-free-test`
  (MAJOR), `go/panic-in-library` (BLOCKER), `rust/hot-loop-clone` (MAJOR),
  `dockerfile/heavy-runtime-base` (MAJOR).

Guidance that no rule can carry is removed rather than left without an
identity. Two rule pairs are mutually exclusive by a condition the reviewer can
check from the code: `common/n-plus-one-hot-path` covers N+1 queries inside an
HTTP handler, route function, or RPC method and `common/n-plus-one-query` the
rest; `rust/hot-loop-clone` covers a collection or large value cloned on every
loop iteration and `rust/clone-to-compile` other borrow-avoiding clones.

APIs that the project's own toolchain deprecates or has removed resolve to
`common/deprecated-api` (MAJOR). The project's declared version (`go.mod`,
`requires-python`, `tsconfig.json`, the Spring Boot version, a `//go:build`
constraint) decides whether it fires, not the newest release.

## Considered Options

- Keeping inline severities as overrides was rejected. `SKILL.md` already
  forbids changing a rule's severity, so the overrides were either ignored or
  produced findings outside the catalog. The live conformance baseline recorded
  15% severity drift, highest on `common/weak-type-model`, which several
  conflicting prose severities mapped to.
- Raising every conflicting case to its own rule was rejected. Most prose
  severities restated the shared rule more loudly instead of describing a
  different merge impact.
- Making "in production" the N+1 split condition was rejected. A diff does not
  show production traffic; a handler or route registration is visible in code.
- Per-version rule sets, such as one deprecation rule per framework release,
  were rejected. One rule gated on the project's declared version keeps the
  catalog stable as toolchains move.

## Consequences

Severity drift should fall in live conformance runs, which is the measure to
check. Three languages now own rules (Go, Rust, Dockerfile), and the validator
already enforces that a reference only declares IDs under its own language.
Narrowing `common/n-plus-one-query` moved two existing required findings, in
the Go and Python order fixtures, to `common/n-plus-one-hot-path`.
