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

This skill works with any AI agent that supports the [Agent Skills spec](https://agentskills.io). Pick the method that matches your setup.

### Quick install (recommended)

The [`npx skills`](https://github.com/vercel-labs/skills) CLI installs to any supported agent:

```bash
# Install for all detected agents
npx skills add William-Yeh/common-code-reviewer

# Install for a specific agent
npx skills add William-Yeh/common-code-reviewer --agent claude-code
npx skills add William-Yeh/common-code-reviewer --agent cursor
npx skills add William-Yeh/common-code-reviewer --agent gemini-cli
```

### Manual install

Clone (or download) this repo, then copy the skill folder into your agent's skills directory:

```bash
git clone https://github.com/William-Yeh/common-code-reviewer.git
```

Copy the entire folder to the path your agent expects:

| Agent | Project scope | User / global scope |
|---|---|---|
| Claude Code | `.claude/skills/common-code-reviewer/` | `~/.claude/skills/common-code-reviewer/` |
| Cursor | `.cursor/skills/common-code-reviewer/` | — |
| Gemini CLI | `.gemini/skills/common-code-reviewer/` | `~/.gemini/skills/common-code-reviewer/` |
| OpenAI Codex | `.agents/skills/common-code-reviewer/` | `~/.agents/skills/common-code-reviewer/` |
| Roo Code | `.roo/skills/common-code-reviewer/` | `~/.roo/skills/common-code-reviewer/` |
| Amp | `.agents/skills/common-code-reviewer/` | `~/.config/agents/skills/common-code-reviewer/` |

For example, to install globally for Claude Code:

```bash
cp -r common-code-reviewer ~/.claude/skills/common-code-reviewer
```

No registration or configuration needed — agents auto-discover skills from these directories.

### Gemini CLI native command

Gemini CLI also has a built-in install command:

```bash
gemini skills install https://github.com/William-Yeh/common-code-reviewer.git
```

## Usage

Compatible with any AI agent that supports the [Agent Skills spec](https://agentskills.io).

### Arguments

| Flag | Effect |
|---|---|
| `--thorough` | Full rigor (default). All severity levels. |
| `--relaxed` | Skip NITs, only flag repeated MINOR patterns. |
| `--no-fixes` | Report issues only, no suggested code. |
| `--files <paths>` | Review specific files instead of auto-detecting diff. |

### Input Detection

The skill auto-detects what to review:

1. `--files` argument → those files
2. Feature branch → `git diff main...HEAD`
3. Unstaged/staged changes → `git diff` + `git diff --cached`
4. PR number → `gh pr diff <number>`

### Severity Levels

| Severity | Meaning | Merge Impact |
|---|---|---|
| **BLOCKER** | Bugs, security vulns, data loss | Must fix |
| **MAJOR** | Core principle violations, reliability risk | Should fix |
| **MINOR** | Suboptimal but functional | Recommended |
| **NIT** | Style preference, no functional impact | Optional |

### Verdict

- **REQUEST CHANGES** — 1+ Blocker
- **APPROVE WITH COMMENTS** — 0 Blockers, 1+ Major
- **APPROVE** — Only Minor/Nit or clean

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
