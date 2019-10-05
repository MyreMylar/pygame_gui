import pygame
import re

from ..core.utility import clipboard_paste, clipboard_copy
from ..core.ui_element import UIElement


class UITextEntryLine(UIElement):
    def __init__(self, relative_rect, manager, container=None, element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['text_entry_line']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('text_entry_line')
        super().__init__(relative_rect, manager, container,
                         starting_height=1, layer_thickness=1,
                         element_ids=new_element_ids,
                         object_id=object_id)
        self.selected = False

        # theme font
        self.font = self.ui_theme.get_font(self.object_id, self.element_ids)

        # colours from theme
        self.bg_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_bg')
        self.text_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_text')
        self.selected_text_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'selected_text')
        self.selected_bg_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'selected_bg')
        self.border_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'border')

        # misc data from the theme
        border_width_str = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'border_width')
        if border_width_str is None:
            self.border_width = 1
        else:
            self.border_width = int(border_width_str)
        self.text = ""

        padding_str = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'padding')
        if padding_str is None:
            self.horiz_line_padding = 4
            self.vert_line_padding = 2
        else:
            self.horiz_line_padding = int(padding_str.split(',')[0])
            self.vert_line_padding = int(padding_str.split(',')[1])

        # input timings - I expect nobody really wants to mess with these that much
        # ideally we could populate from the os settings but that sounds like a headache
        self.key_repeat = 0.5
        self.cursor_blink_delay_after_moving_acc = 0.0
        self.cursor_blink_delay_after_moving = 1.0
        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.4
        self.double_click_select_time = 0.4
        self.double_click_select_time_acc = 0.0

        self.edit_position = 0
        self.select_range = [0, 0]
        self.selection_in_progress = False

        self.cursor_on = False
        self.cursor_has_moved_recently = False
        self.double_click_started = False

        # setup for drawing
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        line_height = self.text_surface.get_rect().height

        self.relative_rect.height = line_height + (2 * self.vert_line_padding) + (2 * self.border_width)
        self.rect.height = self.relative_rect.height

        self.cursor = pygame.Rect((self.text_surface.get_rect().right + 2,
                                   self.vert_line_padding + self.border_width), (1, line_height))

        self.background_and_border = pygame.Surface(self.rect.size)
        self.background_and_border.fill(self.border_colour)
        background_surface = pygame.Surface(((self.rect.width-(self.border_width * 2),
                                              self.rect.height-(self.border_width * 2))))
        background_surface.fill(self.bg_colour)
        self.background_and_border.blit(background_surface, (self.border_width, self.border_width))

        self.text_image = pygame.Surface(((self.rect.width-(self.border_width * 2),
                                           self.rect.height-(self.border_width * 2))))
        self.text_image.fill(self.bg_colour)

        self.image = pygame.Surface(self.rect.size)
        self.start_text_offset = 0

        self.redraw()

    def set_text(self, text):
        self.text = text
        self.edit_position = len(self.text)

    def redraw(self):
        self.text_image.fill(self.bg_colour)
        if self.select_range[0] != self.select_range[1]:
            low_end = min(self.select_range[0], self.select_range[1])
            high_end = max(self.select_range[0], self.select_range[1])
            pre_select_area_text = self.text[:low_end]
            select_area_text = self.text[low_end:high_end]
            post_select_area_text = self.text[high_end:]

            pre_select_area_surface = None
            post_select_area_surface = None

            if len(pre_select_area_text) > 0:
                pre_select_area_surface = self.font.render(pre_select_area_text, True, self.text_colour)
                width_pre = pre_select_area_surface.get_rect().width
            else:
                width_pre = 0

            select_area_surface = self.font.render(select_area_text, True,
                                                   self.selected_text_colour, self.selected_bg_colour)
            if len(post_select_area_text) > 0:
                post_select_area_surface = self.font.render(post_select_area_text, True, self.text_colour)
                width_post = post_select_area_surface.get_rect().width
            else:
                width_post = 0

            text_height = select_area_surface.get_rect().height
            width_select = select_area_surface.get_rect().width

            self.text_surface = pygame.Surface((width_pre + width_select + width_post, text_height))
            self.text_surface.fill(self.bg_colour)
            if pre_select_area_surface is not None:
                self.text_surface.blit(pre_select_area_surface, (0, 0))
            self.text_surface.blit(select_area_surface, (width_pre, 0))
            if post_select_area_surface is not None:
                self.text_surface.blit(post_select_area_surface, (width_pre+width_select, 0))
        else:
            self.text_surface = self.font.render(self.text, True, self.text_colour, self.bg_colour)

        text_clip_width = self.rect.width - (self.horiz_line_padding * 2) - (self.border_width * 2)
        text_clip_height = self.rect.height - (self.vert_line_padding * 2) - (self.border_width * 2)
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
        self.image.blit(self.background_and_border, (0, 0))
        self.image.blit(self.text_image, (self.border_width, self.border_width))
        if self.cursor_on:
            cursor_len_str = self.text[:self.edit_position]
            cursor_size = self.font.size(cursor_len_str)
            self.cursor.x = cursor_size[0] + self.border_width + self.horiz_line_padding - self.start_text_offset
            pygame.draw.rect(self.image, self.text_colour, self.cursor)

    def update(self, time_delta):
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
        self.selected = False
        pygame.key.set_repeat()
        self.select_range = [0, 0]
        self.redraw()

    def select(self):
        self.selected = True
        pygame.key.set_repeat(500, 25)
        self.redraw()

    def process_event(self, event):
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
                if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
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
                    if abs(self.select_range[0] - self.select_range[1]) > 0:
                        low_end = min(self.select_range[0], self.select_range[1])
                        high_end = max(self.select_range[0], self.select_range[1])
                        self.text = self.text[:low_end] + new_text + self.text[high_end:]
                        self.edit_position = low_end + len(new_text)
                        self.select_range = [0, 0]
                        self.cursor_has_moved_recently = True
                    elif len(new_text) > 0:
                        self.text = self.text[:self.edit_position] + new_text + self.text[self.edit_position:]
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
                    character = event.unicode
                    char_metrics = self.font.metrics(character)
                    if len(char_metrics) > 0 and char_metrics[0] is not None:
                        if abs(self.select_range[0] - self.select_range[1]) > 0:
                            low_end = min(self.select_range[0], self.select_range[1])
                            high_end = max(self.select_range[0], self.select_range[1])
                            self.text = self.text[:low_end] + character + self.text[high_end:]
                            self.edit_position = low_end + 1
                            self.select_range = [0, 0]
                        else:
                            self.text = self.text[:self.edit_position] + character + self.text[self.edit_position:]
                            self.edit_position += 1
                        self.cursor_has_moved_recently = True
                        processed_event = True
        return processed_event

    def find_edit_position_from_pixel_pos(self, pixel_pos):
        start_pos = self.rect.x + self.border_width + self.horiz_line_padding
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
