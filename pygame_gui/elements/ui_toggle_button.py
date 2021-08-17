from typing import Union, Tuple, Dict

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, UI_BUTTON_START_PRESS
from pygame_gui._constants import UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import EllipseDrawableShape, RoundedRectangleShape
from pygame_gui.core.drawable_shapes import RectDrawableShape
from pygame_gui.elements.ui_button import UIButton


class UIToggleButton(UIButton):
    def __init__(
        self,
        text: str,
        relative_rect: pygame.Rect,
        manager: IUIManagerInterface,
        container: Union[IContainerLikeInterface, None] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        parent_element: UIElement = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Dict[str, str] = None,
        visible: int = 1,
        is_on: bool = False
    ):
        super().__init__(
            relative_rect,
            text,
            manager,
            container,
            tool_tip_text,
            starting_height,
            parent_element,
            object_id,
            anchors,
            False,
            visible
        )

        self._state = is_on

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles various interactions with the button, including toggling its value.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.is_enabled:
                    if (self.allow_double_clicks and
                            self.double_click_timer <= self.ui_manager.get_double_click_time()):
                        event_data = {'user_type': UI_BUTTON_DOUBLE_CLICKED,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
                    else:
                        event_data = {'user_type': UI_BUTTON_START_PRESS,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
                        self.double_click_timer = 0.0
                        self.held = True
                        if self._state is True:
                            self._set_inactive()
                        else:
                            self._set_active()
                        self.hover_time = 0.0
                        if self.tool_tip is not None:
                            self.tool_tip.kill()
                            self.tool_tip = None
                consumed_event = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if (self.is_enabled and
                    self.drawable_shape.collide_point(scaled_mouse_pos) and
                    self.held):
                self.held = False
                self._state = not self._state
                if self._state is True:
                    self._set_active()
                else:
                    self._set_inactive()
                consumed_event = True
                self.pressed_event = True

                event_data = {'user_type': UI_BUTTON_PRESSED,
                              'ui_element': self,
                              'ui_object_id': self.most_specific_combined_id}
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

            if self.is_enabled and self.held:
                self.held = False
                consumed_event = True

        return consumed_event

    def on_unhovered(self):
        """
        Called when we leave the hover state. Resets the colours and images to normal and kills any
        tooltip that was created while we were hovering the button.
        """
        state = self._get_ui_state()
        self.drawable_shape.set_active_state(state)
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

        event_data = {'user_type': UI_BUTTON_ON_UNHOVERED,
                      'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        state = self._get_ui_state()
        if not self.is_enabled:
            self.is_enabled = True
            self.drawable_shape.set_active_state(state)

    def unselect(self):
        """
        Called when we are no longer select focusing this element. Restores the colours and image
        to the default state then redraws the button.
        """
        state = self._get_ui_state()
        self.is_selected = False
        self.drawable_shape.set_active_state(state)

    def get_state(self) -> bool:
        """
        Get the on/off state of this toggle button.

        :return: Return True if the button is "on" or False if the button is "off."
        """
        return self._state

    def _get_ui_state(self):
        return 'active' if self._state is True else 'normal'
