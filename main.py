import os
import sys
import json
import shutil
import winreg
from requests import get
from threading import Thread
from PyQt5 import QtWidgets, QtCore
from files.installer import Ui_MainWindow


base_url = 'https://pixelsuft.github.io/gdl-installer-files/'
base_folder = ''
REG_PATH = 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GDLoc'
os.chdir(os.path.dirname(__file__))


forward_events = []
back_events = []


def clear_temp():
    for i in os.listdir(os.environ['TEMP']):
        path = os.path.join(os.environ['TEMP'], i)
        if not os.path.isdir(path):
            continue
        if not i.startswith('_MEI'):
            continue
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f'Not fully cleared: {e}')


def unbind_buttons():
    global forward_events, back_events
    for i in forward_events:
        ui.goForwardButton.clicked.disconnect(i)
    for i in back_events:
        ui.goBackButton.clicked.disconnect(i)
    forward_events, back_events = [], []


def bind_forward(func):
    forward_events.append(func)
    ui.goForwardButton.clicked.connect(func)


def bind_back(func):
    back_events.append(func)
    ui.goBackButton.clicked.connect(func)


log_to_do = None
progress_to_do = None
to_setup = 0


def log(text_to_log):
    global log_to_do
    log_to_do = text_to_log.split('\n')
    while log_to_do:
        pass
    # ui.logEdit.addItem(i)


def progress(percent):
    global progress_to_do
    progress_to_do = percent
    while progress_to_do:
        pass
    # ui.barEdit.setValue(percent)


def get_url(url_path):
    return base_url + url_path


def fast_write(filename, content):
    if type(content) == bytes:
        temp_file = open(filename, 'wb')
        temp_file.write(content)
        temp_file.close()
    elif type(content) == str:
        temp_file = open(filename, 'w')
        temp_file.write(content)
        temp_file.close()


def testo():
    global progress_to_do, log_to_do, to_setup
    if to_setup == 2:
        return
    elif to_setup == 1:
        to_setup = 2
        setup_buttons(4)
    if log_to_do:
        need_scroll = ui.logEdit.verticalScrollBar().maximum() == ui.logEdit.verticalScrollBar().value()
        for i in log_to_do:
            ui.logEdit.addItem(i)
            if need_scroll:
                ui.logEdit.scrollToBottom()
        log_to_do = None
    if progress_to_do:
        ui.barEdit.setValue(progress_to_do)
        progress_to_do = None


def install_gdl(install_type):
    global to_setup
    backup = {}
    log(f'Базовый url: {base_url}')
    log(f'Базовая папка: {base_folder}')
    progress(1)
    log(f'Скачиваем файл локализации...')
    progress(3)
    fast_write(os.path.join(base_folder, 'ru_ru.json'), get(get_url('gdl_res/ru_ru.json')).content)
    progress(5)
    if install_type == 'default':
        '''log('Делаем бэкап файла расширений...')
        ext_path = os.path.join(base_folder, 'libExtensions.dll')
        backup[ext_path] = ext_path + '.backup'
        log('Скачиваем модифицированный файл расширений...')
        fast_write(ext_path, get(get_url('gdl_res/libExtensions.dll')).content)
        fast_write(os.path.join(base_folder, 'GDDLLLoader.dll'), get(get_url('gdl_res/GDDLLLoader.dll')).content)'''
        ext_path = os.path.join(base_folder, 'xinput9_1_0.dll')
        if not file_exists(ext_path):
            log('Скачиваем фейковый XInput...')
            fast_write(ext_path, get(get_url('gdl_res/xinput9_1_0.dll')).content)
    progress(7)
    log('Скачиваем dll...')
    dll_dir = os.path.join(base_folder, 'adaf-dll' if install_type == 'default' else install_type)
    if not os.path.isdir(dll_dir):
        os.makedirs(dll_dir)
    progress(8)
    dll_path = os.path.join(dll_dir, 'GDLocalisation.dll')
    progress(9)
    fast_write(dll_path, get(get_url('gdl_res/GDLocalisation.dll')).content)
    progress(10)
    log('Скачиваем дезинсталлятор...')
    progress(11)
    uninstall_path = os.path.join(
        base_folder, 'gdl_unins000.exe'
    ).replace("/", "\\")
    progress(12)
    fast_write(uninstall_path, get(get_url('gdl_res/gdl_unins000_32bit.exe')).content)
    progress(15)
    log('Получаем список файлов...')
    progress(16)
    files_list = get(get_url('gdl_res/res_files.txt')).content.decode().split('\n')
    progress(20)
    list_len = len(files_list)
    one_progress = 70 / list_len if list_len > 0 else 70

    for i in range(list_len):
        log(f'Сохраняем файл {files_list[i]}...')
        file_url = get_url('gd_res/' + files_list[i])
        file_path = os.path.join(base_folder, 'Resources', files_list[i])
        if not files_list[i].strip():
            continue
        try:
            file_content = get(file_url).content
        except Exception as e:
            log(f'Ошибка скачивания файла: {e}')
            continue

        if file_exists(file_path) and not file_exists(file_path + '.backup'):
            log(f'Делаем бэкап файла...')
            os.rename(file_path, file_path + '.backup')

        backup[file_path] = file_path + '.backup'
        fast_write(file_path, file_content)
        progress(20 + int(one_progress * i))
    log('Регистрируем как приложение...')
    icon_path = os.path.join(base_folder, 'Resources', 'gdl_icon.ico').replace("/", "\\")
    shutil.copy('files/gdl_icon.ico', icon_path)

    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
    except WindowsError:
        pass
    key = winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_WRITE)

    winreg.SetValueEx(key, 'DisplayIcon', 0, winreg.REG_SZ, icon_path)
    winreg.SetValueEx(key, 'DisplayName', 0, winreg.REG_SZ, 'Geometry Dash Localisation')
    winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, '1.0.0')
    winreg.SetValueEx(key, 'UninstallString', 0, winreg.REG_SZ, f'"{uninstall_path}"')
    winreg.SetValueEx(key, 'Publisher', 0, winreg.REG_SZ, 'The GDL Community')
    winreg.SetValueEx(key, 'NoModify', 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, 'NoRepair', 0, winreg.REG_DWORD, 1)

    log('Сохраняем файлы бэкапа в файл...')
    fast_write(os.path.join(base_folder, 'gdl_unins000.txt'), json.dumps(backup))
    progress(100)
    to_setup = 1


def file_exists(file_path):
    return os.access(file_path, os.F_OK)


def setup_buttons(tab_id):
    if tab_id == 0:
        ui.tabs.setCurrentIndex(0)
        ui.goBackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(True)

        unbind_buttons()
        bind_forward(lambda: setup_buttons(1))
    elif tab_id == 1:
        ui.tabs.setCurrentIndex(1)
        ui.folderpathEdit.setText('')
        ui.goBackButton.setEnabled(True)
        ui.goForwardButton.setEnabled(False)
        ui.goForwardButton.setText('Далее')

        unbind_buttons()
        bind_back(lambda: setup_buttons(0))
        bind_forward(lambda: setup_buttons(2))
    elif tab_id == 2:
        ui.tabs.setCurrentIndex(2)
        ui.goBackButton.setEnabled(True)
        ui.goForwardButton.setEnabled(True)
        ui.goForwardButton.setText('Установить')

        unbind_buttons()
        bind_back(lambda: setup_buttons(1))
        bind_forward(lambda: setup_buttons(3))
    elif tab_id == 3:
        ui.tabs.setCurrentIndex(3)
        ui.goBackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(False)
        ui.cancelButton.setEnabled(False)
        unbind_buttons()
        install_type = 'default'
        if ui.loaderType.isChecked():
            install_type = 'adaf-dll'
        elif ui.modType.isChecked():
            install_type = 'mods'
        elif ui.hackType.isChecked():
            install_type = 'extensions'
        # install_gdl(install_type)
        MainWindow.tomer=QtCore.QTimer()
        MainWindow.tomer.timeout.connect(testo)
        MainWindow.tomer.start(10)
        Thread(target=lambda: install_gdl(install_type)).start()
    elif tab_id == 4:
        ui.tabs.setCurrentIndex(4)
        ui.goBackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(True)
        ui.goForwardButton.setText('Готово')
        unbind_buttons()

        bind_forward(lambda: sys.exit(on_exit(0)))


def bind_events():
    def on_cancel_pressed():
        box = QtWidgets.QMessageBox(MainWindow)
        box.setIcon(box.Question)
        box.setWindowTitle('Выход из установки')
        box.setText('Вы уверены, что хотите выйти?')
        box.addButton('Да', box.ActionRole).clicked.connect(lambda: sys.exit(on_exit(0)))
        box.addButton('Нет', box.ActionRole).clicked.connect(box.hide)
        box.show()

    ui.cancelButton.clicked.connect(on_cancel_pressed)

    def check_path():
        global base_folder
        path = ui.folderpathEdit.text()
        curl_path = os.path.join(path, 'libcurl.dll')
        extensions_path = os.path.join(path, 'libExtensions.dll')
        if file_exists(curl_path) and file_exists(extensions_path):
            dll_loader_path = os.path.join(path, 'adaf-dll')
            mod_loader_path = os.path.join(path, 'mods')
            mega_hack_path = os.path.join(path, 'extensions')
            if os.path.isdir(dll_loader_path):
                ui.loaderType.setCheckable(True)
                # ui.defaultType.setChecked(False)
                # ui.loaderType.setChecked(True)
            if os.path.isdir(mod_loader_path):
                ui.modType.setCheckable(True)
                # ui.defaultType.setChecked(False)
                # ui.loaderType.setChecked(True)
            if os.path.isdir(mega_hack_path):
                ui.hackType.setCheckable(True)
                # ui.defaultType.setChecked(False)
                # ui.loaderType.setChecked(True)
            ui.goForwardButton.setEnabled(True)
            base_folder = path
        else:
            ui.goForwardButton.setEnabled(False)

    def select_folder_pressed():
        path = QtWidgets.QFileDialog.getExistingDirectory(
            MainWindow, 'Выбор папки с игрой', os.getcwd()
        )
        ui.folderpathEdit.setText(path)
        check_path()

    ui.folderpathButton.clicked.connect(select_folder_pressed)
    ui.folderpathEdit.textChanged.connect(check_path)


def on_init():
    ui.tabs.tabBar().setEnabled(False)
    bind_events()
    setup_buttons(0)


def on_exit(exit_code: int = 0):
    if not exit_code == 0:
        print('App crashed with code ' + str(exit_code) + '.')
    clear_temp()
    return exit_code


app = QtWidgets.QApplication([__file__])
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
on_init()
sys.exit(on_exit(app.exec_()))
