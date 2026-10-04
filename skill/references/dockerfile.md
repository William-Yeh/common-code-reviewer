# Dockerfile Review Rules

These rules supplement the common review framework. Apply them to `Dockerfile`, `Dockerfile.*`, and `*.dockerfile` files.

## Language-Owned Review Rules

| Rule ID | Severity | Review Rule |
|---|---|---|
| `dockerfile/latest-base` | BLOCKER | A base image uses `latest` or no tag. |
| `dockerfile/mutable-base` | MAJOR | A tagged base image is not pinned to a digest. |
| `dockerfile/root-runtime` | MAJOR | The final stage runs as root. |
| `dockerfile/baked-secret` | BLOCKER | A secret is persisted through `ARG`, `ENV`, or copied content. |
| `dockerfile/tls-disabled` | BLOCKER | Artifact retrieval disables TLS verification. |
| `dockerfile/unverified-artifact` | MAJOR | A downloaded artifact is used without integrity verification. |
| `dockerfile/single-stage-toolchain` | MAJOR | Build tools remain in the runtime image. |
| `dockerfile/heavy-runtime-base` | MAJOR | The final stage uses a full OS distribution image that the runtime artifact does not need. |
| `dockerfile/broad-stage-copy` | MAJOR | A stage copy includes more than the runtime artifact. |
| `dockerfile/split-package-cleanup` | MAJOR | Package indexes are removed in a later layer than installation. |
| `dockerfile/cache-hostile-copy` | MINOR | Broad source copying invalidates dependency cache layers. |
| `dockerfile/implicit-add` | MINOR | `ADD` is used where explicit `COPY` semantics are required. |
| `dockerfile/missing-workdir` | MINOR | The image relies on the implicit root working directory. |
| `dockerfile/missing-healthcheck` | MINOR | The runtime image declares no health check. |
| `dockerfile/confused-build-runtime-config` | MINOR | Build-time and runtime configuration semantics are conflated. |
| `dockerfile/unnamed-stage` | NIT | A multi-stage build leaves a stage unnamed. |

## Base Image Hygiene

- **Pin base images to a digest**: `FROM node:20-alpine` is mutable — the tag can be overwritten. Prefer `FROM node:20-alpine@sha256:<digest>` for reproducible builds. Flag floating tags on production images — `dockerfile/mutable-base`. Pair digest pins with automated updates (Dependabot `package-ecosystem: "docker"`, Renovate, or Docker Scout) so pins do not rot; a digest kept current by a bot satisfies this rule.
- **Use minimal base images**: Prefer distroless, Docker Hardened Images, Chainguard, Alpine, or scratch for final stages. Flag `ubuntu`, `debian`, `centos`, or a language image built on one (`node:22`, `python:3.13` without `-slim`/`-alpine`) as the final-stage base when the artifact does not need a distribution — `dockerfile/heavy-runtime-base`. Accept it when the stage installs OS packages the runtime genuinely needs (system libraries for a native extension, a browser for headless rendering). The rule applies only to the final stage.
- **Flag `FROM latest`**: `latest` is unpinned and will silently break on upstream updates — `dockerfile/latest-base`.
- **Avoid using root as the default**: The final stage must set `USER <non-root>`. Missing `USER` instruction — `dockerfile/root-runtime`: containers default to root, which is a container escape risk. Prefer an explicit numeric `UID:GID` (created with `useradd --no-log-init`), since names resolve non-deterministically and Kubernetes `runAsNonRoot` can only verify numeric users — `common/language-idiom`.

## Multi-Stage Builds

- **Separate build and runtime stages**: Flag single-stage builds that install compilers, build tools, or SDKs in the same layer that runs the app. Build deps must not reach the final image — `dockerfile/single-stage-toolchain`.
- **Name stages**: Use `FROM ... AS builder` for readability and to allow targeted builds (`docker build --target builder`). Flag unnamed stages in multi-stage files — `dockerfile/unnamed-stage`.
- **Copy only necessary artifacts**: `COPY --from=builder / /` copies the entire build filesystem. Flag overly broad `COPY --from` that brings in build tools or test artifacts — `dockerfile/broad-stage-copy`.

## Layer and Cache Optimization

- **Order instructions by change frequency** (ascending): `FROM` → system deps → app deps → app source → config. Placing `COPY . .` before `RUN npm install` busts the dependency cache on every source change — `dockerfile/cache-hostile-copy`.
- **Clean package manager caches in the same `RUN` layer**: `apt-get install` followed by a separate `RUN rm -rf /var/lib/apt/lists/*` does not save space — the data is already committed to the layer below. Install and cleanup must be the same `RUN` instruction — `dockerfile/split-package-cleanup`. On BuildKit, prefer a cache mount (`RUN --mount=type=cache,target=/var/cache/apt ...`) to persist the download cache across builds without bloating the image.
- **Avoid `ADD` when `COPY` suffices**: `ADD` has implicit tar-extraction and URL-fetching behavior. Use `COPY` for local files. Flag `ADD` for local file copy — `dockerfile/implicit-add`.
- **`ADD` is the right tool for remote artifacts**: `ADD --checksum=sha256:<digest> https://...` (Dockerfile 1.6+) downloads and verifies in one step, and is preferred over `RUN curl ... && sha256sum -c`. Do not flag it as `dockerfile/implicit-add`. Flag `ADD` of an HTTP URL without `--checksum`, or of a Git source (`ADD https://github.com/org/repo.git#v1.2`) without `--checksum=<commit-sha>`, as `dockerfile/unverified-artifact` — a branch or tag can move.
- **Shell pipes**: a `RUN` that pipes a fallible command (`curl ... | sh`, `wget -O- ... | tar x`) reports only the last command's status, so a failed download can still produce an image. Flag pipes without `set -o pipefail` (use `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` on Debian-based images, since `dash` lacks it) — `common/ignored-error`.

## Security

- **Never bake secrets into image layers**: `ENV SECRET=...`, `ARG SECRET=...` used as runtime secrets, or credentials in `RUN curl -H "Authorization: Bearer ..."` — `dockerfile/baked-secret`. Secrets persist in layer history even after deletion. Use `RUN --mount=type=secret,id=<id>` (BuildKit), with `,env=VAR` (Dockerfile 1.10+) when the tool reads the secret from an environment variable, or inject at runtime.
- **Flag `--no-check-certificate` / `curl -k`**: Disabling TLS verification in `RUN` instructions is a supply chain attack vector — `dockerfile/tls-disabled`.
- **Verify downloaded artifacts**: `RUN wget ... && tar xz ...` without checksum verification — `dockerfile/unverified-artifact`. Verify with `ADD --checksum`, `sha256sum -c`, or GPG signatures.
- **Build checks**: BuildKit runs build checks (`docker build --check`) such as `SecretsUsedInArgOrEnv`, `UndefinedVar`, `UndefinedArgInFrom`, `InvalidDefaultArgInFrom`, `JSONArgsRecommended`, and `CopyIgnoredFile`. Leave issues those checks report to the tool. Flag a `# check=skip=all` directive, or one that skips `SecretsUsedInArgOrEnv`, without a written reason — `common/insecure-default`. Prefer `# check=error=true` in CI-built images.
- **`.dockerignore`**: `COPY . .` without a `.dockerignore` that excludes `.git`, `.env*`, credentials, and local build output can copy secrets into the build context and image — `common/sensitive-data-exposure`.
- **`HEALTHCHECK` presence**: Production images should declare a `HEALTHCHECK`. Without one, orchestrators can't determine container readiness — `dockerfile/missing-healthcheck`.

## Environment and Configuration

- **Prefer `COPY` over `ADD` for config files**: Explicit is better than implicit — `dockerfile/implicit-add`.
- **Use `ENV` for runtime configuration, `ARG` for build-time configuration**: Swapping these means secrets or build metadata leak into the runtime environment (or vice versa). Flag `ARG` used for values that need to persist at runtime — `dockerfile/confused-build-runtime-config`.
- **Set `WORKDIR` explicitly**: Relying on implicit `/` as working directory makes paths fragile. Flag missing `WORKDIR` in any non-trivial Dockerfile — `dockerfile/missing-workdir`.
- **Expose only necessary ports**: `EXPOSE` is documentation, not enforcement, but flag `EXPOSE 0-65535` or overly broad port ranges — `common/insecure-default`.

## Common Anti-Patterns

| Anti-Pattern | Rule | Reason |
|---|---|---|
| `FROM image:latest` or untagged `FROM image` | `dockerfile/latest-base` | Unpinned, non-reproducible |
| Secrets in `ENV` or `ARG` | `dockerfile/baked-secret` | Persisted in image history |
| `curl -k` / `--no-check-certificate` | `dockerfile/tls-disabled` | Disables TLS, supply chain risk |
| No `USER` in final stage | `dockerfile/root-runtime` | Container runs as root |
| Single-stage with build tools | `dockerfile/single-stage-toolchain` | Inflates attack surface and image size |
| Full-distribution final base for a self-contained artifact | `dockerfile/heavy-runtime-base` | Unneeded packages widen the attack surface |
| `RUN apt-get install` without cleanup in same layer | `dockerfile/split-package-cleanup` | Layer bloat |
| `COPY . .` before dependency install | `dockerfile/cache-hostile-copy` | Busts cache on every code change |
| Missing `WORKDIR` | `dockerfile/missing-workdir` | Implicit `/` is fragile |
| Missing `HEALTHCHECK` | `dockerfile/missing-healthcheck` | Orchestrators can't probe readiness |
| `ADD` for local files | `dockerfile/implicit-add` | Use `COPY`; `ADD` semantics are implicit |
| `ADD` of a URL or Git source without `--checksum` | `dockerfile/unverified-artifact` | Unverified or movable artifact |
| `RUN` pipe without `pipefail` | `common/ignored-error` | Failed download still yields an image |
| Unnamed multi-stage | `dockerfile/unnamed-stage` | Reduces readability and targeted build capability |
