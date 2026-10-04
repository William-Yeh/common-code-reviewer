# common-code-reviewer

[![CI](https://github.com/William-Yeh/common-code-reviewer/actions/workflows/ci.yml/badge.svg)](https://github.com/William-Yeh/common-code-reviewer/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-agentskills.io-6B4FBB)](https://agentskills.io)

An Agent Skill that reviews code and pull requests with principal-engineer rigor.

## What It Reviews

| Category | Examples |
|---|---|
| Architecture | Layer violations, circular deps, god classes, missing abstractions |
| Security | Injection (SQL, XSS, command), auth gaps, sensitive data exposure |
| Performance | N+1 queries, unbounded results, blocking in async, missing caching |
| Design | SOLID violations, mutable shared state, hidden side effects |
| Implementation | Dead code, deep nesting, magic numbers, poor naming, testability |
| Change Risk | CRAP Score per touched function (complexity amplified by missing coverage), with a ranked Risk Report |
| Style | Naming inconsistencies, formatting (NIT only) |

### Change Risk

The skill scores every named function that a change touches. The score is the
CRAP Score, short for Change Risk Anti-Patterns, a metric from Savoia and
Evans:

```
CRAP = CC² × (1 − cov)³ + CC
```

CC is the function's cyclomatic complexity and cov is its line coverage. A
complex function with no tests scores high. The same function with full
coverage scores only its CC.

Coverage is read from a report that already exists in the workspace: LCOV,
Cobertura, JaCoCo XML, or a Go coverprofile. The skill never runs tests or
tools to produce one. When no report is present, it scores the function at 0%
coverage and labels the result "worst case".

Three rules are based on the score, and at most one of them fires per function:

| Condition | Severity |
|---|---|
| CRAP Score above 30 | MAJOR |
| CRAP Score above 8, up to 30 | MINOR |
| Cyclomatic complexity above 6, while coverage keeps the CRAP Score at or under 8 | MINOR |

The 30 threshold is the classic one from the original metric. The 8 threshold
and the complexity rule follow Robert C. Martin's practice for agent-written
code. He discusses it in
[Uncle Bob on Software Fundamentals in the Age of AI](https://www.youtube.com/watch?v=zcLPGC-tvgk)
and implements it in [crap4clj](https://github.com/unclebob/crap4clj) and
[crap4java](https://github.com/unclebob/crap4java). ADR-0005 records the
decision.

To check the skill's complexity numbers yourself, run
[lizard](https://github.com/terryyin/lizard). It counts the same decision
points as the skill in every supported language:

```bash
uvx lizard path/to/file.py        # or pipx run lizard
```

Each scored language reference ends with a Scoring Profile. It lists which
declarations get scored and which constructs count as decision points. It also
says how test files are recognised and which coverage report to expect. The
last slot records where lizard or the team's usual gate counts differently.

## Supported Languages

<!-- BEGIN GENERATED LANGUAGES -->
| Language | Frameworks | Style Standard |
|---|---|---|
| TypeScript/JavaScript | React, NestJS, Next.js App Router | ESLint + typescript-eslint |
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
- `Review only the files under src/payments`

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

### Choosing a model

The skill runs on whatever model your agent session uses; it does not pick
one. Measured on this repository's conformance fixtures:

| Model | Expected findings found | Cost of one 25-fixture run |
|---|---|---|
| Sonnet 5.5 | 94.5% (six runs) | about $2 |
| Opus 5.5 | 96.7% (three runs) | about $6 |
| Fable 5.1 | 97.2% (three runs) | about $33 |

Use Sonnet for routine diffs. Switch to Opus for architecture-heavy changes,
large refactors, or a final review before a release; it is better at
whole-unit judgments such as god modules. Fable's lead over Opus is within
run-to-run noise on these fixtures, at about five times the cost.

In Claude Code, run `/model opus` in the session, or start it with
`claude --model opus`. Other agents have their own model setting.
ADR-0009 records why the skill does not pin a model.

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
├── docs/adr/             # Architecture decision records
├── tests/
│   ├── COVERAGE.md       # Generated Review Rule evidence
│   ├── scripts/          # Validation, live conformance, unit tests, and their lcov.info
│   ├── typescript/       # Source + Conformance Fixtures
│   ├── python/           # Includes lcov.info as Coverage Evidence for one fixture
│   ├── java/
│   ├── go/
│   ├── rust/
│   └── dockerfile/
└── .github/workflows/    # CI pipeline
```

## Extending

To add a new language:

1. Write `skill/references/<language>.md`, using the existing language
   references as a model. If the language should get Change Risk scores, end
   the file with a `## Change Risk` section. It fills five Scoring Profile
   slots: Scored Units, Decision Points, Test Files, Coverage Evidence, and
   Oracle Deviations. The Decision Points slot needs one row for each category
   in the shared decision-point table in `SKILL.md`.

   Every instruction that can produce a finding names the rule it resolves to,
   such as `` — `common/ignored-error` ``, and never states a severity of
   its own (ADR-0006). If the language has behavior no shared rule covers,
   add a `## Language-Owned Review Rules` table with `<language>/<rule>`
   IDs, as `go.md`, `rust.md`, and `dockerfile.md` do.
2. Add the language to `skill/languages.yaml`. Set `scored` to `true` or
   `false`, and list the language's `comment_prefixes`. The generated Language
   Detection table picks up the `scored` flag so the reviewer can see it.
3. Put a source file and a matching `*.fixture.yaml` under `tests/<language>/`.
   Add as many pairs as you need. The source must parse with the
   `tree-sitter-language-pack` grammar named after the language's id (add a
   suffix mapping to `GRAMMAR_BY_SUFFIX` in `validate_structure.py` when they
   differ); it may reference code outside the file (ADR-0007).
   Keep hints such as `[ISSUE: ...]` comments out of new sources, since the
   reviewer reads them.
4. Run `uv run tests/scripts/sync_generated.py` to regenerate the tables.

To add a review rule, add its row to the catalog in `SKILL.md` (shared rules)
or to the reference's Language-Owned table, then give it a required finding in
a fixture. When an existing rule covers the same code at a different severity,
separate the two by a condition visible in the code. Then add a `forbidden`
entry for the other rule at the same location.

Three checks apply. Every review rule must appear in the `required` list of at
least one fixture, every fixture source must parse, and every scored language
must have a complete Scoring Profile.

An existing expectation changes in one of four ways (ADR-0008). Widen it to
another genuine site of the same issue, or remap it to a rule that plainly
fits the code better. Drop it if the code does not show the issue, or keep it
as a real miss. A rule
the reviewer keeps missing where it does fit is a skill problem: fix it in the
skill, never in the expectation.

### Refreshing the language references

The references mix lasting principles with version-specific claims, such as
"since Go 1.26" or "removed in Boot 4.0". Re-check the version-specific claims
when a language or major framework ships a release, and at least twice a year:

1. Verify each claim against the primary source: release notes, JEP or PEP
   pages, `go.dev/doc`, the TC39 finished-proposals list, framework
   changelogs. For long changelogs, fetch the raw file and search it rather
   than relying on a summary.
2. Recommend only final features. List previews, incubators, and experiments
   as things to watch.
3. State which version each piece of advice needs, judged against the
   project's own declared version. Map APIs the project's toolchain deprecates
   or removes to `common/deprecated-api`.
4. Give every new instruction its rule ID and no severity of its own
   (ADR-0006). If no rule fits, add one with a fixture.
5. Before releasing, run three live conformance runs and compare recall with
   the last set (ADR-0008).

Open items from the 2026-10 refresh:

- Python 3.15.0 final: confirm the release and its What's New.
- TypeScript 7.1: its compiler API would remove the `@typescript/typescript6`
  advice.
- Next.js removing `middleware.ts`, and Node.js 26 becoming LTS.
- Java preview features going final: primitive patterns, structured
  concurrency, lazy constants.
- Go `encoding/json/v2`, and Rust's never-type fallback lint, which was taken
  from release notes without a second check.

## Tests

The scripts under `tests/scripts/` declare their dependencies inline with PEP
723 metadata. Install [`uv`](https://docs.astral.sh/uv/) once, and `uv run`
will create an isolated environment for each script the first time and reuse
it afterwards.

### Deterministic conformance

These four scripts run in CI and produce the same result every time. They check
that the language registry, the generated tables, and the review rule catalog
agree with each other, that the detection patterns are well-formed, and that
the derived coverage figures are correct.

They also check each fixture. Every location must point at a line of code, not
a blank or comment line. When a fixture declares a coverage report, that report
must cover the fixture's source file. Every fixture source must also parse
cleanly with its tree-sitter grammar. Fixtures are excerpts, so references to
types and packages outside the file are fine; a syntax error is not, because it
shifts what the reviewer reads away from the fixture's line numbers.

```bash
uv run tests/scripts/validate_structure.py
uv run tests/scripts/test_validate_structure.py
uv run tests/scripts/test_conformance.py
uv run tests/scripts/test_sync_generated.py
```

### Coverage reports in the test suite

A fixture can declare `coverage: <file>` to point at a coverage report. This is
how the suite exercises the path where Change Risk is computed from measured
coverage rather than the worst case. `tests/python/lcov.info` is one such
report. It is generated from `tests/python/test_pricing_engine.py`, so
regenerate it after editing either that test or the `pricing_engine.py` it
covers:

```bash
uv run --with pytest --with coverage -- coverage run --include=tests/python/pricing_engine.py \
  -m pytest -q tests/python/test_pricing_engine.py
uv run --with coverage -- coverage lcov -o tests/python/lcov.info && rm .coverage
```

`tests/scripts/lcov.info` serves a different purpose. It is the coverage report
for the development scripts themselves. When you run this skill on this
repository, it lets the scripts be scored on real coverage instead of the worst
case. Regenerate it after changing a script or its tests:

```bash
uv run --with coverage --with pyyaml --with tree-sitter-language-pack==1.20.0 --with hypothesis==6.140.2 -- coverage run \
  --include='tests/scripts/validate_structure.py,tests/scripts/run_conformance.py,tests/scripts/sync_generated.py' \
  -m unittest discover -s tests/scripts -p 'test_*.py'
uv run --with coverage -- coverage lcov -o tests/scripts/lcov.info && rm .coverage
```

<!-- BEGIN GENERATED COVERAGE -->
The Conformance Fixtures cover **92/92 Review Rules (100%)**. See
`tests/COVERAGE.md` for the derived evidence.
<!-- END GENERATED COVERAGE -->

### Live conformance

This run invokes Claude Code, in read-only mode, against every fixture and
matches the findings it produces against the rules the fixture expects. Model
output is probabilistic, so results differ from run to run. One run with
sonnet costs about $2 and takes about 15 minutes.

The run uses `claude --print --bare`, which reads credentials only from
`ANTHROPIC_API_KEY`. Try one fixture first:

```bash
uv run tests/scripts/run_conformance.py --model sonnet --fixture edge_proxy --report conformance-runs/smoke.json
```

By default the runner exits 1 whenever any expectation is missed, and because
recall stays below 100% a full run normally does. Pass `--min-recall 0.89` to
exit 1 only on a runtime error, a forbidden finding, severity drift, or recall
below 89%. That threshold sits two points under the lowest single run of the
current skill and above every run of the v1.5.0 skill.

To measure a change to the skill, make three full runs, then summarize them:

```bash
for i in 1 2 3; do
  uv run tests/scripts/run_conformance.py --model sonnet --report conformance-runs/run-$i.json &
done; wait
uv run tests/scripts/run_conformance.py --summarize conformance-runs/run-*.json
```

`--summarize` re-scores saved reports with the current parser and fixtures,
without calling the model. It prints overall recall, recall per rule, and which
expectations were never found versus found only in some runs. ADR-0008 sets the
method: judge recall over three-run sets, not by how many fixtures pass. A
difference under about 1% between sets is noise, and an expectation is a
systematic miss only after six runs without a hit.

To compare models, run a three-run set per model with `--model sonnet`,
`--model opus`, or `--model fable`, and summarize each set separately. Longer
reviews need a higher cap: `--max-budget-usd 1.00` for Opus and `4.00` for
Fable. The figures under Choosing a model were produced this way.

CI runs one live pass every Monday at 03:17 UTC, and on demand through
**Run workflow** with `run_conformance` checked. It needs the repository secret
`ANTHROPIC_API_KEY`; without it the job stops at "Require Anthropic
credentials". The report is uploaded as the `claude-code-conformance`
artifact. The job passes `--min-recall 0.89`, so it fails on a regression
rather than on every run. A single run is a trend check, not a verdict on a
change.

## Changelog

### v1.7.0 (2026-10-04)

- Every finding-producing instruction in the six references now names its
  rule (up from 53 of 224 bullets), and no reference states a severity of its
  own, completing ADR-0006
- Added four rules for guidance no existing rule could carry, each with a
  focused fixture that sonnet found in 3 of 3 runs:
  `common/brittle-test` (MAJOR), `common/api-misuse` (MAJOR),
  `common/speculative-abstraction` (MINOR), and `common/busy-wait` (MAJOR)
- Python no longer advises "keep models thin", which contradicted
  `common/anemic-domain`. Swallow-and-return-default now resolves to
  `common/ignored-error` when data integrity is at stake and to
  `common/erased-failure` otherwise
- Removed guidance that no rule could carry and no diff could show:
  `.proto` design, whole-function mutex scope, GraalVM reflection, Quarkus
  health checks, and two test-coverage hints
- The `notification-service.ts` layer-violation expectation now accepts the
  call sites where the reviewer reports it, not only the imports
- Documented how to refresh the language references, with the open items
  from this refresh, under Extending
- Recorded the model recommendation as ADR-0009: no model pin, Sonnet by
  default and in CI, Opus for architecture-heavy reviews
- Recorded how conformance is judged as ADR-0008: recall over repeated runs,
  and the four ways a fixture expectation may change
- Recall on three runs of the pre-existing fixtures: 600/642 (93.5%) with
  the fixture fix, against 583/630 (92.5%) before. The rule-ID sweep alone did
  not move it: 583 to 585 is within run-to-run noise. Most newly tagged
  instructions govern patterns that no fixture exercises
- Compared models on the same fixtures. Opus 5.5 found 95.3% of required
  findings over three runs and Sonnet 5.5 found 93.0% over six (before the
  audit below), at about 2.9
  times the cost per run. Every Opus run scored above every Sonnet run
- Audited the five expectations both models missed in all nine runs. Three
  described issues the code does not show and were dropped: an authorization
  check on a class with no entry point, "mixed abstraction" in a short
  single-level method, and a god function that only delegates. One was
  remapped: a controller holding TypeORM's `DataSource` is
  `common/layer-violation`. The fifth was a gap in the skill: `python.md` had
  no `print()` guidance, unlike TypeScript's `console.log` bullet. With the
  bullet added, sonnet found it in 3 of 3 runs
- On the corrected expectations, recall is 94.5% for Sonnet (six runs) and
  96.7% for Opus (three runs), and Sonnet has two expectations it never found
- Fable 5.1 found 97.2% over three runs at about $33 per run. That is within
  noise of Opus, which costs about $6. Fable did report a real bug in the
  `queue_drain.go` fixture that neither other model had: a closed queue made
  `Drain` spin. The fixture now handles the closed channel, so it shows only
  the busy-wait it was written for
- Rule coverage: **92/92 rules (100%)**: 63 common, 1 Go, 12 Rust, 16 Dockerfile

### v1.6.0 (2026-10-03)

- Recall on the live conformance suite (sonnet, three runs per step) went
  from 87.4% to 92.5% on the same 627 expectations (86.6% on the fixture set
  before this release's corrections), with no forbidden findings and no
  severity drift at any step. Fixtures that pass are a blunt measure, so
  each step was judged by recall
- `run_conformance.py --summarize` re-scores saved runs with the current
  parser and fixtures, without calling the model, and reports overall
  recall, recall per rule, and which expectations were never found versus
  found only in some runs. Saved runs go in the git-ignored
  `conformance-runs/`
- `SKILL.md` has a Whole-unit judgments section with triggers for the
  structural rules the reviewer had almost never used, because it judged
  responsibility one function at a time. `god-module` went from 1/15 to
  7/15 and `rust/clone-to-compile` from 0/3 to 3/3; `missing-abstraction`
  went from 0/6 to 3/6 before the fixture corrections below
- Four older reference bullets now name their rule, as ADR-0006 requires:
  Java field injection, Python untyped public APIs, and TypeScript default
  exports. `hard-coded-dependency` went from 16/21 to 21/21 and
  `style-naming` from 0/3 to 3/3
- `SKILL.md` asks for one finding per rule when a construct breaks two, such
  as an anemic entity whose status is a free-form string
- Corrected fixture evidence the code did not support, and added
  `tests/go/scanner_stats.go` as clear evidence for `hot-path-allocation`
- Added a gitleaks pre-commit hook (`pre-commit install` once per clone)
- Known open item: god *functions*, such as Go's `CreateOrder` or Rust's
  `process_order`, are still missed in every run even though the trigger
  now covers functions. A rewording of the catalog definition or a run on a
  stronger model should come before more trigger text
- Rule coverage: **88/88 rules (100%)**: 59 common, 1 Go, 12 Rust, 16 Dockerfile

### v1.5.0 (2026-10-02)

- Refreshed all six language references against the current toolchains and
  their primary sources: Java 27 (25 is still the LTS), Python 3.14 and
  3.15, Go 1.27, Rust 1.99 and edition 2024, TypeScript 6.0/7.0 with Next.js
  16, React 19.2 and ESLint 10, and the Dockerfile 1.x frontend
- Added `common/deprecated-api` (MAJOR) for code or configuration that uses
  an API the project's own toolchain deprecates or has removed, with the
  `tests/go/edge_proxy.go` fixture
- Fixed advice that was wrong rather than stale:
  - Java listed primitive patterns as available since 25. They are still a
    preview feature (fifth preview in 27), and the reference now forbids
    recommending previews
  - Rust called a panic across FFI undefined behavior. Since 1.81 it aborts
  - Java recommended `@MockBean` (removed in Boot 4.0)
  - TypeScript recommended the Airbnb config (unusable under ESLint 10),
    `useMemo` and stable JSX props (counterproductive under React Compiler),
    and `fetch` cache options (superseded by Next.js 16 `'use cache'`)
  - Python had the `NamedTuple` row backwards, required `response_model`
    on every FastAPI route, and steered toward LBYL over EAFP
  - Go recommended `errors.As` over `errors.AsType`
  - Dockerfile rated `ADD` for local files both MINOR and NIT, and
    discouraged `ADD --checksum` for remote artifacts
- Every new instruction names the catalogued rule it resolves to, as
  ADR-0003 requires. A "Prefer Modern Features" row defers to a more
  specific rule when one matches, so a goroutine leak or a mutable default
  argument keeps its own severity instead of dropping to
  `common/language-idiom`
- A missing `// SAFETY:` comment now resolves to `rust/unsafe-without-safety`
  (BLOCKER) instead of an uncatalogued MAJOR, and the Rust mutex guidance
  names `rust/lock-across-await` and `rust/shared-mutex-overuse` separately
- Resolved every inline severity in the references that disagreed with the
  catalog or named no rule:
  - New rules: `common/n-plus-one-hot-path` (BLOCKER, an N+1 inside a
    request handler; `common/n-plus-one-query` now covers the rest),
    `common/assertion-free-test` (MAJOR), `go/panic-in-library` (BLOCKER,
    Go's first language-owned rule), `rust/hot-loop-clone` (MAJOR), and
    `dockerfile/heavy-runtime-base` (MAJOR)
  - Aligned to their catalog rules: mutable default arguments, goroutines
    without cancellation, double type assertions (`as unknown as T`), and
    `http.Server` and `EXPOSE` defaults (now `common/insecure-default`)
  - Removed guidance no rule could carry: `.proto` field changes (no
    Protobuf detection), Kubernetes capability hints, RUN layer counting,
    and the ~20-line function heuristic
- New fixtures: `tests/java/InvoiceServiceTest.java` and
  `tests/dockerfile/Dockerfile.worker`; the Go, Python, and Rust order
  fixtures now separate request-path N+1 queries from the rest
- `validate_structure.py` now parses every fixture source with tree-sitter
  (`tree-sitter-language-pack`, run through `uv`, so no JDK, Go, Rust, or Node
  toolchain is needed) and fails on syntax errors with their line numbers
- Live conformance with sonnet (2026-10-02, $2.00) cut severity drift from
  about 15% to 0.4% of findings, with no forbidden finding in any fixture.
  Fixes that run prompted:
  - Removed the 235 `[ISSUE: ...]` hint comments and file headers that told
    the reviewer what to find, and remapped every fixture location to the
    unchanged code
  - Triaged the 51 remaining misses in the older fixtures against the
    catalog: widened locations to every genuine site, remapped rules whose
    definition fits better, dropped expectations the code doesn't support,
    and kept genuine reviewer misses as signal. Two weak expectations
    (`graceful-shutdown`, `confused-build-runtime-config`) now point at code
    that actually shows the problem
  - The conformance parser no longer drops a finding whose File line lists
    extra sites (`` `file:9` (also `:17`) ``), and an unparseable File line
    can no longer borrow the next finding's rule. `SKILL.md` now names the
    multi-site form: `path/to/file.ext:12, 30-32`
  - The runner tells the reviewer that `tests/<lang>/` is the harness's
    fixture directory, so Scoring Profiles that treat `tests/` paths as test
    files no longer skip every fixture
  - Renamed `Dockerfile.app` to `Dockerfile.web`: Claude Code's Read tool
    rejects files ending in `.app` as binary
  - A second run on the cleaned fixtures (2026-10-03, $2.03), re-scored with
    the final parser: 30 of 211 required findings missed, 8 of 19 fixtures
    passing, no severity drift, no forbidden findings. The remaining misses
    are mostly a different but defensible rule at the right line; they stay
    as recorded expectations instead of being fitted to one model's choices
- Recorded the decisions as ADR-0006 (reference severities resolve through
  the catalog) and ADR-0007 (fixture sources must parse, not compile)
- Rule coverage: **88/88 rules (100%)**: 59 common, 1 Go, 12 Rust, 16 Dockerfile

### v1.4.0 (2026-09-05)

- Added **Change Risk** scoring. Every function a change touches gets a CRAP
  Score, and the review ends with a Risk Report that ranks them
- Added three rules driven by that score: `common/critical-change-risk`,
  `common/elevated-change-risk`, and `common/excess-complexity`. The thresholds
  are the classic 30 and Robert C. Martin's 8 for agent-written code (ADR-0005)
- Every scored language reference now ends with a Scoring Profile, and
  `validate_structure.py` checks that all five slots and all decision-point
  rows are present
- `languages.yaml` now records whether each language is scored, and the
  generated Language Detection table shows that flag to the reviewer
- Fixtures can declare `coverage:` to supply a coverage report.
  `tests/python/lcov.info` exercises the measured-coverage path and
  `tests/go/rate_limiter.go` exercises the worst-case path
- Added `tests/scripts/test_validate_structure.py`
- The live conformance runner now tells the reviewer whether a coverage report
  exists
- Ran the skill on its own scripts until it reported nothing. Every touched
  function in `tests/scripts/` now has cyclomatic complexity of 6 or under, the
  imperative shells delegate to tested pure functions, and
  `tests/scripts/lcov.info` is committed so the scripts are scored on measured
  coverage
- Re-derived every `location` in the 14 existing fixtures from the current
  sources, correcting 175 of them. A full live run had shown them drifting by
  up to 30 lines since the v1.3.0 migration
- The validator now rejects a `location` that points only at blank or comment
  lines, using the `comment_prefixes` declared in `languages.yaml`
- Rule coverage: **82/82 rules (100%)**: 56 common, 11 Rust, 15 Dockerfile

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
