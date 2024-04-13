from typing import Tuple, List

from pygame_gui.core.interfaces import IWindowInterface, IUIContainerInterface
from pygame_gui.core.interfaces.window_stack_interface import IUIWindowStackInterface


class UIWindowStack(IUIWindowStackInterface):
    """
    A class for managing a stack of GUI windows so that only one is 'in front' at a time and the
    rest are sorted based on the last time they were interacted with/created.

    :param window_resolution: The resolution of the OS window.
    :param root_container: The root container for the whole UI.

    """
    def __init__(self, window_resolution: Tuple[int, int], root_container: IUIContainerInterface):
        self.window_resolution = window_resolution
        self.stack: List[IWindowInterface] = []  # the main stack
        # a second stack that sits above the first,
        # contains 'always_on_top' windows
        self.top_stack: List[IWindowInterface] = []
        self.root_container = root_container

    def clear(self):
        """
        Empties the whole stack removing and killing all windows.
        """
        while len(self.stack) != 0:
            self.stack.pop().kill()
        self.stack.clear()

        while len(self.top_stack) != 0:
            self.top_stack.pop().kill()
        self.top_stack.clear()

    def add_new_window(self, window: IWindowInterface):
        """
        Adds a new window to the top of the stack.

        :param window: The window to add.

        """
        if window.always_on_top:
            new_layer = (self.top_stack[-1].get_top_layer() + 1
                         if len(self.top_stack) > 0
                         else (self.stack[-1].get_top_layer() + 1
                         if len(self.stack) > 0
                         else self.root_container.get_top_layer() + 1))

            window.change_layer(new_layer)
            self.top_stack.append(window)
            window.on_moved_to_front()
        else:
            new_layer = (self.stack[-1].get_top_layer() + 1
                         if len(self.stack) > 0
                         else self.root_container.get_top_layer() + 1)

            window.change_layer(new_layer)
            self.stack.append(window)
            window.on_moved_to_front()

            increased_height = window.get_layer_thickness()

            # need to bump up the layers of everything in the top stack as the main stack just got bigger
            for window in self.top_stack:
                window.change_layer(window.layer + increased_height)

    def refresh_window_stack_from_window(self, window_to_refresh_from: IWindowInterface):
        if window_to_refresh_from in self.stack:
            popped_windows_to_add_back = []

            # first clear out the top stack
            try:
                top_window = self.top_stack.pop()
                while top_window is not None:
                    popped_windows_to_add_back.append(top_window)
                    try:
                        top_window = self.top_stack.pop()
                    except IndexError:
                        top_window = None
            except IndexError:
                pass

            # then clear out everything above our target
            window = self.stack.pop()
            while window != window_to_refresh_from:
                popped_windows_to_add_back.append(window)
                window = self.stack.pop()

            # add back our target as well
            popped_windows_to_add_back.append(window_to_refresh_from)

            # reverse the list and re-add them
            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

        elif window_to_refresh_from in self.top_stack:
            popped_windows_to_add_back = []
            window = self.top_stack.pop()
            while window != window_to_refresh_from:
                popped_windows_to_add_back.append(window)
                window = self.top_stack.pop()
            popped_windows_to_add_back.append(window_to_refresh_from)

            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

    def remove_window(self, window_to_remove: IWindowInterface):
        """
        Removes a window from the stack and resorts the remaining windows to adjust for
        its absence.

        :param window_to_remove: the window to remove.

        """
        if window_to_remove in self.stack:
            popped_windows_to_add_back = []
            window = self.stack.pop()
            while window != window_to_remove:
                popped_windows_to_add_back.append(window)
                window = self.stack.pop()

            try:
                top_window = self.top_stack.pop()
                while top_window is not None:
                    popped_windows_to_add_back.append(top_window)
                    try:
                        top_window = self.top_stack.pop()
                    except IndexError:
                        top_window = None
            except IndexError:
                pass

            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

        elif window_to_remove in self.top_stack:
            popped_windows_to_add_back = []
            window = self.top_stack.pop()
            while window != window_to_remove:
                popped_windows_to_add_back.append(window)
                window = self.top_stack.pop()

            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

    def move_window_to_front(self, window_to_front: IWindowInterface):
        """
        Moves the passed in window to the top of its stack and resorts the other windows
        to deal with the change.

        :param window_to_front: the window to move to the front.

        """
        if window_to_front in self.top_stack:
            if window_to_front == self.top_stack[-1]:
                return  # already at top of top stack
            popped_windows_to_add_back = []
            window = self.top_stack.pop()
            while window != window_to_front:
                popped_windows_to_add_back.append(window)
                window = self.top_stack.pop()

            popped_windows_to_add_back.reverse()
            for old_window in popped_windows_to_add_back:
                self.add_new_window(old_window)

            self.add_new_window(window_to_front)
            window_to_front.on_moved_to_front()

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
        window_to_front.on_moved_to_front()

    def is_window_at_top(self, window: IWindowInterface) -> bool:
        """
        Checks if a window is at the top of the normal window stack or not.

        :param window: The window to check.

        :return: returns True if this window is at the top of the stack.

        """
        return window is self.stack[-1]

    def is_window_at_top_of_top(self, window: IWindowInterface) -> bool:
        """
        Checks if a window is at the top of the top window stack or not.

        :param window: The window to check.

        :return: returns True if this window is at the top of the stack.

        """
        return window is self.top_stack[-1]

    def get_full_stack(self) -> List[IWindowInterface]:
        """
        Returns the full stack of normal and always on top windows.

        :return: a list of Windows
        """
        return self.stack + self.top_stack
