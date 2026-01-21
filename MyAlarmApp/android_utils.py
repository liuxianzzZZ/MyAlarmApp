import time
from datetime import datetime

def is_android():
    try:
        import jnius
        return True
    except Exception:
        return False

def get_current_time_str():
    return datetime.now().strftime("%H点%M分")

def speak(text: str):
    if not is_android():
        print(text)
        return
    from jnius import autoclass, cast
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
    Locale = autoclass("java.util.Locale")
    Runnable = autoclass("java.lang.Runnable")
    activity = PythonActivity.mActivity
    tts = TextToSpeech(activity, None)
    tts.setLanguage(Locale.CHINA)
    speak_mode = autoclass("android.speech.tts.TextToSpeech").QUEUE_FLUSH
    activity.runOnUiThread(cast(Runnable, Runnable(lambda: None)))
    tts.speak(text, speak_mode, None, "alarm_tts")

def vibrate(ms: int = 1000):
    if not is_android():
        return
    from jnius import autoclass, cast
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    activity = PythonActivity.mActivity
    vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
    VibrationEffect = autoclass("android.os.VibrationEffect")
    effect = VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE)
    vibrator.vibrate(effect)

def wake_screen():
    if not is_android():
        return
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    PowerManager = autoclass("android.os.PowerManager")
    activity = PythonActivity.mActivity
    pm = activity.getSystemService("power")
    wake_lock = pm.newWakeLock(PowerManager.FULL_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP | PowerManager.ON_AFTER_RELEASE, "MyAlarmApp:WakeLock")
    wake_lock.acquire(3000)

def speak_task(task_title: str, priority: int, note: str):
    intro = "现在时刻，" + get_current_time_str()
    priority_msg = "这是一个高优先级任务。" if int(priority) > 2 else ""
    content = f"{intro}。{priority_msg} 请立即处理：{task_title}。{note}"
    wake_screen()
    vibrate(800)
    speak(content)
    time.sleep(1)
