from datetime import datetime
import hashlib
import os
import secrets
import sqlite3
import subprocess
import cherrypy
from jinja2 import Environment, FileSystemLoader, select_autoescape


LOG_PATH = "/tmp/app.log"
DB_PATH = "/tmp/app.db"
FIX_PREFIX = "CRITICAL ERROR! Fix with: "
LOG_TAIL = 100
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
STATIC_DIR = os.path.join(APP_DIR, "static")

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def render(template_name, **ctx):
    return jinja_env.get_template(template_name).render(**ctx)


def error_page(status, message, traceback, version):
    return render("error.html", status=status, message=message)


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              username TEXT PRIMARY KEY,
              password TEXT NOT NULL
            )
            """
        )
        password = secrets.token_urlsafe(32)
        print(f"Admin password: {password}")
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("admin", hashlib.sha256(password.encode()).hexdigest()),
        )


def read_all_log_lines():
    if not os.path.isfile(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        lines = f.read().split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        return lines


def read_log_lines():
    lines = read_all_log_lines()
    offset = max(0, len(lines) - LOG_TAIL)
    return lines[-LOG_TAIL:], offset


def access_log():
    request = cherrypy.request
    response = cherrypy.response
    date = datetime.now().isoformat(timespec="seconds")
    path = request.wsgi_environ.get("REQUEST_URI", request.path_info).split("?", 1)[0]
    user_agent = request.headers.get("User-Agent", "-")
    status = str(response.status).split(" ", 1)[0]
    length = response.headers.get("Content-Length", "-")
    with open(LOG_PATH, "a") as f:
        f.write(f'[{date}] "{request.method} {path}" {status} {length} "{user_agent}"\n')


cherrypy.tools.access_log = cherrypy.Tool("on_end_resource", access_log)


def check_admin_password(realm, username, password):
    if not username or not password:
        return False
    query = f"SELECT password FROM users WHERE username = '{username}' LIMIT 1"
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(query).fetchone()
    if not row:
        return False
    return hashlib.sha256(password.encode()).hexdigest() == row[0]


class Admin:
    @cherrypy.expose
    def index(self):
        lines, offset = read_log_lines()
        return render(
            "debug.html",
            lines=lines,
            offset=offset,
            fix_prefix=FIX_PREFIX,
        )

    @cherrypy.expose
    def run(self, line=""):
        try:
            idx = int(line)
        except (TypeError, ValueError):
            raise cherrypy.HTTPError(400, "Invalid line")

        lines = read_all_log_lines()
        start = max(0, len(lines) - LOG_TAIL)
        if idx < start or idx >= len(lines):
            raise cherrypy.HTTPError(400, "Invalid line")

        selected = lines[idx]
        if not selected.startswith(FIX_PREFIX):
            raise cherrypy.HTTPError(400, "Not a fix command")

        cmd = selected[len(FIX_PREFIX) :]
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return render("run.html", output=output)


class Root:
    def __init__(self):
        self.admin = Admin()

    @cherrypy.expose
    def index(self):
        return render("index.html")


if __name__ == "__main__":
    init_db()
    conf = {
        "/": {
            "tools.access_log.on": True,
            # Behind the TLS edge cherrypy only sees http, so absolute
            # redirects (e.g. the /admin trailing-slash 301) would downgrade
            # to http:// and clients drop Authorization on the way back.
            # Trust the edge's X-Forwarded-Proto/Host so redirects stay https.
            "tools.proxy.on": True,
            "error_page.default": error_page,
        },
        "/admin": {
            "tools.auth_basic.on": True,
            "tools.auth_basic.realm": "admin",
            "tools.auth_basic.checkpassword": check_admin_password,
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": STATIC_DIR,
            "tools.access_log.on": False,
        },
    }
    cherrypy.config.update(
        {
            "environment": "production",
            "server.socket_host": "0.0.0.0",
            "server.socket_port": 1337,
        }
    )
    cherrypy.quickstart(Root(), config=conf)
