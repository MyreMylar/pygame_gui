import warnings
from typing import Union, Tuple, Optional, Dict

import pygame

from pygame_gui._constants import UI_2D_SLIDER_MOVED
from pygame_gui.core import UIElement, UIContainer, ObjectID
from pygame_gui.core.interfaces import (
    IUIManagerInterface,
    IContainerLikeInterface,
    IUIElementInterface,
    IColourGradientInterface,
)
from pygame_gui.core.gui_type_hints import Coordinate, RectLike
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.elements.ui_button import UIButton


class UI2DSlider(UIElement):
    """
    A 2d slider is intended to help users adjust values within a range, for example a
    volume control.

    :param relative_rect: A rectangle describing the position and dimensions of the element.
    :param start_value_x: The x value to start the slider at.
    :param value_range_x: The full range of x values.
    :param start_value_y: The y value to start the slider at.
    :param value_range_y: The full range of y values.
    :param invert_y: Should the y increase from bottom to top instead of the other way round?
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element "belongs to" in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        start_value_x: Union[float, int],
        value_range_x: Union[Tuple[float, float], Tuple[int, int]],
        start_value_y: Union[float, int],
        value_range_y: Union[Tuple[float, float], Tuple[int, int]],
        invert_y: bool = False,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        starting_height: int = 1,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
    ):
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor
        self.sliding_button: UIButton | None = None
        self.button_container: UIContainer | None = None
        super().__init__(
            relative_rect,
            manager,
            container,
            layer_thickness=2,
            starting_height=starting_height,
            anchors=anchors,
            visible=visible,
            parent_element=parent_element,
            object_id=object_id,
            element_id=["2d_slider"],
        )

        self.default_button_width = 20
        self.sliding_button_width = self.default_button_width
        self.current_x_percentage = 0.5
        self.current_y_percentage = 0.5
        self.left_limit_position = 0.0
        self.top_limit_position = 0.0
        self.starting_grab_difference = 0

        self.invert_y = invert_y

        self.use_integers_for_value = all(
            isinstance(n, int)
            for n in [start_value_x, *value_range_x, start_value_y, *value_range_y]
        )
        self.value_range_x = value_range_x
        value_range_x_length = self.value_range_x[1] - self.value_range_x[0]
        self.current_x_value = self.value_range_x[0] + (
            self.current_x_percentage * value_range_x_length
        )

        self.value_range_y = value_range_y
        value_range_y_length = self.value_range_y[1] - self.value_range_y[0]
        self.current_y_value = self.value_range_y[0] + (
            self.current_y_percentage * value_range_y_length
        )

        if self.use_integers_for_value:
            self.current_x_value = int(self.current_x_value)
            self.current_y_value = int(self.current_y_value)

        self.grabbed_slider = False
        self.has_moved_recently = False
        self.has_been_moved_by_user_recently = False

        self.background_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            0, 0, 0
        )
        self.border_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            0, 0, 0
        )
        self.disabled_border_colour: pygame.Color | IColourGradientInterface = (
            pygame.Color(0, 0, 0)
        )
        self.disabled_background_colour: pygame.Color | IColourGradientInterface = (
            pygame.Color(0, 0, 0)
        )

        self.shape = "rectangle"

        self.background_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.scrollable_width = 0
        self.scrollable_height = 0
        self.right_limit_position = 0
        self.bottom_limit_position = 0
        self.scroll_position: pygame.Vector2 = pygame.Vector2(0.0, 0.0)

        self.rebuild_from_changed_theme_data()

        sliding_x_pos = int(
            self.background_rect.width / 2 - self.sliding_button_width / 2
        )
        sliding_y_pos = int(
            self.background_rect.height / 2 - self.sliding_button_width / 2
        )
        self.sliding_button = UIButton(
            pygame.Rect(
                (sliding_x_pos, sliding_y_pos),
                (self.sliding_button_width, self.sliding_button_width),
            ),
            "",
            self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id=ObjectID(object_id="#sliding_button", class_id=None),
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
            visible=self.visible,
        )

        self.sliding_button.set_hold_range(
            (self.background_rect.width, self.background_rect.height)
        )

        self.set_current_value(start_value_x, start_value_y)

    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """
        total_horiz_space = (
            self.border_width["left"]
            + self.border_width["right"]
            + (2 * self.shadow_width)
        )
        total_vert_space = (
            self.border_width["top"]
            + self.border_width["bottom"]
            + (2 * self.shadow_width)
        )

        self.background_rect = pygame.Rect(
            (
                self.border_width["left"] + self.shadow_width + self.relative_rect.x,
                self.border_width["top"] + self.shadow_width + self.relative_rect.y,
            ),
            (
                self.relative_rect.width - total_horiz_space,
                self.relative_rect.height - total_vert_space,
            ),
        )

        theming_parameters = {
            "normal_bg": self.background_colour,
            "normal_border": self.border_colour,
            "disabled_bg": self.disabled_background_colour,
            "disabled_border": self.disabled_border_colour,
            "border_width": self.border_width,
            "shadow_width": self.shadow_width,
            "shape_corner_radius": self.shape_corner_radius,
            "border_overlap": self.border_overlap,
        }

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(
                self.rect, theming_parameters, ["normal", "disabled"], self.ui_manager
            )
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(
                self.rect, theming_parameters, ["normal", "disabled"], self.ui_manager
            )

        if self.drawable_shape is not None:
            self._set_image(self.drawable_shape.get_fresh_surface())

        if self.button_container is None:
            self.button_container = UIContainer(
                self.background_rect,
                manager=self.ui_manager,
                container=self.ui_container,
                anchors=self.anchors,
                object_id="#2d_slider_buttons_container",
                visible=self.visible,
            )
        else:
            self.button_container.set_dimensions(self.background_rect.size)
            self.button_container.set_relative_position(self.background_rect.topleft)

        self.scrollable_width = self.background_rect.width - self.sliding_button_width
        self.scrollable_height = self.background_rect.height - self.sliding_button_width
        self.right_limit_position = self.scrollable_width
        self.bottom_limit_position = self.scrollable_height
        self.scroll_position = pygame.Vector2(
            self.scrollable_width / 2, self.scrollable_height / 2
        )

        if self.sliding_button is not None:
            self.sliding_button.set_dimensions(
                (self.sliding_button_width, self.sliding_button_width)
            )
            self.sliding_button.set_hold_range(
                (self.background_rect.width, self.background_rect.height)
            )
            self.set_current_value(self.current_x_value, self.current_y_value)

    def kill(self):
        """
        Overrides the normal sprite kill() method to also kill the button elements that help make
        up the slider.

        """
        if self.button_container:
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

        mouse_pos = pygame.Vector2(self.ui_manager.get_mouse_position())
        if self.sliding_button is not None:
            if self.sliding_button.held and self.sliding_button.in_hold_range(
                mouse_pos
            ):
                moved_this_frame = self._move_slider_with_mouse(mouse_pos)
            elif not self.sliding_button.held:
                self.grabbed_slider = False

        if moved_this_frame:
            self._set_slider_values_after_move()

    def _move_slider_with_mouse(self, mouse_pos):
        if self.sliding_button is None:
            return False
        if not self.grabbed_slider:
            self.grabbed_slider = True
            real_scroll_pos = pygame.Vector2(self.sliding_button.rect.topleft)
            self.starting_grab_difference = mouse_pos - real_scroll_pos

        real_scroll_pos = pygame.Vector2(self.sliding_button.rect.topleft)
        current_grab_difference = mouse_pos - real_scroll_pos
        adjustment_required = current_grab_difference - self.starting_grab_difference
        self.scroll_position = self.scroll_position + adjustment_required

        self.scroll_position = pygame.Vector2(
            min(
                max(self.scroll_position.x, self.left_limit_position),
                self.right_limit_position,
            ),
            min(
                max(self.scroll_position.y, self.top_limit_position),
                self.bottom_limit_position,
            ),
        )

        self.sliding_button.set_relative_position(self.scroll_position)

        return True

    def _set_slider_values_after_move(self):
        self.current_x_percentage = self.scroll_position.x / self.scrollable_width
        self.current_x_value = self.value_range_x[0] + (
            self.current_x_percentage * (self.value_range_x[1] - self.value_range_x[0])
        )

        if self.invert_y:
            # Scroll position is inverted, so invert it again to get actual percentage
            self.current_y_percentage = (
                self.scrollable_height - self.scroll_position.y
            ) / self.scrollable_height
        else:
            self.current_y_percentage = self.scroll_position.y / self.scrollable_height
        self.current_y_value = self.value_range_y[0] + (
            self.current_y_percentage * (self.value_range_y[1] - self.value_range_y[0])
        )
        if self.use_integers_for_value:
            self.current_x_value = int(self.current_x_value)
            self.current_y_value = int(self.current_y_value)

        if not self.has_moved_recently:
            self.has_moved_recently = True

        if not self.has_been_moved_by_user_recently:
            self.has_been_moved_by_user_recently = True

        # new event
        event_data = {
            "value": (self.current_x_value, self.current_y_value),
            "ui_element": self,
            "ui_object_id": self.most_specific_combined_id,
        }
        pygame.event.post(pygame.event.Event(UI_2D_SLIDER_MOVED, event_data))

    def get_current_value(self) -> Tuple[Union[float, int], Union[float, int]]:
        """
        Gets the current value the slider is set to.

        :return: The current value recorded by the slider.

        """
        self.has_moved_recently = False
        self.has_been_moved_by_user_recently = False
        return self.current_x_value, self.current_y_value

    def set_current_value(
        self, value_x: Union[float, int], value_y: Union[float, int], warn: bool = True
    ) -> None:
        """
        Sets the value of the slider, which will move the position of the slider to match.
        If warn is True, this function will issue a warning and return without setting the
        value when the value set is not in the value range. If warn is false the value will
        instead be clamped to the minimum & maximum value range and set.

        :param value_x: The x value to set.
        :param value_y: The y value to set.
        :param warn: set to false in order to suppress the default warning,
                     instead the value will be clamped.
        :param: invert_y: Should the y value be inverted? If not passed then will use self.invert_value for this info.
        :return: None
        """
        if self.use_integers_for_value:
            value_x = int(value_x)
            value_y = int(value_y)

        min_x_value = min(self.value_range_x[0], self.value_range_x[1])
        max_x_value = max(self.value_range_x[0], self.value_range_x[1])

        if value_x < min_x_value or value_x > max_x_value:
            if warn:
                warnings.warn("x value not in range", UserWarning)
                return
            else:
                self.current_x_value = max(min(value_x, max_x_value), min_x_value)
        else:
            self.current_x_value = value_x

        min_y_value = min(self.value_range_y[0], self.value_range_y[1])
        max_y_value = max(self.value_range_y[0], self.value_range_y[1])

        if value_y < min_y_value or value_y > max_y_value:
            if warn:
                warnings.warn("y value not in range", UserWarning)
                return
            else:
                self.current_y_value = max(min(value_y, max_y_value), min_y_value)
        else:
            self.current_y_value = value_y

        value_x_range_size = self.value_range_x[1] - self.value_range_x[0]
        value_y_range_size = self.value_range_y[1] - self.value_range_y[0]

        if value_x_range_size != 0 and value_y_range_size != 0:
            self._set_percentages_and_scroll_pos_after_change(
                value_x_range_size, value_y_range_size
            )

    def _set_percentages_and_scroll_pos_after_change(
        self, value_x_range_size, value_y_range_size
    ):
        self.current_x_percentage = (
            float(self.current_x_value) - self.value_range_x[0]
        ) / value_x_range_size
        self.current_y_percentage = (
            float(self.current_y_value) - self.value_range_y[0]
        ) / value_y_range_size

        # Invert the position at which the slider should be
        height = (
            self.scrollable_height * (1 - self.current_y_percentage)
            if self.invert_y
            else self.scrollable_height * self.current_y_percentage
        )
        self.scroll_position = pygame.Vector2(
            self.scrollable_width * self.current_x_percentage,
            height,
        )
        if self.sliding_button is not None:
            self.sliding_button.set_relative_position(self.scroll_position)
        self.has_moved_recently = True

    def rebuild_from_changed_theme_data(self) -> None:
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for
        this element when the theme data has changed.

        :return: None
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        if self._check_misc_theme_data_changed(
            attribute_name="shape",
            default_value="rectangle",
            casting_func=str,
            allowed_values=["rectangle", "rounded_rectangle"],
        ):
            has_any_changed = True

        if self._check_shape_theming_changed(
            defaults={
                "border_width": {"left": 1, "right": 1, "top": 1, "bottom": 1},
                "shadow_width": 2,
                "border_overlap": 1,
                "shape_corner_radius": [2, 2, 2, 2],
            }
        ):
            has_any_changed = True

        background_colour: pygame.Color | IColourGradientInterface = (
            self.ui_theme.get_colour_or_gradient("dark_bg", self.combined_element_ids)
        )
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour: pygame.Color | IColourGradientInterface = (
            self.ui_theme.get_colour_or_gradient(
                "normal_border", self.combined_element_ids
            )
        )
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        disabled_background_colour: pygame.Color | IColourGradientInterface = (
            self.ui_theme.get_colour_or_gradient(
                "disabled_dark_bg", self.combined_element_ids
            )
        )
        if disabled_background_colour != self.disabled_background_colour:
            self.disabled_background_colour = disabled_background_colour
            has_any_changed = True

        disabled_border_colour: pygame.Color | IColourGradientInterface = (
            self.ui_theme.get_colour_or_gradient(
                "disabled_border", self.combined_element_ids
            )
        )
        if disabled_border_colour != self.disabled_border_colour:
            self.disabled_border_colour = disabled_border_colour
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            attribute_name="sliding_button_width",
            default_value=self.default_button_width,
            casting_func=int,
        ):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def set_position(self, position: Coordinate) -> None:
        """
        Sets the absolute screen position of this slider, updating all subordinate button elements
        at the same time.

        :param position: The absolute screen position to set.
        :return: None
        """
        super().set_position(position)

        self.background_rect.x = int(
            self.border_width["left"] + self.shadow_width + self.relative_rect.x
        )
        self.background_rect.y = int(
            self.border_width["top"] + self.shadow_width + self.relative_rect.y
        )

        if self.button_container is not None:
            self.button_container.set_relative_position(self.background_rect.topleft)

    def set_relative_position(self, position: Coordinate) -> None:
        """
        Sets the relative screen position of this slider, updating all subordinate button elements
        at the same time.

        :param position: The relative screen position to set.
        :return: None
        """
        super().set_relative_position(position)

        self.background_rect.x = int(
            self.border_width["left"] + self.shadow_width + self.relative_rect.x
        )
        self.background_rect.y = int(
            self.border_width["top"] + self.shadow_width + self.relative_rect.y
        )

        if self.button_container is not None:
            self.button_container.set_relative_position(self.background_rect.topleft)

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        super().set_dimensions(dimensions, clamp_to_container)

        total_horiz_space = (
            self.border_width["left"]
            + self.border_width["right"]
            + (2 * self.shadow_width)
        )
        total_vert_space = (
            self.border_width["top"]
            + self.border_width["bottom"]
            + (2 * self.shadow_width)
        )

        self.background_rect.width = int(self.relative_rect.width - total_horiz_space)
        self.background_rect.height = int(self.relative_rect.height - total_vert_space)

        if self.button_container is not None:
            self.button_container.set_dimensions(self.background_rect.size)

        # sort out sliding button parameters
        self.scrollable_width = self.background_rect.width - self.sliding_button_width
        self.scrollable_height = self.background_rect.height - self.sliding_button_width
        self.right_limit_position = self.scrollable_width
        self.bottom_limit_position = self.scrollable_height
        self.scroll_position = pygame.Vector2(
            self.scrollable_width * self.current_x_percentage,
            self.scrollable_height * self.current_y_percentage,
        )

        if self.sliding_button is not None:
            self.sliding_button.set_dimensions(
                (self.sliding_button_width, self.sliding_button_width)
            )
            self.sliding_button.set_relative_position(self.scroll_position)

    def disable(self):
        """
        Disable the slider. It should not be interactive and will use the disabled theme colours.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self.sliding_button is not None:
                self.sliding_button.disable()
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state("disabled")

    def enable(self):
        """
        Enable the slider. It should become interactive and will use the normal theme colours.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.sliding_button is not None:
                self.sliding_button.enable()
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state("normal")

    def show(self):
        """
        In addition to the base UIElement.show() - show the sliding button and show
        the button_container which will propagate and show the left and right buttons.
        """
        super().show()

        if self.sliding_button is not None:
            self.sliding_button.show()
        if self.button_container is not None:
            self.button_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - hide the sliding button and hide
        the button_container which will propagate and hide the left and right buttons.
        """
        super().hide()

        if self.sliding_button is not None:
            self.sliding_button.hide()
        if self.button_container is not None:
            self.button_container.hide()
