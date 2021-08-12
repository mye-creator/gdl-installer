@echo off
title building...
color 0a
del files/installer.py
pyuic5 installer.ui -o installer.py -x
copy installer.py files/installer.py
del installer.py
echo ok
