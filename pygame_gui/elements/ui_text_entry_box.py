import re
from typing import Union, Tuple, Dict, Optional

from pygame_gui.core.utility import clipboard_paste, clipboard_copy

from pygame import Rect, MOUSEBUTTONDOWN, MOUSEBUTTONUP, BUTTON_LEFT, KEYDOWN, TEXTINPUT
from pygame import KMOD_SHIFT, KMOD_META, KMOD_CTRL, KMOD_ALT, K_a, K_x, K_c, K_v
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_HOME, K_END, K_BACKSPACE, K_DELETE, K_RETURN
from pygame import key
from pygame.event import Event, post
from pygame_gui._constants import UI_TEXT_ENTRY_CHANGED
from pygame_gui.core import ObjectID
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.elements.ui_text_box import UITextBox


class UITextEntryBox(UITextBox):
    """
    Inherits from UITextBox but allows you to enter text with the keyboard, much like UITextEntryLine.

    :param relative_rect: The 'visible area' rectangle, positioned relative to its container.
    :param initial_text: The text that starts in the text box.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(self,
                 relative_rect: Union[Rect, Tuple[int, int, int, int]],
                 initial_text: str = "",
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
                         visible=visible,
                         allow_split_dashes=False,
                         plain_text_display_only=True,
                         should_html_unescape_input_text=True)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='text_entry_box')

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
        self.vertical_cursor_movement = False
        self.last_horiz_cursor_index = 0

    def get_text(self) -> str:
        """
        Gets the text in the entry box element.

        :return: A string.

        """
        return self.html_text

    def set_text(self, html_text: str, *, text_kwargs: Optional[Dict[str, str]] = None):
        super().set_text(html_text, text_kwargs=text_kwargs)
        self.edit_position = len(self.html_text)
        self.cursor_has_moved_recently = True

    @property
    def select_range(self):
        """
        The selected range for this text. A tuple containing the start
        and end indexes of the current selection.

        Made into a property to keep it synchronised with the underlying drawable shape's
        representation.
        """
        return self._select_range

    @select_range.setter
    def select_range(self, value):
        self._select_range = value
        start_select = min(self._select_range[0], self._select_range[1])
        end_select = max(self._select_range[0], self._select_range[1])

        self.text_box_layout.set_text_selection(start_select, end_select)
        self.redraw_from_text_block()

    def unfocus(self):
        """
        Called when this element is no longer the current focus.
        """
        super().unfocus()
        key.set_repeat(0)
        self.select_range = [0, 0]
        self.edit_position = 0
        self.cursor_on = False
        self.text_box_layout.turn_off_cursor()
        self.redraw_from_text_block()

    def focus(self):
        """
        Called when we 'select focus' on this element. In this case it sets up the keyboard to
        repeat held key presses, useful for natural feeling keyboard input.
        """
        super().focus()
        key.set_repeat(500, 25)

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
        if self.hovered:
            if (self.scroll_bar is None or
                    (self.scroll_bar is not None and
                     not self.scroll_bar.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]))):
                self.ui_manager.set_text_input_hovered(True)

        if self.double_click_timer < self.ui_manager.get_double_click_time():
            self.double_click_timer += time_delta

        if self.selection_in_progress:
            text_layout_space_pos = self._calculate_text_space_pos(scaled_mouse_pos)
            select_end_pos = self.text_box_layout.find_cursor_position_from_click_pos(text_layout_space_pos)
            new_range = [self.select_range[0], select_end_pos]
            if new_range[0] != self.select_range[0] or new_range[1] != self.select_range[1]:
                self.select_range = [new_range[0], new_range[1]]

                self.edit_position = self.select_range[1]
                self.cursor_has_moved_recently = True

        if self.cursor_has_moved_recently:
            self.cursor_has_moved_recently = False
            self.cursor_blink_delay_after_moving_acc = 0.0
            self.cursor_on = True
            self.text_box_layout.set_cursor_position(self.edit_position)
            if not self.vertical_cursor_movement:
                if self.text_box_layout.cursor_text_row is not None:
                    self.last_horiz_cursor_index = self.text_box_layout.cursor_text_row.get_cursor_index()
            self.vertical_cursor_movement = False
            self.text_box_layout.turn_on_cursor()
            if self.scroll_bar is not None:
                cursor_y_pos_top, cursor_y_pos_bottom = self.text_box_layout.get_cursor_y_pos()
                current_height_adjustment = int(self.scroll_bar.start_percentage *
                                                self.text_box_layout.layout_rect.height)
                visible_bottom = current_height_adjustment + self.text_box_layout.view_rect.height
                # handle cursor moving above current scroll position
                if cursor_y_pos_top < current_height_adjustment:
                    new_start_percentage = cursor_y_pos_top / self.text_box_layout.layout_rect.height
                    self.scroll_bar.set_scroll_from_start_percentage(new_start_percentage)
                # handle cursor moving below visible area
                if cursor_y_pos_bottom > visible_bottom:
                    new_top = cursor_y_pos_bottom - self.text_box_layout.view_rect.height
                    new_start_percentage = new_top / self.text_box_layout.layout_rect.height
                    self.scroll_bar.set_scroll_from_start_percentage(new_start_percentage)

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

    def _calculate_text_space_pos(self, scaled_mouse_pos):
        text_layout_top_left = self.get_text_layout_top_left()
        height_adjustment = 0
        if self.scroll_bar is not None:
            height_adjustment = (self.scroll_bar.start_percentage * self.text_box_layout.layout_rect.height)
        text_layout_space_pos = (scaled_mouse_pos[0] - text_layout_top_left[0],
                                 scaled_mouse_pos[1] - text_layout_top_left[1] + height_adjustment)
        return text_layout_space_pos

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
        initial_text_state = self.html_text

        if self._process_mouse_button_event(event):
            consumed_event = True
        if self.is_enabled and self.is_focused and event.type == KEYDOWN:
            if self._process_keyboard_shortcut_event(event):
                consumed_event = True
            elif self._process_action_key_event(event):
                consumed_event = True

        if self.is_enabled and self.is_focused and event.type == TEXTINPUT:
            processed_any_char = False
            for char in event.text:
                if self._process_entered_character(char):
                    processed_any_char = True
            consumed_event = processed_any_char

        if self.html_text != initial_text_state:
            # new event
            event_data = {'text': self.html_text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            post(Event(UI_TEXT_ENTRY_CHANGED, event_data))

        return consumed_event

    def _process_action_key_event(self, event: Event) -> bool:
        """
        Check if event is one of the keys that triggers an action like deleting, or moving
        the edit position.

        :param event: The event to check.

        :return: True if event is consumed.

        """
        consumed_event = False
        if event.key == K_RETURN:
            start_str = self.html_text[:self.edit_position]
            end_str = self.html_text[self.edit_position:]
            self.html_text = start_str + '\n' + end_str
            self.text_box_layout.insert_line_break(self.edit_position, self.parser)
            self.edit_position += 1
            self.redraw_from_text_block()
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_BACKSPACE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.text_box_layout.delete_selected_text()
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.html_text = self.html_text[:low_end] + self.html_text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True

                self.text_box_layout.set_cursor_position(self.edit_position)
                self.redraw_from_text_block()
            elif self.edit_position > 0:
                self.html_text = self.html_text[:self.edit_position - 1] + self.html_text[self.edit_position:]
                self.edit_position -= 1
                self.cursor_has_moved_recently = True

                self.text_box_layout.backspace_at_cursor()
                self.text_box_layout.set_cursor_position(self.edit_position)
                self.redraw_from_text_block()

            consumed_event = True
        elif event.key == K_DELETE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.text_box_layout.delete_selected_text()
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.html_text = self.html_text[:low_end] + self.html_text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                self.text_box_layout.set_cursor_position(self.edit_position)
                self.redraw_from_text_block()

            elif self.edit_position < len(self.html_text):
                self.html_text = self.html_text[:self.edit_position] + self.html_text[self.edit_position + 1:]
                self.edit_position = self.edit_position
                self.cursor_has_moved_recently = True

                self.text_box_layout.delete_at_cursor()
                self.redraw_from_text_block()
            consumed_event = True
        elif self._process_edit_pos_move_key(event):
            consumed_event = True

        return consumed_event

    def _process_edit_pos_move_key(self, event: Event) -> bool:
        """
        Process an action key that is moving the cursor edit position.

        :param event: The event to process.

        :return: True if event is consumed.

        """
        consumed_event = False
        # modded versions of LEFT and RIGHT must go first otherwise the simple
        # cases will absorb the events
        if (event.key == K_HOME or
                (event.key == K_LEFT and
                 (event.mod & KMOD_CTRL or event.mod & KMOD_META))):
            try:
                next_pos = self.edit_position - self.html_text[:self.edit_position][::-1].index("\n")
            except ValueError:
                next_pos = 0
            # include case when shift held down to select everything to start
            # of current line.
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if event.mod & KMOD_SHIFT:
                    if self.edit_position == self.select_range[1]:
                        # undo selection to right, create to left
                        self.select_range = [next_pos, self.select_range[0]]
                    else:
                        # extend left
                        self.select_range = [next_pos, self.select_range[1]]
                else:
                    self.select_range = [0, 0]
            else:
                if event.mod & KMOD_SHIFT:
                    self.select_range = [next_pos, self.edit_position]
                else:
                    self.select_range = [0, 0]
            self.edit_position = next_pos
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif (event.key == K_END or
              (event.key == K_RIGHT and
               (event.mod & KMOD_CTRL or event.mod & KMOD_META))):
            try:
                next_pos = self.edit_position + self.html_text[self.edit_position:].index("\n")
            except ValueError:
                next_pos = len(self.html_text)
            # include case when shift held down to select everything to end
            # of current line.
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if event.mod & KMOD_SHIFT:
                    if self.edit_position == self.select_range[0]:
                        # undo selection to left, create to right
                        self.select_range = [self.select_range[1], next_pos]
                    else:
                        # extend right
                        self.select_range = [self.select_range[0], next_pos]
                else:
                    self.select_range = [0, 0]
            else:
                if event.mod & KMOD_SHIFT:
                    self.select_range = [self.edit_position, next_pos]
                else:
                    self.select_range = [0, 0]
            self.edit_position = next_pos
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_LEFT and event.mod & KMOD_SHIFT:
            # keyboard-based selection
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                # existing selection, so edit_position should correspond to one
                # end of it
                if self.edit_position == self.select_range[0]:
                    # try to extend to the left
                    self.select_range = [max(0, self.edit_position - 1),
                                         self.select_range[1]]
                elif self.edit_position == self.select_range[1]:
                    # reduce to the left
                    self.select_range = [self.select_range[0],
                                         max(0, self.edit_position - 1)]
            else:
                self.select_range = [max(0, self.edit_position - 1),
                                     self.edit_position]
            if self.edit_position > 0:
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_RIGHT and event.mod & KMOD_SHIFT:
            # keyboard-based selection
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if self.edit_position == self.select_range[1]:
                    # try to extend to the right
                    self.select_range = [self.select_range[0],
                                         min(len(self.html_text), self.edit_position + 1)]
                elif self.edit_position == self.select_range[0]:
                    # reduce to the right
                    self.select_range = [min(len(self.html_text), self.edit_position + 1),
                                         self.select_range[1]]
            else:
                self.select_range = [self.edit_position, min(len(self.html_text),
                                                             self.edit_position + 1)]
            if self.edit_position < len(self.html_text):
                self.edit_position += 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_UP and event.mod & KMOD_SHIFT:
            # keyboard-based selection
            new_pos = self.text_box_layout.get_cursor_pos_move_up_one_row(self.last_horiz_cursor_index)
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                # existing selection, so edit_position should correspond to one
                # end of it
                if self.edit_position == self.select_range[0]:
                    # try to extend to the left
                    self.select_range = [max(0, new_pos),
                                         self.select_range[1]]
                elif self.edit_position == self.select_range[1]:
                    # reduce to the left
                    self.select_range = [self.select_range[0],
                                         max(0, new_pos)]
            else:
                self.select_range = [max(0, new_pos),
                                     self.edit_position]
            if self.edit_position > 0:
                self.edit_position = new_pos
                self.cursor_has_moved_recently = True
        elif event.key == K_DOWN and event.mod & KMOD_SHIFT:
            # keyboard-based selection
            new_pos = self.text_box_layout.get_cursor_pos_move_down_one_row(self.last_horiz_cursor_index)
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if self.edit_position == self.select_range[1]:
                    # try to extend to the right
                    self.select_range = [self.select_range[0],
                                                 min(len(self.html_text), new_pos)]
                elif self.edit_position == self.select_range[0]:
                    # reduce to the right
                    self.select_range = [min(len(self.html_text), new_pos),
                                                 self.select_range[1]]
            else:
                self.select_range = [self.edit_position, min(len(self.html_text),
                                                                     new_pos)]
            if self.edit_position < len(self.html_text):
                self.edit_position = new_pos
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_LEFT:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = min(self.select_range[0], self.select_range[1])
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            elif self.edit_position > 0:
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_RIGHT:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = max(self.select_range[0], self.select_range[1])
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            elif self.edit_position < len(self.html_text):
                self.edit_position += 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_UP:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = self.text_box_layout.get_cursor_pos_move_up_one_row(self.last_horiz_cursor_index)
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            else:
                self.edit_position = self.text_box_layout.get_cursor_pos_move_up_one_row(self.last_horiz_cursor_index)
                self.cursor_has_moved_recently = True
            self.vertical_cursor_movement = True
            consumed_event = True
        elif event.key == K_DOWN:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = self.text_box_layout.get_cursor_pos_move_down_one_row(self.last_horiz_cursor_index)
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            else:
                self.edit_position = self.text_box_layout.get_cursor_pos_move_down_one_row(self.last_horiz_cursor_index)
                self.cursor_has_moved_recently = True
            self.vertical_cursor_movement = True
            consumed_event = True
        elif event.key == K_HOME:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.select_range = [0, 0]
            self.edit_position = 0
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == K_END:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.select_range = [0, 0]
            self.edit_position = len(self.html_text)
            self.cursor_has_moved_recently = True
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
                    text_layout_space_pos = self._calculate_text_space_pos(scaled_mouse_pos)
                    self.text_box_layout.set_cursor_from_click_pos(text_layout_space_pos)
                    self.edit_position = self.text_box_layout.get_cursor_index()
                    self.redraw_from_text_block()

                    double_clicking = False
                    if self.double_click_timer < self.ui_manager.get_double_click_time():
                        if self._calculate_double_click_word_selection():
                            double_clicking = True

                    if not double_clicking:
                        self.select_range = [self.edit_position, self.edit_position]
                        self.cursor_has_moved_recently = True
                        self.selection_in_progress = True
                        self.double_click_timer = 0.0

                consumed_event = True

        if (event.type == MOUSEBUTTONUP and
                event.button == BUTTON_LEFT and
                self.selection_in_progress):
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)

            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                consumed_event = True
                text_layout_space_pos = self._calculate_text_space_pos(scaled_mouse_pos)
                self.text_box_layout.set_cursor_from_click_pos(text_layout_space_pos)
                new_edit_pos = self.text_box_layout.get_cursor_index()
                if new_edit_pos != self.edit_position:
                    self.edit_position = new_edit_pos
                    self.cursor_has_moved_recently = True
                    self.select_range = [self.select_range[0], self.edit_position]
                    self.redraw_from_text_block()
            self.selection_in_progress = False

        return consumed_event

    def _process_text_entry_key(self, event: Event) -> bool:
        """
        Process key input that can be added to the text entry text.

        :param event: The event to process.

        :return: True if consumed.
        """
        consumed_event = False

        if hasattr(event, 'unicode'):
            character = event.unicode
            consumed_event = self._process_entered_character(character)
        return consumed_event

    def _process_entered_character(self, character: str) -> bool:
        processed_char = False
        # here we really want to get the font metrics for the current active style where the edit cursor is
        # instead we will make do for now
        font = self.ui_theme.get_font(self.combined_element_ids)
        char_metrics = font.get_metrics(character)
        if len(char_metrics) > 0 and char_metrics[0] is not None:
            valid_character = True
            if valid_character:
                if abs(self.select_range[0] - self.select_range[1]) > 0:
                    low_end = min(self.select_range[0], self.select_range[1])
                    high_end = max(self.select_range[0], self.select_range[1])
                    self.html_text = self.html_text[:low_end] + character + self.html_text[high_end:]
                    self.text_box_layout.delete_selected_text()
                    self.text_box_layout.insert_text(character, low_end, self.parser)
                    self.edit_position = low_end + 1
                    self.select_range = [0, 0]
                else:
                    start_str = self.html_text[:self.edit_position]
                    end_str = self.html_text[self.edit_position:]
                    self.html_text = start_str + character + end_str
                    self.text_box_layout.insert_text(character, self.edit_position, self.parser)
                    self.edit_position += 1
                self.redraw_from_text_block()
                self.cursor_has_moved_recently = True
                processed_char = True
        return processed_char

    def _process_keyboard_shortcut_event(self, event: Event) -> bool:
        """
        Check if event is one of the CTRL key keyboard shortcuts.

        :param event: event to process.

        :return: True if event consumed.

        """
        consumed_event = False
        if (event.key == K_a and
                (event.mod & KMOD_CTRL or event.mod & KMOD_META) and
                not (event.mod & KMOD_ALT)):  # hopefully enable diacritic letters)
            self.select_range = [0, len(self.html_text)]
            self.edit_position = len(self.html_text)
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif (event.key == K_x and
              (event.mod & KMOD_CTRL or event.mod & KMOD_META) and
                not (event.mod & KMOD_ALT)):
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                clipboard_copy(self.html_text[low_end:high_end])
                self.text_box_layout.delete_selected_text()
                self.edit_position = low_end
                self.html_text = self.html_text[:low_end] + self.html_text[high_end:]
                self.text_box_layout.set_cursor_position(self.edit_position)
                self.select_range = [0, 0]
                self.redraw_from_text_block()
                self.cursor_has_moved_recently = True
                consumed_event = True
        elif (event.key == K_c and
              (event.mod & KMOD_CTRL or event.mod & KMOD_META) and
                not (event.mod & KMOD_ALT)):
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                clipboard_copy(self.html_text[low_end:high_end])
                consumed_event = True
        elif self._process_paste_event(event):
            consumed_event = True
        return consumed_event

    def _process_paste_event(self, event: Event) -> bool:
        """
        Process a paste shortcut event. (CTRL+ V)

        :param event: The event to process.

        :return: True if the event is consumed.

        """
        consumed_event = False
        if (event.key == K_v and (event.mod & KMOD_CTRL or event.mod & KMOD_META) and
                not (event.mod & KMOD_ALT)):  # hopefully enable diacritic letters:
            paste = clipboard_paste()
            if paste is not None:
                new_text = self.convert_all_line_endings_to_unix(clipboard_paste())

                if abs(self.select_range[0] - self.select_range[1]) > 0:
                    low_end = min(self.select_range[0], self.select_range[1])
                    high_end = max(self.select_range[0], self.select_range[1])
                    self.html_text = self.html_text[:low_end] + new_text + self.html_text[high_end:]
                    self.set_text(self.html_text)
                    self.edit_position = low_end + len(new_text)
                    self.text_box_layout.set_cursor_position(self.edit_position)
                    self.redraw_from_text_block()
                    self.select_range = [0, 0]
                    self.cursor_has_moved_recently = True
                elif len(new_text) > 0:
                    self.html_text = (self.html_text[:self.edit_position] +
                                      new_text +
                                      self.html_text[self.edit_position:])
                    original_edit_pos = self.edit_position
                    self.set_text(self.html_text)
                    self.edit_position = original_edit_pos + len(new_text)
                    self.text_box_layout.set_cursor_position(self.edit_position)
                    self.redraw_from_text_block()
                    self.cursor_has_moved_recently = True
            consumed_event = True
        return consumed_event

    def _calculate_double_click_word_selection(self):
        """
        If we double clicked on a word in the text, select that word.

        """
        if self.edit_position != self.select_range[0]:
            return False
        index = min(self.edit_position, len(self.html_text) - 1)
        if index >= 0:
            char = self.html_text[index]
            # Check we clicked in the same place on a our second click.
            pattern = re.compile(r"[\w']+")

            while index >= 0 and not pattern.match(char):
                index -= 1
                if index >= 0:
                    char = self.html_text[index]
                else:
                    break
            while index >= 0 and pattern.match(char):
                index -= 1
                if index >= 0:
                    char = self.html_text[index]
                else:
                    break
            start_select_index = index + 1
            index += 1
            if index < len(self.html_text):
                char = self.html_text[index]
                while index < len(self.html_text) and pattern.match(char):
                    index += 1
                    if index < len(self.html_text):
                        char = self.html_text[index]
            end_select_index = index
            self.select_range = [start_select_index, end_select_index]
            self.edit_position = end_select_index
            self.cursor_has_moved_recently = True
            self.selection_in_progress = False
            return True
        else:
            return False

    def redraw_from_text_block(self):
        self.text_box_layout.fit_layout_rect_height_to_rows()
        super().redraw_from_text_block()

    @staticmethod
    def convert_all_line_endings_to_unix(input_str: str):
        return input_str.replace('\r\n', '\n').replace('\r', '\n')

    def rebuild_from_changed_theme_data(self):
        # TODO: refactor this a bit so we don't rebuild twice if base classes and this class has changed data.
        super().rebuild_from_changed_theme_data()

        has_any_changed = False

        text_cursor_colour = self.ui_theme.get_colour_or_gradient('text_cursor',
                                                                  self.combined_element_ids)
        if text_cursor_colour != self.text_cursor_colour:
            self.text_cursor_colour = text_cursor_colour
            has_any_changed = True

        if has_any_changed:
            self._reparse_and_rebuild()
