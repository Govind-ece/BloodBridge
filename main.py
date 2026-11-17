"""BloodBridge: a small public site that connects volunteer blood donors with people who need blood.
Run locally:  python app.py      Production:  gunicorn app:app
Settings come from environment variables: SECRET_KEY, ADMIN_PASSWORD, DB_PATH, CONTACT_EMAIL, PRODUCTION"""
import hmac, os, re, secrets, sqlite3, time
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)  # set SECRET_KEY so logins survive restarts
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=bool(os.environ.get("PRODUCTION")),
                  MAX_CONTENT_LENGTH=16 * 1024)
DB = os.environ.get("DB_PATH", "bloodbridge.db")
ADMIN_PW = os.environ.get("ADMIN_PASSWORD", "")
CONTACT = os.environ.get("CONTACT_EMAIL", "")
GROUPS = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
CAN = {"O-": ["O-"], "O+": ["O+", "O-"], "A-": ["A-", "O-"], "A+": ["A+", "A-", "O+", "O-"], "B-": ["B-", "O-"],
       "B+": ["B+", "B-", "O+", "O-"], "AB-": ["AB-", "A-", "B-", "O-"], "AB+": GROUPS}
PHONE = re.compile(r"^(\+91)?[6-9]\d{9}$")

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d:
        d.close()

with sqlite3.connect(DB) as c:
    c.executescript("""
    CREATE TABLE IF NOT EXISTS donors(id INTEGER PRIMARY KEY, name TEXT, age INT, bgroup TEXT, city TEXT, phone TEXT,
        avail INT DEFAULT 1, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, contact_name TEXT, phone TEXT, bgroup TEXT, city TEXT,
        units INT, urgent INT, note TEXT, done INT DEFAULT 0, created TEXT DEFAULT CURRENT_TIMESTAMP);""")

def csrf():
    session.setdefault("csrf", secrets.token_hex(16))
    return session["csrf"]
app.jinja_env.globals.update(csrf=csrf, GROUPS=GROUPS, CONTACT=CONTACT)

@app.before_request
def guard():
    if request.method == "POST":
        if not hmac.compare_digest(request.form.get("csrf", ""), session.get("csrf", "x")):
            abort(400)

LAST = {}
def too_fast():
    ip = (request.headers.get("X-Forwarded-For", "").split(",")[0] or request.remote_addr or "?").strip()
    now = time.time()
    if now - LAST.get(ip, 0) < 20:
        return True
    LAST[ip] = now
    return False

def clean(name, n=60):
    return re.sub(r"\s+", " ", request.form.get(name, "")).strip()[:n]

def check_common(f):
    """Shared validation for donor and request forms. Returns an error message or ''."""
    if request.form.get("website"):  # honeypot: real people leave this hidden field empty
        abort(400)
    if f["bgroup"] not in GROUPS:
        return "Choose a valid blood group."
    if not f["city"]:
        return "Enter your city."
    if not PHONE.match(f["phone"]):
        return "Enter a valid 10-digit Indian mobile number."
    return ""

@app.get("/")
def index():
    d = db()
    by = {r["bgroup"]: r["n"] for r in d.execute("SELECT bgroup, COUNT(*) n FROM donors WHERE avail=1 GROUP BY bgroup")}
    cities = d.execute("SELECT city, COUNT(*) n FROM donors WHERE avail=1 GROUP BY LOWER(city) ORDER BY n DESC LIMIT 6").fetchall()
    total = d.execute("SELECT COUNT(*) FROM donors WHERE avail=1").fetchone()[0]
    open_r = d.execute("SELECT COUNT(*) FROM requests WHERE done=0").fetchone()[0]
    return render_template("index.html", by=by, cities=cities, total=total, open_r=open_r)

@app.route("/donate", methods=["GET", "POST"])
def donate():
    f = {"name": clean("name"), "age": clean("age", 3), "bgroup": clean("bgroup", 3), "city": clean("city", 40),
         "phone": re.sub(r"[\s-]", "", clean("phone", 16))}
    err = ""
    if request.method == "POST":
        ok_boxes = all(request.form.get(k) for k in ("eligible", "consent"))
        err = check_common(f)
        if not err:
            if not f["name"]: err = "Enter your name."
            elif not (f["age"].isdigit() and 18 <= int(f["age"]) <= 65): err = "Donors must be aged 18 to 65."
            elif not ok_boxes: err = "Please tick both boxes to continue."
            elif too_fast(): err = "Please wait a few seconds and try again."
        if not err:
            db().execute("INSERT INTO donors(name,age,bgroup,city,phone) VALUES(?,?,?,?,?)",
                         (f["name"], int(f["age"]), f["bgroup"], f["city"], f["phone"]))
            db().commit()
            return render_template("thanks.html", kind="donor")
    return render_template("donate.html", f=f, err=err)

@app.route("/request", methods=["GET", "POST"])
def need():
    f = {"name": clean("name"), "bgroup": clean("bgroup", 3), "city": clean("city", 40), "units": clean("units", 2),
         "phone": re.sub(r"[\s-]", "", clean("phone", 16)), "note": clean("note", 200)}
    err = ""
    if request.method == "POST":
        err = check_common(f)
        if not err:
            if not f["name"]: err = "Enter your name."
            elif not (f["units"].isdigit() and 1 <= int(f["units"]) <= 10): err = "Units must be from 1 to 10."
            elif not request.form.get("consent"): err = "Please tick the box to continue."
            elif too_fast(): err = "Please wait a few seconds and try again."
        if not err:
            db().execute("INSERT INTO requests(contact_name,phone,bgroup,city,units,urgent,note) VALUES(?,?,?,?,?,?,?)",
                         (f["name"], f["phone"], f["bgroup"], f["city"], int(f["units"]),
                          int(bool(request.form.get("urgent"))), f["note"]))
            db().commit()
            return render_template("thanks.html", kind="request")
    return render_template("request.html", f=f, err=err)

@app.get("/privacy")
def privacy():
    return render_template("privacy.html")

# ---- admin: only you can see phone numbers and connect people ----
def is_admin():
    return bool(ADMIN_PW) and session.get("admin") is True

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
        if ADMIN_PW and hmac.compare_digest(request.form.get("password", ""), ADMIN_PW):
            session["admin"] = True
            return redirect(url_for("admin"))
        time.sleep(1)
        err = "Wrong password, or ADMIN_PASSWORD is not set on the server."
    return render_template("login.html", err=err)

@app.get("/admin")
def admin():
    if not is_admin():
        return redirect(url_for("login"))
    donors = db().execute("SELECT * FROM donors ORDER BY id DESC").fetchall()
    reqs = db().execute("SELECT * FROM requests ORDER BY done, urgent DESC, id DESC").fetchall()
    match = {}
    for r in reqs:
        c = [d for d in donors if d["bgroup"] in CAN[r["bgroup"]] and d["avail"]]
        c.sort(key=lambda d: d["city"].lower() != r["city"].lower())
        match[r["id"]] = c
    return render_template("admin.html", donors=donors, reqs=reqs, match=match)

@app.post("/admin/<what>/<int:i>/<act>")
def act(what, i, act):
    if not is_admin():
        abort(403)
    sql = {("donor", "toggle"): "UPDATE donors SET avail=1-avail WHERE id=?", ("donor", "delete"): "DELETE FROM donors WHERE id=?",
           ("request", "done"): "UPDATE requests SET done=1-done WHERE id=?", ("request", "delete"): "DELETE FROM requests WHERE id=?"}
    if (what, act) not in sql:
        abort(404)
    db().execute(sql[(what, act)], (i,))
    db().commit()
    return redirect(url_for("admin"))

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
