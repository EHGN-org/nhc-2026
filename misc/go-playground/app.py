import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DEFAULT_CODE = """package main

import "fmt"

func main() {
	fmt.Println("Hello, NHC")
}
"""

CACHE_DIR = Path(os.environ.get("GOCACHE", "/tmp/gocache"))
GOPATH_DIR = Path(os.environ.get("GOPATH", "/tmp/gopath"))
GOMODCACHE_DIR = GOPATH_DIR / "pkg" / "mod"


def _ensure_cache():
    for d in (CACHE_DIR, GOPATH_DIR, GOMODCACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        proc.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()


def _run(argv: list[str], *, cwd: str, env: dict, timeout: float, **popen_kw) -> tuple[str, bool]:
    proc = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
        **popen_kw,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        return "timed out", True
    return out or "", proc.returncode != 0


def run_snippet(code: str) -> tuple[str, bool]:
    _ensure_cache()
    env = os.environ.copy()
    env["GOPROXY"] = "off"
    env["CGO_ENABLED"] = "0"
    env["PATH"] = "/usr/local/go/bin:/usr/bin:/bin"
    env["GOCACHE"] = str(CACHE_DIR)
    env["GOPATH"] = str(GOPATH_DIR)
    env["GOMODCACHE"] = str(GOMODCACHE_DIR)

    with tempfile.TemporaryDirectory(prefix="go-", dir="/tmp") as tmp:
        Path(tmp, "main.go").write_text(code)
        Path(tmp, "go.mod").write_text("module playground\n\ngo 1.23\n")
        os.chmod(tmp, 0o711)
        # Compiler scratch lives in the snippet dir so TemporaryDirectory
        # removes go-build* trees even after a timeout kill.
        env["GOTMPDIR"] = tmp
        out, failed = _run(
            ["/bin/sh", "-c", "go generate && go build -o main ."],
            cwd=tmp,
            env=env,
            timeout=20,
        )
        if failed:
            return out, True
        ran_out, ran_failed = _run(
            [str(Path(tmp, "main"))],
            cwd=tmp,
            env=env,
            timeout=5,
            user="nobody",
            group="nogroup",
        )
        return out + ran_out, ran_failed


@app.route("/", methods=["GET", "POST"])
def index():
    code = DEFAULT_CODE
    output = ""
    elapsed = None
    error = False
    if request.method == "POST":
        code = request.form.get("code") or ""
        if not code.strip():
            output = "code is empty"
            error = True
        elif len(code) > 64 * 1024:
            output = "code is too large"
            error = True
        else:
            t0 = time.perf_counter()
            output, error = run_snippet(code)
            elapsed = time.perf_counter() - t0
    return render_template("index.html", code=code, output=output, elapsed=elapsed, error=error)
