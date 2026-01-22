#Code adapted from my submission for Autumn 2025 Intro to Python Homework 6

import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )

@app.get("/health")
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    cur = conn.cursor(dictionary=True)  # keeps task["id"] style working in template

    if request.method == "POST":
        description = request.form["description"]
        if description:
            cur.execute("INSERT INTO task (description) VALUES (%s)", (description,))
            conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT id, description, completed FROM task ORDER BY id DESC")
    tasks = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/toggle/<int:id>")
def toggle(id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT completed FROM task WHERE id = %s", (id,))
    task = cur.fetchone()

    new_status = 0 if (task and task["completed"]) else 1
    cur.execute("UPDATE task SET completed = %s WHERE id = %s", (new_status, id))
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM task WHERE id = %s", (id,))
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
