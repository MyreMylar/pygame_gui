from abc import ABCMeta
from typing import Tuple, Union

import pygame


class IWindowInterface:
    """
    A meta class that defines the interface that the window stack uses to interface with the
    UIWindow class.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual window class later on and have it make use of the window stack.
    """
    __metaclass__ = ABCMeta

    def set_blocking(self, state: bool):
        """
        Sets whether this window being open should block clicks to the rest of the UI or not.
        Defaults to False.

        :param state: True if this window should block mouse clicks.

        """

    def set_minimum_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                                       Tuple[int, int],
                                                       Tuple[float, float]]):
        """
        If this window is resizable, then the dimensions we set here will be the minimum that
        users can change the window to. They are also used as the minimum size when
        'set_dimensions' is called.

        :param dimensions: The new minimum dimension for the window.

        """

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Set the size of this window and then re-sizes and shifts the contents of the windows
        container to fit the new size.

        :param dimensions: The new dimensions to set.

        """

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles resizing & closing windows. Gives UI Windows access to pygame events. Derived
        windows should super() call this class if they implement their own process_event method.

        :param event: The event to process.

        :return bool: Return True if this element should consume this event and not pass it to the
                      rest of the UI.

        """

    def check_clicked_inside_or_blocking(self, event: pygame.event.Event) -> bool:
        """
        A quick event check outside of the normal event processing so that this window is brought
        to the front of the window stack if we click on any of the elements contained within it.

        :param event: The event to check.

        :return: returns True if the event represents a click inside this window or the window
                 is blocking.

        """

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by
        derived classes but also has a little functionality to make sure the window's layer
        'thickness' is accurate and to handle window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """

    def can_hover(self) -> bool:
        """
        Called to test if this window can be hovered.
        """

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        For the window the only hovering we care about is the edges if this is a resizable window.

        :param time_delta: time passed in seconds between one call to this method and the next.
        :param hovered_higher_element: Have we already hovered an element/window above this one.

        """

    def get_top_layer(self) -> int:
        """
        Returns the 'highest' layer used by this window so that we can correctly place other
        windows on top of it.

        :return: The top layer for this window as a number (greater numbers are higher layers).

        """

    def change_layer(self, layer: int):
        """
        Change the drawing layer of this window.

        :param layer: the new layer to move to.
        """

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this window, and remove if from the window stack.
        """

    def rebuild(self):
        """
        Rebuilds the window when the theme has changed.

        """

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """

    def should_use_window_edge_resize_cursor(self) -> bool:
        """
        Returns true if this window is in a state where we should display one of the resizing
        cursors

        :return: True if a resizing cursor is needed.
        """

    def get_hovering_edge_id(self) -> str:
        """
        Gets the ID of the combination of edges we are hovering for use by the cursor system.

        :return: a string containing the edge combination ID (e.g. xy,yx,xl,xr,yt,yb)

        """

    def on_moved_to_front(self):
        """
        Called when a window is moved to the front of the stack.
        """

    def set_display_title(self, new_title: str):
        """
        Set the title of the window.

        :param new_title: The title to set.
        """