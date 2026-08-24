#!/bin/bash
# Convenience wrapper: run the MADO IG build from the repository root.
# Forwards all arguments to imaging-manifest-fork/_build.sh.
# Defaults to the local terminology server mode (see startLocalTxServer.sh).
#
# Examples:
#   ./build.sh                     # -> _build.sh localtx (uses $TX_URL, default http://localhost:8085)
#   ./build.sh build               # standard build against public tx.fhir.org
#   ./build.sh notx                # offline build
#   TX_URL=http://localhost:9000 ./build.sh localtx
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_dir="$script_dir/build-log"
mkdir -p "$log_dir"
log_file="$log_dir/build-$(date +%Y%m%d-%H%M%S).log"

cd "$script_dir/imaging-manifest-fork"

if [ $# -eq 0 ]; then
  set -- localtx
fi

echo "Logging build output to $log_file"
./_build.sh "$@" 2>&1 | tee "$log_file"
