# Expected Findings: Dockerfile — Dockerfile-builder

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | MAJOR | Security | Image provenance | 4 | `FROM golang:1.22-alpine` uses a mutable tag. Tags can be overwritten — pin to a digest for reproducible builds (e.g. `golang:1.22-alpine@sha256:<digest>`). Same applies to `alpine:3.19` on line 11. |
| 2 | MAJOR | Security | Least privilege | 13 | No `USER` instruction in the final stage — the server process runs as root. Add a non-root user and switch to it before `ENTRYPOINT`. |
| 3 | MAJOR | Architecture | Multi-stage hygiene | 16 | `COPY --from=build / /` copies the entire build filesystem — including the Go toolchain (`/usr/local/go`), build cache, and test artifacts — into the runtime image. Copy only the compiled binary: `COPY --from=build /app/server /app/server`. |
| 4 | MAJOR | Security | Artifact verification | 19-21 | `wget` downloads a binary without checksum verification. A compromised release or MITM can substitute a malicious binary. Verify with `sha256sum` after download. |
| 5 | MINOR | Implementation | ARG vs ENV | 17-18 | `ARG APP_CONFIG` is used to seed an `ENV`. `ARG` values are build-time only and do not persist — this pattern works but the intent is better expressed as a direct `ENV CONFIG_PATH=/etc/app/config.yaml` with an override at runtime. The current form is not wrong but is confusing. |
| 6 | MINOR | Implementation | Observability | (absent) | No `HEALTHCHECK` instruction. For a gRPC service, use `grpc_health_probe` that is already downloaded: `HEALTHCHECK CMD grpc_health_probe -addr=:8080 || exit 1`. |
| 7 | NIT | Style | Stage naming | 11 | The runtime `FROM alpine:3.19` stage is unnamed. Add `AS runtime` (or `AS final`) for readability and to enable targeted builds (`docker build --target runtime`). |

## Coverage Check

- [x] Security — Mutable tag / missing digest (finding 1)
- [x] Security — Running as root in final stage (finding 2)
- [x] Architecture — Overly broad COPY --from (finding 3)
- [x] Security — Unverified artifact download (finding 4)
- [x] Implementation — ARG vs ENV semantics (finding 5)
- [x] Implementation — Missing HEALTHCHECK (finding 6)
- [x] Style — Unnamed multi-stage (finding 7)
- [x] All severity levels represented (MAJOR through NIT)

## Notes

- Finding 3 (overly broad `COPY --from`) is the key multi-stage anti-pattern — tests whether the reviewer understands that copying `/` from a Go build image brings in the full toolchain.
- Finding 4 (unverified binary) tests supply chain security rules unique to Dockerfile review.
- Finding 6 reuses `grpc_health_probe` already present in the image — tests whether the reviewer gives contextually appropriate suggestions rather than generic advice.
