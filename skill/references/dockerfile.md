# Dockerfile Review Rules

These rules supplement the common review framework. Apply them to `Dockerfile`, `Dockerfile.*`, and `*.dockerfile` files.

## Base Image Hygiene

- **Pin base images to a digest**: `FROM node:20-alpine` is mutable — the tag can be overwritten. Prefer `FROM node:20-alpine@sha256:<digest>` for reproducible builds. Flag floating tags on production images as MAJOR.
- **Use minimal base images**: Prefer distroless, Alpine, or scratch for final stages. Flag `ubuntu`, `debian`, or `centos` as final-stage bases unless justified — they carry significant unnecessary attack surface (MAJOR).
- **Flag `FROM latest`**: Always a BLOCKER. `latest` is unpinned and will silently break on upstream updates.
- **Avoid using root as the default**: The final stage must set `USER <non-root>`. Missing `USER` instruction is MAJOR — containers default to root, which is a container escape risk.

## Multi-Stage Builds

- **Separate build and runtime stages**: Flag single-stage builds that install compilers, build tools, or SDKs in the same layer that runs the app. Build deps must not reach the final image (MAJOR).
- **Name stages**: Use `FROM ... AS builder` for readability and to allow targeted builds (`docker build --target builder`). Unnamed stages in multi-stage files are a NIT.
- **Copy only necessary artifacts**: `COPY --from=builder / /` copies the entire build filesystem. Flag overly broad `COPY --from` that brings in build tools or test artifacts (MAJOR).

## Layer and Cache Optimization

- **Order instructions by change frequency** (ascending): `FROM` → system deps → app deps → app source → config. Placing `COPY . .` before `RUN npm install` busts the dependency cache on every source change — flag as MINOR.
- **Combine related `RUN` commands**: Multiple `RUN apt-get install` calls create unnecessary layers. Combine with `&&` and clean up in the same layer (`rm -rf /var/lib/apt/lists/*`). Flag as MINOR.
- **Clean package manager caches in the same `RUN` layer**: `apt-get install` followed by a separate `RUN rm -rf /var/lib/apt/lists/*` does not save space — the data is already committed to the layer below. Must be the same `RUN` instruction (MAJOR).
- **Avoid `ADD` when `COPY` suffices**: `ADD` has implicit tar-extraction and URL-fetching behavior. Use `COPY` for local files. Flag `ADD` for local file copy as MINOR.

## Security

- **Never bake secrets into image layers**: `ENV SECRET=...`, `ARG SECRET=...` used as runtime secrets, or credentials in `RUN curl -H "Authorization: Bearer ..."` are BLOCKERs. Secrets persist in layer history even after deletion. Use `--secret` (BuildKit) or inject at runtime via environment.
- **Flag `--no-check-certificate` / `curl -k`**: Disabling TLS verification in `RUN` instructions is a BLOCKER — supply chain attack vector.
- **Verify downloaded artifacts**: `RUN wget ... && tar xz ...` without checksum verification is MAJOR. Always verify with `sha256sum` or GPG signatures.
- **Drop capabilities and set read-only root filesystem**: Not enforceable in the Dockerfile itself, but flag if the image is being built for Kubernetes and no `securityContext` equivalent is visible. Raise as an advisory NIT.
- **`HEALTHCHECK` presence**: Production images should declare a `HEALTHCHECK`. Missing healthcheck is MINOR — orchestrators can't determine container readiness without it.

## Environment and Configuration

- **Prefer `COPY` over `ADD` for config files**: Explicit is better than implicit.
- **Use `ENV` for runtime configuration, `ARG` for build-time configuration**: Swapping these means secrets or build metadata leak into the runtime environment (or vice versa). Flag `ARG` used for values that need to persist at runtime as MINOR.
- **Set `WORKDIR` explicitly**: Relying on implicit `/` as working directory makes paths fragile. Flag missing `WORKDIR` in any non-trivial Dockerfile as MINOR.
- **Expose only necessary ports**: `EXPOSE` is documentation, not enforcement, but flag `EXPOSE 0-65535` or overly broad port ranges as MAJOR.

## Common Anti-Patterns

| Anti-Pattern | Severity | Reason |
|---|---|---|
| `FROM ... AS ... \| FROM latest` | BLOCKER | Unpinned, non-reproducible |
| Secrets in `ENV` or `ARG` | BLOCKER | Persisted in image history |
| `curl -k` / `--no-check-certificate` | BLOCKER | Disables TLS, supply chain risk |
| No `USER` in final stage | MAJOR | Container runs as root |
| Single-stage with build tools | MAJOR | Inflates attack surface and image size |
| `RUN apt-get install` without cleanup in same layer | MAJOR | Layer bloat |
| `COPY . .` before dependency install | MINOR | Busts cache on every code change |
| Multiple `RUN` for related commands | MINOR | Unnecessary layers |
| Missing `WORKDIR` | MINOR | Implicit `/` is fragile |
| Missing `HEALTHCHECK` | MINOR | Orchestrators can't probe readiness |
| `ADD` for local files | NIT | Use `COPY`; `ADD` semantics are implicit |
| Unnamed multi-stage | NIT | Reduces readability and targeted build capability |
