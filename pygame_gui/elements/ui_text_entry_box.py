from typing import Union, Dict, Optional

from pygame import KEYDOWN, TEXTINPUT
from pygame import KMOD_META, KMOD_CTRL, KMOD_ALT, K_x, K_v
from pygame import K_BACKSPACE, K_DELETE, K_RETURN
from pygame import key
from pygame.event import Event, post

from pygame_gui.core.utility import clipboard_paste, clipboard_copy
from pygame_gui._constants import UI_TEXT_ENTRY_CHANGED
from pygame_gui.core import ObjectID
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IUIElementInterface,
)
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core.gui_type_hints import RectLike


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
    :param: placeholder_text: If the text line is empty, and not focused, this placeholder text will be
                              shown instead.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        initial_text: str = "",
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
        *,
        placeholder_text: Optional[str] = None,
    ):
        super().__init__(
            initial_text,
            relative_rect,
            manager=manager,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            allow_split_dashes=False,
            plain_text_display_only=True,
            should_html_unescape_input_text=True,
            placeholder_text=placeholder_text,
        )

        self._create_valid_ids(
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            element_id="text_entry_box",
        )

        # input timings - I expect nobody really wants to mess with these that much
        # ideally we could populate from the os settings but that sounds like a headache
        self.key_repeat = 0.5
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_blink_delay_after_moving = 1.0
        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.4
        self.paste_text_enabled = True

        self.text_box_rows = 0

        self.cursor_on = False
        self.has_edit_cursor = True

        self.should_redraw_from_text_block = False

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

    def unfocus(self):
        """
        Called when this element is no longer the current focus.
        """
        super().unfocus()
        key.set_repeat(0)
        self.cursor_on = False
        self.text_box_layout.turn_off_cursor()
        self.cursor_has_moved_recently = False
        self.should_redraw_from_text_block = True

    def focus(self):
        """
        Called when we 'select focus' on this element. In this case it sets up the keyboard to
        repeat held key presses, useful for natural feeling keyboard input.
        """
        super().focus()
        key.set_repeat(500, 25)

        self.text_box_layout.set_cursor_position(self.edit_position)
        self.cursor_has_moved_recently = True

    def update(self, time_delta: float):
        """
        Called every update loop of our UI Manager. Largely handles text drag selection and
        making sure our edit cursor blinks on and off.

        :param time_delta: The time in seconds between this update method call and the previous one.

        """
        super().update(time_delta)

        if not self.alive():
            return

        if self.text_box_rows != len(self.text_box_layout.layout_rows):
            self.text_box_rows = len(self.text_box_layout.layout_rows)
            self._align_all_text_rows()
            self.redraw_from_chunks()

        if (
            self.cursor_blink_delay_after_moving_acc
            > self.cursor_blink_delay_after_moving
        ):
            if self.blink_cursor_time_acc >= self.blink_cursor_time:
                self.blink_cursor_time_acc = 0.0
                if self.cursor_on:
                    self._change_cursor_state(cursor_on=False)
                elif self.is_focused:
                    self._change_cursor_state(cursor_on=True)
            else:
                self.blink_cursor_time_acc += time_delta
        else:
            self.cursor_blink_delay_after_moving_acc += time_delta

        if self.should_redraw_from_text_block:
            self.should_redraw_from_text_block = False
            self.redraw_from_text_block()

    def _change_cursor_state(self, cursor_on: bool):
        self.cursor_on = cursor_on
        self.text_box_layout.toggle_cursor()
        self.redraw_from_text_block()

    def _handle_cursor_visibility(self):
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_on = True
        self.text_box_layout.turn_on_cursor()

    def process_event(self, event: Event) -> bool:
        """
        Allows the text entry box to react to input events, which is its primary function.
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
            key_mods = key.get_mods()
            if event.text == "v" and ((key_mods & KMOD_CTRL) or (key_mods & KMOD_META)):
                self._do_paste()
                consumed_event = True
            else:
                processed_any_char = False
                for char in event.text:
                    if self._process_entered_character(char):
                        processed_any_char = True
                consumed_event = processed_any_char

        if self.html_text != initial_text_state:
            # new event
            event_data = {
                "text": self.html_text,
                "ui_element": self,
                "ui_object_id": self.most_specific_combined_id,
            }
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
            consumed_event = self._insert_line_break_at_edit_cursor()
        elif event.key == K_BACKSPACE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self._delete_selected_text()
            elif self.edit_position > 0:
                self._backspace_at_edit_cursor()
            consumed_event = True
        elif event.key == K_DELETE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self._delete_selected_text()
            elif self.edit_position < len(self.html_text):
                self.html_text = (
                    self.html_text[: self.edit_position]
                    + self.html_text[self.edit_position + 1 :]
                )
                self.edit_position = self.edit_position
                self.cursor_has_moved_recently = True

                self.text_box_layout.delete_at_cursor()
                self.redraw_from_text_block()
            consumed_event = True
        elif self._process_edit_pos_move_key(event):
            consumed_event = True

        return consumed_event

    def _replace_selected_text_with_character(self, character):
        start_of_selection = self._replace_selection_with_text_in_html_string(character)
        self.text_box_layout.delete_selected_text()
        self.text_box_layout.insert_text(character, start_of_selection, self.parser)
        self.edit_position = start_of_selection + 1
        self.select_range = [0, 0]

    def _delete_selected_text(self):
        self.text_box_layout.delete_selected_text()
        low_end = min(self.select_range[0], self.select_range[1])
        high_end = max(self.select_range[0], self.select_range[1])
        self.html_text = self.html_text[:low_end] + self.html_text[high_end:]
        self.edit_position = low_end
        self.select_range = [0, 0]
        self.cursor_has_moved_recently = True

        self.text_box_layout.set_cursor_position(self.edit_position)
        self.redraw_from_text_block()

    def _insert_line_break_at_edit_cursor(self):
        self._insert_text_into_html_string("\n")
        self.text_box_layout.insert_line_break(self.edit_position, self.parser)
        self.edit_position += 1
        self.redraw_from_text_block()
        self.cursor_has_moved_recently = True
        return True

    def _backspace_at_edit_cursor(self):
        self.html_text = (
            self.html_text[: self.edit_position - 1]
            + self.html_text[self.edit_position :]
        )
        self.edit_position -= 1
        self.cursor_has_moved_recently = True

        self.text_box_layout.backspace_at_cursor()
        self.text_box_layout.set_cursor_position(self.edit_position)
        self.redraw_from_text_block()

    def _process_text_entry_key(self, event: Event) -> bool:
        """
        Process key input that can be added to the text entry text.

        :param event: The event to process.

        :return: True if consumed.
        """
        consumed_event = False

        if hasattr(event, "unicode"):
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
                    self._replace_selected_text_with_character(character)
                else:
                    self._insert_text_into_html_string(character)
                    self.text_box_layout.insert_text(
                        character, self.edit_position, self.parser
                    )
                    self.edit_position += 1
                self.redraw_from_text_block()
                self.cursor_has_moved_recently = True
                processed_char = True
        return processed_char

    def _insert_text_into_html_string(self, new_text):
        start_str = self.html_text[: self.edit_position]
        end_str = self.html_text[self.edit_position :]
        self.html_text = start_str + new_text + end_str

    def _process_keyboard_shortcut_event(self, event: Event) -> bool:
        """
        Check if event is one of the CTRL key keyboard shortcuts.

        :param event: event to process.

        :return: True if event consumed.

        """
        consumed_event = super()._process_keyboard_shortcut_event(event)
        if self._process_cut_event(event):
            consumed_event = True
        elif self._process_paste_event(event):
            consumed_event = True
        return consumed_event

    def _process_cut_event(self, event: Event) -> bool:
        """
        Process a cut shortcut event. (CTRL+ X)

        :param event: The event to process.

        :return: True if the event is consumed.

        """
        consumed_event = False
        if (
            event.key == K_x
            and (event.mod & KMOD_CTRL or event.mod & KMOD_META)
            and not (event.mod & KMOD_ALT)
        ):
            self._do_cut()
            consumed_event = True
        return consumed_event

    def _do_cut(self):
        if (
            self.ui_manager.copy_text_enabled
            and self.copy_text_enabled
            and abs(self.select_range[0] - self.select_range[1]) > 0
        ):
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

    def _process_paste_event(self, event: Event) -> bool:
        """
        Process a paste shortcut event. (CTRL+ V)

        :param event: The event to process.

        :return: True if the event is consumed.

        """
        consumed_event = False
        if (
            event.key == K_v
            and (event.mod & KMOD_CTRL or event.mod & KMOD_META)
            and not (event.mod & KMOD_ALT)
        ):  # hopefully enable diacritic letters:
            self._do_paste()
            consumed_event = True
        return consumed_event

    def _do_paste(self):
        if not self.ui_manager.paste_text_enabled or not self.paste_text_enabled:
            return
        paste = clipboard_paste()
        if paste is not None:
            new_text = self.convert_all_line_endings_to_unix(paste)

            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self._replace_selection_with_new_pasted_text(new_text)
            elif len(new_text) > 0:
                self.html_text = (
                    self.html_text[: self.edit_position]
                    + new_text
                    + self.html_text[self.edit_position :]
                )
                original_edit_pos = self.edit_position
                self._set_text_and_adjust_edit_pos_after_paste(
                    original_edit_pos, new_text
                )
                self.cursor_has_moved_recently = True

    def _set_text_and_adjust_edit_pos_after_paste(self, starting_paste_pos, new_text):
        self.set_text(self.html_text)
        self.edit_position = starting_paste_pos + len(new_text)
        self.text_box_layout.set_cursor_position(self.edit_position)
        self.redraw_from_text_block()

    def _replace_selection_with_new_pasted_text(self, new_text):
        start_of_selection = self._replace_selection_with_text_in_html_string(new_text)
        self._set_text_and_adjust_edit_pos_after_paste(start_of_selection, new_text)
        self.select_range = [0, 0]
        self.cursor_has_moved_recently = True

    def _replace_selection_with_text_in_html_string(self, new_text):
        low_end = min(self.select_range[0], self.select_range[1])
        high_end = max(self.select_range[0], self.select_range[1])
        self.html_text = self.html_text[:low_end] + new_text + self.html_text[high_end:]
        return low_end

    def redraw_from_text_block(self):
        self.text_box_layout.fit_layout_rect_height_to_rows()
        super().redraw_from_text_block()

    @staticmethod
    def convert_all_line_endings_to_unix(input_str: str):
        """
        Returns a copy of the input string with all the line endings changed to the unix style.

        :param input_str: string to copy and replace
        :return: a copy of the input string with the line endings replaced
        """
        return input_str.replace("\r\n", "\n").replace("\r", "\n")
