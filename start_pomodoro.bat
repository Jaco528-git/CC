@echo off
title 🍅 番茄钟
"C:\Users\31070\AppData\Local\Programs\Python\Python314\python.exe" "%~dp0pomodoro.py"
if errorlevel 1 (
    echo.
    echo 启动失败！
    pause
)
