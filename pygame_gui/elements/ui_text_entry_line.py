import pygame
import re
import warnings
from typing import Union, List

import pygame_gui
from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.utility import clipboard_paste, clipboard_copy
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.ui_appearance_theme import ColourGradient


class UITextEntryLine(UIElement):
    """
    A GUI element for text entry from a keyboard, on a single line. The element supports the standard
    copy and paste keyboard shortcuts CTRL+V, CTRL+C & CTRL+X as well as CTRL+A.

    There are methods that allow the entry element to restrict the characters that can be input into the text box

    The height of the text entry line element will be determined by the font used rather than the standard method
    for UIElements of just using the height of the input rectangle.

    :param relative_rect: A rectangle describing the position and width of the text entry element.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """

    _number_character_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    # excluding these characters won't ensure that user entered text is a valid filename but they can help
    # reduce the problems that input will leave you with.
    _forbidden_file_path_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0', '.']

    def __init__(self, relative_rect: pygame.Rect,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='text_entry_line')
        super().__init__(relative_rect, manager, container,
                         starting_height=1, layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids)
        self.selected = False

        self.text = ""

        # theme font
        self.font = None

        self.shadow_width = None
        self.border_width = None
        self.horiz_line_padding = None
        self.vert_line_padding = None
        self.text_surface = None
        self.cursor = None
        self.background_and_border = None
        self.text_image_rect = None
        self.text_image = None

        # colours from theme
        self.background_colour = None
        self.text_colour = None
        self.selected_text_colour = None
        self.selected_bg_colour = None
        self.border_colour = None
        self.padding = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        # input timings - I expect nobody really wants to mess with these that much
        # ideally we could populate from the os settings but that sounds like a headache
        self.key_repeat = 0.5
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_blink_delay_after_moving = 1.0
        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.4
        self.double_click_select_time = 0.4
        self.double_click_select_time_acc = 0.0

        self.start_text_offset = 0
        self.edit_position = 0
        self.select_range = [0, 0]
        self.selection_in_progress = False

        self.cursor_on = False
        self.cursor_has_moved_recently = False
        self.double_click_started = False

        # restrictions on text input
        self.allowed_characters = None
        self.forbidden_characters = None
        self.length_limit = None

        self.rebuild_from_changed_theme_data()

    def rebuild(self):
        """
        Rebuild whatever needs building.

        """
        line_height = self.font.size(' ')[1]

        self.relative_rect.height = (line_height + (2 * self.vert_line_padding) +
                                     (2 * self.border_width) + (2 * self.shadow_width))
        self.rect.height = self.relative_rect.height

        self.text_image_rect = pygame.Rect((self.border_width + self.shadow_width + self.shape_corner_radius,
                                            self.border_width + self.shadow_width),
                                           (self.rect.width - (self.border_width * 2) - (self.shadow_width * 2) -
                                            (2 * self.shape_corner_radius),
                                            self.rect.height - (self.border_width * 2) - (self.shadow_width * 2)))

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.background_and_border = self.drawable_shape.get_surface('normal')

        self.text_image = pygame.Surface(self.text_image_rect.size, flags=pygame.SRCALPHA, depth=32)
        if type(self.background_colour) == ColourGradient:
            self.text_image.fill(pygame.Color("#FFFFFFFF"))
            self.background_colour.apply_gradient_to_surface(self.text_image)
        else:
            self.text_image.fill(self.background_colour)

        self.image = self.background_and_border.copy()

        self.cursor = pygame.Rect((self.text_image_rect.x +
                                   self.horiz_line_padding - self.start_text_offset,
                                   self.text_image_rect.y +
                                   self.vert_line_padding), (1, line_height))

        # setup for drawing
        self.redraw()

    def set_text_length_limit(self, limit: int):
        """
        Allows a character limit to be set on the text entry element. By default there is no limit on the number
        of characters that can be entered.

        :param limit: The character limit as an integer.
        """
        self.length_limit = limit

    def get_text(self) -> str:
        """
        Gets the text in the entry line element.

        :return: A string .
        """
        return self.text

    def set_text(self, text: str):
        """
        Allows the text displayed in the text entry element to be set via code. Useful for setting an initial or
        existing value that is able to be edited.

        The string to set must be valid for the text entry element for this to work.

        :param text: The text string to set.
        """
        if self.validate_text_string(text):
            within_length_limit = True
            if self.length_limit is not None:
                if len(text) > self.length_limit:
                    within_length_limit = False
            if within_length_limit:
                self.text = text
                self.edit_position = len(self.text)
                self.cursor_has_moved_recently = True
            else:
                warnings.warn("Tried to set text string that is too long on text entry element")
        else:
            warnings.warn("Tried to set text string with invalid characters on text entry element")

    def redraw(self):
        """
        Redraws the entire text entry element onto the underlying sprite image. Usually called when the displayed text
        has been edited or changed in some fashion.
        """
        if type(self.background_colour) == ColourGradient:
            self.text_image.fill(pygame.Color("#FFFFFFFF"))
            self.background_colour.apply_gradient_to_surface(self.text_image)
        else:
            self.text_image.fill(self.background_colour)
        if self.select_range[0] != self.select_range[1]:
            low_end = min(self.select_range[0], self.select_range[1])
            high_end = max(self.select_range[0], self.select_range[1])
            pre_select_area_text = self.text[:low_end]
            select_area_text = self.text[low_end:high_end]
            post_select_area_text = self.text[high_end:]

            pre_select_area_surface = None
            post_select_area_surface = None

            if len(pre_select_area_text) > 0:
                if type(self.text_colour) != ColourGradient:
                    pre_select_area_surface = self.font.render(pre_select_area_text, True, self.text_colour)
                else:
                    pre_select_area_surface = self.font.render(pre_select_area_text, True, pygame.Color('#FFFFFFFF'))
                    self.text_colour.apply_gradient_to_surface(pre_select_area_surface)
                width_pre = pre_select_area_surface.get_rect().width
            else:
                width_pre = 0

            if type(self.selected_bg_colour) == ColourGradient:
                select_size = self.font.size(select_area_text)
                select_area_surface = pygame.Surface(select_size, flags=pygame.SRCALPHA, depth=32)
                select_area_surface.fill(pygame.Color('#FFFFFFFF'))
                self.selected_bg_colour.apply_gradient_to_surface(select_area_surface)
                if type(self.selected_text_colour) != ColourGradient:
                    alpha_text = self.font.render(select_area_text, True, self.selected_text_colour)
                else:
                    alpha_text = self.font.render(select_area_text, True, pygame.Color('#FFFFFFFF'))
                    self.selected_text_colour.apply_gradient_to_surface(alpha_text)
                select_area_surface.blit(alpha_text, (0, 0))
            else:
                if type(self.selected_text_colour) != ColourGradient:
                    select_area_surface = self.font.render(select_area_text, True,
                                                           self.selected_text_colour, self.selected_bg_colour)
                else:
                    select_size = self.font.size(select_area_text)
                    select_area_surface = pygame.Surface(select_size, flags=pygame.SRCALPHA, depth=32)
                    select_area_surface.fill(self.selected_bg_colour)

                    alpha_text = self.font.render(select_area_text, True, pygame.Color('#FFFFFFFF'))
                    self.selected_text_colour.apply_gradient_to_surface(alpha_text)
                    select_area_surface.blit(alpha_text, (0, 0))

            if len(post_select_area_text) > 0:
                if type(self.text_colour) != ColourGradient:
                    post_select_area_surface = self.font.render(post_select_area_text, True, self.text_colour)
                else:
                    post_select_area_surface = self.font.render(post_select_area_text, True, pygame.Color('#FFFFFFFF'))
                    self.text_colour.apply_gradient_to_surface(post_select_area_surface)
                width_post = post_select_area_surface.get_rect().width
            else:
                width_post = 0

            text_height = select_area_surface.get_rect().height
            width_select = select_area_surface.get_rect().width

            self.text_surface = pygame.Surface((width_pre + width_select + width_post, text_height),
                                               flags=pygame.SRCALPHA, depth=32)
            if type(self.background_colour) == ColourGradient:
                self.text_image.fill(pygame.Color("#FFFFFFFF"))
                self.background_colour.apply_gradient_to_surface(self.text_image)
            else:
                self.text_image.fill(self.background_colour)
            if pre_select_area_surface is not None:
                self.text_surface.blit(pre_select_area_surface, (0, 0))
            self.text_surface.blit(select_area_surface, (width_pre, 0))
            if post_select_area_surface is not None:
                self.text_surface.blit(post_select_area_surface, (width_pre+width_select, 0))
        else:
            if type(self.text_colour) != ColourGradient:
                self.text_surface = self.font.render(self.text, True, self.text_colour)
            else:
                self.text_surface = self.font.render(self.text, True, pygame.Color('#FFFFFFFF'))
                self.text_colour.apply_gradient_to_surface(self.text_surface)

        text_clip_width = (self.rect.width - (self.horiz_line_padding * 2) - (self.shape_corner_radius * 2) -
                           (self.border_width * 2) - (self.shadow_width * 2))
        text_clip_height = (self.rect.height - (self.vert_line_padding * 2) -
                            (self.border_width * 2) - (self.shadow_width * 2))
        text_surface_clip = pygame.Rect((0,
                                         0),
                                        (text_clip_width,
                                         text_clip_height))

        edit_pos_str = self.text[:self.edit_position]
        width_to_edit_pos = self.font.size(edit_pos_str)[0]

        if self.start_text_offset > width_to_edit_pos:
            total_width_minus_visible = width_to_edit_pos
            self.start_text_offset = total_width_minus_visible
        elif width_to_edit_pos > (self.start_text_offset + text_clip_width):
            total_width_minus_visible = max(0, width_to_edit_pos - text_clip_width)
            self.start_text_offset = total_width_minus_visible
        elif width_to_edit_pos == 0:
            self.start_text_offset = 0
        else:
            pass

        text_surface_clip.x += self.start_text_offset

        if len(self.text) > 0:
            self.text_image.blit(self.text_surface,
                                 (self.horiz_line_padding,
                                  self.vert_line_padding),
                                 text_surface_clip)

        self.redraw_cursor()

    def redraw_cursor(self):
        """
        Redraws only the blinking edit cursor. This allows us to blink the cursor on and off without spending time
        redrawing all the text.
        """
        self.image = self.background_and_border.copy()
        self.image.blit(self.text_image, self.text_image_rect)
        if self.cursor_on:
            cursor_len_str = self.text[:self.edit_position]
            cursor_size = self.font.size(cursor_len_str)
            self.cursor.x = (cursor_size[0] + self.text_image_rect.x +
                             self.horiz_line_padding - self.start_text_offset)

            if type(self.text_colour) != ColourGradient:
                pygame.draw.rect(self.image, self.text_colour, self.cursor)
            else:
                cursor_surface = pygame.Surface(self.cursor.size)
                cursor_surface.fill(pygame.Color('#FFFFFFFF'))
                self.text_colour.apply_gradient_to_surface(cursor_surface)
                self.image.blit(cursor_surface, self.cursor)

    def update(self, time_delta: float):
        """
        Called every update loop of our UI Manager. Largely handles text drag selection and making sure our
        edit cursor blinks on and off.

        :param time_delta: The time in seconds between this update method call and the previous one.
        :return:
        """
        if self.alive():
            if self.double_click_started and self.double_click_select_time_acc < self.double_click_select_time:
                self.double_click_select_time_acc += time_delta
            if self.selection_in_progress:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                select_end_pos = self.find_edit_position_from_pixel_pos(self.start_text_offset + mouse_x)
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
                self.redraw()

            if self.cursor_blink_delay_after_moving_acc > self.cursor_blink_delay_after_moving:
                if self.blink_cursor_time_acc >= self.blink_cursor_time:
                    self.blink_cursor_time_acc = 0.0
                    if self.cursor_on:
                        self.cursor_on = False
                        self.redraw_cursor()
                    elif self.selected:
                        self.cursor_on = True
                        self.redraw_cursor()
                else:
                    self.blink_cursor_time_acc += time_delta
            else:
                self.cursor_blink_delay_after_moving_acc += time_delta

    def unselect(self):
        """
        Called when this element is no longer the current focus.
        """
        self.selected = False
        pygame.key.set_repeat()
        self.select_range = [0, 0]
        self.redraw()

    def select(self):
        """
        Called when we 'select focus' on this element. In this case it sets up the keyboard to repeat held key presses,
        useful for natural feeling keyboard input.
        """
        self.selected = True
        pygame.key.set_repeat(500, 25)
        self.redraw()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Allows the text entry box to react to input events, which is it's primary function. The entry element reacts to
        various types of mouse clicks (double click selecting words, drag select), keyboard combos (CTRL+C, CTRL+V,
        CTRL+X, CTRL+A), individual editing keys (Backspace, Delete, Left & Right arrows) and other keys for inputting
        letters, symbols and numbers.

        :param event: The current event to consider reacting to.
        :return bool: Returns True if we've done something with the input event.
        """
        processed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    if self.double_click_started and self.double_click_select_time_acc < self.double_click_select_time:
                        self.double_click_started = False
                        pattern = re.compile(r"[\w']+")
                        index = min(self.edit_position, len(self.text)-1)
                        if index > 0:
                            char = self.text[index]
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
                            if index > 0:
                                start_select_index = index+1
                            else:
                                start_select_index = index
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
                    else:
                        self.double_click_started = True
                        self.edit_position = self.find_edit_position_from_pixel_pos(self.start_text_offset + mouse_x)
                        self.select_range[0] = self.edit_position
                        self.select_range[1] = self.edit_position
                        self.cursor_has_moved_recently = True
                        self.selection_in_progress = True
                        self.double_click_select_time_acc = 0.0

                    processed_event = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    processed_event = True
                    new_edit_pos = self.find_edit_position_from_pixel_pos(self.start_text_offset + mouse_x)
                    if new_edit_pos != self.edit_position:
                        self.cursor_has_moved_recently = True
                        self.select_range[1] = self.edit_position
                    self.selection_in_progress = False
                else:
                    self.selection_in_progress = False

        if self.selected:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    entry_finished_event = pygame.event.Event(pygame.USEREVENT,
                                                              {'user_type': pygame_gui.UI_TEXT_ENTRY_FINISHED,
                                                               'text': self.text,
                                                               'ui_element': self,
                                                               'ui_object_id': self.object_ids[-1]})
                    pygame.event.post(entry_finished_event)
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    self.select_range = [0, len(self.text)]
                    self.edit_position = len(self.text)
                    self.cursor_has_moved_recently = True
                elif event.key == pygame.K_x and event.mod & pygame.KMOD_CTRL:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        clipboard_copy(self.text[low_end:high_end])
                        self.text = self.text[:low_end] + self.text[high_end:]
                        self.edit_position = low_end
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        clipboard_copy(self.text[low_end:high_end])
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                    new_text = clipboard_paste()
                    if self.validate_text_string(new_text):
                        if abs(self.select_range[0] - self.select_range[1]) > 0:
                            low_end = min(self.select_range[0], self.select_range[1])
                            high_end = max(self.select_range[0], self.select_range[1])
                            final_text = self.text[:low_end] + new_text + self.text[high_end:]
                            within_length_limit = True
                            if self.length_limit is not None:
                                if len(final_text) > self.length_limit:
                                    within_length_limit = False
                            if within_length_limit:
                                self.text = final_text
                                self.edit_position = low_end + len(new_text)
                                self.select_range = [0, 0]
                                self.cursor_has_moved_recently = True
                        elif len(new_text) > 0:
                            final_text = self.text[:self.edit_position] + new_text + self.text[self.edit_position:]
                            within_length_limit = True
                            if self.length_limit is not None:
                                if len(final_text) > self.length_limit:
                                    within_length_limit = False
                            if within_length_limit:
                                self.text = final_text
                                self.edit_position += len(new_text)
                                self.cursor_has_moved_recently = True
                        processed_event = True
                elif event.key == pygame.K_BACKSPACE:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        self.text = self.text[:low_end] + self.text[high_end:]
                        self.edit_position = low_end
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                    elif self.edit_position > 0:
                        if self.start_text_offset > 0:
                            self.start_text_offset -= self.font.size(self.text[self.edit_position-1])[0]
                        self.text = self.text[:self.edit_position-1] + self.text[self.edit_position:]
                        self.edit_position -= 1
                        self.cursor_has_moved_recently = True
                    processed_event = True
                elif event.key == pygame.K_DELETE:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        self.text = self.text[:low_end] + self.text[high_end:]
                        self.edit_position = low_end
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                    elif self.edit_position < len(self.text):
                        self.text = self.text[:self.edit_position] + self.text[self.edit_position+1:]
                        self.edit_position = self.edit_position
                        self.cursor_has_moved_recently = True
                    processed_event = True
                elif event.key == pygame.K_LEFT:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        self.edit_position = min(self.select_range[0], self.select_range[1])
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                    elif self.edit_position > 0:
                        self.edit_position -= 1
                        self.cursor_has_moved_recently = True
                    processed_event = True
                elif event.key == pygame.K_RIGHT:
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        self.edit_position = max(self.select_range[0], self.select_range[1])
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                    elif self.edit_position < len(self.text):
                        self.edit_position += 1
                        self.cursor_has_moved_recently = True
                    processed_event = True
                else:
                    within_length_limit = True
                    if self.length_limit is not None:
                        if len(self.text) >= self.length_limit:
                            within_length_limit = False
                    if within_length_limit:
                        character = event.unicode
                        char_metrics = self.font.metrics(character)
                        if len(char_metrics) > 0 and char_metrics[0] is not None:
                            valid_character = True
                            if self.allowed_characters is not None:
                                if character not in self.allowed_characters:
                                    valid_character = False
                            if self.forbidden_characters is not None:
                                if character in self.forbidden_characters:
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
                                    self.edit_position += 1
                                self.cursor_has_moved_recently = True
                                processed_event = True
        return processed_event

    def find_edit_position_from_pixel_pos(self, pixel_pos: int):
        """
        Locates the correct position to move the edit cursor to, when reacting to a mouse click inside the text entry
        element.

        :param pixel_pos: The x position of our click after being adjusted for text in our box scrolling off-screen.
        """
        start_pos = (self.rect.x + self.border_width + self.shadow_width +
                     self.shape_corner_radius + self.horiz_line_padding)
        acc_pos = start_pos
        index = 0
        for char in self.text:
            x_width = self.font.size(char)[0]

            if acc_pos + (x_width/2) > pixel_pos:
                break
            else:
                index += 1
            acc_pos += x_width
        return index

    def set_allowed_characters(self, allowed_characters: Union[str, List[str]]):
        """
        Sets a whitelist of characters that will be the only ones allowed in our text entry element.
        We can either set the list directly, or request one of the already existing lists by a string
        identifier. The currently supported lists for allowed characters are:

        - 'numbers'

        :param allowed_characters: The characters to allow, either in a list form or one of the supported string ids.
        """
        if type(allowed_characters) is str:
            if allowed_characters == 'numbers':
                self.allowed_characters = UITextEntryLine._number_character_set

        else:
            self.allowed_characters = allowed_characters.copy()

    def set_forbidden_characters(self, forbidden_characters: Union[str, List[str]]):
        """
        Sets a blacklist of characters that will be banned from our text entry element.
        We can either set the list directly, or request one of the already existing lists by a string
        identifier. The currently supported lists for forbidden characters are:

        - 'numbers'
        - 'forbidden_file_path'

        :param forbidden_characters: The characters to forbid, either in a list form or one of the supported string ids.
        """
        if type(forbidden_characters) is str:
            if forbidden_characters == 'numbers':
                self.forbidden_characters = UITextEntryLine._number_character_set
            elif forbidden_characters == 'forbidden_file_path':
                self.forbidden_characters = UITextEntryLine._forbidden_file_path_characters

        else:
            self.forbidden_characters = forbidden_characters.copy()

    def validate_text_string(self, text_to_validate: str) -> bool:
        """
        Checks a string of text to see if any of it's characters don't meet the requirements of the allowed and
        forbidden character sets.

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
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for this element when
        the theme data has changed.
        """
        has_any_changed = False

        font = self.ui_theme.get_font(self.object_ids, self.element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        shape_type = 'rectangle'
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if shape_type_string is not None:
            if shape_type_string in ['rectangle', 'rounded_rectangle']:
                shape_type = shape_type_string
        if shape_type != self.shape_type:
            self.shape_type = shape_type
            has_any_changed = True

        corner_radius = 2
        shape_corner_radius_string = self.ui_theme.get_misc_data(self.object_ids,
                                                                 self.element_ids, 'shape_corner_radius')
        if shape_corner_radius_string is not None:
            try:
                corner_radius = int(shape_corner_radius_string)
            except ValueError:
                corner_radius = 2
        if corner_radius != self.shape_corner_radius:
            self.shape_corner_radius = corner_radius
            has_any_changed = True

        border_width = 1
        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            try:
                border_width = int(border_width_string)
            except ValueError:
                border_width = 1

        if border_width != self.border_width:
            self.border_width = border_width
            has_any_changed = True

        shadow_width = 2
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            try:
                shadow_width = int(shadow_width_string)
            except ValueError:
                shadow_width = 2
        if shadow_width != self.shadow_width:
            self.shadow_width = shadow_width
            has_any_changed = True

        padding_str = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'padding')
        if padding_str is None:
            horiz_line_padding = 2
            vert_line_padding = 2
        else:
            try:
                horiz_line_padding = int(padding_str.split(',')[0])
                vert_line_padding = int(padding_str.split(',')[1])
            except ValueError:
                horiz_line_padding = 2
                vert_line_padding = 2

        if horiz_line_padding != self.horiz_line_padding or vert_line_padding != self.vert_line_padding:
            self.vert_line_padding = vert_line_padding
            self.horiz_line_padding = horiz_line_padding
            has_any_changed = True

        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_text')
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            has_any_changed = True

        selected_text_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'selected_text')
        if selected_text_colour != self.selected_text_colour:
            self.selected_text_colour = selected_text_colour
            has_any_changed = True

        selected_bg_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'selected_bg')
        if selected_bg_colour != self.selected_bg_colour:
            self.selected_bg_colour = selected_bg_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
