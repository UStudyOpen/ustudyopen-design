#!/usr/bin/env bash
# Invoked with bash; no executable bits, installation or elevated privileges.
set -euo pipefail
uso_suite="${1:-all}"
case "$uso_suite" in all|browser|callouts|instances|subpath|sandbox) ;; *) echo "Unknown suite: $uso_suite" >&2; exit 2 ;; esac
cd "$(dirname "$0")/.."
uso_browser_bin="${USO_BROWSER_BIN:-/opt/brave.com/brave/brave}"
uso_deno_bin="${USO_DENO_BIN:-/opt/quarto/bin/tools/x86_64/deno}"
mkdir -p artifacts/v0.2/screenshots artifacts/v0.2/subpath
# Refuse a collision instead of connecting to an existing/personal CDP profile.
python3 - <<'PY'
import socket
for port in (4850, 4851, 9228):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port))
PY
uso_profile=$(mktemp -d "$PWD/artifacts/v0.2/browser-XXXXXX")
uso_pids=()
cleanup() {
  if [[ -n "${uso_browser_pid:-}" ]]; then kill -- "-$uso_browser_pid" 2>/dev/null || true; fi
  for pid in "${uso_pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  for pid in "${uso_pids[@]}"; do wait "$pid" 2>/dev/null || true; done
  python3 - "$uso_profile" <<'PY_CLEAN'
import shutil, sys, time
for attempt in range(20):
    try:
        shutil.rmtree(sys.argv[1])
        break
    except FileNotFoundError: break
    except OSError:
        if attempt == 19: raise
        time.sleep(.1)
PY_CLEAN
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
python3 tests/make_fixtures.py
ln -sfn ../../../_site artifacts/v0.2/subpath/ustudyopen-design
python3 -m http.server 4850 --bind 127.0.0.1 --directory _site > artifacts/v0.2/server.log 2>&1 &
uso_pids+=("$!")
python3 -m http.server 4851 --bind 127.0.0.1 --directory artifacts/v0.2/subpath > artifacts/v0.2/subpath-server.log 2>&1 &
uso_pids+=("$!")
# Keep Chromium's sandbox enabled. Fail with diagnostics if the host cannot run
# it; do not chmod a system binary, elevate privileges or silently disable it.
XDG_CONFIG_HOME="$uso_profile/config" XDG_CACHE_HOME="$uso_profile/cache" \
setsid "$uso_browser_bin" --headless --disable-gpu --disable-dev-shm-usage \
  --disable-background-networking --disable-component-update --disable-crash-reporter \
  --no-first-run --no-default-browser-check --password-store=basic \
  --user-data-dir="$uso_profile" --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9228 about:blank > artifacts/v0.2/browser.log 2>&1 &
uso_browser_pid=$!
uso_pids+=("$uso_browser_pid")
python3 - <<'PY'
import time, urllib.request
for url in ('http://127.0.0.1:4850/', 'http://127.0.0.1:4851/', 'http://127.0.0.1:9228/json/version'):
    for attempt in range(100):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200: break
        except OSError: time.sleep(.1)
    else: raise SystemExit(f'Test service unavailable: {url}; inspect artifacts/v0.2/browser.log')
PY
if [[ "$uso_suite" == all || "$uso_suite" == browser ]]; then
  "$uso_deno_bin" run --no-config --no-lock --allow-net=127.0.0.1:9228,127.0.0.1:4850 --allow-write=artifacts/v0.2 tests/browser.mjs > artifacts/v0.2/browser-tests.log 2>&1
fi
if [[ "$uso_suite" == all || "$uso_suite" == callouts ]]; then
  "$uso_deno_bin" run --no-config --no-lock --allow-net=127.0.0.1:9228,127.0.0.1:4850 --allow-write=artifacts/v0.2 tests/callouts.mjs > artifacts/v0.2/callouts-after.log 2>&1
fi
if [[ "$uso_suite" == all || "$uso_suite" == instances ]]; then
  "$uso_deno_bin" run --no-config --no-lock --allow-net=127.0.0.1:9228,127.0.0.1:4851 --allow-write=artifacts/v0.2 tests/instances.mjs > artifacts/v0.2/instances-tests.log 2>&1
fi
if [[ "$uso_suite" == all || "$uso_suite" == subpath ]]; then
  "$uso_deno_bin" run --no-config --no-lock --allow-net=127.0.0.1:9228,127.0.0.1:4851 --allow-write=artifacts/v0.2 tests/browser.mjs http://127.0.0.1:4851/ustudyopen-design/ http://127.0.0.1:9228 subpath > artifacts/v0.2/subpath-tests.log 2>&1
fi
if [[ "$uso_suite" == all || "$uso_suite" == sandbox ]]; then
  "$uso_deno_bin" run --no-config --no-lock --allow-net=127.0.0.1:9228 --allow-write=artifacts/v0.2 tests/sandbox.mjs > artifacts/v0.2/sandbox-tests.log 2>&1
fi
python3 - "$uso_suite" <<'PY'
from pathlib import Path
import json, sys
names = ('browser', 'callouts-after', 'instances', 'subpath') if sys.argv[1] == 'all' else (('callouts-after' if sys.argv[1] == 'callouts' else sys.argv[1]),)
for name in names:
    report=json.loads((Path('artifacts/v0.2')/(name+'-results.json' if name != 'callouts-after' else name+'.json')).read_text())
    print(name, report.get('summary', {'pass':report.get('pass')}))
PY
