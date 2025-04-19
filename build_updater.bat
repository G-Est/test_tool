@echo off
pip install pyinstaller requests
pyinstaller --noconsole --onefile updater.py
pause
