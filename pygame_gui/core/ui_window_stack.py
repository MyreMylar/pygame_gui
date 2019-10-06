from typing import Union

from . import ui_window


class UIWindowStack:
    """
    A class for managing a stack of GUI windows so that only one is 'in front' at a time and the rest are sorted based
    on the last time they were interacted with/created.
    """
    def __init__(self, window_resolution):
        self.window_resolution = window_resolution
        self.stack = []

    def clear(self):
        """
        Empties the whole stack removing and killing all windows.
        """
        while len(self.stack) != 0:
            self.stack.pop().kill()
        self.stack.clear()

    def add_new_window(self, window: ui_window.UIWindow):
        """
        Adds a window to the top of the stack.

        :param window: The window to add.
        """
        if len(self.stack) > 0:
            new_layer = self.stack[-1].get_top_layer() + 1
        else:
            new_layer = 0
        window.change_window_layer(new_layer)
        self.stack.append(window)

    def remove_window(self, window_to_remove: ui_window.UIWindow):
        """
        Removes a window from the stack and resorts the remaining windows to adjust for it's absence.

        :param window_to_remove: the window to remove.
        """
        if window_to_remove in self.stack:
            popped_windows_to_readd = []
            window = self.stack.pop()
            while window != window_to_remove:
                popped_windows_to_readd.append(window)
                window = self.stack.pop()

            popped_windows_to_readd.reverse()
            for old_window in popped_windows_to_readd:
                self.add_new_window(old_window)

    def move_window_to_front(self, window_to_front: ui_window.UIWindow):
        """
        Moves the passed in window to the top of the window stack and resorts the other windows to deal with the
        change.

        :param window_to_front: the window to move to the front.
        """
        if window_to_front in self.stack:
            popped_windows_to_readd = []
            window = self.stack.pop()
            while window != window_to_front:
                popped_windows_to_readd.append(window)
                window = self.stack.pop()

            popped_windows_to_readd.reverse()
            for old_window in popped_windows_to_readd:
                self.add_new_window(old_window)

            self.add_new_window(window_to_front)

    def get_root_window(self) -> Union[ui_window.UIWindow, None]:
        """
        Gets the 'root' window, which should always be the first one in the stack and should represent an imaginary
        window the size of the whole pygame application's display surface.

        :return Union[ui_window.UIWindow, None]:  The 'root' window
        """
        if len(self.stack) > 0:
            return self.stack[0]
        else:
            return None

    def is_window_at_top(self, window: ui_window.UIWindow) -> bool:
        """
        Checks if a window is at the top of the window stack or not.

        :param window: The window to check.
        :return bool: returns True if this window is at the top of the stack.
        """
        if window is self.stack[-1]:
            return True
        else:
            return False
