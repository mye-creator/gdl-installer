@echo off
title building...
color 0a
venv\scripts\pyinstaller --onefile --add-data "files;files" -w -i files/gdl_icon.ico main.py