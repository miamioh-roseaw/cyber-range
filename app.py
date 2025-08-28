import os
from pathlib import Path
from flask import (
    Flask, render_template, request, abort, send_from_directory,
    redirect, url_for, jsonify, flash
)
from markdown import Markdown
from dotenv import load_dotenv

# Auth
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# --- Auth config ---
AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH")

login_manager = LoginManager()
login_manager.login_view = "login"   # redirect here when @login_required
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

# Single user (from env vars)
def get_env_user():
    if not AUTH_USERNAME or not AUTH_PASSWORD_HASH:
        return None
    return User(user_id=AUTH_USERNAME, name=AUTH_USERNAME)

@login_manager.user_loader
def load_user(user_id):
    if AUTH_USERNAME and user_id == AUTH_USERNAME:
        return User(user_id=AUTH_USERNAME, name=AUTH_USERNAME)
    return None

# --- App config ---
DEFAULT_GNS3_URL = os.getenv("GNS3_URL", "http://127.0.0.1:3080")
LABS_DIR = Path(__file__).parent / "labs"
LABS_DIR.mkdir(exist_ok=True)

def list_labs():
    return sorted([p.stem for p in LABS_DIR.glob("*.md")])

def render_markdown_with_toc(text: str):
    md = Markdown(
        extensions=[
            "toc", "fenced_code", "tables", "codehilite", "sane_lists", "admonition"
        ],
        extension_configs={
            "toc": {"toc_depth": "2-6", "permalink": True}
        }
    )
    html = md.convert(text)
    toc_html = md.toc
    return html, toc_html

def load_lab_raw(lab_name: str) -> str:
    md_path = LABS_DIR / f"{lab_name}.md"
    if not md_path.exists():
        abort(404, description=f"Lab '{lab_name}' not found.")
    return md_path.read_text(encoding="utf-8")

# ---------- App routes (Option A: lock app pages; static remains public) ----------
@app.route("/")
@login_required
def home():
    labs = list_labs()
    if not labs:
        return render_template(
            "index.html",
            lab_html="<h2>No labs found</h2><p>Add a <code>.md</code> under <code>labs/</code>.</p>",
            toc_html="",
            labs=[],
            current_lab=None,
            gns3_url=DEFAULT_GNS3_URL,
            raw_md="",
            editing=False,
        )

    lab = request.args.get("lab") or labs[0]
    if lab not in labs:
        return redirect(url_for("home", lab=labs[0]))

    # Edit mode switch (still requires login)
    editing_param = request.args.get("edit") == "1"
    editing = editing_param and current_user.is_authenticated

    raw_md = load_lab_raw(lab)
    lab_html, toc_html = render_markdown_with_toc(raw_md)

    return render_template(
        "index.html",
        lab_html=lab_html,
        toc_html=toc_html,
        labs=labs,
        current_lab=lab,
        gns3_url=DEFAULT_GNS3_URL,
        raw_md=raw_md,
        editing=editing,
    )

@app.route("/save_lab", methods=["POST"])
@login_required
def save_lab():
    lab = request.form.get("lab")
    content = request.form.get("content", "")

    if not lab:
        return jsonify({"ok": False, "error": "Missing 'lab'"}), 400

    labs = list_labs()
    if lab not in labs:
        return jsonify({"ok": False, "error": f"Unknown lab '{lab}'"}), 404

    md_path = LABS_DIR / f"{lab}.md"
    try:
        md_path.write_text(content, encoding="utf-8")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/labs/<path:filename>")
@login_required
def serve_lab_raw(filename):
    return send_from_directory(LABS_DIR, filename, as_attachment=False)

# ---------- Auth routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    env_user = get_env_user()
    if not env_user:
        # No credentials configured—block login and editing
        flash("Auth is not configured. Set AUTH_USERNAME and AUTH_PASSWORD_HASH.", "error")
        return render_template("login.html", auth_configured=False)

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD_HASH, password):
            login_user(env_user)
            next_url = request.args.get("next") or url_for("home")
            return redirect(next_url)
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html", auth_configured=True)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
