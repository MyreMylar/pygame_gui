import pygame
import pygame_gui.elements.ui_button
from pygame_gui.core.ui_element import UIElement


class UIVerticalScrollBar(UIElement):
    def __init__(self, relative_rect, visible_percentage, ui_manager,
                 ui_container=None, element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['vertical_scroll_bar']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('vertical_scroll_bar')
        super().__init__(relative_rect, ui_manager, ui_container,
                         layer_thickness=1, starting_height=1,
                         element_ids=new_element_ids, object_id=object_id)

        self.button_height = 20
        self.background_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'dark_bg')

        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.background_colour)

        self.top_button = pygame_gui.elements.ui_button.UIButton(pygame.Rect(self.relative_rect.topleft,
                                                                             (self.relative_rect.width,
                                                                      self.button_height)),
                                                         '▲', self.ui_manager,
                                                                 ui_container=self.ui_container,
                                                                 starting_height=2,
                                                                 element_ids=self.element_ids,
                                                                 object_id=self.object_id)

        bottom_button_y = self.relative_rect.y + self.relative_rect.height - self.button_height
        self.bottom_button = pygame_gui.elements.ui_button.UIButton(pygame.Rect((self.relative_rect.x,
                                                                                 bottom_button_y),
                                                                                (self.relative_rect.width,
                                                                         self.button_height)),
                                                            '▼', self.ui_manager,
                                                                    ui_container=self.ui_container,
                                                                    starting_height=2,
                                                                    element_ids=self.element_ids,
                                                                    object_id=self.object_id)

        self.visible_percentage = visible_percentage
        self.start_percentage = 0.0

        self.sliding_rect_position = pygame.math.Vector2(self.relative_rect.x,
                                                         self.relative_rect.y + self.button_height)

        self.scrollable_height = self.relative_rect.height - (2 * self.button_height)
        scroll_bar_height = int(self.scrollable_height * self.visible_percentage)
        self.sliding_button = pygame_gui.elements.ui_button.UIButton(pygame.Rect(self.sliding_rect_position,
                                                                                 (self.relative_rect.width,
                                                                          scroll_bar_height)),
                                                             '', self.ui_manager,
                                                                     ui_container=self.ui_container,
                                                                     starting_height=2,
                                                                     element_ids=self.element_ids,
                                                                     object_id=self.object_id)

        self.sliding_button.set_hold_range((100, self.relative_rect.height))

        self.scroll_position = 0.0
        self.top_limit_position = 0.0
        self.bottom_limit_position = self.scrollable_height

        self.grabbed_slider = False
        self.starting_grab_y_difference = 0

        self.has_moved_recently = False

        self.scroll_wheel_up = False
        self.scroll_wheel_down = False

    def check_has_moved_and_reset(self):
        if self.has_moved_recently:
            self.has_moved_recently = False
            return True
        else:
            return False

    def kill(self):
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.sliding_button)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.top_button)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.bottom_button)
        super().kill()
        self.top_button.kill()
        self.bottom_button.kill()
        self.sliding_button.kill()

    def select(self):
        if self.sliding_button is not None:
            self.ui_manager.unselect_focus_element()
            self.ui_manager.select_focus_element(self.sliding_button)

    def process_event(self, event):
        processed_event = False
        last_focused_scrollbar_element = self.ui_manager.get_last_focused_vert_scrollbar()
        if (last_focused_scrollbar_element is self) or (
                last_focused_scrollbar_element is self.sliding_button) or (
                last_focused_scrollbar_element is self.top_button) or (
            last_focused_scrollbar_element is self.bottom_button
        ):
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.scroll_wheel_up = True
                    processed_event = True
                elif event.y < 0:
                    self.scroll_wheel_down = True
                    processed_event = True

        return processed_event

    def update(self, time_delta):
        if self.alive():
            moved_this_frame = False
            if (self.top_button.held or self.scroll_wheel_up) and self.scroll_position > self.top_limit_position:
                self.scroll_wheel_up = False
                self.scroll_position -= (250.0 * time_delta)
                self.scroll_position = max(self.scroll_position, self.top_limit_position)
                self.sliding_button.rect.y = self.scroll_position + self.rect.y + self.button_height
                self.sliding_button.relative_rect.y = self.scroll_position + self.relative_rect.y + self.button_height
                moved_this_frame = True
            elif (self.bottom_button.held or self.scroll_wheel_down) and self.scroll_position < self.bottom_limit_position:
                self.scroll_wheel_down = False
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position,
                                           self.bottom_limit_position - self.sliding_button.rect.height)
                self.sliding_button.rect.y = self.scroll_position + self.rect.y + self.button_height
                self.sliding_button.relative_rect.y = self.scroll_position + self.relative_rect.y + self.button_height
                moved_this_frame = True

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.sliding_button.held and self.sliding_button.in_hold_range((mouse_x, mouse_y)):

                if not self.grabbed_slider:
                    self.grabbed_slider = True
                    real_scroll_pos = (self.scroll_position + self.rect.y + self.button_height)
                    self.starting_grab_y_difference = mouse_y - real_scroll_pos

                real_scroll_pos = (self.scroll_position + self.rect.y + self.button_height)
                current_grab_difference = mouse_y - real_scroll_pos
                adjustment_required = current_grab_difference - self.starting_grab_y_difference
                self.scroll_position = self.scroll_position + adjustment_required

                self.scroll_position = min(max(self.scroll_position, self.top_limit_position),
                                           self.bottom_limit_position - self.sliding_button.rect.height)

                self.sliding_button.rect.y = self.scroll_position + self.rect.y + self.button_height
                self.sliding_button.relative_rect.y = self.scroll_position + self.relative_rect.y + self.button_height
                moved_this_frame = True
            elif not self.sliding_button.held:
                self.grabbed_slider = False

            if moved_this_frame:
                self.start_percentage = self.scroll_position / self.scrollable_height
                if not self.has_moved_recently:
                    self.has_moved_recently = True

    def redraw_scrollbar(self):
        self.sliding_button.kill()

        self.scrollable_height = self.rect.height - (2 * self.button_height)
        scroll_bar_height = int(self.scrollable_height * self.visible_percentage)
        self.sliding_rect_position.y = self.rect.y + 20 + (self.start_percentage * self.scrollable_height)
        self.sliding_button = pygame_gui.elements.ui_button.UIButton(pygame.Rect(self.sliding_rect_position,
                                                                                 (self.rect.width, scroll_bar_height)),
                                                             '', self.ui_manager,
                                                                     ui_container=self.ui_container,
                                                                     starting_height=2,
                                                                     element_ids=self.element_ids,
                                                                     object_id=self.object_id)

    def set_visible_percentage(self, percentage):
        self.visible_percentage = percentage
        if 1.0 - self.start_percentage < self.visible_percentage:
            self.start_percentage = 1.0 - self.visible_percentage

        self.redraw_scrollbar()
