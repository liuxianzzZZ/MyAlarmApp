[app]
title = MyAlarmApp
package.name = myalarmapp
package.domain = org.example
source.dir = .
source.include_exts = py,kv,db
version = 0.1.0
requirements = python3,kivy,pyjnius,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = WAKE_LOCK,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,VIBRATE,SYSTEM_ALERT_WINDOW
services = alarm:service.py
android.allow_backup = False
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
