from typing import Union, Dict, Callable, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IUIElementInterface,
)
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.gui_type_hints import RectLike, SpriteWithHealth


class UIStatusBar(UIElement):
    """
    Displays a status/progress bar.

    This is a flexible class that can be used to display status for a sprite (health/mana/fatigue, etc.),
    or to provide a status bar on the screen not attached to any particular object. You can use multiple
    status bars for a sprite to show different status items if desired.

    You can use the percent_full attribute to manually set the status, or you can provide a pointer to a method
    that will provide the percentage information.

    This is a kitchen sink class with several ways to use it; you may want to look at the subclasses built on top
    of it that are designed to be simpler to use, such as UIProgressBar, UIWorldSpaceHealthBar, and
    UIScreenSpaceHealthBar.

    :param relative_rect: The rectangle that defines the size of the health bar.
    :param sprite: Optional sprite to monitor for status info, and for drawing the bar with the sprite.
    :param follow_sprite: If there's a sprite, this indicates whether the bar should be drawn at the sprite's location.
    :param percent_method: Optional method signature to call to get the percent complete.
                           (To provide a method signature, simply reference the method without parenthesis,
                           such as self.health_percent.)
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.

    """

    element_id = "status_bar"

    def __init__(
        self,
        relative_rect: RectLike,
        manager: Optional[IUIManagerInterface] = None,
        sprite: Optional[SpriteWithHealth] = None,
        follow_sprite: bool = True,
        percent_method: Union[Callable[[], float], None] = None,
        container: Union[IContainerLikeInterface, None] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
    ):
        super().__init__(
            relative_rect,
            manager,
            container,
            starting_height=1,
            layer_thickness=1,
            anchors=anchors,
            visible=visible,
            parent_element=parent_element,
            object_id=object_id,
            element_id=[self.element_id],
        )

        self.sprite: Optional[SpriteWithHealth] = sprite
        self.follow_sprite = follow_sprite
        self.follow_sprite_offset = (0, 0)

        self.percent_method = percent_method
        self._percent_full = 0
        self.status_changed = False

        self.border_colour = None
        self.bar_filled_colour = None
        self.bar_unfilled_colour = None
        self.hover_height = None

        self.border_rect = None
        self.capacity_width = None
        self.capacity_height = None
        self.capacity_rect = None
        self.current_status_rect = None

        self.drawable_shape = None
        self.shape = "rectangle"

        self.font = None
        self.text_shadow_colour = None
        self.text_colour = None
        self.text_horiz_alignment = "center"
        self.text_vert_alignment = "center"
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1
        self.background_text = None
        self.foreground_text = None

        self._set_image(None)

        self.rebuild_from_changed_theme_data()

    @property
    def percent_full(self):
        """Use this property to directly change the status bar."""
        return self._percent_full

    @percent_full.setter
    def percent_full(self, value):
        # We need a decimal percentage
        if value > 1:
            value = value / 100
        if value != self._percent_full:
            self._percent_full = value
            self.status_changed = True

    @property
    def position(self):
        """
        Returns the drawing position of the status bar.

        :return: two integers representing the drawing position
        """
        if not self.sprite or not self.follow_sprite:
            return self.relative_rect.x, self.relative_rect.y
        offset_x = self.sprite.rect.x + self.follow_sprite_offset[0]
        offset_y = self.sprite.rect.y + self.follow_sprite_offset[1] - self.hover_height
        return offset_x, offset_y

    def rebuild(self):
        """
        Rebuild the status bar entirely because the theming data has changed.

        """
        if self.percent_method:
            # This triggers status_changed if necessary.
            self.percent_full = self.percent_method()

        self.border_rect = pygame.Rect(
            (self.shadow_width, self.shadow_width),
            (
                self.rect.width - (self.shadow_width * 2),
                self.rect.height - (self.shadow_width * 2),
            ),
        )

        self.capacity_width = (
            self.rect.width - (self.shadow_width * 2) - (self.border_width * 2)
        )
        self.capacity_height = (
            self.rect.height - (self.shadow_width * 2) - (self.border_width * 2)
        )
        self.capacity_rect = pygame.Rect(
            (
                self.border_width + self.shadow_width,
                self.border_width + self.shadow_width,
            ),
            (self.capacity_width, self.capacity_height),
        )

        self.redraw()

    def update(self, time_delta: float):
        """
        Updates the status bar sprite's image and rectangle with the latest status and position
        data from the sprite we are monitoring

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if self.alive():
            if self.sprite is not None and self.follow_sprite:
                self.set_relative_position(self.position)

            # If they've provided a method to call, we'll track previous value in percent_full.
            if self.percent_method:
                # This triggers status_changed if necessary.
                self.percent_full = self.percent_method()

            if self.status_changed:
                self.status_changed = False
                self.redraw()

    def status_text(self):
        """To display text in the bar, subclass UIStatusBar and override this method."""
        return None

    def redraw(self):
        """
        Redraw the status bar when something, other than it's position has changed.

        """
        theming_parameters = {
            "normal_bg": self.bar_unfilled_colour,
            "normal_border": self.border_colour,
            "border_width": self.border_width,
            "shadow_width": self.shadow_width,
            "shape_corner_radius": self.shape_corner_radius,
            "filled_bar": self.bar_filled_colour,
            "filled_bar_width_percentage": self.percent_full,
            "follow_sprite_offset": self.follow_sprite_offset,
            "border_overlap": self.border_overlap,
        }

        if text := self.status_text():
            text_parameters = {
                "font": self.font,
                "text": text,
                "normal_text": self.text_colour,
                "normal_text_shadow": self.text_shadow_colour,
                "text_shadow": (1, 0, 0, self.text_shadow_colour, False),
                "text_horiz_alignment": self.text_horiz_alignment,
                "text_vert_alignment": self.text_vert_alignment,
                "text_horiz_alignment_padding": self.text_horiz_alignment_padding,
                "text_vert_alignment_padding": self.text_vert_alignment_padding,
            }
            theming_parameters |= text_parameters

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )

        self._set_image(self.drawable_shape.get_fresh_surface())

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.

        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(
            attribute_name="follow_sprite_offset",
            default_value=(0, 0),
            casting_func=self.tuple_extract,
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            attribute_name="shape",
            default_value="rectangle",
            casting_func=str,
            allowed_values=["rectangle", "rounded_rectangle"],
        ):
            has_any_changed = True

        if self._check_shape_theming_changed(
            defaults={
                "border_width": 1,
                "shadow_width": 2,
                "border_overlap": 1,
                "shape_corner_radius": [2, 2, 2, 2],
            }
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            attribute_name="hover_height", default_value=1, casting_func=int
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            attribute_name="tool_tip_delay", default_value=1.0, casting_func=float
        ):
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(
            "normal_border", self.combined_element_ids
        )
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        bar_unfilled_colour = self.ui_theme.get_colour_or_gradient(
            "unfilled_bar", self.combined_element_ids
        )
        if bar_unfilled_colour != self.bar_unfilled_colour:
            self.bar_unfilled_colour = bar_unfilled_colour
            has_any_changed = True

        bar_filled_colour = self.ui_theme.get_colour_or_gradient(
            "filled_bar", self.combined_element_ids
        )
        if bar_filled_colour != self.bar_filled_colour:
            self.bar_filled_colour = bar_filled_colour
            has_any_changed = True

        if self.status_text():
            font = self.ui_theme.get_font(self.combined_element_ids)
            if font != self.font:
                self.font = font
                has_any_changed = True

            text_shadow_colour = self.ui_theme.get_colour(
                "text_shadow", self.combined_element_ids
            )
            if text_shadow_colour != self.text_shadow_colour:
                self.text_shadow_colour = text_shadow_colour
                has_any_changed = True

            text_colour = self.ui_theme.get_colour_or_gradient(
                "normal_text", self.combined_element_ids
            )
            if text_colour != self.text_colour:
                self.text_colour = text_colour
                has_any_changed = True

        if has_any_changed:
            self.rebuild()
