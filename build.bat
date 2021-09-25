@echo off
title building...
color 0a
pyinstaller --onefile --uac-admin --add-data "files;files" -w -i files/gdl_icon.ico main.py