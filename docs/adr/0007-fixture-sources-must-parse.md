# ADR-0007: Fixture sources must parse, not compile

Date: 2026-10-02

## Status

Accepted

## Decision

Every Conformance Fixture source must parse without syntax errors under the
tree-sitter grammar for its `languages.yaml` id (`tsx` for `.tsx` and `.jsx`).
`validate_structure.py` checks this in CI using `tree-sitter-language-pack`,
pinned in the script's PEP 723 header and installed by `uv`, and reports each
failing line. Fixtures stay excerpts: references to types, packages, and
functions outside the file are allowed.

## Considered Options

- Compiling every fixture was rejected. Fixtures reference application classes
  and test libraries that are not in the repository, so a compile would need
  stub code and downloaded dependencies maintained only to satisfy compilers,
  and that code would drift from what the fixtures show.
- Compiling only self-contained fixtures with real toolchains pinned through
  `mise` was rejected as a CI gate. It needs a JDK, Go, Rust, and Node in CI
  and a per-fixture flag, and it checks only the few fixtures that happen to
  be self-contained. `go vet`, `rustc --emit=metadata`, and `javac` remain
  useful local checks for authors.

## Consequences

A syntax slip in a fixture now fails CI, where before it would shift what the
reviewer reads away from the fixture's line numbers and show up only as an
unexplained miss in a paid live run. Type errors and undefined symbols are
still not caught; that is intended. Scripts that import `validate_structure.py`
without parsing fixtures (`run_conformance.py`) do not need the parser: it is
imported inside the one function that uses it.
