import pygame
import warnings
from typing import Union, List, Tuple

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement
from ..elements.ui_button import UIButton


class UIHorizontalSlider(UIElement):
    """
    A horizontal slider is intended to help users adjust values within a range, for example a volume control.

    :param relative_rect: A rectangle describing the position and dimensions of the element.
    :param start_value: The value to start the slider at.
    :param value_range: The full range of values.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 start_value: Union[float, int],
                 value_range: Tuple[Union[float, int], Union[float, int]],
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='horizontal_slider')
        super().__init__(relative_rect, manager, container,
                         object_ids=new_object_ids,
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

        self.background_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'dark_bg')

        self.image = pygame.Surface((self.relative_rect.width, self.relative_rect.height))
        self.image.fill(self.background_colour)

        self.left_button = UIButton(pygame.Rect(self.relative_rect.topleft,
                                                (self.button_width, self.relative_rect.height)),
                                    '◀',
                                    self.ui_manager, self.ui_container, starting_height=2,
                                    parent_element=self)
        self.right_button = UIButton(pygame.Rect((self.relative_rect.x + self.relative_rect.width - self.button_width,
                                                  self.relative_rect.y),
                                                 (self.button_width, self.relative_rect.height)),
                                     '▶',
                                     self.ui_manager, self.ui_container, starting_height=2,
                                     parent_element=self)

        sliding_x_pos = self.relative_rect.x + self.relative_rect.width/2 - self.button_width/2
        self.sliding_button = UIButton(pygame.Rect((sliding_x_pos,
                                                    self.relative_rect.y),
                                                   (self.button_width, self.relative_rect.height)),
                                       '', self.ui_manager, self.ui_container, starting_height=2,
                                       parent_element=self)

        self.sliding_button.set_hold_range((self.relative_rect.width, 100))
        self.grabbed_slider = False
        self.starting_grab_x_difference = 0
        self.has_moved_recently = False

        self.set_current_value(start_value)

    def kill(self):
        """
        Overrides the normal sprite kill() method to also kill the button elements that help make up the slider.

        """
        self.left_button.kill()
        self.right_button.kill()
        self.sliding_button.kill()
        super().kill()

    def update(self, time_delta: float):
        """
        Takes care of actually moving the slider based on interactions reported by the buttons or based on movement of
        the mouse if we are gripping the slider itself.

        :param time_delta: the time in seconds between calls to update.
        """
        if self.alive():
            moved_this_frame = False
            if self.left_button.held and self.scroll_position > self.left_limit_position:
                self.scroll_position -= (250.0 * time_delta)
                self.scroll_position = max(self.scroll_position, self.left_limit_position)
                self.sliding_button.set_position(pygame.Vector2(self.scroll_position + self.rect.x + self.button_width,
                                                                self.rect.y))
                moved_this_frame = True
            elif self.right_button.held and self.scroll_position < self.right_limit_position:
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position,
                                           self.right_limit_position)
                self.sliding_button.set_position(pygame.Vector2(self.scroll_position + self.rect.x + self.button_width,
                                                                self.rect.y))
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

                self.sliding_button.set_position(pygame.Vector2(self.scroll_position + self.rect.x + self.button_width,
                                                                self.rect.y))
                # self.sliding_button.rect.x = self.scroll_position + self.rect.x + self.button_width
                # self.sliding_button.relative_rect.x = self.scroll_position + self.relative_rect.x + self.button_width
                moved_this_frame = True
            elif not self.sliding_button.held:
                self.grabbed_slider = False

            if moved_this_frame:
                self.current_value = self.value_range[0] + (
                        (self.scroll_position / self.scrollable_width) * (self.value_range[1] - self.value_range[0]))
                if not self.has_moved_recently:
                    self.has_moved_recently = True

    def get_current_value(self) -> Union[float, int]:
        """
        Gets the current value the slider is set to.

        :return: The current value recorded by the slider.
        """
        self.has_moved_recently = False
        return self.current_value

    def set_current_value(self, value: Union[float, int]):
        """
        Sets the value of the slider, which will move the position of the slider to match. Will issue a warning if the
        value set is not in the value range.

        :param value: The value to set.
        """
        if self.value_range[0] <= value <= self.value_range[1]:
            self.current_value = float(value)
            value_range_size = (self.value_range[1] - self.value_range[0])
            if value_range_size != 0:
                percentage = (self.current_value - self.value_range[0])/value_range_size
                self.scroll_position = self.scrollable_width * percentage

                self.sliding_button.set_position(pygame.Vector2(self.scroll_position + self.rect.x + self.button_width,
                                                                self.rect.y))
                self.has_moved_recently = True

        else:
            warnings.warn('value not in range', UserWarning)
