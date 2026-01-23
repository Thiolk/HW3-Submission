import os

import mysql.connector
import pytest


def db_connect():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


@pytest.fixture()
def clean_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM task;")
    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture
def client():
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def insert_task(description: str, completed: int = 0) -> int:
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task (description, completed) VALUES (%s, %s)",
        (description, completed),
    )
    conn.commit()
    task_id = cur.lastrowid
    cur.close()
    conn.close()
    return task_id


def get_task(task_id: int):
    conn = db_connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, description, completed FROM task WHERE id=%s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def count_tasks() -> int:
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM task;")
    (count,) = cur.fetchone()
    cur.close()
    conn.close()
    return count
