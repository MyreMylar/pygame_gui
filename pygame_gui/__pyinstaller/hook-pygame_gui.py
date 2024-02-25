# pylint: disable=invalid-name
import os
import pathlib


# Get data folder
pygame_gui_folder = os.path.dirname(pathlib.Path(__file__).parent.absolute())

# datas is the variable that pyinstaller looks for while processing hooks
datas = []


# A helper to append the relative path of a resource to hook variable - datas
def _append_to_datas(file_path):
    res_path = os.path.join(pygame_gui_folder, file_path)
    if os.path.exists(res_path):
        datas.append((res_path, "pygame_gui/data"))


def _append_translations_to_datas(file_path):
    res_path = os.path.join(pygame_gui_folder, file_path)
    if os.path.exists(res_path):
        datas.append((res_path, "pygame_gui/data/translations"))


# Append the theme and all the default fonts
_append_to_datas("data/__init__.py")
_append_to_datas("data/NotoSans-Bold.ttf")
_append_to_datas("data/NotoSans-Regular.ttf")
_append_to_datas("data/NotoSans-BoldItalic.ttf")
_append_to_datas("data/NotoSans-RegularItalic.ttf")
_append_to_datas("data/NotoSansArabic-Bold.otf")
_append_to_datas("data/NotoSansArabic-Regular.otf")
_append_to_datas("data/NotoSansHebrew-Bold.otf")
_append_to_datas("data/NotoSansHebrew-Regular.otf")
_append_to_datas("data/NotoSansJP-Bold.otf")
_append_to_datas("data/NotoSansJP-Regular.otf")
_append_to_datas("data/NotoSansKR-Bold.otf")
_append_to_datas("data/NotoSansKR-Regular.otf")
_append_to_datas("data/NotoSansSC-Bold.otf")
_append_to_datas("data/NotoSansSC-Regular.otf")
_append_to_datas("data/default_theme.json")

# Append all the translation data
_append_translations_to_datas("data/translations/__init__.py")
_append_translations_to_datas("data/translations/pygame-gui.de.json")
_append_translations_to_datas("data/translations/pygame-gui.en.json")
_append_translations_to_datas("data/translations/pygame-gui.es.json")
_append_translations_to_datas("data/translations/pygame-gui.fr.json")
_append_translations_to_datas("data/translations/pygame-gui.id.json")
_append_translations_to_datas("data/translations/pygame-gui.it.json")
_append_translations_to_datas("data/translations/pygame-gui.ja.json")
_append_translations_to_datas("data/translations/pygame-gui.ko.json")
_append_translations_to_datas("data/translations/pygame-gui.pl.json")
_append_translations_to_datas("data/translations/pygame-gui.pt.json")
_append_translations_to_datas("data/translations/pygame-gui.ru.json")
_append_translations_to_datas("data/translations/pygame-gui.uk.json")
_append_translations_to_datas("data/translations/pygame-gui.vi.json")
_append_translations_to_datas("data/translations/pygame-gui.zh.json")
