from typing import List, Union, Tuple, Dict

import pygame

from pygame_gui.core.interfaces import IContainerInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement


class UIContainer(UIElement, IContainerInterface):
    """
    A UI Container holds any number of other UI elements inside of a rectangle. When we move the UIContainer
    all the UI elements contained within it can be moved as well.

    This class helps us make UI Windows, but likely will have wider uses as well as the GUI system develops.

    :param relative_rect: A pygame.Rect whose position is relative to whatever UIContainer it is inside of, if any.
    :param manager: The UIManager that manages this UIElement.
    :param container: The UIContainer that this UIElement is contained within.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 *,
                 starting_height: int = 1,
                 is_window_root_container: bool = False,
                 container: Union[IContainerInterface, None] = None,
                 parent_element: Union[UIElement, None] = None,
                 object_id: Union[str, None] = None,
                 anchors: Union[Dict[str, str], None] = None):

        self.ui_manager = manager
        self.is_window_root_container = is_window_root_container
        self.elements = []  # type: List[UIElement]

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='container')

        super().__init__(relative_rect, manager, container,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors)

        self.sprite_group = self.ui_manager.get_sprite_group()
        self.set_image(self.ui_manager.get_universal_empty_surface())

        self.layer_thickness = 0  # default to 0 thickness for an empty container

        self.hovered = False

    def get_container(self):
        return self

    def add_element(self, element: UIElement):
        """
        Add a UIElement to the container. The UI's relative_rect parameter will be relative to this container.

        :param element: A UIElement to add to this container.
        """
        element.change_layer(self._layer + element.starting_height)
        self.elements.append(element)
        self.recalculate_container_layer_thickness()

    def remove_element(self, element: UIElement):
        """
        Remove a UIElement from this container.

        :param element: A UIElement to remove from this container.
        """
        if element in self.elements:
            self.elements.remove(element)
        self.recalculate_container_layer_thickness()

    def recalculate_container_layer_thickness(self):
        """
        This function will iterate through the elements in our container and determine the maximum 'height'
        that they reach in the 'layer stack'. We then use that to determine the overall 'thickness' of this container.
        The thickness value is used to determine where to place overlapping windows in the layers
        """
        max_element_top_layer = self._layer
        for element in self.elements:
            if ((element not in self.ui_manager.ui_window_stack.stack) and
                not (isinstance(element, UIContainer) and element.is_window_root_container) and
                    element.get_top_layer() > max_element_top_layer):
                max_element_top_layer = element.get_top_layer()

        new_thickness = max_element_top_layer - self._layer
        if new_thickness != self.layer_thickness:
            self.layer_thickness = new_thickness
            if self.ui_container is not None and self.ui_container != self:
                self.ui_container.recalculate_container_layer_thickness()

    def change_layer(self, new_layer: int):
        """
        Change the layer of this container. Layers are used by the GUI to control the order in which things are drawn
        and which things should currently be interactive (so you can't interact with things behind other things).

        This particular method is most often used to shift the visible contents of a window in front of any others when
        it is moved to the front of the window stack.

        :param new_layer: The layer to move our container to.
        """
        if new_layer != self._layer:
            super().change_layer(new_layer)

            for element in self.elements:
                element.change_layer(self._layer + element.starting_height)

    def update_containing_rect_position(self):
        """
        This function is called when we move the container to update all the contained UI Elements to move as well.
        """
        super().update_containing_rect_position()

        for element in self.elements:
            element.update_containing_rect_position()

    def set_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the absolute position of this container - it is usually less chaotic to deal with setting
        relative positions.

        :param position: the new absolute position to set.
        """
        super().set_position(position)
        self.update_containing_rect_position()

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the position of this container, relative to the container it is within.

        :param position: the new relative position to set.
        """
        super().set_relative_position(position)
        self.update_containing_rect_position()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the dimension of this container and update the positions of elements within it accordingly.

        :param dimensions: the new dimensions.
        """
        super().set_dimensions(dimensions)
        self.update_containing_rect_position()

    def get_top_layer(self) -> int:
        """
        Assuming we have correctly calculated the 'thickness' of this container, this method will return the 'highest'
        layer in the LayeredUpdates UI Group.

        :return int: An integer representing the current highest layer being used by this container.
        """
        return self._layer + self.layer_thickness

    def kill(self):
        """
        Overrides the standard kill method of UI Elements (and pygame sprites beyond that) to also call the kill method
        on all contained UI Elements.
        """
        self.clear()
        super().kill()

    def clear(self):
        """
        Removes and kills all the UI elements inside this container.
        """
        while len(self.elements) > 0:
            self.elements.pop().kill()

    # noinspection PyUnusedLocal
    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a 'higher' element.
        :return bool: A boolean that is true if we have hovered a UI element, either just now or before this method.
        """
        if self.alive():
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()

            if self.rect.collidepoint(mouse_x, mouse_y) and not hovered_higher_element:
                if not self.hovered:
                    self.hovered = True
                hovered_higher_element = True

            else:
                if self.hovered:
                    self.hovered = False

        elif self.hovered:
            self.hovered = False
        return hovered_higher_element
