from typing import Union, Dict, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IUIContainerInterface,
    IUIElementInterface,
    IColourGradientInterface,
)
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.gui_type_hints import Coordinate, RectLike


class UIHorizontalScrollBar(UIElement):
    """
    A horizontal scroll bar allows users to position a smaller visible area within a horizontally
    larger area.

    :param relative_rect: The size and position of the scroll bar.
    :param visible_percentage: The horizontal percentage of the larger area that is visible,
                               between 0.0 and 1.0.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If set to None will be the
                      root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        visible_percentage: float,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
    ):
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor
        self.button_container: UIContainer | None = None

        super().__init__(
            relative_rect,
            manager,
            container,
            layer_thickness=2,
            starting_height=1,
            anchors=anchors,
            visible=visible,
            parent_element=parent_element,
            object_id=object_id,
            element_id=["horizontal_scroll_bar"],
        )

        self.button_width = 20
        self.arrow_button_width = self.button_width
        self.scroll_position = 0.0
        self.target_scroll_position = 0.0
        self.scroll_to_target_speed = 40.0
        self.left_limit = 0.0
        self.starting_grab_x_difference = 0
        self.visible_percentage = max(0.0, min(visible_percentage, 1.0))
        self._start_percentage = 0.0

        self.grabbed_slider = False
        self.has_moved_recently = False
        self.scroll_wheel_moved = False
        self.scroll_wheel_amount = 0
        self.scroll_wheel_speed = 40.0

        self.button_scroll_amount = 300.0

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
        self.left_arrow_text = "◀"
        self.right_arrow_text = "▶"

        self.background_rect = pygame.Rect(0, 0, 0, 0)

        self.scrollable_width: int = 0
        self.right_limit: int = 0
        self.sliding_rect_position = pygame.math.Vector2(0.0, 0.0)

        self.left_button: UIButton | None = None
        self.right_button: UIButton | None = None
        self.sliding_button: UIButton | None = None
        self.enable_arrow_buttons = True

        self.rebuild_from_changed_theme_data()

        scroll_bar_width = max(5, int(self.scrollable_width * self.visible_percentage))
        self.sliding_button = UIButton(
            pygame.Rect(
                (
                    int(self.sliding_rect_position[0]),
                    int(self.sliding_rect_position[1]),
                ),
                (scroll_bar_width, self.background_rect.height),
            ),
            "",
            self.ui_manager,
            container=self.button_container,
            starting_height=1,
            parent_element=self,
            object_id="#sliding_button",
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "bottom"},
        )
        self.join_focus_sets(self.sliding_button)

        self.sliding_button.set_hold_range((self.background_rect.width, 100))

        self._container_to_scroll: Optional[IUIContainerInterface] = None

    def set_container_to_check_hover_for_mousewheel_events(
        self, container: IUIContainerInterface
    ):
        """
        The container related to this scrollbar to check for hovering when we are rolling the mousewheel.
        This allows us to move the scroll bar when the mousewheel is rolled while the mouse pointer is hovering
        over a scrollable container.

        NB: this function on its own will not set up a container to be scrolled by this scrollbar

        :param container: the container to set as attached/related to this scrollbar for the mousewheel events
        """
        self._container_to_scroll = container

    @property
    def start_percentage(self):
        """
        turning start_percentage into a property, so we can round it to mitigate floating point errors
        """
        return self._start_percentage

    @start_percentage.setter
    def start_percentage(self, value):
        rounded_value = round(value, 4)
        self._start_percentage = rounded_value

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
                object_id="#horiz_scrollbar_buttons_container",
                visible=self.visible,
            )
            self.join_focus_sets(self.button_container)
        else:
            self.button_container.set_dimensions(self.background_rect.size)
            self.button_container.set_relative_position(self.background_rect.topleft)

        if self.enable_arrow_buttons:
            self.arrow_button_width = self.button_width
            if self.left_button is not None:
                self.left_button.kill()
                self.left_button = None
            if self.right_button is not None:
                self.right_button.kill()
                self.right_button = None

            if self.left_button is None:
                self.left_button = UIButton(
                    pygame.Rect(
                        (0, 0), (self.arrow_button_width, self.background_rect.height)
                    ),
                    self.left_arrow_text,
                    self.ui_manager,
                    container=self.button_container,
                    starting_height=1,
                    parent_element=self,
                    object_id=ObjectID("#left_button", "@arrow_button"),
                    anchors={
                        "left": "left",
                        "right": "left",
                        "top": "top",
                        "bottom": "bottom",
                    },
                )
                self.join_focus_sets(self.left_button)

            if self.right_button is None:
                self.right_button = UIButton(
                    pygame.Rect(
                        (-self.arrow_button_width, 0),
                        (self.arrow_button_width, self.background_rect.height),
                    ),
                    self.right_arrow_text,
                    self.ui_manager,
                    container=self.button_container,
                    starting_height=1,
                    parent_element=self,
                    object_id=ObjectID("#right_button", "@arrow_button"),
                    anchors={
                        "left": "right",
                        "right": "right",
                        "top": "top",
                        "bottom": "bottom",
                    },
                )
                self.join_focus_sets(self.right_button)
        else:
            self.arrow_button_width = 0
            if self.left_button is not None:
                self.left_button.kill()
                self.left_button = None
            if self.right_button is not None:
                self.right_button.kill()
                self.right_button = None

        self.scrollable_width = self.background_rect.width - (
            2 * self.arrow_button_width
        )
        self.right_limit = self.scrollable_width

        scroll_bar_width = max(5, int(self.scrollable_width * self.visible_percentage))
        self.scroll_position = min(
            max(self.scroll_position, self.left_limit),
            self.right_limit - scroll_bar_width,
        )
        self.target_scroll_position = self.scroll_position

        x_pos = self.scroll_position + self.arrow_button_width
        y_pos = 0
        self.sliding_rect_position = pygame.math.Vector2(x_pos, y_pos)

        if self.sliding_button is not None:
            self.sliding_button.kill()
            self.sliding_button = None

            scroll_bar_width = max(
                5, int(self.scrollable_width * self.visible_percentage)
            )
            self.sliding_button = UIButton(
                pygame.Rect(
                    (
                        int(self.sliding_rect_position[0]),
                        int(self.sliding_rect_position[1]),
                    ),
                    (scroll_bar_width, self.background_rect.height),
                ),
                "",
                self.ui_manager,
                container=self.button_container,
                starting_height=1,
                parent_element=self,
                object_id="#sliding_button",
                anchors={
                    "left": "left",
                    "right": "left",
                    "top": "top",
                    "bottom": "bottom",
                },
            )
            self.join_focus_sets(self.sliding_button)

            self.sliding_button.set_hold_range((self.background_rect.width, 100))

    def check_has_moved_recently(self) -> bool:
        """
        Returns True if the scroll bar was moved in the last call to the update function.

        :return: True if we've recently moved the scroll bar, False otherwise.

        """
        return self.has_moved_recently

    def kill(self):
        """
        Overrides the kill() method of the UI element class to kill all the buttons in the scroll
        bar and clear any of the parts of the scroll bar that are currently recorded as the
        'last focused horizontal scroll bar element' on the ui manager.

        NOTE: the 'last focused' state on the UI manager is used so that the mouse wheel will
        move whichever scrollbar we last fiddled with even if we've been doing other stuff.
        This seems to be consistent with the most common mousewheel/scrollbar interactions
        used elsewhere.
        """
        if self.button_container is not None:
            self.button_container.kill()
        super().kill()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Checks an event from pygame's event queue to see if the scroll bar needs to react to it.
        In this case it is just mousewheel events, mainly because the buttons that make up
        the scroll bar will handle the required mouse click events.

        :param event: The event to process.

        :return: Returns True if we've done something with the input event.

        """
        consumed_event = False
        if (
            self.is_enabled
            and self._check_should_handle_mousewheel_event()
            and event.type == pygame.MOUSEWHEEL
        ) and event.x != 0:
            self.scroll_wheel_moved = True
            if (self.scroll_wheel_amount > 0 > event.x) or (
                self.scroll_wheel_amount < 0 < event.x
            ):
                # changed direction, reset target position
                self.target_scroll_position = self.scroll_position
            self.scroll_wheel_amount = event.x

            consumed_event = True

        return consumed_event

    def _check_is_focus_set_hovered(self) -> bool:
        """
        Check if this scroll bar's focus set is currently hovered in the UI.

        :return: True if it was.

        """
        is_focus_set_hovered = False
        focus_set = self.get_focus_set()
        if focus_set is not None:
            is_focus_set_hovered = any(element.hovered for element in focus_set)
        return is_focus_set_hovered

    def _check_should_handle_mousewheel_event(self) -> bool:
        should_handle = False
        if (
            self._container_to_scroll
            and self._container_to_scroll.are_contents_hovered()
        ):
            should_handle = True
        elif self._check_is_focus_set_hovered():
            should_handle = True
        return should_handle

    def _update_scroll_position_from_target(self, time_delta: float) -> bool:
        distance = self.target_scroll_position - self.scroll_position

        return (
            (self._update_scroll_position_from_distance_and_time(distance, time_delta))
            if distance != 0.0
            and (
                self.scroll_position != self.left_limit
                or self.scroll_position != self.right_limit
            )
            else False
        )

    def _update_scroll_position_from_distance_and_time(self, distance, time_delta):
        direction = distance / abs(distance)
        self.scroll_position = self.scroll_position + (
            direction
            * max(abs(distance), 4.0)
            * self.scroll_to_target_speed
            * time_delta
            * self.visible_percentage
        )
        new_distance = self.target_scroll_position - self.scroll_position
        if new_distance != 0.0:
            new_direction = new_distance / abs(new_distance)
            if new_direction != direction:  # overshot
                self.scroll_position = self.target_scroll_position

        if self.sliding_button is not None:
            self.scroll_position = min(
                max(self.scroll_position, self.left_limit),
                self.right_limit - self.sliding_button.relative_rect.width,
            )
            x_pos = self.scroll_position + self.arrow_button_width
            self.sliding_button.set_relative_position((x_pos, 0))
        return True

    def update(self, time_delta: float):
        """
        Called once per update loop of our UI manager. Deals largely with moving the scroll bar
        and updating the resulting 'start_percentage' variable that is then used by other
        'scrollable' UI elements to control the point they start drawing.

        Reacts to presses of the up and down arrow buttons, movement of the mouse wheel and
        dragging of the scroll bar itself.

        :param time_delta: A float, roughly representing the time in seconds between calls to this
                           method.

        """
        super().update(time_delta)
        self.has_moved_recently = False
        if self.alive():
            if self.scroll_wheel_moved and (
                self.left_limit <= self.scroll_position <= self.right_limit
            ):
                self.scroll_wheel_moved = False
                scroll_wheel_proportional_amount = (
                    self.scroll_wheel_amount * self.visible_percentage
                )
                self.target_scroll_position -= (
                    scroll_wheel_proportional_amount * self.scroll_wheel_speed
                )
                # Don't clamp target on scroll wheel, so we get nice acceleration into the buffers

            elif self.left_button is not None and self.left_button.held:
                self.target_scroll_position -= (
                    self.button_scroll_amount * self.visible_percentage * time_delta
                )
                if self.sliding_button is not None:
                    self.target_scroll_position = min(
                        max(self.target_scroll_position, self.left_limit),
                        self.right_limit - self.sliding_button.relative_rect.width,
                    )

            elif self.right_button is not None and self.right_button.held:
                self.target_scroll_position += (
                    self.button_scroll_amount * self.visible_percentage * time_delta
                )
                if self.sliding_button is not None:
                    self.target_scroll_position = min(
                        max(self.target_scroll_position, self.left_limit),
                        self.right_limit - self.sliding_button.relative_rect.width,
                    )

            moved_this_frame = self._update_scroll_position_from_target(time_delta)

            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            if (
                self.sliding_button is not None
                and self.sliding_button.held
                and self.sliding_button.in_hold_range((mouse_x, mouse_y))
            ):
                if not self.grabbed_slider:
                    self.grabbed_slider = True
                    real_scroll_pos = self.sliding_button.rect.left
                    self.starting_grab_x_difference = mouse_x - real_scroll_pos

                real_scroll_pos = self.sliding_button.rect.left
                current_grab_difference = mouse_x - real_scroll_pos
                adjustment_required = (
                    current_grab_difference - self.starting_grab_x_difference
                )
                self.target_scroll_position = (
                    self.target_scroll_position + adjustment_required
                )

                self.target_scroll_position = min(
                    max(self.target_scroll_position, self.left_limit),
                    self.right_limit - self.sliding_button.rect.width,
                )
                self.scroll_position = self.target_scroll_position
                x_pos = self.scroll_position + self.arrow_button_width
                y_pos = 0
                self.sliding_button.set_relative_position((x_pos, y_pos))
                moved_this_frame = True

            elif self.sliding_button is not None and not self.sliding_button.held:
                self.grabbed_slider = False

            if moved_this_frame:
                self.start_percentage = self.scroll_position / self.scrollable_width
                if not self.has_moved_recently:
                    self.has_moved_recently = True

    def set_scroll_from_start_percentage(self, new_start_percentage: float):
        """
        Set the scroll bar's scrolling position from a percentage between 0.0 and 1.0.

        :param new_start_percentage: the percentage to set.
        """
        new_start_percentage = min(1.0, max(new_start_percentage, 0.0))
        self.start_percentage = new_start_percentage

        new_scroll_position = new_start_percentage * self.scrollable_width

        if self.sliding_button is not None:
            self.scroll_position = min(
                max(new_scroll_position, self.left_limit),
                self.right_limit - self.sliding_button.rect.width,
            )
        self.target_scroll_position = self.scroll_position
        self.start_percentage = self.scroll_position / self.scrollable_width

        x_pos = self.scroll_position + self.arrow_button_width
        y_pos = 0
        if self.sliding_button is not None:
            self.sliding_button.set_relative_position((x_pos, y_pos))
        self.has_moved_recently = True

    def redraw_scrollbar(self):
        """
        Redraws the 'scrollbar' portion of the whole UI element. Called when we change the
        visible percentage.
        """
        self.scrollable_width = self.background_rect.width - (
            2 * self.arrow_button_width
        )
        self.right_limit = self.scrollable_width

        scroll_bar_width = max(5, int(self.scrollable_width * self.visible_percentage))

        # x_pos = (self.scroll_position + self.arrow_button_width)
        x_pos = min(
            (self.right_limit + self.arrow_button_width) - scroll_bar_width,
            int(self.scroll_position + self.arrow_button_width),
        )
        y_pos = 0
        self.sliding_rect_position = pygame.math.Vector2(x_pos, y_pos)

        self._set_sliding_button_data(scroll_bar_width)

    def set_visible_percentage(self, percentage: float):
        """
        Sets the percentage of the total 'scrollable area' that is currently visible. This will
        affect the size of the scrollbar and should be called if the horizontal size of the
        'scrollable area' or the horizontal size of the visible area change.

        :param percentage: A float between 0.0 and 1.0 representing the percentage that is visible.

        """
        self.visible_percentage = max(0.0, min(1.0, percentage))
        if 1.0 - self.start_percentage < self.visible_percentage:
            self.start_percentage = 1.0 - self.visible_percentage

        self.redraw_scrollbar()

    def reset_scroll_position(self):
        """
        Reset the current scroll position back to the top.

        """
        self.scroll_position = 0.0
        self.target_scroll_position = 0.0
        self.start_percentage = 0.0

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
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

        if self._check_misc_theme_data_changed(
            attribute_name="tool_tip_delay", default_value=1.0, casting_func=float
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

        background_colour = self.ui_theme.get_colour_or_gradient(
            "dark_bg", self.combined_element_ids
        )
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(
            "normal_border", self.combined_element_ids
        )
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        disabled_background_colour = self.ui_theme.get_colour_or_gradient(
            "disabled_dark_bg", self.combined_element_ids
        )
        if disabled_background_colour != self.disabled_background_colour:
            self.disabled_background_colour = disabled_background_colour
            has_any_changed = True

        disabled_border_colour = self.ui_theme.get_colour_or_gradient(
            "disabled_border", self.combined_element_ids
        )
        if disabled_border_colour != self.disabled_border_colour:
            self.disabled_border_colour = disabled_border_colour
            has_any_changed = True

        def parse_to_bool(str_data: str):
            return bool(int(str_data))

        if self._check_misc_theme_data_changed(
            attribute_name="enable_arrow_buttons",
            default_value=True,
            casting_func=parse_to_bool,
        ):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def set_position(self, position: Coordinate):
        """
        Sets the absolute screen position of this scroll bar, updating all subordinate button
        elements at the same time.

        :param position: The absolute screen position to set.

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

    def set_relative_position(self, position: Coordinate):
        """
        Sets the relative screen position of this scroll bar, updating all subordinate button
        elements at the same time.

        :param position: The relative screen position to set.

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

    def _set_sliding_button_data(self, scroll_bar_width):
        if self.sliding_button is None:
            return
        self.sliding_button.set_relative_position(self.sliding_rect_position)
        self.sliding_button.set_dimensions(
            (scroll_bar_width, self.background_rect.height)
        )
        self.sliding_button.set_hold_range((self.background_rect.width, 100))

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        should_rebuild = False
        if (self.rect.height == 0 and dimensions[1] != 0) or (
            self.rect.width == 0 and dimensions[0] != 0
        ):
            should_rebuild = True

        super().set_dimensions(dimensions)

        if should_rebuild:
            self.rebuild()
        else:
            self.background_rect.width = max(
                0,
                int(
                    self.relative_rect.width
                    - (
                        (2 * self.shadow_width)
                        + self.border_width["left"]
                        + self.border_width["right"]
                    )
                ),
            )
            self.background_rect.height = max(
                0,
                int(
                    self.relative_rect.height
                    - (
                        (2 * self.shadow_width)
                        + self.border_width["top"]
                        + self.border_width["bottom"]
                    )
                ),
            )

            if self.button_container is not None:
                self.button_container.set_dimensions(self.background_rect.size)

            # sort out scroll bar parameters
            self.scrollable_width = max(
                0, self.background_rect.width - (2 * self.arrow_button_width)
            )
            self.right_limit = self.scrollable_width

            scroll_bar_width = max(
                5, int(self.scrollable_width * self.visible_percentage)
            )
            base_scroll_bar_x = self.arrow_button_width
            max_scroll_bar_x = base_scroll_bar_x + (
                self.scrollable_width - scroll_bar_width
            )
            self.sliding_rect_position.x = max(
                base_scroll_bar_x,
                min(
                    (
                        base_scroll_bar_x
                        + int(self.start_percentage * self.scrollable_width)
                    ),
                    max_scroll_bar_x,
                ),
            )
            self.scroll_position = self.sliding_rect_position.x - base_scroll_bar_x
            self.target_scroll_position = self.scroll_position

            if self.sliding_button is not None:
                self.sliding_button.set_dimensions(
                    (scroll_bar_width, self.background_rect.height)
                )
                self.sliding_button.set_relative_position(self.sliding_rect_position)

    def disable(self):
        """
        Disables the scroll bar, so it is no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self.button_container is not None:
                self.button_container.disable()

            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state("disabled")

    def enable(self):
        """
        Enables the scroll bar, so it is interactive once again.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.button_container is not None:
                self.button_container.enable()

            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state("normal")

    def show(self):
        """
        In addition to the base UIElement.show() - show the self.button_container which
        will propagate and show all the buttons.
        """
        super().show()
        if self.button_container is not None:
            self.button_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - hide the self.button_container which
        will propagate and hide all the buttons.
        """
        if not self.visible:
            return

        super().hide()
        if self.button_container is not None:
            self.button_container.hide()
