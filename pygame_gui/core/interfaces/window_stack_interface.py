from abc import ABCMeta, abstractmethod
from typing import List

from pygame_gui.core.interfaces.window_interface import IWindowInterface


class IUIWindowStackInterface(metaclass=ABCMeta):
    """
    A class for managing a stack of GUI windows so that only one is 'in front' at a time and the
    rest are sorted based on the last time they were interacted with/created.

    """

    @abstractmethod
    def clear(self):
        """
        Empties the whole stack removing and killing all windows.
        """

    @abstractmethod
    def add_new_window(self, window: IWindowInterface):
        """
        Adds a window to the top of the stack.

        :param window: The window to add.

        """

    @abstractmethod
    def remove_window(self, window_to_remove: IWindowInterface):
        """
        Removes a window from the stack and resorts the remaining windows to adjust for
        it's absence.

        :param window_to_remove: the window to remove.

        """

    @abstractmethod
    def move_window_to_front(self, window_to_front: IWindowInterface):
        """
        Moves the passed in window to the top of the window stack and resorts the other windows
        to deal with the change.

        :param window_to_front: the window to move to the front.

        """

    @abstractmethod
    def is_window_at_top(self, window: IWindowInterface) -> bool:
        """
        Checks if a window is at the top of the window stack or not.

        :param window: The window to check.

        :return: returns True if this window is at the top of the stack.

        """

    def is_window_at_top_of_top(self, window: IWindowInterface) -> bool:
        """
        Checks if a window is at the top of the top window stack or not.

        :param window: The window to check.

        :return: returns True if this window is at the top of the stack.

        """

    @abstractmethod
    def get_full_stack(self) -> List[IWindowInterface]:
        """
        Returns the full stack of normal and always on top windows.

        :return: a list of Windows
        """
