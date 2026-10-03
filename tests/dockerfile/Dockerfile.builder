FROM golang:1.22-alpine AS build

WORKDIR /src
COPY . .
RUN go mod download && go build -o /app/server ./cmd/server

FROM alpine:3.19


WORKDIR /app

COPY --from=build / /

ARG LOG_LEVEL=info
ENV CONFIG_PATH=/etc/app/config.yaml

RUN wget https://github.com/grpc-health-probe/releases/download/v0.4.19/grpc_health_probe-linux-amd64 \
    -O /usr/local/bin/grpc_health_probe && \
    chmod +x /usr/local/bin/grpc_health_probe


EXPOSE 8080

ENTRYPOINT ["/app/server", "--log-level=${LOG_LEVEL}"]
