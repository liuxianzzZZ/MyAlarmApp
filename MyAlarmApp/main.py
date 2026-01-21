from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from database import Database, DATE_FMT
from android_utils import speak_task, is_android

def is_today(dt_str: str):
    try:
        d = datetime.strptime(dt_str, DATE_FMT)
    except Exception:
        return False
    now = datetime.now()
    return d.date() == now.date()

class TaskCard(BoxLayout):
    task_id = StringProperty("")
    title = StringProperty("")
    note = StringProperty("")
    due = StringProperty("")
    priority = StringProperty("")
    repeat_mode = StringProperty("")
    def on_complete(self):
        App.get_running_app().db.mark_done(int(self.task_id))
        App.get_running_app().refresh_task_list()
    def on_delete(self):
        App.get_running_app().db.soft_delete(int(self.task_id))
        App.get_running_app().refresh_task_list()
    def on_speak(self):
        speak_task(self.title, int(self.priority), self.note)

class Root(BoxLayout):
    title_input = ObjectProperty(None)
    note_input = ObjectProperty(None)
    due_input = ObjectProperty(None)
    priority_input = ObjectProperty(None)
    repeat_input = ObjectProperty(None)
    today_list = ObjectProperty(None)
    future_list = ObjectProperty(None)
    def add_task(self):
        title = self.title_input.text.strip()
        note = self.note_input.text.strip()
        due = self.due_input.text.strip()
        try:
            datetime.strptime(due, DATE_FMT)
        except Exception:
            return
        priority = int(self.priority_input.text)
        repeat_mode = self.repeat_input.text
        App.get_running_app().db.add_task(title, note, due, priority, repeat_mode)
        self.title_input.text = ""
        self.note_input.text = ""
        self.due_input.text = ""
        self.refresh()
    def refresh(self):
        App.get_running_app().refresh_task_list()

class MyAlarmApp(App):
    db: Database
    def build(self):
        self.db = Database()
        ui = Builder.load_file("myapp.kv")
        Clock.schedule_once(lambda _: self.refresh_task_list(), 0)
        Clock.schedule_once(lambda _: self._start_service(), 0.1)
        Clock.schedule_once(lambda _: self._handle_alarm_intent(), 0.2)
        return ui
    def refresh_task_list(self):
        tasks = self.db.get_all_pending_tasks()
        def dt_key(x):
            try:
                return datetime.strptime(x["due_datetime"], DATE_FMT)
            except Exception:
                return datetime.max
        tasks.sort(key=dt_key)
        tasks.sort(key=lambda x: int(x["priority"]), reverse=True)
        root = self.root
        root.today_list.clear_widgets()
        root.future_list.clear_widgets()
        for t in tasks:
            card = TaskCard()
            card.task_id = str(t["id"])
            card.title = t["title"]
            card.note = t["note"]
            card.due = t["due_datetime"]
            card.priority = str(t["priority"])
            card.repeat_mode = t["repeat_mode"]
            if is_today(t["due_datetime"]):
                root.today_list.add_widget(card)
            else:
                root.future_list.add_widget(card)
    def _handle_alarm_intent(self):
        if not is_android():
            return
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        activity = PythonActivity.mActivity
        intent = activity.getIntent()
        if intent and intent.hasExtra("alarm_task_id"):
            task_id = intent.getIntExtra("alarm_task_id", -1)
            task = self.db.get_task_by_id(int(task_id))
            if task:
                speak_task(task["title"], int(task["priority"]), task["note"])
    def _start_service(self):
        if not is_android():
            return
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        activity = PythonActivity.mActivity
        ServiceClass = autoclass("org.kivy.android.PythonService")
        intent = Intent(activity, ServiceClass)
        intent.putExtra("android.service.argument", "alarm")
        activity.startService(intent)

if __name__ == "__main__":
    MyAlarmApp().run()
