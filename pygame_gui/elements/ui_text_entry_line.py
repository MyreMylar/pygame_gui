import re
import warnings

from typing import Union, List, Dict, Optional, Tuple

import pygame

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED, OldType

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.utility import clipboard_paste, clipboard_copy, translate

from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UITextEntryLine(UIElement):
    """
    A GUI element for text entry from a keyboard, on a single line. The element supports
    the standard copy and paste keyboard shortcuts CTRL+V, CTRL+C & CTRL+X as well as CTRL+A.

    There are methods that allow the entry element to restrict the characters that can be input
    into the text box

    The height of the text entry line element will be determined by the font used rather than
    the standard method for UIElements of just using the height of the input rectangle.

    :param relative_rect: A rectangle describing the position and width of the text entry element.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    :param: initial_text: A string that will start in this box. This text will remain when box is focused
                          for editing.
    :param: placeholder_text: If the text line is empty, and not focused, this placeholder text will be
                              shown instead.
    """

    _number_character_set = {'en': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']}

    # excluding these characters won't ensure that user entered text is a valid filename but they
    # can help reduce the problems that input will leave you with.
    _forbidden_file_path_characters = {'en': ['<', '>', ':', '"', '/',
                                              '\\', '|', '?', '*', '\0', '.']}

    _alphabet_characters_lower = {'en': ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                                         'h', 'i', 'j', 'k', 'l', 'm', 'n',
                                         'o', 'p', 'q', 'r', 's', 't', 'u',
                                         'v', 'w', 'x', 'y', 'z']}
    _alphabet_characters_upper: Dict[str, List[str]] = {
        'en': [char.upper() for char in _alphabet_characters_lower['en']],
        'ja': [],  # no upper case in japanese
        'zh': []}  # no upper case in chinese

    _alphabet_characters_all = {'en': _alphabet_characters_lower['en'] +
                                _alphabet_characters_upper['en']}

    _alpha_numeric_characters = {'en': (_alphabet_characters_all['en'] +
                                        _number_character_set['en'])}

    def __init__(self,
                 relative_rect: Union[pygame.Rect, Tuple[int, int, int, int]],
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1,
                 *,
                 initial_text: Optional[str] = None,
                 placeholder_text: Optional[str] = None):

        super().__init__(relative_rect, manager, container,
                         starting_height=1, layer_thickness=1,
                         anchors=anchors, visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['text_entry_line'])

        self.text = ""
        if initial_text is not None:
            self.text = translate(initial_text)
        self.is_text_hidden = False
        self.hidden_text_char = '●'
        self.placeholder_text = ""
        if placeholder_text is not None:
            self.placeholder_text = placeholder_text

        # theme font
        self.font: Optional[IGUIFontInterface] = None
        self.hidden_font: Optional[IGUIFontInterface] = self.ui_theme.get_font_dictionary().get_default_symbol_font()

        self.shadow_width = None
        self.border_width = None
        self.padding = None
        self.text_surface = None
        self.cursor = None
        self.background_and_border = None
        self.text_image_rect = None

        # colours from theme
        self.background_colour = None
        self.text_colour = None
        self.selected_text_colour = None
        self.selected_bg_colour = None
        self.border_colour = None
        self.disabled_background_colour = None
        self.disabled_border_colour = None
        self.disabled_text_colour = None
        self.text_cursor_colour = None
        self.padding = (0, 0)

        self.shape = 'rectangle'
        self.shape_corner_radius = None

        # input timings - I expect nobody really wants to mess with these that much
        # ideally we could populate from the os settings but that sounds like a headache
        self.key_repeat = 0.5
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_blink_delay_after_moving = 1.0
        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.4

        self.double_click_timer = self.ui_manager.get_double_click_time() + 1.0

        self.start_text_offset = 0
        self.edit_position = 0
        self._select_range = [0, 0]
        self.selection_in_progress = False

        self.cursor_on = False
        self.cursor_has_moved_recently = False
        self.text_entered = False  # Reset when enter key up or focus lost

        # restrictions on text input
        self.allowed_characters: Optional[List[str]] = None
        self.forbidden_characters: Optional[List[str]] = None
        self.length_limit: Optional[int] = None

        self.rebuild_from_changed_theme_data()

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
        if self.drawable_shape is not None:
            self.drawable_shape.text_box_layout.set_text_selection(start_select, end_select)
            self.drawable_shape.apply_active_text_changes()

    def set_text_hidden(self, is_hidden=True):
        """
        Passing in True will hide text typed into the text line, replacing it with ●
        characters and also disallow copying the text into the clipboard. It is designed
        for basic 'password box' usage.

        :param is_hidden: Can be set to True or False. Defaults to True because
                          if you are calling this you likely want a password box with no fuss.
                          Set it back to False if you want to un-hide the text (e.g.
                          for one of those 'Show my password' buttons).
        """

        self.is_text_hidden = is_hidden
        self.rebuild()

    def rebuild(self):
        """
        Rebuild whatever needs building.

        """

        display_text = self.text
        display_font = self.font
        if self.is_text_hidden:
            display_font = self.hidden_font
            # test if self.hidden_text_char is supported by font here
            # currently we can't do this
            # if self.font.get_metrics(self.hidden_text_char)[0] is None:
            #     self.hidden_text_char = '*'
            #     if self.font.get_metrics(self.hidden_text_char)[0] is None:
            #         self.hidden_text_char = '.'
            #         if self.font.get_metrics(self.hidden_text_char)[0] is None:
            #             raise ValueError('Selected font for UITextEntryLine does not contain '
            #                              '●, * or . characters used for hidden text. Please choose'
            #                              'a different font for this element')
            display_text = self.hidden_text_char*len(self.text)

        text_direction = self.font.get_direction()
        text_horiz_alignment = 'left'
        if text_direction == pygame.DIRECTION_LTR:
            text_horiz_alignment = 'left'
        elif text_direction == pygame.DIRECTION_RTL:
            text_horiz_alignment = 'right'

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_text': self.text_colour,
                              'normal_text_shadow': pygame.Color('#000000'),
                              'normal_border': self.border_colour,
                              'disabled_bg': self.disabled_background_colour,
                              'disabled_text': self.disabled_text_colour,
                              'disabled_text_shadow': pygame.Color('#000000'),
                              'disabled_border': self.disabled_border_colour,
                              'selected_text': self.selected_text_colour,
                              'selected_bg': self.selected_bg_colour,
                              'text_cursor_colour': self.text_cursor_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'font': display_font,
                              'text': display_text if len(display_text) > 0 else translate(self.placeholder_text),
                              'text_width': -1,
                              'text_horiz_alignment': text_horiz_alignment,
                              'text_vert_alignment': 'centre',
                              'text_horiz_alignment_padding': self.padding[0],
                              'text_vert_alignment_padding': self.padding[1],
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal', 'disabled'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal', 'disabled'], self.ui_manager)

        if self.drawable_shape is not None:
            self._set_image(self.drawable_shape.get_fresh_surface())
            if self.rect.width == -1 or self.rect.height == -1:
                self.set_dimensions(self.drawable_shape.containing_rect.size)

    def set_text_length_limit(self, limit: int):
        """
        Allows a character limit to be set on the text entry element. By default there is no
        limit on the number of characters that can be entered.

        :param limit: The character limit as an integer.

        """
        self.length_limit = limit

    def get_text(self) -> str:
        """
        Gets the text in the entry line element.

        :return: A string.

        """
        return self.text

    def set_text(self, text: str):
        """
        Allows the text displayed in the text entry element to be set via code. Useful for
        setting an initial or existing value that is able to be edited.

        The string to set must be valid for the text entry element for this to work.

        :param text: The text string to set.

        """
        if self.validate_text_string(text):
            within_length_limit = True
            if self.length_limit is not None and len(text) > self.length_limit:
                within_length_limit = False
            if within_length_limit:
                self.text = text
                self.edit_position = len(self.text)
                display_text = self.text
                if self.is_text_hidden:
                    display_text = self.hidden_text_char * len(self.text)
                if self.drawable_shape is not None:
                    self.drawable_shape.set_text(display_text if len(display_text) > 0
                                                 else translate(self.placeholder_text))
                    self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                    self.drawable_shape.apply_active_text_changes()
            else:
                warnings.warn("Tried to set text string that is too long on text entry element")
        else:
            warnings.warn("Tried to set text string with invalid characters on text entry element")

    def redraw(self):
        """
        Redraws the entire text entry element onto the underlying sprite image. Usually called
        when the displayed text has been edited or changed in some fashion.
        """
        if self.drawable_shape is not None:
            self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
            self.drawable_shape.redraw_all_states()

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
            self.ui_manager.set_text_input_hovered(True)

        if self.double_click_timer < self.ui_manager.get_double_click_time():
            self.double_click_timer += time_delta
        if self.selection_in_progress:
            drawable_shape_space_click = (scaled_mouse_pos[0] - self.rect.left,
                                          scaled_mouse_pos[1] - self.rect.top)
            if self.drawable_shape is not None:
                self.drawable_shape.text_box_layout.set_cursor_from_click_pos(
                    drawable_shape_space_click)
                self.drawable_shape.apply_active_text_changes()
                select_end_pos = self.drawable_shape.text_box_layout.get_cursor_index()
                new_range = [self.select_range[0], select_end_pos]

                if new_range[0] != self.select_range[0] or new_range[1] != self.select_range[1]:
                    self.select_range = [new_range[0], new_range[1]]

                    self.edit_position = self.select_range[1]
                    self.cursor_has_moved_recently = True

        if self.cursor_has_moved_recently:
            self.cursor_has_moved_recently = False
            self.cursor_blink_delay_after_moving_acc = 0.0
            self.cursor_on = True
            if self.drawable_shape is not None:
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.toggle_text_cursor()
                self.drawable_shape.apply_active_text_changes()

        if self.cursor_blink_delay_after_moving_acc > self.cursor_blink_delay_after_moving:
            if self.blink_cursor_time_acc >= self.blink_cursor_time:
                self.blink_cursor_time_acc = 0.0
                if self.cursor_on:
                    self.cursor_on = False
                    if self.drawable_shape is not None:
                        self.drawable_shape.toggle_text_cursor()
                elif self.is_focused:
                    self.cursor_on = True
                    if self.drawable_shape is not None:
                        self.drawable_shape.toggle_text_cursor()
            else:
                self.blink_cursor_time_acc += time_delta
        else:
            self.cursor_blink_delay_after_moving_acc += time_delta

    def unfocus(self):
        """
        Called when this element is no longer the current focus.
        """
        super().unfocus()
        pygame.key.set_repeat(0)
        self.select_range = [0, 0]
        self.edit_position = 0
        self.cursor_on = False
        self.text_entered = False
        if len(self.text) == 0:
            if self.drawable_shape is not None:
                self.drawable_shape.set_text(translate(self.placeholder_text))
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.apply_active_text_changes()
        self.redraw()

    def focus(self):
        """
        Called when we 'select focus' on this element. In this case it sets up the keyboard to
        repeat held key presses, useful for natural feeling keyboard input.
        """
        super().focus()
        pygame.key.set_repeat(500, 25)
        if len(self.text) == 0:
            if self.drawable_shape is not None:
                self.drawable_shape.set_text(self.text)
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.apply_active_text_changes()

    def process_event(self, event: pygame.event.Event) -> bool:
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

        initial_text_state = self.text
        if self._process_mouse_button_event(event):
            consumed_event = True
        if self.is_enabled and self.is_focused and event.type == pygame.KEYDOWN:
            if self._process_keyboard_shortcut_event(event):
                consumed_event = True
            elif self._process_action_key_event(event):
                consumed_event = True

        if self.is_enabled and self.is_focused and event.type == pygame.TEXTINPUT:
            # sometimes we don't get a keydown event for a paste shortcut on mac (?)
            key_mods = pygame.key.get_mods()
            if event.text == "v" and ((key_mods & pygame.KMOD_CTRL) or (key_mods & pygame.KMOD_META)):
                self._do_paste()
                consumed_event = True
            else:
                processed_any_char = False
                for char in event.text:
                    if self._process_entered_character(char):
                        processed_any_char = True
                consumed_event = processed_any_char

        if self.is_enabled and self.is_focused and event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.text_entered = False  # reset text input entry

        if self.text != initial_text_state:
            # old event to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_TEXT_ENTRY_CHANGED),
                          'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

            # new event
            event_data = {'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_TEXT_ENTRY_CHANGED, event_data))
        return consumed_event

    def _process_text_entry_key(self, event: pygame.event.Event) -> bool:
        consumed_event = False
        if hasattr(event, 'unicode'):
            consumed_event = self._process_entered_character(event.unicode)
        return consumed_event

    def _process_entered_character(self, character: str) -> bool:
        """
        Process key input that can be added to the text entry text.

        :param event: The event to process.

        :return: True if consumed.
        """
        processed_character = False
        within_length_limit = True
        if (self.length_limit is not None
                and (len(self.text) -
                     abs(self.select_range[0] -
                         self.select_range[1])) >= self.length_limit):
            within_length_limit = False
        if within_length_limit and self.font is not None:
            char_metrics = self.font.get_metrics(character)
            if len(char_metrics) > 0 and char_metrics[0] is not None:
                valid_character = True
                if (self.allowed_characters is not None and
                        character not in self.allowed_characters):
                    valid_character = False
                if (self.forbidden_characters is not None and
                        character in self.forbidden_characters):
                    valid_character = False
                if valid_character:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        self.text = self.text[:low_end] + character + self.text[high_end:]

                        if self.drawable_shape is not None:
                            self.drawable_shape.set_text(self.text)
                        self.edit_position = low_end + 1
                        self.select_range = [0, 0]
                    else:
                        start_str = self.text[:self.edit_position]
                        end_str = self.text[self.edit_position:]
                        self.text = start_str + character + end_str
                        display_character = character
                        if self.is_text_hidden:
                            display_character = self.hidden_text_char
                        if self.drawable_shape is not None:
                            self.drawable_shape.insert_text(display_character, self.edit_position)

                        self.edit_position += 1
                    self.cursor_has_moved_recently = True
                    processed_character = True
        return processed_character

    def _process_action_key_event(self, event: pygame.event.Event) -> bool:
        """
        Check if event is one of the keys that triggers an action like deleting, or moving
        the edit position.

        :param event: The event to check.

        :return: True if event is consumed.

        """
        consumed_event = False
        if ((event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER)
                and not self.text_entered):
            # old event - to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_TEXT_ENTRY_FINISHED),
                          'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

            # new event
            event_data = {'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_TEXT_ENTRY_FINISHED, event_data))
            consumed_event = True
            self.text_entered = True
        elif event.key == pygame.K_BACKSPACE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.delete_selected_text()
                    self.drawable_shape.apply_active_text_changes()
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.text = self.text[:low_end] + self.text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                    self.drawable_shape.apply_active_text_changes()
            elif self.edit_position > 0 and self.font is not None:
                if self.start_text_offset > 0:
                    self.start_text_offset -= self.font.get_rect(
                        self.text[self.edit_position - 1]).width
                self.text = self.text[:self.edit_position - 1] + self.text[self.edit_position:]
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.backspace_at_cursor()
                    self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                    self.drawable_shape.apply_active_text_changes()
            consumed_event = True
        elif event.key == pygame.K_DELETE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.delete_selected_text()
                    self.drawable_shape.apply_active_text_changes()
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.text = self.text[:low_end] + self.text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                    self.drawable_shape.apply_active_text_changes()
            elif self.edit_position < len(self.text):
                self.text = self.text[:self.edit_position] + self.text[self.edit_position + 1:]
                self.edit_position = self.edit_position
                self.cursor_has_moved_recently = True
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.delete_at_cursor()
                    self.drawable_shape.apply_active_text_changes()
            consumed_event = True
        elif self._process_edit_pos_move_key(event):
            consumed_event = True

        return consumed_event

    def _process_edit_pos_move_key(self, event: pygame.event.Event) -> bool:
        """
        Process an action key that is moving the cursor edit position.

        :param event: The event to process.

        :return: True if event is consumed.

        """
        consumed_event = False
        # modded versions of LEFT and RIGHT must go first otherwise the simple
        # cases will absorb the events
        if event.key == pygame.K_HOME or (event.key == pygame.K_LEFT
            and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META)
            ):
            # include case when shift held down to select everything to start
            # of current line.
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if event.mod & pygame.KMOD_SHIFT:
                    if self.edit_position == self.select_range[1]:
                        # undo selection to right, create to left
                        self.select_range = [0, self.select_range[0]]
                    else:
                        # extend left
                        self.select_range = [0, self.select_range[1]]
                else:
                    self.select_range = [0, 0]
            else:
                if event.mod & pygame.KMOD_SHIFT:
                    self.select_range = [0, self.edit_position]
                else:
                    self.select_range = [0, 0]
            self.edit_position = 0
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_END or (event.key == pygame.K_RIGHT
            and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META)
            ):
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if event.mod & pygame.KMOD_SHIFT:
                    if self.edit_position == self.select_range[0]:
                        # undo selection to left, create to right
                        self.select_range = [self.select_range[1], len(self.text)]
                    else:
                        # extend right
                        self.select_range = [self.select_range[0], len(self.text)]
                else:
                    self.select_range = [0, 0]
            else:
                if event.mod & pygame.KMOD_SHIFT:
                    self.select_range = [self.edit_position, len(self.text)]
                else:
                    self.select_range = [0, 0]
            self.edit_position = len(self.text)
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_LEFT and event.mod & pygame.KMOD_SHIFT:
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
                    self.select_range = [self.select_range[0], max(0,
                                                    self.edit_position - 1)]
            else:
                self.select_range = [max(0, self.edit_position - 1),
                                     self.edit_position]
            if self.edit_position > 0:
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_RIGHT and event.mod & pygame.KMOD_SHIFT:
            # keyboard-based selection
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                if self.edit_position == self.select_range[1]:
                    # try to extend to the right
                    self.select_range = [self.select_range[0],
                                         min(len(self.text), self.edit_position + 1)]
                elif self.edit_position == self.select_range[0]:
                    # reduce to the right
                    self.select_range = [min(len(self.text), self.edit_position + 1),
                                         self.select_range[1]]
            else:
                self.select_range = [self.edit_position, min(len(self.text),
                                                    self.edit_position + 1)]
            if self.edit_position < len(self.text):
                self.edit_position += 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_LEFT:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = min(self.select_range[0], self.select_range[1])
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            elif self.edit_position > 0:
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_RIGHT:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.edit_position = max(self.select_range[0], self.select_range[1])
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
            elif self.edit_position < len(self.text):
                self.edit_position += 1
                self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_HOME:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.select_range = [0, 0]
            self.edit_position = 0
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_END:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                self.select_range = [0, 0]
            self.edit_position = len(self.text)
            self.cursor_has_moved_recently = True
            consumed_event = True
        return consumed_event

    def _process_keyboard_shortcut_event(self, event: pygame.event.Event) -> bool:
        """
        Check if event is one of the CTRL key keyboard shortcuts.

        :param event: event to process.

        :return: True if event consumed.

        """
        consumed_event = False
        if (event.key == pygame.K_a and
                (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META) and
                not (event.mod & pygame.KMOD_ALT)):  # hopefully enable diacritic letters):
            self.select_range = [0, len(self.text)]
            self.edit_position = len(self.text)
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif (event.key == pygame.K_x and
              (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META) and
              not self.is_text_hidden and
                not (event.mod & pygame.KMOD_ALT)):  # hopefully enable diacritic letters:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                clipboard_copy(self.text[low_end:high_end])
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.delete_selected_text()
                    self.drawable_shape.apply_active_text_changes()
                self.edit_position = low_end
                self.text = self.text[:low_end] + self.text[high_end:]
                if self.drawable_shape is not None:
                    self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                    self.drawable_shape.apply_active_text_changes()
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                consumed_event = True
        elif (event.key == pygame.K_c and
              (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META) and
              not self.is_text_hidden and
                not (event.mod & pygame.KMOD_ALT)):  # hopefully enable diacritic letters:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                clipboard_copy(self.text[low_end:high_end])
                consumed_event = True
        elif self._process_paste_event(event):
            consumed_event = True
        return consumed_event

    def _process_paste_event(self, event: pygame.event.Event) -> bool:
        """
        Process a paste shortcut event. (CTRL+ V)

        :param event: The event to process.

        :return: True if the event is consumed.

        """
        consumed_event = False
        if (event.key == pygame.K_v and
                (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META) and
                not (event.mod & pygame.KMOD_ALT)):  # hopefully enable diacritic letters
            self._do_paste()
            consumed_event = True
        return consumed_event

    def _do_paste(self):
        new_text = clipboard_paste()
        if self.validate_text_string(new_text):
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                final_text = self.text[:low_end] + new_text + self.text[high_end:]
                within_length_limit = True
                if self.length_limit is not None and len(final_text) > self.length_limit:
                    within_length_limit = False
                if within_length_limit:
                    self.text = final_text
                    if self.drawable_shape is not None:
                        self.drawable_shape.text_box_layout.delete_selected_text()
                        self.drawable_shape.apply_active_text_changes()
                    display_new_text = new_text
                    if self.is_text_hidden:
                        display_new_text = self.hidden_text_char * len(new_text)
                    if self.drawable_shape is not None:
                        self.drawable_shape.insert_text(display_new_text, low_end)
                    self.edit_position = low_end + len(new_text)
                    if self.drawable_shape is not None:
                        self.drawable_shape.text_box_layout.set_cursor_position(
                            self.edit_position)
                        self.drawable_shape.apply_active_text_changes()
                    self.select_range = [0, 0]
                    self.cursor_has_moved_recently = True
            elif len(new_text) > 0:
                final_text = (self.text[:self.edit_position] +
                              new_text +
                              self.text[self.edit_position:])
                within_length_limit = True
                if self.length_limit is not None and len(final_text) > self.length_limit:
                    within_length_limit = False
                if within_length_limit:
                    self.text = final_text
                    display_new_text = new_text
                    if self.is_text_hidden:
                        display_new_text = self.hidden_text_char * len(new_text)
                    if self.drawable_shape is not None:
                        self.drawable_shape.insert_text(display_new_text, self.edit_position)
                    self.edit_position += len(new_text)
                    if self.drawable_shape is not None:
                        self.drawable_shape.text_box_layout.set_cursor_position(
                            self.edit_position)
                        self.drawable_shape.apply_active_text_changes()
                    self.cursor_has_moved_recently = True

    def _process_mouse_button_event(self, event: pygame.event.Event) -> bool:
        """
        Process a mouse button event.

        :param event: Event to process.

        :return: True if we consumed the mouse event.

        """
        consumed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:

            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.is_enabled:
                    drawable_shape_space_click = (scaled_mouse_pos[0] - self.rect.left,
                                                  scaled_mouse_pos[1] - self.rect.top)
                    if self.drawable_shape is not None:
                        self.drawable_shape.text_box_layout.set_cursor_from_click_pos(
                            drawable_shape_space_click)
                        self.edit_position = self.drawable_shape.text_box_layout.get_cursor_index()
                        self.drawable_shape.apply_active_text_changes()
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
        if (event.type == pygame.MOUSEBUTTONUP and
                event.button == pygame.BUTTON_LEFT and
                self.selection_in_progress):
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.drawable_shape is not None:
                if self.drawable_shape.collide_point(scaled_mouse_pos):
                    consumed_event = True
                    drawable_shape_space_click = (scaled_mouse_pos[0] - self.rect.left,
                                                  scaled_mouse_pos[1] - self.rect.top)
                    self.drawable_shape.text_box_layout.set_cursor_from_click_pos(
                        drawable_shape_space_click)
                    new_edit_pos = self.drawable_shape.text_box_layout.get_cursor_index()
                    if new_edit_pos != self.edit_position:
                        self.edit_position = new_edit_pos
                        self.cursor_has_moved_recently = True
                        self.select_range = [self.select_range[0], self.edit_position]
                    self.drawable_shape.apply_active_text_changes()
            self.selection_in_progress = False
        return consumed_event

    def _calculate_double_click_word_selection(self):
        """
        If we double clicked on a word in the text, select that word.

        """
        if self.edit_position != self.select_range[0]:
            return False
        index = min(self.edit_position, len(self.text) - 1)
        if index >= 0:
            char = self.text[index]
            # Check we clicked in the same place on a our second click.
            pattern = re.compile(r"[\w']+")
            if index > 0:
                while not pattern.match(char):
                    index -= 1
                    if index > 0:
                        char = self.text[index]
                    else:
                        break
                while pattern.match(char):
                    index -= 1
                    if index > 0:
                        char = self.text[index]
                    else:
                        break
            start_select_index = index + 1 if index > 0 else index
            index += 1
            if index < len(self.text):
                char = self.text[index]
                while index < len(self.text) and pattern.match(char):
                    index += 1
                    if index < len(self.text):
                        char = self.text[index]
            end_select_index = index
            self.select_range = [start_select_index, end_select_index]
            self.edit_position = end_select_index
            self.cursor_has_moved_recently = True
            self.selection_in_progress = False
            return True
        else:
            return False

    def set_allowed_characters(self, allowed_characters: Union[str, List[str]]):
        """
        Sets a whitelist of characters that will be the only ones allowed in our text entry
        element. We can either set the list directly, or request one of the already existing
        lists by a string identifier. The currently supported lists for allowed characters are:

        - 'numbers'
        - 'letters'
        - 'alpha_numeric'

        :param allowed_characters: The characters to allow, either in a list form or one of the
                                   supported string ids.

        """
        if isinstance(allowed_characters, str):
            if allowed_characters == 'numbers':
                if self.ui_manager.get_locale() in UITextEntryLine._number_character_set:
                    self.allowed_characters = UITextEntryLine._number_character_set[
                        self.ui_manager.get_locale()]
                else:
                    self.allowed_characters = UITextEntryLine._number_character_set['en']
            elif allowed_characters == 'letters':
                if self.ui_manager.get_locale() in UITextEntryLine._alphabet_characters_all:
                    self.allowed_characters = UITextEntryLine._alphabet_characters_all[
                        self.ui_manager.get_locale()]
                else:
                    self.allowed_characters = UITextEntryLine._alphabet_characters_all['en']
            elif allowed_characters == 'alpha_numeric':
                if self.ui_manager.get_locale() in UITextEntryLine._alpha_numeric_characters:
                    self.allowed_characters = UITextEntryLine._alpha_numeric_characters[
                        self.ui_manager.get_locale()]
                else:
                    self.allowed_characters = UITextEntryLine._alpha_numeric_characters['en']
            else:
                warnings.warn('Trying to set allowed characters by type string, but no match: '
                              'did you mean to use a list?')

        else:
            self.allowed_characters = allowed_characters.copy()

    def set_forbidden_characters(self, forbidden_characters: Union[str, List[str]]):
        """
        Sets a blacklist of characters that will be banned from our text entry element.
        We can either set the list directly, or request one of the already existing lists by a
        string identifier. The currently supported lists for forbidden characters are:

        - 'numbers'
        - 'forbidden_file_path'

        :param forbidden_characters: The characters to forbid, either in a list form or one of
                                     the supported string ids.

        """
        if isinstance(forbidden_characters, str):
            if forbidden_characters == 'numbers':
                if self.ui_manager.get_locale() in UITextEntryLine._number_character_set:
                    self.forbidden_characters = UITextEntryLine._number_character_set[
                        self.ui_manager.get_locale()]
                else:
                    self.forbidden_characters = UITextEntryLine._number_character_set['en']
            elif forbidden_characters == 'forbidden_file_path':
                if self.ui_manager.get_locale() in UITextEntryLine._forbidden_file_path_characters:
                    self.forbidden_characters = UITextEntryLine._forbidden_file_path_characters[
                        self.ui_manager.get_locale()]
                else:
                    self.forbidden_characters = (
                        UITextEntryLine._forbidden_file_path_characters['en'])
            else:
                warnings.warn('Trying to set forbidden characters by type string, but no match: '
                              'did you mean to use a list?')

        else:
            self.forbidden_characters = forbidden_characters.copy()

    def validate_text_string(self, text_to_validate: str) -> bool:
        """
        Checks a string of text to see if any of it's characters don't meet the requirements of
        the allowed and forbidden character sets.

        :param text_to_validate: The text string to check.

        """
        is_valid = True
        if text_to_validate is not None:
            if self.forbidden_characters is not None:
                for character in text_to_validate:
                    if character in self.forbidden_characters:
                        is_valid = False

            if is_valid and self.allowed_characters is not None:
                for character in text_to_validate:
                    if character not in self.allowed_characters:
                        is_valid = False
        else:
            is_valid = False

        return is_valid

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle']):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='padding',
                                               default_value=(2, 2),
                                               casting_func=self.tuple_extract):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='tool_tip_delay',
                                               default_value=1.0,
                                               casting_func=float):
            has_any_changed = True

        if self._check_theme_colours_changed():
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def _check_theme_colours_changed(self):
        """
        Check if any colours have changed in the theme.

        :return: colour has changed.

        """
        has_any_changed = False
        background_colour = self.ui_theme.get_colour_or_gradient('dark_bg',
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True
        border_colour = self.ui_theme.get_colour_or_gradient('normal_border',
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True
        text_colour = self.ui_theme.get_colour_or_gradient('normal_text', self.combined_element_ids)
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            has_any_changed = True
        selected_text_colour = self.ui_theme.get_colour_or_gradient('selected_text',
                                                                    self.combined_element_ids)
        if selected_text_colour != self.selected_text_colour:
            self.selected_text_colour = selected_text_colour
            has_any_changed = True
        selected_bg_colour = self.ui_theme.get_colour_or_gradient('selected_bg',
                                                                  self.combined_element_ids)
        if selected_bg_colour != self.selected_bg_colour:
            self.selected_bg_colour = selected_bg_colour
            has_any_changed = True

        disabled_background_colour = self.ui_theme.get_colour_or_gradient('disabled_dark_bg',
                                                                          self.combined_element_ids)
        if disabled_background_colour != self.disabled_background_colour:
            self.disabled_background_colour = disabled_background_colour
            has_any_changed = True

        disabled_border_colour = self.ui_theme.get_colour_or_gradient('disabled_border',
                                                                      self.combined_element_ids)
        if disabled_border_colour != self.disabled_border_colour:
            self.disabled_border_colour = disabled_border_colour
            has_any_changed = True

        disabled_text_colour = self.ui_theme.get_colour_or_gradient('disabled_text',
                                                                    self.combined_element_ids)
        if disabled_text_colour != self.disabled_text_colour:
            self.disabled_text_colour = disabled_text_colour
            has_any_changed = True

        text_cursor_colour = self.ui_theme.get_colour_or_gradient('text_cursor',
                                                                  self.combined_element_ids)
        if text_cursor_colour != self.text_cursor_colour:
            self.text_cursor_colour = text_cursor_colour
            has_any_changed = True

        return has_any_changed

    def disable(self):
        """
        Disables the element so that it is no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False

            # clear state
            self.is_focused = False
            self.selection_in_progress = False
            self.cursor_on = False
            self.cursor_has_moved_recently = False

            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state('disabled')
                self.background_and_border = self.drawable_shape.get_surface('disabled')
            self.edit_position = 0
            self.select_range = [0, 0]
            self.redraw()

    def enable(self):
        """
        Re-enables the element so we can once again interact with it.
        """
        if not self.is_enabled:
            self.is_enabled = True
            self.text_entered = False
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state('normal')
                self.background_and_border = self.drawable_shape.get_surface('normal')
            self.redraw()

    def on_locale_changed(self):
        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            self.rebuild()
        else:
            display_text = self.text
            if self.is_text_hidden:
                display_text = self.hidden_text_char * len(self.text)
            if self.drawable_shape is not None:
                self.drawable_shape.set_text(display_text if len(display_text) > 0
                                             else translate(self.placeholder_text))

    def clear(self):
        self.set_text("")
