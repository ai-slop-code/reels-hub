#!/bin/sh
# Container tests (spec §23.6, §24.2; R63, R64, R125). Builds the node, test and runtime stages,
# runs the in-image tests and a smoke test of the runtime image. Everything created here is named
# reels-hub-test-<random> and is removed on exit; the real `reels-hub` container and volume are never touched.
#
# CONTAINER_ENGINE=podman (default) or docker (CI). REELS_HUB_INSECURE_TLS=1 is for the build
# machine only (R125): TLS verification is off for the build. Without the npm registry, the
# node stage can't build, so the run is reported as skipped (CI is the authority).
set -eu

cd "$(dirname "$0")/.."
ENGINE="${CONTAINER_ENGINE:-podman}"
INSECURE="${REELS_HUB_INSECURE_TLS:-0}"
RUN_ID="reels-hub-test-$(openssl rand -hex 4)"
NAME="$RUN_ID"
VOLUME="$RUN_ID-data"
MEDIA="$HOME/.cache/reels-hub-test/$RUN_ID"
IMG_NODE="$RUN_ID:node"
IMG_RUNTIME="$RUN_ID:runtime"
IMG_TEST="$RUN_ID:test"

TLS=""
if [ "$INSECURE" = 1 ] && [ "$ENGINE" = podman ]; then
  TLS="--tls-verify=false"
fi

cleanup() {
  "$ENGINE" rm -f "$NAME" >/dev/null 2>&1 || true
  "$ENGINE" volume rm -f "$VOLUME" >/dev/null 2>&1 || true
  # The container writes as root into the bind mount (backups, proxies), so the files are cleared
  # from inside a container; the host user may not own them.
  if [ -d "$MEDIA" ] && "$ENGINE" image inspect "$IMG_RUNTIME" >/dev/null 2>&1; then
    "$ENGINE" run --rm --entrypoint sh -v "$MEDIA:/media" "$IMG_RUNTIME" \
      -c 'rm -rf /media/* /media/.[!.]* 2>/dev/null; true' >/dev/null 2>&1 || true
  fi
  rm -rf "$MEDIA" 2>/dev/null || true
  "$ENGINE" rmi -f "$IMG_TEST" "$IMG_RUNTIME" "$IMG_NODE" >/dev/null 2>&1 || true
}
trap cleanup EXIT

build() {
  # $1 = stage, $2 = tag
  # shellcheck disable=SC2086
  "$ENGINE" build $TLS --build-arg "INSECURE_TLS=$INSECURE" -f Containerfile --target "$1" -t "$2" .
}

echo "==> node stage (HyperFrames 0.9.39 via npm, R126)"
if ! build node "$IMG_NODE"; then
  if [ "$INSECURE" = 1 ]; then
    echo "SKIPPED: the node stage did not build here. npm is blocked on this network (R125)." >&2
    echo "         Container tests did not run here. CI runs them in full." >&2
    exit 0
  fi
  echo "FAILED: the node stage did not build." >&2
  exit 1
fi

echo "==> runtime stage"
build runtime "$IMG_RUNTIME"

echo "==> test stage and in-image tests (pytest -m container)"
build test "$IMG_TEST"
"$ENGINE" run --rm "$IMG_TEST"

echo "==> smoke test of the runtime image"
mkdir -p "$MEDIA"
"$ENGINE" volume create "$VOLUME" >/dev/null
"$ENGINE" run -d --name "$NAME" -p 127.0.0.1::8787 -v "$MEDIA:/media" -v "$VOLUME:/data" "$IMG_RUNTIME" >/dev/null
PORT="$("$ENGINE" port "$NAME" 8787 | head -n 1 | sed 's/.*://')"

HEALTH="$MEDIA/health.json"
i=0
until curl -fsS "http://127.0.0.1:$PORT/health" >"$HEALTH" 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 60 ]; then
    echo "FAILED: /health did not answer within 60 s." >&2
    "$ENGINE" logs "$NAME" >&2 || true
    exit 1
  fi
  sleep 1
done
grep -q '"status":"ok"' "$HEALTH"
"$ENGINE" exec "$NAME" /app/bin/healthcheck
echo "OK: runtime image starts and answers /health"
