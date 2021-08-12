import os
import sys
import json
from requests import get
from PyQt5 import QtWidgets
from installer import Ui_MainWindow


base_url = 'https://pixelsuft.github.io/gdl-installer-files/'
base_folder = ''


def log(text_to_log):
    for i in text_to_log.split('\n'):
        ui.logEdit.addItem(i)


def progress(percent):
    ui.barEdit.setValue(percent)


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


def install_gdl(install_type):
    backup = {}
    log(f'Базовый url: {base_url}')
    log(f'Базовая папка: {base_folder}')
    progress(1)
    log(f'Скачиваем файл локализации...')
    fast_write(os.path.join(base_folder, 'ru_ru.json'), get(get_url('gdl_res/ru_ru.json')).content)
    progress(5)
    if install_type == 'default':
        log(f'Делаем бэкап файла расширений...')
        ext_path = os.path.join(base_folder, 'libExtensions.dll')
        os.rename(ext_path, ext_path + '.backup')
        backup[ext_path] = ext_path + '.backup'
        log(f'Скачиваем модиффицированный файл расширений...')
        fast_write(ext_path, get(get_url('gdl_res/libExtensions.dll')).content)
    log('Скачиваем dll...')
    dll_path = os.path.join(
        base_folder, 'adaf-dll' if install_type == 'default' else install_type, 'GDLocalisation.dll'
    )
    fast_write(dll_path, get(get_url('gdl_res/GDLocalisation.dll')).content)
    progress(10)
    log('Скачиваем дезинсталлятор...')
    uninstall_path = os.path.join(
        base_folder, 'gdl_unins000.exe'
    )
    fast_write(uninstall_path, get(get_url('gdl_res/gdl_unins000.exe')).content)
    progress(15)
    log('Получаем список файлов...')
    files_list = get(get_url('gdl_res/res_files.txt')).content.decode().split('\n')
    progress(25)
    one_progress = 70 / len(files_list)
    for i in range(len(files_list)):
        log(f'Сохраняем файл {files_list[i]}...')
        file_url = get_url('gd_res/' + files_list[i])
        file_path = os.path.join(base_folder, 'Resources', files_list[i])
        if not file_exists(file_path):
            continue
        file_content = get(file_url).content
        os.rename(file_path, file_path + '.backup')
        backup[file_path] = file_path + '.backup'
        fast_write(file_path, file_content)
        progress(25 + int(one_progress * i))
    log('Сохраняем файлы бэкапа в файл...')
    fast_write(os.path.join(base_folder, 'gdl_unins000.txt'), json.dumps(backup))
    progress(100)
    setup_buttons(4)


def file_exists(file_path):
    return os.access(file_path, os.F_OK)


def setup_buttons(tab_id):
    if tab_id == 0:
        ui.tabs.setCurrentIndex(0)
        ui.gobackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(True)

        ui.goForwardButton.clicked.connect(lambda: setup_buttons(1))
    elif tab_id == 1:
        ui.tabs.setCurrentIndex(1)
        ui.folderpathEdit.setText('')
        ui.gobackButton.setEnabled(True)
        ui.goForwardButton.setEnabled(False)
        ui.goForwardButton.setText('Далее')

        ui.gobackButton.clicked.connect(lambda: setup_buttons(0))
        ui.goForwardButton.clicked.connect(lambda: setup_buttons(2))
    elif tab_id == 2:
        ui.tabs.setCurrentIndex(2)
        ui.gobackButton.setEnabled(True)
        ui.goForwardButton.setEnabled(True)
        ui.goForwardButton.setText('Установить')

        ui.gobackButton.clicked.connect(lambda: setup_buttons(1))
        ui.goForwardButton.clicked.connect(lambda: setup_buttons(3))
    elif tab_id == 3:
        ui.tabs.setCurrentIndex(3)
        ui.gobackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(False)
        ui.cancelButton.setEnabled(False)
        install_type = 'default'
        if ui.loaderType.isChecked():
            install_type = 'adaf-dll'
        elif ui.modType.isChecked():
            install_type = 'mods'
        elif ui.hackType.isChecked():
            install_type = 'extensions'
        install_gdl(install_type)
    elif tab_id == 4:
        ui.tabs.setCurrentIndex(4)
        ui.gobackButton.setEnabled(False)
        ui.goForwardButton.setEnabled(True)
        ui.goForwardButton.setText('Готово')
        ui.goForwardButton.clicked.connect(lambda: sys.exit(on_exit(0)))


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
                ui.defaultType.setChecked(False)
                ui.loaderType.setChecked(True)
            if os.path.isdir(mod_loader_path):
                ui.modType.setCheckable(True)
                ui.defaultType.setChecked(False)
                ui.loaderType.setChecked(True)
            if os.path.isdir(mega_hack_path):
                ui.hackType.setCheckable(True)
                ui.defaultType.setChecked(False)
                ui.loaderType.setChecked(True)
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
    return exit_code


app = QtWidgets.QApplication([__file__])
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
on_init()
sys.exit(on_exit(app.exec_()))
