import pygame
import warnings
from typing import Union, Tuple

from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


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
        self.grabbed_slider = False
        self.starting_grab_x_difference = 0
        self.has_moved_recently = False
        value_range_length = self.value_range[1] - self.value_range[0]
        self.current_value = int(self.value_range[0] + (self.current_percentage * value_range_length))
        self.left_limit_position = 0.0

        self.border_width = None
        self.shadow_width = None
        self.border_colour = None
        self.background_colour = None
        self.background_rect = None
        self.sliding_button = None
        self.scrollable_width = None
        self.right_limit_position = None
        self.scroll_position = None
        self.left_button = None
        self.right_button = None
        self.sliding_button = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        self.rebuild_from_changed_theme_data()

        # Things below here depend on theme data so need to be updated on a rebuild
        self.left_button = UIButton(pygame.Rect(self.background_rect.topleft,
                                                (self.button_width, self.background_rect.height)),
                                    '◀',
                                    self.ui_manager, self.ui_container, starting_height=2,
                                    parent_element=self,
                                    object_id='#left_button')
        self.right_button = UIButton(pygame.Rect((self.background_rect.x + self.background_rect.width - self.button_width,
                                                  self.background_rect.y),
                                                 (self.button_width, self.background_rect.height)),
                                     '▶',
                                     self.ui_manager, self.ui_container, starting_height=2,
                                     parent_element=self,
                                     object_id='#right_button')

        sliding_x_pos = self.background_rect.x + self.background_rect.width/2 - self.button_width/2
        self.sliding_button = UIButton(pygame.Rect((sliding_x_pos,
                                                    self.background_rect.y),
                                                   (self.button_width, self.background_rect.height)),
                                       '', self.ui_manager, self.ui_container, starting_height=2,
                                       parent_element=self,
                                       object_id='#sliding_button')

        self.sliding_button.set_hold_range((self.background_rect.width, 100))

        self.set_current_value(start_value)

    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """
        relative_background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                self.border_width + self.shadow_width),
                                               (self.rect.width - (2 * self.shadow_width) - (2 * self.border_width),
                                                self.rect.height - (2 * self.shadow_width) - (2 * self.border_width)))

        self.background_rect = pygame.Rect((relative_background_rect.x + self.relative_rect.x,
                                            relative_background_rect.y + self.relative_rect.y),
                                           relative_background_rect.size)

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

        self.image = self.drawable_shape.get_surface('normal')

        # Things below here depend on theme data so need to be updated on a rebuild
        self.scrollable_width = self.background_rect.width - (3 * self.button_width)
        self.right_limit_position = self.scrollable_width
        self.scroll_position = self.scrollable_width / 2

        if self.sliding_button is not None:
            sliding_x_pos = self.background_rect.x + self.background_rect.width / 2 - self.button_width / 2
            self.sliding_button.set_relative_position((sliding_x_pos, self.background_rect.y))
            self.sliding_button.set_dimensions((self.button_width, self.background_rect.height))
            self.sliding_button.set_hold_range((self.background_rect.width, 100))
            self.set_current_value(self.current_value)

        if self.left_button is not None:
            self.left_button.set_relative_position(self.background_rect.topleft),
            self.left_button.set_dimensions((self.button_width, self.background_rect.height))

        if self.right_button is not None:
            self.right_button.set_relative_position((self.background_rect.x + self.background_rect.width - self.button_width,
                                            self.background_rect.y)),
            self.right_button.set_dimensions((self.button_width, self.background_rect.height))

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
                x_pos = self.scroll_position + self.rect.x + self.shadow_width + self.border_width + self.button_width
                y_pos = self.rect.y + self.shadow_width + self.border_width
                self.sliding_button.set_position(pygame.Vector2(x_pos, y_pos))
                moved_this_frame = True
            elif self.right_button.held and self.scroll_position < self.right_limit_position:
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position, self.right_limit_position)
                x_pos = self.scroll_position + self.rect.x + self.shadow_width + self.border_width + self.button_width
                y_pos = self.rect.y + self.shadow_width + self.border_width
                self.sliding_button.set_position(pygame.Vector2(x_pos, y_pos))
                moved_this_frame = True

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.sliding_button.held and self.sliding_button.in_hold_range((mouse_x, mouse_y)):
                if not self.grabbed_slider:
                    self.grabbed_slider = True
                    real_scroll_pos = (self.scroll_position + self.rect.x +
                                       self.shadow_width + self.border_width + self.button_width)
                    self.starting_grab_x_difference = mouse_x - real_scroll_pos

                real_scroll_pos = (self.scroll_position + self.rect.x +
                                   self.shadow_width + self.border_width + self.button_width)
                current_grab_difference = mouse_x - real_scroll_pos
                adjustment_required = current_grab_difference - self.starting_grab_x_difference
                self.scroll_position = self.scroll_position + adjustment_required

                self.scroll_position = min(max(self.scroll_position, self.left_limit_position),
                                           self.right_limit_position)
                x_pos = self.scroll_position + self.rect.x + self.shadow_width + self.border_width + self.button_width
                y_pos = self.rect.y + self.shadow_width + self.border_width
                self.sliding_button.set_position(pygame.Vector2(x_pos, y_pos))

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
        if min(self.value_range[0], self.value_range[1]) <= value <= max(self.value_range[0], self.value_range[1]):
            self.current_value = float(value)
            value_range_size = (self.value_range[1] - self.value_range[0])
            if value_range_size != 0:
                percentage = (self.current_value - self.value_range[0])/value_range_size
                self.scroll_position = self.scrollable_width * percentage

                x_pos = self.scroll_position + self.rect.x + self.shadow_width + self.border_width + self.button_width
                y_pos = self.rect.y + self.shadow_width + self.border_width
                self.sliding_button.set_position(pygame.Vector2(x_pos, y_pos))
                self.has_moved_recently = True

        else:
            warnings.warn('value not in range', UserWarning)

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for this element when
        the theme data has changed.
        """
        has_any_changed = False

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

        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
