# common-code-reviewer

[![CI](https://github.com/William-Yeh/common-code-reviewer/actions/workflows/ci.yml/badge.svg)](https://github.com/William-Yeh/common-code-reviewer/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-agentskills.io-6B4FBB)](https://agentskills.io)

An Agent Skill that performs rigorous code review as a principal engineer with 10+ years of enterprise experience.

## What It Reviews

| Category | Examples |
|---|---|
| Architecture | Layer violations, circular deps, god classes, missing abstractions |
| Security | Injection (SQL, XSS, command), auth gaps, sensitive data exposure |
| Performance | N+1 queries, unbounded results, blocking in async, missing caching |
| Design | SOLID violations, mutable shared state, hidden side effects |
| Implementation | Dead code, deep nesting, magic numbers, poor naming, testability |
| Style | Naming inconsistencies, formatting (NIT only) |

## Supported Languages

<!-- BEGIN GENERATED LANGUAGES -->
| Language | Frameworks | Style Standard |
|---|---|---|
| TypeScript/JavaScript | React, NestJS, Next.js App Router | ESLint / Airbnb |
| Python | FastAPI, SQLAlchemy | PEP 8 / 484 / 585 |
| Java | Spring Boot, Quarkus | Google Java Style |
| Go | stdlib, Gin, gRPC | Effective Go |
| Rust | std, Tokio | Rust API Guidelines / Clippy |
| Dockerfile | Docker, BuildKit, multi-stage builds | Docker best practices |
<!-- END GENERATED LANGUAGES -->

## Installation

### Recommended: `npx skills`

```bash
npx skills add William-Yeh/common-code-reviewer
```

### Manual installation

Copy the `skill/` directory to your agent's skill folder:

| Agent | Directory |
|-------|-----------|
| Claude Code | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` |
| Amp | `.amp/skills/` |
| Roo Code | `.roo/skills/` |
| Copilot | `.github/skills/` |

## Usage

Compatible with any AI agent that supports the [Agent Skills spec](https://agentskills.io).

### Starter prompts

- `Review my changes`
- `Review PR #42`
- `Review this code but skip the nitpicks`
- `Do a thorough review of src/auth.ts`
- `Check only the security and performance issues`

### CLI

```bash
/common-code-reviewer                                    # auto-detect diff, full rigor
/common-code-reviewer --relaxed                         # skip NITs, pattern-only MINORs
/common-code-reviewer --no-fixes                        # findings only, no suggested code
/common-code-reviewer --files src/auth.ts src/middleware.ts
```

### Arguments

| Flag | Effect |
|---|---|
| `--thorough` | Full rigor (default). All severity levels. |
| `--relaxed` | Skip NITs, only flag repeated MINOR patterns. |
| `--no-fixes` | Report issues only, no suggested code. |
| `--files <paths>` | Review specific files instead of auto-detecting diff. |

## Project Structure

```
common-code-reviewer/
├── skill/                # Agent-installable skill artifact
│   ├── SKILL.md          # Skill definition (review rules + process)
│   ├── languages.yaml    # Canonical language and detection registry
│   └── references/       # Language-specific rules (loaded on demand)
│       ├── typescript.md
│       ├── python.md
│       ├── java.md
│       ├── go.md
│       ├── rust.md
│       └── dockerfile.md
├── tests/
│   ├── COVERAGE.md       # Generated Review Rule evidence
│   ├── scripts/          # Validation and live conformance modules
│   ├── typescript/       # Source + Conformance Fixtures
│   ├── python/
│   ├── java/
│   ├── go/
│   ├── rust/
│   └── dockerfile/
└── .github/workflows/    # CI pipeline
```

## Extending

To add a new language:

1. Create `references/<language>.md` following the existing Language References
2. Add one entry to `skill/languages.yaml`
3. Add source and `*.fixture.yaml` pairs under `tests/<language>/`
4. Run `uv run tests/scripts/sync_generated.py`

Every language-specific Review Rule must have required fixture evidence.

## Tests

Development scripts declare runtime dependencies with PEP 723 inline metadata.
Install [`uv`](https://docs.astral.sh/uv/) once; `uv run` creates and reuses an
isolated environment for each script.

**Deterministic conformance** — validates the language registry, generated tables,
Review Rule catalog, fixture semantics, detection patterns, and derived coverage:

```bash
uv run tests/scripts/validate_structure.py
```

<!-- BEGIN GENERATED COVERAGE -->
The Conformance Fixtures cover **79/79 Review Rules (100%)**. See
`tests/COVERAGE.md` for the derived evidence.
<!-- END GENERATED COVERAGE -->

**Live conformance** — invokes Claude Code read-only against every fixture. It is
manual/scheduled because model behavior is probabilistic and requires credentials:

```bash
uv run tests/scripts/run_conformance.py --model sonnet
```

## Changelog

### v1.3.0 (2026-07-27)

- Added an explicit **Review Rule Catalog** to `skill/SKILL.md` — every finding-producing
  instruction now resolves to a catalogued rule ID with a fixed severity. Rule IDs and
  severities are part of the skill's interface (see ADR-0003)
- Migrated Conformance Fixtures from prose `expected-*.md` files to canonical
  `*.fixture.yaml`, enabling semantic recall-oriented matching by rule identity, file,
  and location rather than exact prose
- Added `tests/scripts/sync_generated.py` (generates language tables and coverage blocks)
  and `tests/scripts/run_conformance.py` (read-only live conformance runs against
  Claude Code); rewrote `validate_structure.py` around the canonical registry
- Rule coverage: **79/79 rules (100%)** — 53 common, 11 Rust, 15 Dockerfile
- Recorded accepted `agent-skill-linter` semantic deviations in ADR-0004

### v1.2.0 (2026-06-24)

- Added Rust review rules (`skill/references/rust.md`) — covering `.unwrap()`/`panic` in libraries, ownership/clone smells, `unsafe`/SAFETY, error-type design (`Box<dyn Error>` vs typed enums), and async hazards (blocking-in-async, lock-across-`.await`)
- Added two Rust test fixtures with expected findings (`tests/rust/`)
- Closed two previously-uncovered general rules via Rust idioms: *unnecessary allocations in hot paths* and *missing Result/Option types*
- Rule coverage: 86% → 91% (64/70 rules) — counted under the pre-catalog rule
  accounting; superseded by the canonical catalog introduced in v1.3.0
- Refreshed existing language references for current toolchains: fixed an incorrect PEP 657 citation (now PEP 695 — `type` statement / inline generics) and added Python 3.14 notes (t-strings); refreshed Java to the 25 LTS (scoped values, primitive patterns, flexible constructor bodies); added Go 1.25 (`WaitGroup.Go`, `testing/synctest`), TypeScript `isolatedDeclarations`, and a BuildKit cache-mount note for Dockerfile

### v1.1.0 (2026-04-08)

- Added Dockerfile review rules (`skill/references/dockerfile.md`) — 15 rules covering base image hygiene, multi-stage builds, layer optimization, and supply chain security
- Added two Dockerfile test fixtures with expected findings (`tests/dockerfile/`)
- Rule coverage: 82% → 86% (51/59 rules)

### v1.0.0 (2026-04-02)

- Initial release with TypeScript/JavaScript, Python, Java, and Go review rules
- Structural validation CI via `tests/scripts/validate_structure.py`

## Author

William Yeh ([@William-Yeh](https://github.com/William-Yeh)) — william.pjyeh@gmail.com

## License

Apache-2.0 — see [LICENSE](LICENSE).
