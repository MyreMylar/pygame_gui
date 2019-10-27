import pygame
from typing import List, Union

from ..core.ui_element import UIElement
from ..core.ui_container import UIContainer
from .. import ui_manager


class UIWindow(UIElement):
    """
    A base class for window GUI elements, any windows should inherit from this class.

    :param rect: A rectangle that completely surrounds the window.
    :param manager: The UIManager that manages this UIElement.
    :param element_ids: A list of ids that describe the 'hierarchy' of UIElements that this UIElement is part of.
    :param object_ids: A list of custom defined IDs that describe the 'hierarchy' that this UIElement is part of.
    """
    def __init__(self, rect: pygame.Rect,
                 manager: 'ui_manager.UIManager',
                 element_ids: List[str],
                 object_ids: Union[List[Union[str, None]], None] = None):

        new_element_ids = element_ids.copy()
        if object_ids is not None:
            new_object_ids = object_ids.copy()
        else:
            new_object_ids = [None]

        self.window_container = None
        # need to create the container that holds the elements first if this is the root window
        # so we can bootstrap everything and effectively add the root window to it's own container.
        # It's a little bit weird.
        if len(element_ids) == 1 and element_ids[0] == 'root_window':
            self._layer = 0
            self.window_container = UIContainer(rect.copy(), manager, None, None, None)
            self.window_stack = manager.get_window_stack()
            self.window_stack.add_new_window(self)

        super().__init__(rect, manager, container=None,
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids)

        if self.window_container is None:
            self.window_container = UIContainer(self.rect.copy(), manager, None, self, None)
            self.window_stack = self.ui_manager.get_window_stack()
            self.window_stack.add_new_window(self)

        self.image = self.image = pygame.Surface((0, 0))

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        A stub to override. Gives UI Windows access to pygame events.

        :param event: The event to process.
        :return bool: Should return True if this element makes use fo this event.
        """
        if self is not None:
            return False

    def check_clicked_inside(self, event: pygame.event.Event) -> bool:
        """
        A quick event check outside of the normal event processing so that this window is brought to the front of the
        window stack if we click on any of the elements contained within it.

        :param event: The event to check.
        :return bool: returns True if the processed event represents a click inside this window
        """
        event_handled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    self.window_stack.move_window_to_front(self)
                    event_handled = True
        return event_handled

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived classes
        but also has a little functionality to make sure the window's layer 'thickness' is accurate.

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        if self.get_container().layer_thickness + 1 != self.layer_thickness:
            self.layer_thickness = self.get_container().layer_thickness + 1

    def get_container(self) -> UIContainer:
        """
        Returns the container that should contain all the UI elements in this window.

        :return UIContainer: The window's container.
        """
        return self.window_container

    # noinspection PyUnusedLocal
    def check_hover(self, time_delta: float, hovered_higher_element: bool):
        """
        A stub, called to check if this window is being hovered. Since the UIWindow contains a
        UIContainer of the same dimensions it doesn't really need to do anything here as the container
        completely encompasses/overlaps it.

        :param time_delta: time passed in seconds between one call to this method and the next.
        :param hovered_higher_element: Have we already hovered an element/window above this one.
        """
        pass

    def get_top_layer(self) -> int:
        """
        Returns the 'highest' layer used by this window so that we can correctly place other windows on top of it.

        :return int: The top layer for this window as a number (greater numbers are higher layers).
        """
        return self._layer + self.layer_thickness

    def change_window_layer(self, new_layer: int):
        """
        Move this window, and it's contents, to a new layer in the UI.

        :param new_layer: The layer to move to.
        """
        if new_layer != self._layer:
            self._layer = new_layer
            self.ui_manager.get_sprite_group().change_layer(self, new_layer)
            self.window_container.change_container_layer(new_layer+1)

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI elements in this window,
        and remove if from the window stack.
        """
        self.window_stack.remove_window(self)
        self.window_container.kill()
        super().kill()

    def select(self):
        """
        A stub to override. Called when we select focus this UI element.
        """
        pass

    def unselect(self):
        """
        A stub to override. Called when we stop select focusing this UI element.
        """
        pass
