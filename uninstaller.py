import os
import sys
import winreg
import json
import shutil
import time
import ctypes
import subprocess

ctypes.windll.kernel32.SetConsoleTitleW('GD Localisation Uninstaller')


REG_PATH = 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GDLoc'
EXPLORER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


input('Нажмите ENTER, чтобы удалить GDL (Press ENTER to remove GDL): ')


def explore(path):
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([EXPLORER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([EXPLORER_PATH, '/select,', path])


def clear_temp():
    for j in os.listdir(os.environ['TEMP']):
        path = os.path.join(os.environ['TEMP'], j)
        if not os.path.isdir(path):
            continue
        if not j.startswith('_MEI'):
            continue
        try:
            shutil.rmtree(path)
        except Exception as er:
            print(f'Not fully cleared: {er}')


try:
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_READ)
    os.chdir(os.path.dirname(winreg.QueryValueEx(key, 'UninstallString')[0].replace('"', '')))
    winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
except Exception as e:
    print(f'Error clearing regedit: {e}')


if os.path.isdir('adaf-dll'):
    if os.access('adaf-dll/GDLocalisation.dll', os.F_OK):
        os.remove('adaf-dll/GDLocalisation.dll')


temp_file = open('gdl_unins000.txt', 'rb')
backup = json.loads(temp_file.read().decode())
temp_file.close()

for i in backup:
    if not os.access(i, os.F_OK) or not os.access(backup[i], os.F_OK):
        continue
    try:
        os.remove(i)
    except Exception as e:
        print(f'Error removing backup: {e}')
    try:
        os.rename(backup[i], i)
    except Exception as e:
        print(f'Error renaming backup: {e}')

try:
    os.remove('gdl_unins000.txt')
except Exception as e:
    print(f'Error removing file: {e}')

print('Данный файл удалите вручную... (Remove this file manually...)')
time.sleep(3)
explore(sys.executable)
clear_temp()
