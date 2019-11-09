import pygame
from typing import List, Union

from pygame_gui.core import ui_container
from pygame_gui import ui_manager


class UIElement(pygame.sprite.Sprite):
    """
    A base class for UI elements. You shouldn't create UI Element objects, instead all UI Element classes should
    derive from this class.

    Inherits from pygame.sprite.Sprite.

    :param relative_rect: A rectangle shape of the UI element, the position is relative to the element's container.
    :param manager: The UIManager that manages this UIElement.
    :param container: A container that this element is contained in.
    :param starting_height: Used to record how many layers above it's container this element should be. Normally 1.
    :param layer_thickness: Used to record how 'thick' this element is in layers. Normally 1.
    :param element_ids: A list of ids that describe the 'hierarchy' of UIElements that this UIElement is part of.
    :param object_ids: A list of custom defined IDs that describe the 'hierarchy' that this UIElement is part of.
    """
    def __init__(self, relative_rect: pygame.Rect, manager: 'ui_manager.UIManager',
                 container: Union['ui_container.UIContainer', None],
                 starting_height: int, layer_thickness: int,
                 object_ids: Union[List[Union[str, None]], None] = None,
                 element_ids: Union[List[str], None] = None):

        self._layer = 0
        self.ui_manager = manager
        super().__init__(self.ui_manager.get_sprite_group())
        self.relative_rect = relative_rect
        self.ui_group = self.ui_manager.get_sprite_group()
        self.ui_theme = self.ui_manager.get_theme()
        self.object_ids = object_ids
        self.element_ids = element_ids

        self.layer_thickness = layer_thickness
        self.starting_height = starting_height
        self.top_layer = self._layer + self.layer_thickness

        if container is None:
            root_window = self.ui_manager.get_window_stack().get_root_window()
            if root_window is not None:
                container = root_window.get_container()
            else:
                container = self

        self.ui_container = container
        if self.ui_container is not None and self.ui_container is not self:
            self.ui_container.add_element(self)

        if self.ui_container is self:
            self.rect = pygame.Rect((relative_rect.x,
                                    relative_rect.y),
                                    relative_rect.size)
        else:
            self.rect = pygame.Rect((self.ui_container.rect.x + relative_rect.x,
                                     self.ui_container.rect.y + relative_rect.y),
                                    relative_rect.size)

        self.image = None

        self.is_enabled = True
        self.hovered = False
        self.hover_time = 0.0

    @staticmethod
    def create_valid_ids(parent_element, object_id, element_id):
        """
        Creates valid id lists for an element. It will assert if users supply object IDs that won't work such as those
        containing full stops. These ID lists are used by the theming system to identify what theming parameters to
        apply to which element.

        :param parent_element: Element that this element 'belongs to' in theming. Elements inherit colours from parents.
        :param object_id: An optional ID to help distinguish this element from other elements of the same class.
        :param element_id: A string ID representing this element's class.
        :return:
        """
        if object_id is not None and ('.' in object_id or ' ' in object_id):
            raise ValueError('Object ID cannot contain fullstops or spaces: ' + str(object_id))

        if parent_element is not None:
            new_element_ids = parent_element.element_ids.copy()
            new_element_ids.append(element_id)

            new_object_ids = parent_element.object_ids.copy()
            new_object_ids.append(object_id)
        else:
            new_element_ids = [element_id]
            new_object_ids = [object_id]

        return new_element_ids, new_object_ids

    def update_containing_rect_position(self):
        """
        Updates the position of this element based on the position of it's container. Usually called when the container
        has moved.
        """
        self.rect = pygame.Rect((self.ui_container.rect.x + self.relative_rect.x,
                                 self.ui_container.rect.y + self.relative_rect.y),
                                self.relative_rect.size)

    def change_layer(self, new_layer: int):
        """
        Changes the layer this element is on.

        :param new_layer: The layer to change this element to.
        """
        self.ui_group.change_layer(self, new_layer)
        self._layer = new_layer
        self.top_layer = new_layer + self.layer_thickness

    def kill(self):
        """
        Overriding regular sprite kill() method to remove the element from it's container.
        """
        self.ui_container.remove_element(self)
        super().kill()

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a 'higher' element.
        :return bool: A boolean that is true if we have hovered a UI element, either just now or before this method.
        """
        if self.alive() and self.can_hover():
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            if self.is_enabled and self.hover_point(mouse_x, mouse_y) and not hovered_higher_element:
                if not self.hovered:
                    self.hovered = True
                    self.on_hovered()

                hovered_higher_element = True
                self.while_hovering(time_delta, mouse_pos)

            else:
                if self.hovered:
                    self.hovered = False
                    self.on_unhovered()
        elif self.hovered:
            self.hovered = False
        return hovered_higher_element

    def on_hovered(self):
        """
        A stub to override. Called when this UI element first enters the 'hovered' state.
        """
        pass

    def while_hovering(self, time_delta: float, mouse_pos: pygame.math.Vector2):
        """
        A stub method to override. Called when this UI element is currently hovered.

        :param time_delta: A float, the time in seconds between the last call to this function and now (roughly).
        :param mouse_pos: The current position of the mouse as 2D Vector.
        """
        pass

    def hover_point(self, x: float, y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a straightforward matter of
        seeing if a point is inside the rectangle. Occasionally it will also check if we are in a wider zone around
        a UI element once it is already active, this makes it easier to move scroll bars and the like.

        :param x: The x (horizontal) position of the point.
        :param y: The y (vertical) position of the point.
        :return bool: Returns True if we are hovering this element.
        """
        return self.rect.collidepoint(x, y)

    def on_unhovered(self):
        """
        A stub to override. Called when this UI element leaves the 'hovered' state.
        """
        pass

    def can_hover(self) -> bool:
        """
        A stub method to override. Called to test if this method can be hovered.
        """
        return True

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        A stub to override. Gives UI Elements access to pygame events.

        :param event: The event to process.
        :return bool: Should return True if this element makes use fo this event.
        """
        if self is not None:
            return False

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

    def rebuild_from_changed_theme_data(self):
        pass
