from pygame_gui.core.interfaces import IWindowInterface


class UIWindowStack:
    """
    A class for managing a stack of GUI windows so that only one is 'in front' at a time and the rest are sorted based
    on the last time they were interacted with/created.
    """
    def __init__(self, window_resolution, root_container):
        self.window_resolution = window_resolution
        self.stack = []
        self.root_container = root_container

    def clear(self):
        """
        Empties the whole stack removing and killing all windows.
        """
        while len(self.stack) != 0:
            self.stack.pop().kill()
        self.stack.clear()

    def add_new_window(self, window: IWindowInterface):
        """
        Adds a window to the top of the stack.

        :param window: The window to add.
        """
        new_layer = self.stack[-1].get_top_layer() if len(self.stack) > 0 else self.root_container.get_top_layer()
        window.change_layer(new_layer)
        self.stack.append(window)

    def remove_window(self, window_to_remove: IWindowInterface):
        """
        Removes a window from the stack and resorts the remaining windows to adjust for it's absence.

        :param window_to_remove: the window to remove.
        """
        if window_to_remove in self.stack:
            popped_windows_to_add_back = []
            window = self.stack.pop()
            while window != window_to_remove:
                popped_windows_to_add_back.append(window)
                window = self.stack.pop()

            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

    def move_window_to_front(self, window_to_front: IWindowInterface):
        """
        Moves the passed in window to the top of the window stack and resorts the other windows to deal with the
        change.

        :param window_to_front: the window to move to the front.
        """
        if window_to_front not in self.stack or window_to_front == self.stack[-1]:
            return
        popped_windows_to_add_back = []
        window = self.stack.pop()
        while window != window_to_front:
            popped_windows_to_add_back.append(window)
            window = self.stack.pop()

        popped_windows_to_add_back.reverse()
        for old_window in popped_windows_to_add_back:
            self.add_new_window(old_window)

        self.add_new_window(window_to_front)

    # def get_root_window(self) -> Union[ui_window.UIWindow, None]:
    #     """
    #     Gets the 'root' window, which should always be the first one in the stack and should represent an imaginary
    #     window the size of the whole pygame application's display surface.
    #
    #     :return Union[ui_window.UIWindow, None]:  The 'root' window
    #     """
    #     if len(self.stack) > 0:
    #         return self.stack[0]
    #     else:
    #         return None

    def is_window_at_top(self, window: IWindowInterface) -> bool:
        """
        Checks if a window is at the top of the window stack or not.

        :param window: The window to check.
        :return bool: returns True if this window is at the top of the stack.
        """
        return window is self.stack[-1]
