@echo off
title building...
color 0a
venv/scripts/pyinstaller --onefile --uac-admin -w -i files/gdl_icon.ico uninstaller.py
