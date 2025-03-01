from abc import ABCMeta, abstractmethod

from pygame_gui.core.gui_type_hints import Coordinate


class IUITooltipInterface(metaclass=ABCMeta):
    """
    A metaclass that defines the interface that a UI Tool tip uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """

    @abstractmethod
    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """

    @abstractmethod
    def kill(self):
        """
        Overrides the UIElement's default kill method to also kill the text block element that
        helps make up the complete tool tip.
        """

    @abstractmethod
    def find_valid_position(self, position: Coordinate) -> bool:
        """
        Finds a valid position for the tool tip inside the root container of the UI.

        The algorithm starts from the position of the target we are providing a tool tip for then it
        tries to fit the rectangle for the tool tip onto the screen by moving it above, below, to
        the left and to the right, until we find a position that fits the whole tooltip rectangle
        on the screen at once.

        If we fail to manage this then the method will return False. Otherwise, it returns True and
        set the position of the tool tip to our valid position.

        :param position: A 2D vector representing the position of the target this tool tip is for.

        :return: returns True if we find a valid (visible) position and False if we do not.

        """

    @abstractmethod
    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for
        this element when the theme data has changed.
        """

    @abstractmethod
    def set_position(self, position: Coordinate):
        """
        Sets the absolute screen position of this tool tip, updating its subordinate text box at
        the same time.

        :param position: The absolute screen position to set.

        """

    @abstractmethod
    def set_relative_position(self, position: Coordinate):
        """
        Sets the relative screen position of this tool tip, updating its subordinate text box at
        the same time.

        :param position: The relative screen position to set.

        """

    @abstractmethod
    def set_dimensions(self, dimensions: Coordinate):
        """
        Directly sets the dimensions of this tool tip. This will overwrite the normal theming.

        :param dimensions: The new dimensions to set

        """
