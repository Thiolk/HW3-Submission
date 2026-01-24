from conftest import count_tasks, get_task, insert_task


def test_tasks_are_displayed(client):
    insert_task("Task A", completed=0)
    insert_task("Task B", completed=1)

    resp = client.get("/")
    assert resp.status_code == 200

    html = resp.data.decode("utf-8")
    # To force fail pytest
    assert "FAIL THE TEST" in html
    assert "Task A" in html
    assert "Task B" in html


def test_add_task_increases_count(client):
    before = count_tasks()

    resp = client.post("/", data={"description": "New Task"}, follow_redirects=True)
    assert resp.status_code == 200

    after = count_tasks()
    assert after == before + 1

    html = resp.data.decode("utf-8")
    assert "New Task" in html


def test_delete_task_decreases_count(client):
    task_id = insert_task("Delete Me", completed=0)
    before = count_tasks()

    resp = client.get(f"/delete/{task_id}", follow_redirects=True)
    assert resp.status_code == 200

    after = count_tasks()
    assert after == before - 1


def test_toggle_task_to_completed(client):
    task_id = insert_task("Toggle Me", completed=0)

    resp = client.get(f"/toggle/{task_id}", follow_redirects=True)
    assert resp.status_code == 200

    task = get_task(task_id)
    assert task is not None
    assert task["completed"] == 1


def test_toggle_task_back_to_not_completed(client):
    task_id = insert_task("Toggle Back", completed=1)

    resp = client.get(f"/toggle/{task_id}", follow_redirects=True)
    assert resp.status_code == 200

    task = get_task(task_id)
    assert task is not None
    assert task["completed"] == 0
