import warnings
from typing import Union, Tuple, Dict, Optional

import pygame

from pygame_gui._constants import UI_HORIZONTAL_SLIDER_MOVED, UI_BUTTON_PRESSED

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.elements.ui_button import UIButton


class UIHorizontalSlider(UIElement):
    """
    A horizontal slider is intended to help users adjust values within a range, for example a
    volume control.

    :param relative_rect: A rectangle describing the position and dimensions of the element.
    :param start_value: The value to start the slider at.
    :param value_range: The full range of values.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    :param click_increment: the amount to increment by when clicking one of the arrow buttons.
    """
    def __init__(self,
                 relative_rect: pygame.Rect,
                 start_value: Union[float, int],
                 value_range: Tuple[Union[float, int], Union[float, int]],
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 click_increment: Union[float, int] = 1
                 ):

        super().__init__(relative_rect, manager, container,
                         layer_thickness=2,
                         starting_height=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='horizontal_slider')

        self.default_button_width = 20
        self.arrow_button_width = self.default_button_width
        self.sliding_button_width = self.default_button_width
        self.current_percentage = 0.5
        self.left_limit_position = 0.0
        self.starting_grab_x_difference = 0

        if (isinstance(start_value, int) and
                isinstance(value_range[0], int) and
                isinstance(value_range[1], int)):
            self.use_integers_for_value = True
        else:
            self.use_integers_for_value = False
        self.value_range = value_range
        value_range_length = self.value_range[1] - self.value_range[0]

        self.current_value = self.value_range[0] + (self.current_percentage * value_range_length)
        if self.use_integers_for_value:
            self.current_value = int(self.current_value)

        self.grabbed_slider = False
        self.has_moved_recently = False
        self.has_been_moved_by_user_recently = False

        self.background_colour = None
        self.border_colour = None
        self.disabled_border_colour = None
        self.disabled_background_colour = None

        self.border_width = None
        self.shadow_width = None

        self.drawable_shape = None
        self.shape = 'rectangle'
        self.shape_corner_radius = None

        self.background_rect = None  # type: Optional[pygame.Rect]

        self.scrollable_width = None
        self.right_limit_position = None
        self.scroll_position = None

        self.left_button = None
        self.right_button = None
        self.sliding_button = None
        self.enable_arrow_buttons = True

        self.button_container = None

        self.button_held_repeat_time = 0.3
        self.button_held_repeat_acc = 0.0

        self.increment = click_increment

        self.rebuild_from_changed_theme_data()

        sliding_x_pos = int(self.background_rect.width / 2 - self.sliding_button_width / 2)
        self.sliding_button = UIButton(pygame.Rect((sliding_x_pos, 0),
                                                   (self.sliding_button_width,
                                                    self.background_rect.height)),
                                       '', self.ui_manager,
                                       container=self.button_container,
                                       starting_height=1,
                                       parent_element=self,
                                       object_id=ObjectID(object_id='#sliding_button',
                                                          class_id='None'),
                                       anchors={'left': 'left',
                                                'right': 'left',
                                                'top': 'top',
                                                'bottom': 'bottom'},
                                       visible=self.visible
                                       )

        self.sliding_button.set_hold_range((self.background_rect.width, 100))

        self.set_current_value(start_value)

    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """
        border_and_shadow = self.border_width + self.shadow_width
        self.background_rect = pygame.Rect((border_and_shadow + self.relative_rect.x,
                                            border_and_shadow + self.relative_rect.y),
                                           (self.relative_rect.width - (2 * border_and_shadow),
                                            self.relative_rect.height - (2 * border_and_shadow)))

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'disabled_bg': self.disabled_background_colour,
                              'disabled_border': self.disabled_border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal', 'disabled'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal', 'disabled'], self.ui_manager)

        self.set_image(self.drawable_shape.get_fresh_surface())

        if self.button_container is None:
            self.button_container = UIContainer(self.background_rect,
                                                manager=self.ui_manager,
                                                container=self.ui_container,
                                                anchors=self.anchors,
                                                object_id='#horiz_scrollbar_buttons_container',
                                                visible=self.visible)
        else:
            self.button_container.set_dimensions(self.background_rect.size)
            self.button_container.set_relative_position(self.background_rect.topleft)

        # Things below here depend on theme data so need to be updated on a rebuild
        if self.enable_arrow_buttons:
            self.arrow_button_width = self.default_button_width

            if self.left_button is None:
                self.left_button = UIButton(pygame.Rect((0, 0),
                                                        (self.arrow_button_width,
                                                         self.background_rect.height)),
                                            '◀', self.ui_manager,
                                            container=self.button_container,
                                            starting_height=1,
                                            parent_element=self,
                                            object_id=ObjectID("#left_button", "@arrow_button"),
                                            anchors={'left': 'left',
                                                     'right': 'left',
                                                     'top': 'top',
                                                     'bottom': 'bottom'},
                                            visible=self.visible
                                            )

            if self.right_button is None:
                self.right_button = UIButton(pygame.Rect((-self.arrow_button_width, 0),
                                                         (self.arrow_button_width,
                                                          self.background_rect.height)),
                                             '▶', self.ui_manager,
                                             container=self.button_container,
                                             starting_height=1,
                                             parent_element=self,
                                             object_id=ObjectID("#right_button", "@arrow_button"),
                                             anchors={'left': 'right',
                                                      'right': 'right',
                                                      'top': 'top',
                                                      'bottom': 'bottom'},
                                             visible=self.visible
                                             )

        else:
            self.arrow_button_width = 0
            if self.left_button is not None:
                self.left_button.kill()
                self.left_button = None
            if self.right_button is not None:
                self.right_button.kill()
                self.right_button = None

        self.scrollable_width = (self.background_rect.width -
                                 self.sliding_button_width - (2 * self.arrow_button_width))
        self.right_limit_position = self.scrollable_width
        self.scroll_position = self.scrollable_width / 2

        if self.sliding_button is not None:
            sliding_x_pos = int((self.background_rect.width / 2) - (self.sliding_button_width / 2))
            self.sliding_button.set_relative_position((sliding_x_pos, 0))
            self.sliding_button.set_dimensions((self.sliding_button_width,
                                                self.background_rect.height))
            self.sliding_button.set_hold_range((self.background_rect.width, 100))
            self.set_current_value(self.current_value, False)

    def kill(self):
        """
        Overrides the normal sprite kill() method to also kill the button elements that help make
        up the slider.

        """
        self.button_container.kill()
        super().kill()

    def update(self, time_delta: float):
        """
        Takes care of actually moving the slider based on interactions reported by the buttons or
        based on movement of the mouse if we are gripping the slider itself.

        :param time_delta: the time in seconds between calls to update.

        """
        super().update(time_delta)

        if not (self.alive() and self.is_enabled):
            return
        moved_this_frame = False
        if self.left_button is not None and (self.left_button.held and
                                             self.scroll_position > self.left_limit_position):

            if self.button_held_repeat_acc > self.button_held_repeat_time:
                self.scroll_position -= (250.0 * time_delta)
                self.scroll_position = max(self.scroll_position, self.left_limit_position)
                x_pos = (self.scroll_position + self.arrow_button_width)
                y_pos = 0
                self.sliding_button.set_relative_position((x_pos, y_pos))
                moved_this_frame = True
            else:
                self.button_held_repeat_acc += time_delta
        elif self.right_button is not None and (self.right_button.held and
                                                self.scroll_position < self.right_limit_position):
            if self.button_held_repeat_acc > self.button_held_repeat_time:
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position, self.right_limit_position)
                x_pos = (self.scroll_position + self.arrow_button_width)
                y_pos = 0
                self.sliding_button.set_relative_position((x_pos, y_pos))
                moved_this_frame = True
            else:
                self.button_held_repeat_acc += time_delta
        else:
            self.button_held_repeat_acc = 0.0

        mouse_x, mouse_y = self.ui_manager.get_mouse_position()
        if self.sliding_button.held and self.sliding_button.in_hold_range((mouse_x, mouse_y)):
            if not self.grabbed_slider:
                self.grabbed_slider = True
                real_scroll_pos = self.sliding_button.rect.left
                self.starting_grab_x_difference = mouse_x - real_scroll_pos

            real_scroll_pos = self.sliding_button.rect.left
            current_grab_difference = mouse_x - real_scroll_pos
            adjustment_required = current_grab_difference - self.starting_grab_x_difference
            self.scroll_position = self.scroll_position + adjustment_required

            self.scroll_position = min(max(self.scroll_position, self.left_limit_position),
                                       self.right_limit_position)
            x_pos = (self.scroll_position + self.arrow_button_width)
            y_pos = 0
            self.sliding_button.set_relative_position((x_pos, y_pos))

            moved_this_frame = True
        elif not self.sliding_button.held:
            self.grabbed_slider = False

        if moved_this_frame:
            self.current_percentage = self.scroll_position / self.scrollable_width
            self.current_value = self.value_range[0] + (self.current_percentage *
                                                        (self.value_range[1] - self.value_range[0]))
            if self.use_integers_for_value:
                self.current_value = int(self.current_value)
            if not self.has_moved_recently:
                self.has_moved_recently = True

            if not self.has_been_moved_by_user_recently:
                self.has_been_moved_by_user_recently = True

            event_data = {'user_type': UI_HORIZONTAL_SLIDER_MOVED,
                          'value': self.current_value,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            slider_moved_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(slider_moved_event)

    def process_event(self, event: pygame.event.Event) -> bool:
        processed_event = False
        if event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED:
            if event.ui_element == self.left_button:
                if self.button_held_repeat_acc < self.button_held_repeat_time:
                    if self.get_current_value() > self.value_range[0]:
                        self.set_current_value(self.get_current_value() - self.increment, False)
                        processed_event = True
            elif event.ui_element == self.right_button:
                if self.button_held_repeat_acc < self.button_held_repeat_time:
                    if self.get_current_value() < self.value_range[1]:
                        self.set_current_value(self.get_current_value() + self.increment, False)
                        processed_event = True
        return processed_event

    def get_current_value(self) -> Union[float, int]:
        """
        Gets the current value the slider is set to.

        :return: The current value recorded by the slider.

        """
        self.has_moved_recently = False
        self.has_been_moved_by_user_recently = False
        return self.current_value

    def set_current_value(self, value: Union[float, int], warn: bool = True):
        """
        Sets the value of the slider, which will move the position of the slider to match. Will
        issue a warning if the value set is not in the value range.

        :param value: The value to set.
        :param warn: set to false to suppress the default warning,
                     instead the value will be clamped.

        """
        if self.use_integers_for_value:
            value = int(value)

        min_value = min(self.value_range[0], self.value_range[1])
        max_value = max(self.value_range[0], self.value_range[1])
        if value <= min_value or value >= max_value:
            if warn:
                warnings.warn('value not in range', UserWarning)
                return
            else:
                self.current_value = max(min(value, max_value), min_value)
        else:
            self.current_value = value

        value_range_size = (self.value_range[1] - self.value_range[0])
        if value_range_size != 0:
            self.current_percentage = (float(self.current_value) -
                                       self.value_range[0]) / value_range_size
            self.scroll_position = self.scrollable_width * self.current_percentage

            x_pos = (self.scroll_position + self.arrow_button_width)
            y_pos = 0
            self.sliding_button.set_relative_position((x_pos, y_pos))
            self.has_moved_recently = True

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for
        this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

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

        def parse_to_bool(str_data: str):
            return bool(int(str_data))

        if self._check_misc_theme_data_changed(attribute_name='enable_arrow_buttons',
                                               default_value=True,
                                               casting_func=parse_to_bool):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='sliding_button_width',
                                               default_value=self.default_button_width,
                                               casting_func=int):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this slider, updating all subordinate button elements
        at the same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)

        border_and_shadow = self.border_width + self.shadow_width
        self.background_rect.x = border_and_shadow + self.relative_rect.x
        self.background_rect.y = border_and_shadow + self.relative_rect.y

        self.button_container.set_relative_position(self.background_rect.topleft)

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Sets the relative screen position of this slider, updating all subordinate button elements
        at the same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)

        border_and_shadow = self.border_width + self.shadow_width
        self.background_rect.x = border_and_shadow + self.relative_rect.x
        self.background_rect.y = border_and_shadow + self.relative_rect.y

        self.button_container.set_relative_position(self.background_rect.topleft)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.

        """
        super().set_dimensions(dimensions)

        border_and_shadow = self.border_width + self.shadow_width
        self.background_rect.width = self.relative_rect.width - (2 * border_and_shadow)
        self.background_rect.height = self.relative_rect.height - (2 * border_and_shadow)

        self.button_container.set_dimensions(self.background_rect.size)

        # sort out sliding button parameters
        self.scrollable_width = (self.background_rect.width -
                                 self.sliding_button_width -
                                 (2 * self.arrow_button_width))
        self.right_limit_position = self.scrollable_width
        self.scroll_position = self.scrollable_width * self.current_percentage

        slider_x_pos = self.scroll_position + self.arrow_button_width
        slider_y_pos = 0

        self.sliding_button.set_dimensions((self.sliding_button_width, self.background_rect.height))
        self.sliding_button.set_relative_position((slider_x_pos, slider_y_pos))

    def disable(self):
        """
        Disable the slider. It should not be interactive and will use the disabled theme colours.
        """
        if self.is_enabled:
            self.is_enabled = False
            self.sliding_button.disable()
            if self.left_button:
                self.left_button.disable()
            if self.right_button:
                self.right_button.disable()
            self.drawable_shape.set_active_state('disabled')

    def enable(self):
        """
        Enable the slider. It should become interactive and will use the normal theme colours.
        """
        if not self.is_enabled:
            self.is_enabled = True
            self.sliding_button.enable()
            if self.left_button:
                self.left_button.enable()
            if self.right_button:
                self.right_button.enable()
            self.drawable_shape.set_active_state('normal')

    def show(self):
        """
        In addition to the base UIElement.show() - show the sliding button and show
        the button_container which will propagate and show the left and right buttons.
        """
        super().show()

        self.sliding_button.show()
        if self.button_container is not None:
            self.button_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - hide the sliding button and hide
        the button_container which will propagate and hide the left and right buttons.
        """
        super().hide()

        self.sliding_button.hide()
        if self.button_container is not None:
            self.button_container.hide()
