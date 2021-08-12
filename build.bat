@echo off
title building...
color 0a
del installer.py
pyuic5 installer.ui -o installer.py -x
echo ok
