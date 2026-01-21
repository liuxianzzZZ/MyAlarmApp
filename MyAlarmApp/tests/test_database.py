import os
from datetime import datetime, timedelta
from database import Database, DATE_FMT

TEST_DB = "test_tasks.db"

def setup_module(module=None):
    try:
        os.remove(TEST_DB)
    except Exception:
        pass

def test_add_and_query():
    db = Database(TEST_DB)
    due = (datetime.now() + timedelta(minutes=5)).strftime(DATE_FMT)
    task_id = db.add_task("测试任务", "备注", due, 2, "once")
    tasks = db.get_all_pending_tasks()
    assert any(t["id"] == task_id for t in tasks)

def test_check_alarm_once():
    db = Database(TEST_DB)
    due = (datetime.now() - timedelta(minutes=1)).strftime(DATE_FMT)
    db.add_task("到点一次", "", due, 3, "once")
    task = db.check_alarm(datetime.now())
    assert task is not None
    tasks = db.get_all_pending_tasks()
    assert all(t["title"] != "到点一次" or t["status"] == "pending" for t in tasks)

def test_check_alarm_daily_advance():
    db = Database(TEST_DB)
    due = (datetime.now() - timedelta(minutes=1)).strftime(DATE_FMT)
    db.add_task("到点每日", "", due, 3, "daily")
    task = db.check_alarm(datetime.now())
    assert task is not None
    next_tasks = db.get_all_pending_tasks()
    assert any(t["title"] == "到点每日" for t in next_tasks)

