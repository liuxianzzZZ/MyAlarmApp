import time
from datetime import datetime
from database import Database

def _is_android():
    try:
        import jnius
        return True
    except Exception:
        return False

def _start_activity(task_id: int):
    if not _is_android():
        return
    from jnius import autoclass
    PythonService = autoclass("org.kivy.android.PythonService")
    Context = autoclass("android.content.Context")
    Intent = autoclass("android.content.Intent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    service = PythonService.mService
    intent = Intent(service, PythonActivity)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP)
    intent.putExtra("alarm_task_id", int(task_id))
    service.startActivity(intent)

def run():
    db = Database()
    while True:
        now_dt = datetime.now()
        task = db.check_alarm(now_dt)
        if task:
            _start_activity(task["id"])
        time.sleep(60)

if __name__ == "__main__":
    run()
