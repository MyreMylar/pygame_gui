import pytest
import importlib

from pygame_gui.__pyinstaller import get_hook_dirs
importlib.import_module("pygame_gui.__pyinstaller.hook-pygame_gui")


class TestPyInstallerHook:
    """
    Testing the PyInstaller Hook
    """

    def test_get_hooks_dir(self):
        assert get_hook_dirs()[0].split("\\")[-1] == "__pyinstaller"
