from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os, time, subprocess, threading, psutil, uuid

app = Flask(__name__)
app.secret_key = "NASSIM_ULTRA_SECRET"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== DATABASE =====
def db():
    return sqlite3.connect("database.db")

def init_db():
    conn = db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS codes (code TEXT, expire INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS bots (id TEXT, name TEXT, status TEXT)")
    conn.commit()
    conn.close()

init_db()

# ===== LOGIN =====
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        if password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        conn = db()
        c = conn.cursor()
        c.execute("SELECT * FROM codes WHERE code=?", (password,))
        data = c.fetchone()

        if data and time.time() < data[1]:
            session["user"] = True
            return redirect("/dashboard")

        return "❌ كلمة السر خاطئة"

    return render_template("login.html")

# ===== DASHBOARD =====
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("dashboard.html", files=files)

# ===== ADMIN =====
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        code = request.form["code"]
        hours = int(request.form["time"])
        expire = time.time() + hours*3600

        conn = db()
        c = conn.cursor()
        c.execute("INSERT INTO codes VALUES (?,?)",(code,expire))
        conn.commit()
        conn.close()

    return render_template("admin.html")

# ===== UPLOAD + RUN =====
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    file = request.files["file"]
    filename = file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    bot_id = str(uuid.uuid4())

    def run():
        subprocess.Popen(["python", path])

    threading.Thread(target=run).start()

    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO bots VALUES (?,?,?)",(bot_id, filename, "running"))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ===== STATUS =====
@app.route("/status")
def status():
    return jsonify({
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    })

# ===== RUN =====
app.run(host="0.0.0.0", port=5000)
