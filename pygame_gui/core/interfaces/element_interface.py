from abc import ABCMeta, abstractmethod
from typing import Tuple, Union, List, Set, Any

import pygame


class IUIElementInterface(metaclass=ABCMeta):
    """
    Interface for the ui element class. This is so we can refer to ui elements in other classes
    before the UIElement has itself been defined.

    """

    @abstractmethod
    def get_relative_rect(self) -> pygame.Rect:
        """
        The relative positioning rect.

        :return: A pygame rect.

        """

    @abstractmethod
    def get_abs_rect(self) -> pygame.Rect:
        """
        The absolute positioning rect.

        :return: A pygame rect.

        """

    @abstractmethod
    def get_element_base_ids(self) -> List[str]:
        """
        A list of all the element base IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """

    @abstractmethod
    def get_element_ids(self) -> List[str]:
        """
        A list of all the element IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """

    @abstractmethod
    def get_class_ids(self) -> List[str]:
        """
        A list of all the class IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """

    @abstractmethod
    def get_object_ids(self) -> List[str]:
        """
        A list of all the object IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """

    @abstractmethod
    def update_containing_rect_position(self):
        """
        Updates the position of this element based on the position of it's container. Usually
        called when the container has moved.
        """

    @abstractmethod
    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """

    @abstractmethod
    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """

    @abstractmethod
    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]],
                       clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.

        NOTE: Using this on elements inside containers with non-default anchoring arrangements
        may make a mess of them.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """

    @abstractmethod
    def update(self, time_delta: float):
        """
        Updates this element's drawable shape, if it has one.

        :param time_delta: The time passed between frames, measured in seconds.

        """

    @abstractmethod
    def change_layer(self, new_layer: int):
        """
        Changes the layer this element is on.

        :param new_layer: The layer to change this element to.

        """

    @abstractmethod
    def kill(self):
        """
        Overriding regular sprite kill() method to remove the element from it's container.
        """

    @abstractmethod
    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered
        by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function
                           and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a
                                       'higher' element.

        :return bool: A boolean that is true if we have hovered a UI element, either just now or
                      before this method.
        """

    @abstractmethod
    def on_fresh_drawable_shape_ready(self):
        """
        Called when our drawable shape has finished rebuilding the active surface. This is needed
        because sometimes we defer rebuilding until a more advantageous (read quieter) moment.
        """

    @abstractmethod
    def on_hovered(self):
        """
        A stub to override. Called when this UI element first enters the 'hovered' state.
        """

    @abstractmethod
    def on_unhovered(self):
        """
        A stub to override. Called when this UI element leaves the 'hovered' state.
        """

    @abstractmethod
    def while_hovering(self, time_delta: float, mouse_pos: pygame.math.Vector2):
        """
        A stub method to override. Called when this UI element is currently hovered.

        :param time_delta: A float, the time in seconds between the last call to this function
                           and now (roughly).
        :param mouse_pos: The current position of the mouse as 2D Vector.

        """

    @abstractmethod
    def can_hover(self) -> bool:
        """
        A stub method to override. Called to test if this method can be hovered.
        """

    @abstractmethod
    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a
        straightforward matter of seeing if a point is inside the rectangle. Occasionally it
        will also check if we are in a wider zone around a UI element once it is already active,
        this makes it easier to move scroll bars and the like.

        :param hover_x: The x (horizontal) position of the point.
        :param hover_y: The y (vertical) position of the point.

        :return: Returns True if we are hovering this element.

        """

    @abstractmethod
    def process_event(self, event: pygame.event.Event) -> bool:
        """
        A stub to override. Gives UI Elements access to pygame events.

        :param event: The event to process.

        :return: Should return True if this element makes use of this event.

        """

    @abstractmethod
    def focus(self):
        """
        A stub to override. Called when we focus this UI element.
        """

    @abstractmethod
    def unfocus(self):
        """
        A stub to override. Called when we stop focusing this UI element.
        """

    @abstractmethod
    def rebuild_from_changed_theme_data(self):
        """
        A stub to override. Used to test if the theming data for this element has changed and
        rebuild the element if so.

        """

    @abstractmethod
    def rebuild(self):
        """
        Takes care of rebuilding this element. Most derived elements are going to override this,
        and hopefully call the super() class method.

        """

    @abstractmethod
    def set_visual_debug_mode(self, activate_mode: bool):
        """
        Enables a debug mode for the element which displays layer information on top of it in
        a tiny font.

        :param activate_mode: True or False to enable or disable the mode.

        """

    @abstractmethod
    def _set_image_clip(self, rect: Union[pygame.Rect, None]):
        """
        Sets a clipping rectangle on this element's image determining what portion of it will
        actually be displayed when this element is blitted to the screen.

        :param rect: A clipping rectangle, or None to clear the clip.

        """

    @abstractmethod
    def get_image_clipping_rect(self) -> Union[pygame.Rect, None]:
        """
        Obtain the current image clipping rect.

        :return: The current clipping rect. May be None.

        """

    @abstractmethod
    def set_image(self, new_image: Union[pygame.surface.Surface, None]):
        """
        Deprecated for most elements - to avoid confusion with setting the image for the UIImage element.

        Generally the average user shouldn't be directly setting what this was setting.

        :param new_image: The new image to set.

        """

    @abstractmethod
    def _set_image(self, new_image: Union[pygame.surface.Surface, None]):
        """
        Wraps setting the image variable of this element so that we also set the current image
        clip on the image at the same time.

        :param new_image: The new image to set.

        """

    @abstractmethod
    def get_top_layer(self) -> int:
        """
        Assuming we have correctly calculated the 'thickness' of it, this method will
        return the top of this element.

        :return int: An integer representing the current highest layer being used by this element.

        """

    @abstractmethod
    def get_starting_height(self) -> int:
        """
        Get the starting layer height of this element. (i.e. the layer we start placing it on
        *above* it's container, it may use more layers above this layer)

        :return: an integer representing the starting layer height.

        """

    @abstractmethod
    def get_focus_set(self) -> Set[Any]:
        """
        Return the set of elements to focus when we focus this element.
        """

    @abstractmethod
    def set_focus_set(self, focus_set: Set[Any]):
        """
        Set the focus set to a specific set of elements.

        :param focus_set: The focus set to set.
        """

    @abstractmethod
    def join_focus_sets(self, element):
        """
        Join this element's focus set with another's.

        :param element: The other element whose focus set we are joining with.
        """

    @abstractmethod
    def remove_element_from_focus_set(self, element):
        """
        remove an element from this sets focus group.

        :param element: The element to remove.
        """

    @abstractmethod
    def disable(self):
        """
        Disables elements so they are no longer interactive.

        Elements should handle their own enabling and disabling.
        """

    @abstractmethod
    def enable(self):
        """
        Enables elements so they are interactive again.

        Elements should handle their own enabling and disabling.
        """

    @abstractmethod
    def show(self):
        """
        Shows the widget, which means the widget will get drawn and will process events.
        """

    @abstractmethod
    def hide(self):
        """
        Hides the widget, which means the widget will not get drawn and will not process events.
        Clear hovered state.
        """

    @abstractmethod
    def on_locale_changed(self):
        """
        Called for each element when the locale is changed on their UIManager

        """

    @abstractmethod
    def get_anchor_targets(self) -> list:
        """
        Get any anchor targets this element has so we can update them when their targets change
        :return: the list of anchor targets.
        """
