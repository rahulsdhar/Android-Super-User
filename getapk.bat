@echo off
copy /b /y %1 temp.apk
if %2=="a" (platform-tools\adb install temp.apk)
if %2=="b" (platform-tools\adb install -s temp.apk)
if %2=="c" (platform-tools\adb install -r temp.apk)
if %2=="d" (platform-tools\adb install -s -r temp.apk)
del temp.apk