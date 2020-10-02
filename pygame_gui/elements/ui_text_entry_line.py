import re
import warnings

from typing import Union, List, Tuple, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.utility import clipboard_paste, clipboard_copy

from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

try:
    # mouse button constants not defined in pygame 1.9.3
    assert pygame.BUTTON_LEFT == 1
    assert pygame.BUTTON_MIDDLE == 2
    assert pygame.BUTTON_RIGHT == 3
except (AttributeError, AssertionError):
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class UITextEntryLine(UIElement):
    """
    A GUI element for text entry from a keyboard, on a single line. The element supports
    the standard copy and paste keyboard shortcuts CTRL+V, CTRL+C & CTRL+X as well as CTRL+A.

    There are methods that allow the entry element to restrict the characters that can be input
    into the text box

    The height of the text entry line element will be determined by the font used rather than
    the standard method for UIElements of just using the height of the input rectangle.

    :param relative_rect: A rectangle describing the position and width of the text entry element.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the
                      root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    _number_character_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    # excluding these characters won't ensure that user entered text is a valid filename but they
    # can help reduce the problems that input will leave you with.
    _forbidden_file_path_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0', '.']

    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager, container,
                         starting_height=1, layer_thickness=1,
                         anchors=anchors, visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='text_entry_line')

        self.text = ""

        # theme font
        self.font = None

        self.shadow_width = None
        self.border_width = None
        self.padding = None
        self.text_surface = None
        self.cursor = None
        self.background_and_border = None
        self.text_image_rect = None
        # self.text_image = None

        # colours from theme
        self.background_colour = None
        self.text_colour = None
        self.selected_text_colour = None
        self.selected_bg_colour = None
        self.border_colour = None
        self.disabled_background_colour = None
        self.disabled_border_colour = None
        self.disabled_text_colour = None
        self.padding = (0, 0)

        self.drawable_shape = None
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
        self.select_range = [0, 0]
        self.selection_in_progress = False

        self.cursor_on = False
        self.cursor_has_moved_recently = False
        self.should_redraw = False

        # restrictions on text input
        self.allowed_characters = None
        self.forbidden_characters = None
        self.length_limit = None

        self.rebuild_from_changed_theme_data()

    def rebuild(self):
        """
        Rebuild whatever needs building.

        """

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_text': self.text_colour,
                              'normal_border': self.border_colour,
                              'disabled_bg': self.disabled_background_colour,
                              'disabled_text': self.disabled_text_colour,
                              'disabled_border': self.disabled_border_colour,
                              'selected_text': self.selected_text_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'font': self.font,
                              'text': self.text,
                              'text_width': -1,
                              'text_horiz_alignment': 'left',
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

        self.set_image(self.drawable_shape.get_fresh_surface())

        # if self.text_image is None:
        #     self.text_image = pygame.surface.Surface(self.text_image_rect.size,
        #                                              flags=pygame.SRCALPHA,
        #                                              depth=32)
        #
        # if isinstance(self.background_colour, ColourGradient):
        #     self.text_image.fill(pygame.Color("#FFFFFFFF"))
        #     self.background_colour.apply_gradient_to_surface(self.text_image)
        # else:
        #     self.text_image.fill(self.background_colour)
        #
        # self.set_image(self.background_and_border.copy())
        #
        # # TODO: get line spacing from theme?
        # line_spacing = 1.2
        # line_height = self.font.size * line_spacing
        # self.cursor = pygame.Rect((self.text_image_rect.x +
        #                            self.padding[0] - self.start_text_offset,
        #                            self.text_image_rect.y +
        #                            self.padding[1]), (1, line_height))
        #
        # # setup for drawing
        # self.redraw()

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
                self.edit_position = 0
                self.drawable_shape.set_text(self.text)
                self.should_redraw = True
            else:
                warnings.warn("Tried to set text string that is too long on text entry element")
        else:
            warnings.warn("Tried to set text string with invalid characters on text entry element")

    def redraw(self):
        """
        Redraws the entire text entry element onto the underlying sprite image. Usually called
        when the displayed text has been edited or changed in some fashion.
        """
        self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
        self.drawable_shape.redraw_all_states()
    #     if self.is_enabled:
    #         if isinstance(self.background_colour, ColourGradient):
    #             self.text_image.fill(pygame.Color("#FFFFFFFF"))
    #             self.background_colour.apply_gradient_to_surface(self.text_image)
    #         else:
    #             self.text_image.fill(self.background_colour)
    #     else:
    #         if isinstance(self.disabled_background_colour, ColourGradient):
    #             self.text_image.fill(pygame.Color("#FFFFFFFF"))
    #             self.disabled_background_colour.apply_gradient_to_surface(self.text_image)
    #         else:
    #             self.text_image.fill(self.disabled_background_colour)
    #
    #     if self.select_range[0] == self.select_range[1]:
    #         self._redraw_unselected_text()
    #     else:
    #         self._redraw_selected_text()
    #
    #     text_clip_width = (self.rect.width -
    #                        (self.padding[0] * 2) -
    #                        (self.shape_corner_radius * 2) -
    #                        (self.border_width * 2) -
    #                        (self.shadow_width * 2))
    #
    #     width_to_edit_pos = self.font.get_rect(self.text[:self.edit_position]).width
    #
    #     if self.start_text_offset > width_to_edit_pos:
    #         self.start_text_offset = width_to_edit_pos
    #     elif width_to_edit_pos > (self.start_text_offset + text_clip_width):
    #         self.start_text_offset = max(0, width_to_edit_pos - text_clip_width)
    #     elif width_to_edit_pos == 0:
    #         self.start_text_offset = 0
    #
    #     if len(self.text) > 0:
    #         basic_blit(self.text_image,
    #                    self.text_surface,
    #                    self.padding,
    #                    pygame.Rect((self.start_text_offset, 0),
    #                                (text_clip_width,
    #                                 (self.rect.height -
    #                                  (self.padding[1] * 2) -
    #                                  (self.border_width * 2) -
    #                                  (self.shadow_width * 2)))))
    #
    #     self.redraw_cursor()

    # def _redraw_unselected_text(self):
    #     """
    #     Redraw text where none has been selected by a user.
    #     """
    #     self.text_surface = render_white_text_alpha_black_bg(font=self.font,
    #                                                          text=self.text)
    #     if self.is_enabled:
    #         if isinstance(self.text_colour, ColourGradient):
    #             self.text_colour.apply_gradient_to_surface(self.text_surface)
    #         else:
    #             apply_colour_to_surface(self.text_colour, self.text_surface)
    #     else:
    #         if isinstance(self.disabled_text_colour, ColourGradient):
    #             self.disabled_text_colour.apply_gradient_to_surface(self.text_surface)
    #         else:
    #             apply_colour_to_surface(self.disabled_text_colour, self.text_surface)
    #
    # def _redraw_selected_text(self):
    #     """
    #     Redraw text where some has been selected by a user.
    #     """
    #     low_end = min(self.select_range[0], self.select_range[1])
    #     high_end = max(self.select_range[0], self.select_range[1])
    #     pre_select_area_text = self.text[:low_end]
    #     select_area_text = self.text[low_end:high_end]
    #     post_select_area_text = self.text[high_end:]
    #     pre_select_area_surface = None
    #     post_select_area_surface = None
    #
    #     overall_size = self.font.get_rect(self.text).size
    #     advances = [letter_metrics[4] for letter_metrics in self.font.get_metrics(self.text)]
    #     pre_select_width = sum(advances[:low_end])
    #     select_area_width = sum(advances[low_end:high_end])
    #
    #     if len(pre_select_area_text) > 0:
    #         pre_select_area_surface = self._draw_text_with_grad_or_col(pre_select_area_text,
    #                                                                    self.text_colour)
    #
    #     if isinstance(self.selected_bg_colour, ColourGradient):
    #         select_area_surface = pygame.surface.Surface((select_area_width,
    #                                                       overall_size[1]),
    #                                                      flags=pygame.SRCALPHA,
    #                                                      depth=32)
    #         select_area_surface.fill(pygame.Color('#FFFFFFFF'))
    #         self.selected_bg_colour.apply_gradient_to_surface(select_area_surface)
    #
    #         alpha_text = self._draw_text_with_grad_or_col(select_area_text,
    #                                                       self.selected_text_colour)
    #
    #         basic_blit(select_area_surface, alpha_text, (0, 0))
    #     else:
    #         if isinstance(self.selected_text_colour, ColourGradient):
    #             select_area_surface = pygame.surface.Surface((select_area_width,
    #                                                           overall_size[1]),
    #                                                          flags=pygame.SRCALPHA,
    #                                                          depth=32)
    #             select_area_surface.fill(self.selected_bg_colour)
    #
    #             alpha_text = render_white_text_alpha_black_bg(font=self.font,
    #                                                           text=select_area_text)
    #             self.selected_text_colour.apply_gradient_to_surface(alpha_text)
    #             basic_blit(select_area_surface, alpha_text, (0, 0))
    #
    #         else:
    #             select_area_surface, _ = self.font.render(select_area_text,
    #                                                       self.selected_text_colour,
    #                                                       self.selected_bg_colour)
    #             select_area_surface = select_area_surface.convert_alpha()
    #     if len(post_select_area_text) > 0:
    #         post_select_area_surface = self._draw_text_with_grad_or_col(post_select_area_text,
    #                                                                     self.text_colour)
    #
    #     self.text_surface = pygame.surface.Surface(overall_size,
    #                                                flags=pygame.SRCALPHA,
    #                                                depth=32)
    #
    #     if isinstance(self.background_colour, ColourGradient):
    #         self.text_image.fill(pygame.Color("#FFFFFFFF"))
    #         self.background_colour.apply_gradient_to_surface(self.text_image)
    #     else:
    #         self.text_image.fill(self.background_colour)
    #
    #     if pre_select_area_surface is not None:
    #         basic_blit(self.text_surface, pre_select_area_surface, (0, 0))
    #
    #     basic_blit(self.text_surface, select_area_surface, (pre_select_width, 0))
    #
    #     if post_select_area_surface is not None:
    #         basic_blit(self.text_surface, post_select_area_surface,
    #                    (pre_select_width + select_area_width, 0))
    #
    # def _draw_text_with_grad_or_col(self,
    #                                 text: str,
    #                                 col_or_grad: Union[ColourGradient,
    #                                                    pygame.Color]) -> pygame.surface.Surface:
    #     """
    #     Draw text to a surface using either a colour or gradient.
    #
    #     :param text: The text to render.
    #     :param col_or_grad: A colour or a colour gradient.
    #
    #     :return: A surface with the text on.
    #
    #     """
    #     text_surface = render_white_text_alpha_black_bg(font=self.font,
    #                                                     text=text)
    #     if isinstance(col_or_grad, ColourGradient):
    #         col_or_grad.apply_gradient_to_surface(text_surface)
    #     else:
    #         apply_colour_to_surface(col_or_grad, text_surface)
    #     return text_surface
    #
    # def redraw_cursor(self):
    #     """
    #     Redraws only the blinking edit cursor. This allows us to blink the cursor on and off
    #     without spending time redrawing all the text.
    #     """
    #     new_image = self.background_and_border.copy()
    #     basic_blit(new_image, self.text_image, self.text_image_rect)
    #     if self.cursor_on and self.is_enabled:
    #         cursor_len_str = self.text[:self.edit_position]
    #         cursor_size = self.font.get_rect(cursor_len_str).size
    #         self.cursor.x = (cursor_size[0] + self.text_image_rect.x +
    #                          self.padding[0] - self.start_text_offset)
    #
    #         if not isinstance(self.text_colour, ColourGradient):
    #             pygame.draw.rect(new_image, self.text_colour, self.cursor)
    #         else:
    #             cursor_surface = pygame.surface.Surface(self.cursor.size,
    #                                                     flags=pygame.SRCALPHA, depth=32)
    #             cursor_surface.fill(pygame.Color('#FFFFFFFF'))
    #             self.text_colour.apply_gradient_to_surface(cursor_surface)
    #             basic_blit(new_image, cursor_surface, self.cursor)
    #
    #     self.set_image(new_image)

    def update(self, time_delta: float):
        """
        Called every update loop of our UI Manager. Largely handles text drag selection and
        making sure our edit cursor blinks on and off.

        :param time_delta: The time in seconds between this update method call and the previous one.

        """
        super().update(time_delta)

        if not self.alive():
            return
        if self.double_click_timer < self.ui_manager.get_double_click_time():
            self.double_click_timer += time_delta
        if self.selection_in_progress:
            mouse_x, _ = self.ui_manager.get_mouse_position()
            select_end_pos = self.find_edit_position_from_pixel_pos(self.start_text_offset +
                                                                    mouse_x)
            new_range = [self.select_range[0], select_end_pos]

            if new_range[0] != self.select_range[0] or new_range[1] != self.select_range[1]:
                self.select_range[0] = new_range[0]
                self.select_range[1] = new_range[1]

                self.edit_position = self.select_range[1]
                self.cursor_has_moved_recently = True

        if self.cursor_has_moved_recently:
            self.cursor_has_moved_recently = False
            self.cursor_blink_delay_after_moving_acc = 0.0
            self.cursor_on = True

            start_select = min(self.select_range[0], self.select_range[1])
            end_select = max(self.select_range[0], self.select_range[1])
            self.drawable_shape.text_box_layout.set_text_selection(start_select, end_select)
            self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
            self.drawable_shape.toggle_text_cursor()

        if self.should_redraw:
            self.should_redraw = False
            self.redraw()

        if self.cursor_blink_delay_after_moving_acc > self.cursor_blink_delay_after_moving:
            if self.blink_cursor_time_acc >= self.blink_cursor_time:
                self.blink_cursor_time_acc = 0.0
                if self.cursor_on:
                    self.cursor_on = False
                    self.drawable_shape.toggle_text_cursor()
                elif self.is_focused:
                    self.cursor_on = True
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
        self.redraw()

    def focus(self):
        """
        Called when we 'select focus' on this element. In this case it sets up the keyboard to
        repeat held key presses, useful for natural feeling keyboard input.
        """
        super().focus()
        pygame.key.set_repeat(500, 25)
        self.redraw()

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
            elif self._process_text_entry_key(event):
                consumed_event = True

        if self.text != initial_text_state:
            event_data = {'user_type': UI_TEXT_ENTRY_CHANGED,
                          'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
        return consumed_event

    def _process_text_entry_key(self, event: pygame.event.Event) -> bool:
        """
        Process key input that can be added to the text entry text.

        :param event: The event to process.

        :return: True if consumed.
        """
        consumed_event = False
        within_length_limit = True
        if (self.length_limit is not None
                and (len(self.text) -
                     abs(self.select_range[0] -
                         self.select_range[1])) >= self.length_limit):
            within_length_limit = False
        if within_length_limit:
            character = event.unicode
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

                        self.edit_position = low_end + 1
                        self.select_range = [0, 0]
                    else:
                        start_str = self.text[:self.edit_position]
                        end_str = self.text[self.edit_position:]
                        self.text = start_str + character + end_str
                        self.drawable_shape.text_box_layout.insert_text(character, self.edit_position)

                        self.edit_position += 1
                    self.cursor_has_moved_recently = True
                    consumed_event = True
        return consumed_event

    def _process_action_key_event(self, event: pygame.event.Event) -> bool:
        """
        Check if event is one of the keys that triggers an action like deleting, or moving
        the edit position.

        :param event: The event to check.

        :return: True if event is consumed.

        """
        consumed_event = False
        if event.key == pygame.K_RETURN:
            event_data = {'user_type': UI_TEXT_ENTRY_FINISHED,
                          'text': self.text,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            consumed_event = True
        elif event.key == pygame.K_BACKSPACE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.text = self.text[:low_end] + self.text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.text_box_layout.delete_selected_text()
            elif self.edit_position > 0:
                if self.start_text_offset > 0:
                    self.start_text_offset -= self.font.get_rect(
                        self.text[self.edit_position - 1]).width
                self.text = self.text[:self.edit_position - 1] + self.text[self.edit_position:]
                self.edit_position -= 1
                self.cursor_has_moved_recently = True
                self.drawable_shape.text_box_layout.backspace_at_cursor()
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
            consumed_event = True
        elif event.key == pygame.K_DELETE:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                self.text = self.text[:low_end] + self.text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.cursor_has_moved_recently = True
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.text_box_layout.delete_selected_text()
            elif self.edit_position < len(self.text):
                self.text = self.text[:self.edit_position] + self.text[self.edit_position + 1:]
                self.edit_position = self.edit_position
                self.cursor_has_moved_recently = True
                self.drawable_shape.text_box_layout.delete_at_cursor()
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
        if event.key == pygame.K_LEFT:
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
        return consumed_event

    def _process_keyboard_shortcut_event(self, event: pygame.event.Event) -> bool:
        """
        Check if event is one of the CTRL key keyboard shortcuts.

        :param event: event to process.

        :return: True if event consumed.

        """
        consumed_event = False
        if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
            self.select_range = [0, len(self.text)]
            self.edit_position = len(self.text)
            self.cursor_has_moved_recently = True
            consumed_event = True
        elif event.key == pygame.K_x and event.mod & pygame.KMOD_CTRL:
            if abs(self.select_range[0] - self.select_range[1]) > 0:
                low_end = min(self.select_range[0], self.select_range[1])
                high_end = max(self.select_range[0], self.select_range[1])
                clipboard_copy(self.text[low_end:high_end])
                self.text = self.text[:low_end] + self.text[high_end:]
                self.edit_position = low_end
                self.select_range = [0, 0]
                self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                self.drawable_shape.text_box_layout.delete_selected_text()
                self.cursor_has_moved_recently = True
                consumed_event = True
        elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
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
        if event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
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
                        self.drawable_shape.text_box_layout.delete_selected_text()
                        self.drawable_shape.text_box_layout.insert_text(new_text, low_end)
                        self.edit_position = low_end + len(new_text)
                        self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
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
                        self.drawable_shape.text_box_layout.insert_text(new_text, self.edit_position)
                        self.edit_position += len(new_text)
                        self.drawable_shape.text_box_layout.set_cursor_position(self.edit_position)
                        self.cursor_has_moved_recently = True
                consumed_event = True
        return consumed_event

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
                    pixel_x_pos = self.start_text_offset + scaled_mouse_pos[0]
                    self.edit_position = self.find_edit_position_from_pixel_pos(pixel_x_pos)

                    double_clicking = False
                    if self.double_click_timer < self.ui_manager.get_double_click_time():
                        if self._calculate_double_click_word_selection():
                            double_clicking = True

                    if not double_clicking:
                        self.select_range[0] = self.edit_position
                        self.select_range[1] = self.edit_position
                        self.cursor_has_moved_recently = True
                        self.selection_in_progress = True
                        self.double_click_timer = 0.0

                consumed_event = True
        if (event.type == pygame.MOUSEBUTTONUP and
                event.button == pygame.BUTTON_LEFT and
                self.selection_in_progress):
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.drawable_shape.collide_point(scaled_mouse_pos):
                consumed_event = True
                pixel_x_pos = self.start_text_offset + scaled_mouse_pos[0]
                new_edit_pos = self.find_edit_position_from_pixel_pos(pixel_x_pos)
                if new_edit_pos != self.edit_position:
                    self.edit_position = new_edit_pos
                    self.cursor_has_moved_recently = True
                    self.select_range[1] = self.edit_position
            self.selection_in_progress = False
        return consumed_event

    def _calculate_double_click_word_selection(self):
        """
        If we double clicked on a word in the text, select that word.

        """
        if self.edit_position != self.select_range[0]:
            return False
        index = min(self.edit_position, len(self.text) - 1)
        if index > 0:
            char = self.text[index]
            # Check we clicked in the same place on a our second click.
            pattern = re.compile(r"[\w']+")
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
            char = self.text[index]
            while index < len(self.text) and pattern.match(char):
                index += 1
                if index < len(self.text):
                    char = self.text[index]
            end_select_index = index

            self.select_range[0] = start_select_index
            self.select_range[1] = end_select_index
            self.edit_position = end_select_index
            self.cursor_has_moved_recently = True
            self.selection_in_progress = False
            return True
        else:
            return False

    def find_edit_position_from_pixel_pos(self, pixel_pos: int) -> int:
        """
        Locates the correct position to move the edit cursor to, when reacting to a mouse click
        inside the text entry element.

        :param pixel_pos: The x position of our click after being adjusted for text in our box
                          scrolling off-screen.

        """
        start_pos = (self.rect.x + self.border_width + self.shadow_width +
                     self.shape_corner_radius + self.padding[0])
        acc_pos = start_pos
        index = 0
        for char in self.text:
            x_width = self.font.get_rect(char).width

            if acc_pos + (x_width/2) > pixel_pos:
                break

            index += 1
            acc_pos += x_width
        return index

    def set_allowed_characters(self, allowed_characters: Union[str, List[str]]):
        """
        Sets a whitelist of characters that will be the only ones allowed in our text entry
        element. We can either set the list directly, or request one of the already existing
        lists by a string identifier. The currently supported lists for allowed characters are:

        - 'numbers'

        :param allowed_characters: The characters to allow, either in a list form or one of the
                                   supported string ids.

        """
        if isinstance(allowed_characters, str):
            if allowed_characters == 'numbers':
                self.allowed_characters = UITextEntryLine._number_character_set
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
                self.forbidden_characters = UITextEntryLine._number_character_set
            elif forbidden_characters == 'forbidden_file_path':
                self.forbidden_characters = UITextEntryLine._forbidden_file_path_characters
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
        if self.forbidden_characters is not None:
            for character in text_to_validate:
                if character in self.forbidden_characters:
                    is_valid = False

        if is_valid and self.allowed_characters is not None:
            for character in text_to_validate:
                if character not in self.allowed_characters:
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

        def tuple_extract(str_data: str) -> Tuple[int, int]:
            return int(str_data.split(',')[0]), int(str_data.split(',')[1])

        if self._check_misc_theme_data_changed(attribute_name='padding',
                                               default_value=(2, 2),
                                               casting_func=tuple_extract):
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

        return has_any_changed

    # def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
    #                                            Tuple[int, int],
    #                                            Tuple[float, float]]):
    #     """
    #     Will allow us to change the width of the text entry line, but not it's height which is
    #     determined by the height of the font.
    #
    #     :param dimensions: The dimensions to set. Only the first, the width, will actually be used.
    #
    #     """
    #     corrected_dimensions = [int(dimensions[0]), int(dimensions[1])]
    #     # TODO: get line spacing from theme?
    #     line_spacing = 1.2
    #     line_height = self.font.size * line_spacing
    #     corrected_dimensions[1] = int(line_height + (2 * self.padding[1]) +
    #                                   (2 * self.border_width) + (2 * self.shadow_width))
    #     super().set_dimensions((corrected_dimensions[0], corrected_dimensions[1]))
    #
    #     self.text_image_rect = pygame.Rect((self.border_width +
    #                                         self.shadow_width +
    #                                         self.shape_corner_radius,
    #                                         self.border_width +
    #                                         self.shadow_width),
    #                                        (self.relative_rect.width -
    #                                         (self.border_width * 2) -
    #                                         (self.shadow_width * 2) -
    #                                         (2 * self.shape_corner_radius),
    #                                         self.relative_rect.height -
    #                                         (self.border_width * 2) -
    #                                         (self.shadow_width * 2)))
    #
    #     if self.drawable_shape is not None:
    #         self.background_and_border = self.drawable_shape.get_fresh_surface()
    #         self.text_image = pygame.surface.Surface(self.text_image_rect.size,
    #                                                  flags=pygame.SRCALPHA,
    #                                                  depth=32)
    #         self.redraw()

    def disable(self):
        """
        Disables the button so that it is no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False

            # clear state
            self.is_focused = False
            self.selection_in_progress = False
            self.cursor_on = False
            self.cursor_has_moved_recently = False

            self.drawable_shape.set_active_state('disabled')
            self.background_and_border = self.drawable_shape.get_surface('disabled')
            self.edit_position = 0
            self.select_range = [0, 0]
            self.redraw()

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        if not self.is_enabled:
            self.is_enabled = True
            self.drawable_shape.set_active_state('normal')
            self.background_and_border = self.drawable_shape.get_surface('normal')
            self.redraw()
