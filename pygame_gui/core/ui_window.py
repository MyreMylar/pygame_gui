import pygame
from typing import List, Union, Tuple, Dict

from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.ui_container import UIContainer
from pygame_gui import ui_manager


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
                 object_ids: Union[List[Union[str, None]], None] = None,
                 window_container_margins: Dict[str, int] = None,
                 resizable=False):

        new_element_ids = element_ids.copy()
        new_object_ids = object_ids.copy() if object_ids is not None else [None]
        self.window_container = None
        self.resizable = resizable
        self.minimum_dimensions = (100, 100)
        self.edge_hovering = [False, False, False, False]
        # need to create the container that holds the elements first if this is the root window
        # so we can bootstrap everything and effectively add the root window to it's own container.
        # It's a little bit weird.
        starting_height = 1
        if len(element_ids) == 1 and element_ids[0] == 'root_window':
            self._layer = 0
            self.window_container = UIContainer(rect.copy(), manager, None, None, None)
            self.window_stack = manager.get_window_stack()
            self.window_stack.add_new_window(self)
            starting_height = 0  # nothing to draw in the root window

        super().__init__(rect, manager, container=None,
                         starting_height=starting_height,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids)

        if self.window_container is None:
            if window_container_margins is None:
                relative_container_rect = self.relative_rect.copy()
                self.container_margins = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
            else:
                self.container_margins = window_container_margins
                relative_container_rect = pygame.Rect(self.relative_rect.left + window_container_margins['left'],
                                                      self.relative_rect.right + window_container_margins['top'],
                                                      self.relative_rect.width - (self.container_margins['left'] +
                                                                                  self.container_margins['right']),
                                                      self.relative_rect.height - (self.container_margins['top'] +
                                                                                   self.container_margins['bottom']))
            self.window_container = UIContainer(relative_container_rect, manager, None, self, None)
            self.window_stack = self.ui_manager.get_window_stack()
            self.window_stack.add_new_window(self)

        self.image = pygame.Surface((0, 0))
        self.bring_to_front_on_focused = True

        self.resizing_mode_active = False
        self.start_resize_point = (0, 0)
        self.start_resize_rect = None

    def set_minimum_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        If this window is resizable, then the dimensions we set here will be the minimum that users can change the
        window to. They are also used as the minimum size when 'set_dimensions' is called.
        """
        self.minimum_dimensions = (min(self.ui_container.rect.width, int(dimensions[0])),
                                   min(self.ui_container.rect.height, int(dimensions[1])))

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the size of this window and then resizes and shifts the contents of the windows container to fit the new
        size.

        :param dimensions:
        """
        # clamp to minimum dimensions and container size
        dimensions = (min(self.ui_container.rect.width, max(self.minimum_dimensions[0], int(dimensions[0]))),
                      min(self.ui_container.rect.height, max(self.minimum_dimensions[1], int(dimensions[1]))))

        # Don't use a basic gate on this set dimensions method because the container may be a different size to the
        # window
        super().set_dimensions(dimensions)

        new_container_dimensions = (self.relative_rect.width - (self.container_margins['left'] +
                                                                self.container_margins['right']),
                                    self.relative_rect.height - (self.container_margins['top'] +
                                                                 self.container_margins['bottom']))
        if new_container_dimensions != self.get_container().relative_rect.size:
            self.get_container().set_dimensions(new_container_dimensions)
            self.get_container().set_relative_position((self.relative_rect.x + self.container_margins['left'],
                                                        self.relative_rect.y + self.container_margins['top']))
            self.get_container().update_containing_rect_position()

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_relative_position(position)

        self.get_container().set_relative_position((self.relative_rect.x + self.container_margins['left'],
                                                    self.relative_rect.y + self.container_margins['top']))
        self.get_container().update_containing_rect_position()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.

        TODO: Check for drawable shape and use that instead of rect?

        :param event: The event to process.
        :return bool: Should return True if this element makes use of this event.
        """
        handled = False
        if self is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
            scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))

            if event.button == 1 and (self.edge_hovering[0] or self.edge_hovering[1] or
                                      self.edge_hovering[2] or self.edge_hovering[3]):
                self.resizing_mode_active = True
                self.start_resize_point = scaled_mouse_pos
                self.start_resize_rect = self.rect.copy()
                handled = True
            elif self.rect.collidepoint(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                handled = True

        if self is not None and event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.resizing_mode_active:
            self.resizing_mode_active = False
            handled = True

        return handled

    def check_clicked_inside(self, event: pygame.event.Event) -> bool:
        """
        A quick event check outside of the normal event processing so that this window is brought to the front of the
        window stack if we click on any of the elements contained within it.

        TODO: Check for drawable shape and use that instead of rect?

        :param event: The event to check.
        :return bool: returns True if the processed event represents a click inside this window
        """
        event_handled = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))
            if self.rect.collidepoint(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.bring_to_front_on_focused:
                    self.window_stack.move_window_to_front(self)
                event_handled = True
        return event_handled

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived classes
        but also has a little functionality to make sure the window's layer 'thickness' is accurate and to handle
        window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        super().update(time_delta)
        if self.get_container().layer_thickness != self.layer_thickness:
            self.layer_thickness = self.get_container().layer_thickness

        if self.resizing_mode_active:
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            x_diff = mouse_x - self.start_resize_point[0]
            y_diff = mouse_y - self.start_resize_point[1]

            y_pos = self.start_resize_rect.y
            y_dimension = self.start_resize_rect.height
            if self.edge_hovering[1]:
                y_dimension = self.start_resize_rect.height - y_diff
                y_pos = self.start_resize_rect.y + y_diff
            elif self.edge_hovering[3]:
                y_dimension = self.start_resize_rect.height + y_diff

            x_pos = self.start_resize_rect.x
            x_dimension = self.start_resize_rect.width
            if self.edge_hovering[0]:
                x_dimension = self.start_resize_rect.width - x_diff
                x_pos = self.start_resize_rect.x + x_diff
            elif self.edge_hovering[2]:
                x_dimension = self.start_resize_rect.width + x_diff

            x_dimension = max(self.minimum_dimensions[0], min(self.ui_container.rect.width, x_dimension))
            y_dimension = max(self.minimum_dimensions[1], min(self.ui_container.rect.height, y_dimension))

            self.set_position((x_pos, y_pos))
            self.set_dimensions((x_dimension, y_dimension))

    def get_container(self) -> UIContainer:
        """
        Returns the container that should contain all the UI elements in this window.

        :return UIContainer: The window's container.
        """
        return self.window_container

    # noinspection PyUnusedLocal
    def check_hover(self, time_delta: float, hovered_higher_element: bool):
        """
        For the window the only hovering we care about is the edges if this is a resizable window.

        :param time_delta: time passed in seconds between one call to this method and the next.
        :param hovered_higher_element: Have we already hovered an element/window above this one.
        """
        hovered = False
        if self.alive() and self.can_hover() and self.resizable and not hovered_higher_element and not self.resizing_mode_active:
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            # Build a temporary rect just a little bit larger than our container rect.
            resize_rect = pygame.Rect(self.get_container().rect.left - 4,
                                      self.get_container().rect.top - 4,
                                      self.get_container().rect.width + 8,
                                      self.get_container().rect.height + 8)
            self.edge_hovering = [False, False, False, False]
            if resize_rect.collidepoint(mouse_x, mouse_y):
                if resize_rect.right > mouse_x > resize_rect.right - 6:
                    self.edge_hovering[2] = True
                    hovered = True

                if resize_rect.left + 6 > mouse_x > resize_rect.left:
                    self.edge_hovering[0] = True
                    hovered = True

                if resize_rect.bottom > mouse_y > resize_rect.bottom - 6:
                    self.edge_hovering[3] = True
                    hovered = True

                if resize_rect.top + 6 > mouse_y > resize_rect.top:
                    self.edge_hovering[1] = True
                    hovered = True

        if hovered:
            hovered_higher_element = True
            self.hovered = True
        else:
            self.hovered = False

        return hovered_higher_element

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
            self.window_container.change_container_layer(new_layer)

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
