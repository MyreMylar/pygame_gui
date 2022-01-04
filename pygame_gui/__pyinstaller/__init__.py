import os


def get_hook_dirs():
    """
    Used by PyInstaller.

    :return: the hook directories
    """
    return [os.path.dirname(__file__)]
