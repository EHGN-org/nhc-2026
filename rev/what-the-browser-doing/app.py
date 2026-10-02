from base64 import b64encode
import gzip
from pathlib import Path
import itertools
from gen import encrypt_data

from flask import Flask, Response, jsonify, redirect, render_template, request

app = Flask(__name__)

FAKE_SOURCE = "//youtu.be/dQw4w9WgXcQ\n\n//# sourceMappingURL=sw.js.map"
FAKE_RESPONSE = redirect("//youtu.be/dQw4w9WgXcQ")

HASH, CIPHERTEXT = encrypt_data("NHC391", "NHC{wh3N_Th3_S3Rv1C3_W0Rk3Rs_W0Rk_4G41Nst_Y0U}")

class DoubleGzipMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        collected = []
        captured = []

        def _start_response(status, headers, exc_info=None):
            captured[:] = [status, headers, exc_info]
            return collected.append

        app_iter = self.wsgi_app(environ, _start_response)
        try:
            body = b"".join(collected) + b"".join(app_iter)
        finally:
            close = getattr(app_iter, "close", None)
            if close is not None:
                close()

        status, headers, exc_info = captured
        code = int(status.split(None, 1)[0])
        if environ["REQUEST_METHOD"] == "HEAD" or code < 200 or code in (204, 304):
            start_response(status, headers, exc_info)
            return [body]

        body = gzip.compress(body) + b'\'"><meta http-equiv=refresh content=0;https://youtu.be/dQw4w9WgXcQ>'
        compressed = gzip.compress(body)
        headers = [
            (key, value)
            for key, value in headers
            if key.lower() not in ("content-length", "content-encoding")
        ]
        headers.append(("Content-Encoding", "gzip, gzip"))
        headers.append(("Content-Length", str(len(compressed))))
        start_response(status, headers)
        return [compressed]


app.wsgi_app = DoubleGzipMiddleware(app.wsgi_app)


def invisible_permutations(s):
    result = []
    for amount in itertools.product(range(3), repeat=len(s)+1):
        result.append("\u2065" * amount[0] + "".join(s[i] + "\u2065" * amount[i+1] for i in range(len(s))))
    return result

def fake_sourcemap(generated: str) -> dict:
    n_lines = generated.count("\n") + (0 if generated.endswith("\n") else 1)
    sources = invisible_permutations("sw.js")
    sources.remove("s\u2065w.j\u2065s")  # remove original source
    return {
        "version": 3,
        "file": "sw.js",
        "sources": sources,
        "sourcesContent": [FAKE_SOURCE] * len(sources),
        "names": [],
        "mappings": ";".join(["AAAA"] * max(n_lines, 1)),
    }


def html_escape_all(s: str) -> str:
    return "".join(f"&#{ord(c)};" for c in s)

def sw_source() -> str:
    source = (Path(__file__).parent / "js" / "sw.js").read_text()
    source = source.replace("REPLACEME_HASH", HASH)
    source = source.replace("REPLACEME_CIPHERTEXT", CIPHERTEXT)
    password_js = (Path(__file__).parent / "js" / "password.js").read_text()
    source = source.replace("REPLACEME_PASSWORD_JS", html_escape_all(password_js))
    return source


@app.after_request
def encode_response(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/s\u2065w.j\u2065s")
def sw():
    if request.headers.get("Sec-Fetch-Dest") != "serviceworker" or \
        request.headers.get("Sec-Fetch-Mode") != "same-origin" or \
        request.headers.get("Sec-Fetch-Site") != "same-origin" or \
        request.headers.get("Service-Worker") != "script" or \
            "Mozilla/5.0" not in request.headers.get("User-Agent"):
        return FAKE_RESPONSE
    
    body = FAKE_SOURCE.replace("\n\n", "\n" + " "*1000 + "\uFFA0"*1000 + f"=eval(atob('{b64encode(sw_source().encode()).decode()}'))\n")
    return Response(body, headers={"SourceMap": "sw.js.map"}, mimetype="application/javascript")


@app.route("/sw.js.map")
def sw_map():
    return jsonify(fake_sourcemap(sw_source()))

@app.route("/<path:path>")
def fallback(path):
    return FAKE_RESPONSE

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
