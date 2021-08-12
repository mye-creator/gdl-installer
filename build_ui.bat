@echo off
title building...
color 0a
del files\installer.py
pyuic5 installer.ui -o files/installer.py -x
echo ok
