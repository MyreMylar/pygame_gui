import typing
from abc import ABCMeta, abstractmethod
from typing import Tuple, Union

import pygame

from pygame_gui.core.interfaces.element_interface import IUIElementInterface
from pygame_gui.core.gui_type_hints import Coordinate


class IUIContainerInterface(IUIElementInterface, metaclass=ABCMeta):
    """
    Interface for the actual container class. Not to be confused with the IContainerLikeInterface
    which is an interface for all the things we can treat like containers when creating elements.

    """

    @abstractmethod
    def get_rect(self) -> pygame.Rect:
        """
        Access to the container's rect

        :return: a pygame rectangle
        """

    @abstractmethod
    def add_element(self, element: IUIElementInterface):
        """
        Add a UIElement to the container. The element's relative_rect parameter will be relative to
        this container.

        :param element: A UIElement to add to this container.

        """

    @abstractmethod
    def remove_element(self, element: IUIElementInterface):
        """
        Remove a UIElement from this container.

        :param element: A UIElement to remove from this container.

        """

    @abstractmethod
    def recalculate_container_layer_thickness(self):
        """
        This function will iterate through the elements in our container and determine the
        maximum 'height' that they reach in the 'layer stack'. We then use that to determine the
        overall 'thickness' of this container. The thickness value is used to determine where to
        place overlapping windows in the layers
        """

    @abstractmethod
    def change_layer(self, new_layer: int):
        """
        Change the layer of this container. Layers are used by the GUI to control the order in
        which things are drawn and which things should currently be interactive (so you can't
        interact with things behind other things).

        This particular method is most often used to shift the visible contents of a window in
        front of any others when it is moved to the front of the window stack.

        :param new_layer: The layer to move our container to.

        """

    @abstractmethod
    def update_containing_rect_position(self):
        """
        This function is called when we move the container to update all the contained UI Elements
        to move as well.
        """

    @abstractmethod
    def set_position(self, position: Coordinate):
        """
        Set the absolute position of this container - it is usually less chaotic to deal with
        setting relative positions.

        :param position: the new absolute position to set.

        """

    @abstractmethod
    def set_relative_position(self, position: Coordinate):
        """
        Set the position of this container, relative to the container it is within.

        :param position: the new relative position to set.

        """

    @abstractmethod
    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Set the dimension of this container and update the positions of elements within it
        accordingly.

        :param clamp_to_container:
        :param dimensions: the new dimensions.

        """

    @abstractmethod
    def get_top_layer(self) -> int:
        """
        Assuming we have correctly calculated the 'thickness' of this container, this method will
        return the 'highest' layer in the LayeredDirty UI Group.

        :return: An integer representing the current highest layer being used by this container.
        """

    @abstractmethod
    def get_thickness(self) -> int:
        """
        Get the container's layer thickness.

        :return: the thickness as an integer.
        """

    @abstractmethod
    def get_size(self) -> Tuple[int, int] | Tuple[float, float]:
        """
        Get the container's pixel size.

        :return: the pixel size as tuple [x, y]
        """

    @abstractmethod
    def kill(self):
        """
        Overrides the standard kill method of UI Elements (and pygame sprites beyond that) to also
        call the kill method on all contained UI Elements.
        """

    @abstractmethod
    def clear(self):
        """
        Removes and kills all the UI elements inside this container.
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

        :return: A boolean that is true if we have hovered a UI element, either just now or
                 before this method.

        """

    @abstractmethod
    def get_image_clipping_rect(self) -> Union[pygame.Rect, None]:
        """
        Obtain the current image clipping rect.

        :return: The current clipping rect. It may be None.

        """

    def on_contained_elements_changed(self, target: IUIElementInterface) -> None:
        """
        Update the contents of this container that one of their layout anchors may have moved, or
        been resized.

        :param target: the UI element that has been benn moved or resized.
        """

    def calc_add_element_changes_thickness(self, element: IUIElementInterface):
        """
        This function checks if a single added element will increase the containers thickness
        and if so updates containers recursively.

        :param element: the element to check.
        """

    @abstractmethod
    def __iter__(self) -> typing.Iterator[IUIElementInterface]:
        """
        Iterates over the elements within the container-like interface.
        This method allows iterating over the children elements within the container.
        """

    @abstractmethod
    def __contains__(self, item: IUIElementInterface) -> bool:
        """
        Checks if the given element is contained within the container.
        :return bool: Return True if the element is found, False otherwise.
        """


class IContainerLikeInterface(metaclass=ABCMeta):
    """
    A metaclass that defines the interface for containers used by elements.

    This interface lets us treat classes like UIWindows and UIPanels like containers for
    elements even though they actually pass this functionality off to the proper UIContainer
    class.
    """

    @abstractmethod
    def get_container(self) -> "IContainerAndContainerLike":
        """
        Gets an actual container from this container-like UI element.
        """

    @abstractmethod
    def show(self):
        """
        Shows the container, which means the container will get drawn and will process events.
        Should also show all the children elements.
        If the container was visible before - ignore.
        """

    @abstractmethod
    def hide(self):
        """
        Hides the container, which means the container will not get drawn and will not
        process events. Should also hide all the children elements.
        If the container was hidden before - ignore.
        """

    @abstractmethod
    def __iter__(self) -> typing.Iterator[IUIElementInterface]:
        """
        Iterates over the elements within the container-like interface.
        This method allows iterating over the children elements within the container.
        """

    @abstractmethod
    def __contains__(self, item: IUIElementInterface) -> bool:
        """
        Checks if the given element is contained within the container.
        :return bool: Return True if the element is found, False otherwise.
        """

    @abstractmethod
    def are_contents_hovered(self) -> bool:
        """
        Are any of the elements in the container hovered? Used for handling mousewheel events.

        :return: True if one of the elements is hovered, False otherwise.
        """


class IContainerAndContainerLike(
    IUIContainerInterface, IContainerLikeInterface, metaclass=ABCMeta
):
    """
    Combination of IUIContainerInterface and IContainerLikeInterface mostly for type checking
    """
