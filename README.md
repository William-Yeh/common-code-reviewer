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

| Language | Frameworks | Style Standard |
|---|---|---|
| TypeScript/JavaScript | React, NestJS, Next.js App Router | ESLint / Airbnb |
| Python | FastAPI, SQLAlchemy | PEP 8 / 484 / 585 |
| Java | Spring Boot, Quarkus | Google Java Style |
| Go | stdlib, Gin, gRPC | Effective Go |

## Installation

### Recommended: `npx skills`

```bash
npx skills add William-Yeh/common-code-reviewer
```

### Manual installation

Copy the skill directory to your agent's skill folder:

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

```
Review my changes
Review PR #42
/common-code-reviewer --relaxed
/common-code-reviewer --files src/auth.ts src/middleware.ts
/common-code-reviewer --no-fixes
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
├── SKILL.md              # Skill definition (review rules + process)
├── references/           # Language-specific rules (loaded on demand)
│   ├── typescript.md
│   ├── python.md
│   ├── java.md
│   └── go.md
├── tests/
│   ├── COVERAGE.md       # Rule coverage matrix
│   ├── scripts/          # CI validation scripts
│   ├── typescript/       # TS test samples + expected findings
│   ├── python/
│   ├── java/
│   └── go/
└── .github/workflows/    # CI pipeline
```

## Extending

To add a new language:

1. Create `references/<language>.md` following the structure of existing references
2. Add the language to the detection table in `SKILL.md`
3. Add test samples under `tests/<language>/`
4. Update `tests/COVERAGE.md`

## Tests

**Structural validation** — checks spec compliance (frontmatter, references, links):

```bash
python tests/scripts/validate_structure.py
```

**Review accuracy** — runs the skill against intentionally flawed samples and compares against expected findings. See `tests/COVERAGE.md` for the full rule coverage matrix (82%, 36/44 rules).

## Author

William Yeh ([@William-Yeh](https://github.com/William-Yeh)) — william.pjyeh@gmail.com

## License

Apache-2.0 — see [LICENSE](LICENSE).
