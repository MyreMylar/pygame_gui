from typing import Union, Tuple, Dict, Optional, Any

from pygame import Rect, MOUSEBUTTONDOWN, BUTTON_LEFT
from pygame.event import Event
from pygame_gui.core import ObjectID
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.elements.ui_text_box import UITextBox


class UITextEntryBox(UITextBox):
    def __init__(self,
                 relative_rect: Union[Rect, Tuple[int, int, int, int]],
                 initial_text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):
        super().__init__(initial_text,
                         relative_rect,
                         manager=manager,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

        # input timings - I expect nobody really wants to mess with these that much
        # ideally we could populate from the os settings but that sounds like a headache
        self.key_repeat = 0.5
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_blink_delay_after_moving = 1.0
        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.4

        self.double_click_timer = self.ui_manager.get_double_click_time() + 1.0

        self.edit_position = 0
        self._select_range = [0, 0]
        self.selection_in_progress = False

        self.cursor_on = False
        self.cursor_has_moved_recently = False

    def update(self, time_delta: float):
        """
        Called every update loop of our UI Manager. Largely handles text drag selection and
        making sure our edit cursor blinks on and off.

        :param time_delta: The time in seconds between this update method call and the previous one.

        """
        super().update(time_delta)

        if not self.alive():
            return
        scaled_mouse_pos = self.ui_manager.get_mouse_position()
        if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
            self.ui_manager.set_text_input_hovered(True)

        if self.cursor_has_moved_recently:
            self.cursor_has_moved_recently = False
            self.cursor_blink_delay_after_moving_acc = 0.0
            self.cursor_on = True
            self.text_box_layout.set_cursor_position(self.edit_position)
            self.text_box_layout.toggle_cursor()
            self.redraw_from_text_block()

        if self.cursor_blink_delay_after_moving_acc > self.cursor_blink_delay_after_moving:
            if self.blink_cursor_time_acc >= self.blink_cursor_time:
                self.blink_cursor_time_acc = 0.0
                if self.cursor_on:
                    self.cursor_on = False
                    self.text_box_layout.toggle_cursor()
                    self.redraw_from_text_block()
                elif self.is_focused:
                    self.cursor_on = True
                    self.text_box_layout.toggle_cursor()
                    self.redraw_from_text_block()
            else:
                self.blink_cursor_time_acc += time_delta
        else:
            self.cursor_blink_delay_after_moving_acc += time_delta

    def process_event(self, event: Event) -> bool:
        """
        Allows the text entry box to react to input events, which is it's primary function.
        The entry element reacts to various types of mouse clicks (double click selecting words,
        drag select), keyboard combos (CTRL+C, CTRL+V, CTRL+X, CTRL+A), individual editing keys
        (Backspace, Delete, Left & Right arrows) and other keys for inputting letters, symbols
        and numbers.

        :param event: The current event to consider reacting to.

        :return: Returns True if we've done something with the input event.

        """
        consumed_event = False

        if self._process_mouse_button_event(event):
            consumed_event = True

        return consumed_event

    def _process_mouse_button_event(self, event: Event) -> bool:
        """
        Process a mouse button event.

        :param event: Event to process.

        :return: True if we consumed the mouse event.

        """
        consumed_event = False
        if event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.is_enabled:
                    text_layout_top_left = self.get_text_layout_top_left()
                    # need to account for scroll bar scrolling here - see example code
                    text_layout_space_pos = (scaled_mouse_pos[0] - text_layout_top_left[0],
                                             scaled_mouse_pos[1] - text_layout_top_left[1])
                    self.text_box_layout.set_cursor_from_click_pos(text_layout_space_pos)
                    self.edit_position = self.text_box_layout.get_cursor_index()
                    self.redraw_from_text_block()

                    double_clicking = False
                    # if self.double_click_timer < self.ui_manager.get_double_click_time():
                    #     if self._calculate_double_click_word_selection():
                    #         double_clicking = True

                    if not double_clicking:
                        self.select_range = [self.edit_position, self.edit_position]
                        self.cursor_has_moved_recently = True
                        self.selection_in_progress = True
                        self.double_click_timer = 0.0

                consumed_event = True

        return consumed_event
