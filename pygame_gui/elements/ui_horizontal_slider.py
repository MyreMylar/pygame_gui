import pygame
import warnings

from ..core.ui_element import UIElement
from ..elements.ui_button import UIButton


class UIHorizontalSlider(UIElement):
    def __init__(self, relative_rect, start_value, value_range, manager,
                 container=None, object_id=None, element_ids=None):
        if element_ids is None:
            new_element_ids = ['horizontal_slider']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('horizontal_slider')
        super().__init__(relative_rect, manager, container,
                         object_id=object_id,
                         element_ids=new_element_ids,
                         starting_height=1,
                         layer_thickness=1)

        self.button_width = 20
        self.current_percentage = 0.5
        self.value_range = value_range

        value_range_length = self.value_range[1] - self.value_range[0]
        self.current_value = int(self.value_range[0] + (self.current_percentage * value_range_length))

        self.scrollable_width = self.relative_rect.width - (3 * self.button_width)
        self.left_limit_position = 0.0
        self.right_limit_position = self.scrollable_width

        self.scroll_position = self.scrollable_width/2

        self.background_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'dark_bg')

        self.image = pygame.Surface((self.relative_rect.width, self.relative_rect.height))
        self.image.fill(self.background_colour)

        self.left_button = UIButton(pygame.Rect(self.relative_rect.topleft,
                                                (self.button_width, self.relative_rect.height)),
                                    '◀',
                                    self.ui_manager, self.ui_container, starting_height=2,
                                    element_ids=self.element_ids,
                                    object_id=self.object_id)
        self.right_button = UIButton(pygame.Rect((self.relative_rect.x + self.relative_rect.width - self.button_width,
                                                  self.relative_rect.y),
                                                 (self.button_width, self.relative_rect.height)),
                                     '▶',
                                     self.ui_manager, self.ui_container, starting_height=2,
                                     element_ids=self.element_ids,
                                     object_id=self.object_id)

        sliding_x_pos = self.relative_rect.x + self.relative_rect.width/2 - self.button_width/2
        self.sliding_button = UIButton(pygame.Rect((sliding_x_pos,
                                                    self.relative_rect.y),
                                                   (self.button_width, self.relative_rect.height)),
                                       '', self.ui_manager, self.ui_container, starting_height=2,
                                       element_ids=self.element_ids,
                                       object_id=self.object_id)

        self.sliding_button.set_hold_range((self.relative_rect.width, 100))
        self.grabbed_slider = False
        self.starting_grab_x_difference = 0
        self.has_moved_recently = False

        self.set_current_value(start_value)

    def kill(self):
        self.left_button.kill()
        self.right_button.kill()
        self.sliding_button.kill()
        super().kill()

    def update(self, time_delta):
        if self.alive():
            moved_this_frame = False
            if self.left_button.held and self.scroll_position > self.left_limit_position:
                self.scroll_position -= (250.0 * time_delta)
                self.scroll_position = max(self.scroll_position, self.left_limit_position)
                self.sliding_button.rect.x = self.scroll_position + self.rect.x + self.button_width
                self.sliding_button.relative_rect.x = self.scroll_position + self.relative_rect.x + self.button_width
                moved_this_frame = True
            elif self.right_button.held and self.scroll_position < self.right_limit_position:
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position,
                                           self.right_limit_position)
                self.sliding_button.rect.x = self.scroll_position + self.rect.x + self.button_width
                self.sliding_button.relative_rect.x = self.scroll_position + self.relative_rect.x + self.button_width
                moved_this_frame = True

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.sliding_button.held and self.sliding_button.in_hold_range((mouse_x, mouse_y)):
                if not self.grabbed_slider:
                    self.grabbed_slider = True
                    real_scroll_pos = (self.scroll_position + self.rect.x + self.button_width)
                    self.starting_grab_x_difference = mouse_x - real_scroll_pos

                real_scroll_pos = (self.scroll_position + self.rect.x + self.button_width)
                current_grab_difference = mouse_x - real_scroll_pos
                adjustment_required = current_grab_difference - self.starting_grab_x_difference
                self.scroll_position = self.scroll_position + adjustment_required

                self.scroll_position = min(max(self.scroll_position, self.left_limit_position),
                                           self.right_limit_position)

                self.sliding_button.rect.x = self.scroll_position + self.rect.x + self.button_width
                self.sliding_button.relative_rect.x = self.scroll_position + self.relative_rect.x + self.button_width
                moved_this_frame = True
            elif not self.sliding_button.held:
                self.grabbed_slider = False

            if moved_this_frame:
                self.current_value = self.value_range[0] + (
                        (self.scroll_position / self.scrollable_width) * (self.value_range[1] - self.value_range[0]))
                if not self.has_moved_recently:
                    self.has_moved_recently = True

    def get_current_value(self):
        self.has_moved_recently = False
        return self.current_value

    def set_current_value(self, value):
        if self.value_range[0] <= value <= self.value_range[1]:
            self.current_value = float(value)
            value_range_size = (self.value_range[1] - self.value_range[0])
            if value_range_size != 0:
                percentage = (self.current_value - self.value_range[0])/value_range_size
                self.scroll_position = self.scrollable_width * percentage

                self.sliding_button.rect.x = self.scroll_position + self.rect.x + self.button_width
                self.sliding_button.relative_rect.x = self.scroll_position + self.relative_rect.x + self.button_width
                self.has_moved_recently = True

        else:
            warnings.warn('value not in range', UserWarning)
