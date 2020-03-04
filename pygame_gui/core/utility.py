import platform
import subprocess
import time
import contextlib
import os
import sys

from pathlib import Path
from typing import Union

# noinspection SpellCheckingInspection
"""
This code owes a lot to pyperclip by Al Sweigart al@inventwithpython.com.

I would just use the damn library but working in schools frequently requires
minimal dependencies.
"""

plat = platform.system().upper()
if plat == 'WINDOWS':
    import ctypes
    # from ctypes import c_size_t, sizeof, c_wchar_p, c_wchar
    from ctypes.wintypes import HGLOBAL, LPVOID, BOOL, UINT, HANDLE, HWND, DWORD, INT, HMENU, HINSTANCE, LPCSTR


    @contextlib.contextmanager
    def __windows_clipboard(hwnd):
        ctypes.windll.user32.OpenClipboard.argtypes = [HWND]
        ctypes.windll.user32.OpenClipboard.restype = BOOL

        ctypes.windll.user32.CloseClipboard.argtypes = []
        ctypes.windll.user32.CloseClipboard.restype = BOOL

        t = time.time() + 0.5
        success = False
        while time.time() < t:
            success = ctypes.windll.user32.OpenClipboard(hwnd)
            if success:
                break
            time.sleep(0.01)
        if not success:
            raise Exception

        try:
            yield
        finally:
            ctypes.windll.user32.CloseClipboard()


    def __windows_paste():
        ctypes.windll.user32.GetClipboardData.argtypes = [UINT]
        ctypes.windll.user32.GetClipboardData.restype = HANDLE
        with __windows_clipboard(None):
            cf_unicode_text = 13
            handle = ctypes.windll.user32.GetClipboardData(cf_unicode_text)
            if not handle:
                return ""
            return ctypes.c_wchar_p(handle).value


    # noinspection PyUnresolvedReferences
    class CheckedCall(object):

        def __init__(self, f):
            super(CheckedCall, self).__setattr__("f", f)

        def __call__(self, *args):
            return self.f(*args)

        def __setattr__(self, key, value):
            setattr(self.f, key, value)


    def __windows_copy(data: str):
        msvcrt = ctypes.CDLL('msvcrt')

        safe_create_window = CheckedCall(ctypes.windll.user32.CreateWindowExA)
        safe_create_window.argtypes = [DWORD, LPCSTR, LPCSTR, DWORD, INT, INT,
                                       INT, INT, HWND, HMENU, HINSTANCE, LPVOID]
        safe_create_window.restype = HWND

        safe_destroy_window = CheckedCall(ctypes.windll.user32.DestroyWindow)
        safe_destroy_window.argtypes = [HWND]
        safe_destroy_window.restype = BOOL

        safe_empty = ctypes.windll.user32.EmptyClipboard
        safe_empty.argtypes = []
        safe_empty.restype = BOOL

        safe_alloc = CheckedCall(ctypes.windll.kernel32.GlobalAlloc)
        safe_alloc.argtypes = [UINT, ctypes.c_size_t]
        safe_alloc.restype = HGLOBAL

        safe_lock = CheckedCall(ctypes.windll.kernel32.GlobalLock)
        safe_lock.argtypes = [HGLOBAL]
        safe_lock.restype = LPVOID

        safe_unlock = CheckedCall(ctypes.windll.kernel32.GlobalUnlock)
        safe_unlock.argtypes = [HGLOBAL]
        safe_unlock.restype = BOOL

        safe_set_clipboard = CheckedCall(ctypes.windll.user32.SetClipboardData)
        safe_set_clipboard.argtypes = [UINT, HANDLE]
        safe_set_clipboard.restype = HANDLE

        wcslen = msvcrt.wcslen
        wcslen.argtypes = [ctypes.c_wchar_p]
        wcslen.restype = UINT

        gmem_moveable = 0x0002
        # weirdly this temporary window handle seems to work for pasting where the
        # normal pygame window handle does not
        hwnd = safe_create_window(0, b"STATIC", None, 0, 0, 0, 0, 0,
                                  None, None, None, None)

        data = str(data)
        with __windows_clipboard(hwnd):
            safe_empty()

            if data:
                count = wcslen(data) + 1
                handle = safe_alloc(gmem_moveable, count * ctypes.sizeof(ctypes.c_wchar))
                locked_handle = safe_lock(handle)

                ctypes.memmove(ctypes.c_wchar_p(locked_handle),
                               ctypes.c_wchar_p(data),
                               count * ctypes.sizeof(ctypes.c_wchar))

                safe_unlock(handle)
                cf_unicode_text = 13

                safe_set_clipboard(cf_unicode_text, handle)

        safe_destroy_window(hwnd)
elif plat == 'LINUX':

    def __linux_copy(data: str):
        process = subprocess.Popen(['xsel', '-b', '-i'], stdin=subprocess.PIPE, close_fds=True)
        process.communicate(input=data.encode('utf-8'))


    def __linux_paste():
        process = subprocess.Popen(['xsel', '-b', '-o'], stdout=subprocess.PIPE, close_fds=True)
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8')

else:
    def __mac_copy(data: str):
        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(data.encode('utf-8'))


    def __mac_paste():
        return subprocess.check_output(
            'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


def clipboard_copy(data: str):
    current_platform = platform.system().upper()
    if current_platform == 'WINDOWS':
        __windows_copy(data)
    elif current_platform == 'LINUX':
        __linux_copy(data)
    else:
        __mac_copy(data)


def clipboard_paste():
    current_platform = platform.system().upper()
    if current_platform == 'WINDOWS':
        return __windows_paste()
    elif current_platform == 'LINUX':
        return __linux_paste()
    else:
        return __mac_paste()


def create_resource_path(relative_path: Union[str, Path]):
    """
    Get absolute path to resource, works for dev and for PyInstaller's 'onefile' mode
    """

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
