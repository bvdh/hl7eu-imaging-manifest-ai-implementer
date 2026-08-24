#!/bin/bash
# Start a local FHIR terminology server (FHIRsmith, the software that runs tx.fhir.org)
# in Docker so IG builds do not depend on the shared public tx.fhir.org session, which
# drops its cache during long builds. Run from the repository root.
#
#   ./startLocalTxServer.sh                               # terminal 1 (keeps running)
#   TX_URL=http://localhost:8085/r4 ./build.sh localtx    # terminal 2 (root build wrapper)
#
# Overridable via environment variables:
#   TX_IMAGE           server image        (default ghcr.io/healthintersections/fhirsmith:latest)
#   TX_PORT            host port           (default 8085)
#   TX_CONTAINER_PORT  server port         (default 3000, FHIRsmith default)
#   TX_CONTAINER_NAME  docker container name (default mado-txserver)
#   TX_DATA_DIR        host data directory (default ./tx-data)
#   DOCKER_PLATFORM    override platform (e.g. --platform=linux/amd64)
#
# FHIRsmith config (tx module) is version-controlled in ./tx-config/ and auto-seeded
# into the data directory on first run. On first start it downloads/indexes terminology
# content into <data>/terminology-cache/; it is ready once "curl $TX_URL/metadata"
# returns a CapabilityStatement.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tx_config_src="$script_dir/tx-config"

tx_image="${TX_IMAGE:-ghcr.io/healthintersections/fhirsmith:latest}"
tx_port="${TX_PORT:-8085}"
tx_container_port="${TX_CONTAINER_PORT:-3000}"
tx_data_dir="${TX_DATA_DIR:-$script_dir/tx-data}"

mkdir -p "$tx_data_dir"

# Seed the versioned config (tx-config/) into the data dir on first run.
if [ ! -f "$tx_data_dir/config.json" ]; then
    if [ -f "$tx_config_src/config.json" ]; then
        echo "Seeding FHIRsmith config into $tx_data_dir from tx-config/"
        cp "$tx_config_src/config.json" "$tx_data_dir/config.json"
        [ -f "$tx_config_src/library.yml" ] && cp "$tx_config_src/library.yml" "$tx_data_dir/library.yml"
    else
        echo "ERROR: No FHIRsmith config at $tx_data_dir/config.json and no template in $tx_config_src" >&2
        echo "Restore tx-config/config.json (+ library.yml), or" >&2
        echo "point the build at an already-running tx server instead:" >&2
        echo "  TX_URL=http://<host>:<port>/r4 ./build.sh localtx" >&2
        exit 2
    fi
fi

container_name="${TX_CONTAINER_NAME:-mado-txserver}"

# The IG Publisher calls <TX_URL>/metadata directly, so TX_URL must be the R4 endpoint.
tx_url="http://localhost:${tx_port}/r4"

# Singleton: do not start a second instance.
if docker ps --filter "name=^/${container_name}$" --filter "status=running" --format '{{.Names}}' | grep -q .; then
    echo "Local terminology server '$container_name' is already running at $tx_url"
    echo "Stop it with: docker stop $container_name"
    exit 0
fi

# Something else is already serving this port (e.g. a container with a different name).
if curl -sS -m 5 -o /dev/null "$tx_url/metadata" 2>/dev/null; then
    echo "A terminology server is already responding at $tx_url — not starting another."
    exit 0
fi

# Remove a leftover stopped container with the same name, if any.
docker rm -f "$container_name" >/dev/null 2>&1 || true

# Apple Silicon needs the amd64 variant of the image.
docker_platform="${DOCKER_PLATFORM:-}"
if [ -z "$docker_platform" ]; then
    host_arch=$(uname -m)
    if [ "$host_arch" = "arm64" ] || [ "$host_arch" = "aarch64" ]; then
        docker_platform="--platform=linux/amd64"
    fi
fi

echo "Starting local terminology server (FHIRsmith):"
echo "  image:     $tx_image"
echo "  name:      $container_name"
echo "  url:       $tx_url  (container port ${tx_container_port})"
echo "  data:      $tx_data_dir"
echo
echo "When ready, build with:  TX_URL=$tx_url ./_build.sh localtx"
echo "Check readiness with:    curl $tx_url/metadata"
echo

docker_args=(--name "$container_name" --rm)
if [ -n "$docker_platform" ]; then
    docker_args+=("$docker_platform")
fi
docker_args+=(-p "${tx_port}:${tx_container_port}")
docker_args+=(-e "FHIRSMITH_DATA_DIR=/app/data")
docker_args+=(-v "${tx_data_dir}:/app/data")

docker run "${docker_args[@]}" "$tx_image"
