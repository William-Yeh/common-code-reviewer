# Expected Findings: Dockerfile — Dockerfile-app

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Image provenance | 4 | `FROM node:latest` — floating tag is unpinned and non-reproducible. Upstream rewrites can silently break the build or introduce vulnerabilities. Use a specific version with a digest (e.g. `node:20-alpine@sha256:<digest>`). |
| 2 | BLOCKER | Security | Secret management | 8 | `ENV DB_PASSWORD=supersecret123` bakes a credential into the image layer. The value persists in history even if overwritten in a later layer. Inject secrets at runtime via orchestrator env vars or a secrets manager. |
| 3 | BLOCKER | Security | TLS verification | 20 | `curl -k` disables TLS certificate verification. Fetching and executing a shell script over an unverified connection is a direct supply chain attack vector. |
| 4 | MAJOR | Security | Least privilege | 24 | No `USER` instruction — the container runs as root. A process escape grants host root access. Add `RUN addgroup -S app && adduser -S app -G app` and `USER app` before `CMD`. |
| 5 | MAJOR | Architecture | Single-stage build | 4 | No multi-stage build: `python3` and `build-essential` (native compilers) are installed in the same stage that runs the application. These add significant attack surface and image size. Separate the build stage from the runtime stage. |
| 6 | MAJOR | Performance | Layer hygiene | 13-14 | `apt-get install` and `rm -rf /var/lib/apt/lists/*` are in separate `RUN` layers. The deleted files are still committed in the layer below — they waste space and are not actually removed from the image. Combine into one `RUN` with `&&`. |
| 7 | MINOR | Performance | Cache ordering | 16-17 | `COPY . .` before `RUN npm install` invalidates the dependency install cache on every source change. Move `COPY package*.json ./` and `RUN npm install` before `COPY . .`. |
| 8 | MINOR | Implementation | Base image hygiene | 22 | `ADD config/app.json /app/config.json` — use `COPY` for local file copies. `ADD` has implicit tar-extraction and URL-fetching behavior that is unexpected here. |
| 9 | MINOR | Implementation | Working directory | 4 | No `WORKDIR` instruction — all paths are relative to the implicit `/`. Set an explicit `WORKDIR /app` to make paths predictable and avoid writing files to the filesystem root. |
| 10 | MINOR | Implementation | Observability | (absent) | No `HEALTHCHECK` instruction. Orchestrators (Docker Swarm, Kubernetes readiness probes) cannot determine container health without it. Add a `HEALTHCHECK CMD curl -f http://localhost:3000/health || exit 1`. |

## Coverage Check

- [x] Security — Secret in ENV (finding 2)
- [x] Security — FROM latest / unpinned base (finding 1)
- [x] Security — TLS disabled (finding 3)
- [x] Security — Running as root (finding 4)
- [x] Architecture — Single-stage with build tools (finding 5)
- [x] Performance — Layer hygiene / apt cleanup (finding 6)
- [x] Performance — Cache ordering (finding 7)
- [x] Implementation — ADD vs COPY (finding 8)
- [x] Implementation — Missing WORKDIR (finding 9)
- [x] Implementation — Missing HEALTHCHECK (finding 10)
- [x] All severity levels represented (BLOCKER through MINOR)

## Notes

- Findings 1–3 are BLOCKERs, testing that the reviewer correctly prioritizes image provenance and secret hygiene.
- Finding 6 (layer bloat via split RUN) is a common misunderstanding — tests that the reviewer understands how Docker layer snapshots work.
- Finding 7 (COPY order) tests cache-aware layer ordering, a Dockerfile-specific performance rule.
