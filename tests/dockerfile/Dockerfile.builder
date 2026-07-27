# Test sample: Go app multi-stage Dockerfile with build optimization and image hygiene issues.
# This file contains ~8 deliberate problems for the code review skill to catch.

# [ISSUE: Mutable base image tag — no digest pin]
FROM golang:1.22-alpine AS build

WORKDIR /src
COPY . .
RUN go mod download && go build -o /app/server ./cmd/server

# [ISSUE: Unnamed runtime stage — reduces readability and targeted build capability]
FROM alpine:3.19

# [ISSUE: No non-root USER in final stage]

WORKDIR /app

# [ISSUE: Overly broad COPY --from — copies entire build filesystem, includes build tools and test artifacts]
COPY --from=build / /

# [ISSUE: ARG used for a value that needs to persist at runtime — should be ENV]
ARG APP_CONFIG=/etc/app/config.yaml
ENV CONFIG_PATH=$APP_CONFIG

# [ISSUE: wget without checksum verification]
RUN wget https://github.com/grpc-health-probe/releases/download/v0.4.19/grpc_health_probe-linux-amd64 \
    -O /usr/local/bin/grpc_health_probe && \
    chmod +x /usr/local/bin/grpc_health_probe

# [ISSUE: Missing HEALTHCHECK]

EXPOSE 8080

ENTRYPOINT ["/app/server"]
