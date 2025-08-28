# Flask GNS3 Split View (Labs + GNS3 Web UI) — Auth (Option A)

A Flask app that shows **lab instructions on the left** (Markdown — with a table of contents) and the **GNS3 Web UI on the right** in an iframe.
- **Edit Mode**: in‑browser Markdown editing + save
- **Left Index**: auto‑generated Table of Contents
- **Auth (Option A)**: All app pages require login (labs, save, index), while **static files remain public**. The login page is fully styled.

## Demo layout
- Left: lab selector, on‑page ToC, rendered Markdown or editor
- Right: configurable iframe to your GNS3 Web UI (set via `GNS3_URL`)

---

## Quick start

```bash
git clone <your-repo-url>
cd flask-gns3-split-auth
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env, see below
python app.py
```

Visit http://localhost:5000 — you'll be redirected to **/login**.

---

## Environment configuration

Create a strong app secret and a password hash for your login user.

```bash
export FLASK_SECRET_KEY='change-me'
export AUTH_USERNAME='admin'
python - <<'PY'
from werkzeug.security import generate_password_hash
print(generate_password_hash(input("Password to hash: "), method="pbkdf2:sha256", salt_length=16))
PY
# Copy the output into AUTH_PASSWORD_HASH in your .env
```

Then edit `.env`:

```ini
FLASK_SECRET_KEY=change-me
AUTH_USERNAME=admin
AUTH_PASSWORD_HASH=pbkdf2:sha256:600000$...   # paste the generated hash
GNS3_URL=http://127.0.0.1:3080                # your GNS3 Web UI
PORT=5000
```

---

## Option A Lockdown behavior

- **Login required** for:
  - `/` (main lab view)
  - `/labs/<file>` (raw markdown)
  - `/save_lab` (saving edits)
- **Public**:
  - `/login` (sign in)
  - `/logout` (sign out; requires login)
  - `/static/*` (CSS/JS/images) → allows a styled login page

If you need *total lockdown*, see Option B (not included here).

---

## Add labs

Drop Markdown files in the `labs/` folder (e.g., `intro.md`, `vlan_lab.md`). Their basenames become selectable lab names.

Markdown features enabled: fenced code blocks, tables, sane lists, admonitions, and a generated **ToC**.

---

## Security notes

- This sample uses single-user auth via environment variables. For production, consider a proper user store (DB), CSRF protection, reverse-proxy auth, and HTTPS.
- The GNS3 Web UI must allow embedding in an `<iframe>` (check `X-Frame-Options` / CSP on your GNS3 host). If the iframe is blocked, open GNS3 in a new tab instead.

---

## License

MIT
