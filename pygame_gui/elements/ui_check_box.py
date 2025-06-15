from typing import Optional, Union, Dict, Set, Any, List, Tuple, Callable, Type

import pygame

from pygame_gui._constants import UI_CHECK_BOX_CHECKED, UI_CHECK_BOX_UNCHECKED
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IColourGradientInterface,
    IUIElementInterface,
    IGUIFontInterface,
)
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import (
    RectDrawableShape,
    RoundedRectangleShape,
    EllipseDrawableShape,
)
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.core.gui_type_hints import Coordinate, RectLike


class UICheckBox(UIElement):
    """
    A checkbox element that can be toggled on and off. When checked, it displays a checkmark or similar
    indicator. The checkbox can be clicked to toggle its state.

    Features:
    - Three-state support: checked, unchecked, and indeterminate
    - Keyboard accessibility (Space/Enter keys)
    - Customizable check symbols
    - Tooltip support on both checkbox and text label
    - Flexible positioning (coordinates or full rect)
    - Comprehensive theming support

    :param relative_rect: The rectangle that defines the size and position of the checkbox.
                          Also accepts a position Coordinate where the dimensions will default
                          to 20x20 pixels.
    :param text: The text label displayed next to the checkbox.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default.
    :param initial_state: The initial state of the checkbox (True for checked, False for unchecked).
    :param tool_tip_text: Optional tooltip text that appears when hovering over the checkbox.
    :param tool_tip_object_id: Optional object ID for the tooltip for theming purposes.
    :param tool_tip_text_kwargs: Optional keyword arguments for tooltip text formatting.
    """

    def __init__(
        self,
        relative_rect: Union[RectLike, Coordinate],
        text: str,
        manager: Optional[IUIManagerInterface] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
        *,
        initial_state: bool = False,
        tool_tip_text: Optional[str] = None,
        tool_tip_object_id: Optional[ObjectID] = None,
        tool_tip_text_kwargs: Optional[Dict[str, str]] = None,
    ):
        # Handle coordinate positioning like UIButton does
        rel_rect: RectLike = (
            relative_rect
            if (
                isinstance(relative_rect, (pygame.Rect, pygame.FRect))
                or (isinstance(relative_rect, tuple) and len(relative_rect) == 4)
            )
            else pygame.Rect(relative_rect, (20, 20))  # Default 20x20 size
        )

        super().__init__(
            rel_rect,
            manager,
            container,
            starting_height=1,
            layer_thickness=1,
            anchors=anchors,
            visible=visible,
            parent_element=parent_element,
            object_id=object_id,
            element_id=["check_box"],
        )

        # Validate inputs
        if not isinstance(text, str):
            raise ValueError("Checkbox text must be a string")
        if not isinstance(initial_state, bool):
            raise ValueError("Initial state must be a boolean")

        self.text = text
        self.is_checked = initial_state
        self.is_indeterminate = False  # New indeterminate state
        self.is_focused = False
        self.hovered = False
        self.text_label = None  # Initialize to None

        # Set up tooltip support
        self.set_tooltip(tool_tip_text, tool_tip_object_id, tool_tip_text_kwargs)

        # Initialize theme attributes
        self.shape = "rectangle"
        self.background_image = None
        self.border_width = {"left": 1, "right": 1, "top": 1, "bottom": 1}
        self.shadow_width = 2
        self.shape_corner_radius = [2, 2, 2, 2]
        self.colours: Dict[str, Union[pygame.Color, IColourGradientInterface]] = {}

        # Checkbox symbols/images
        self.check_symbol = "✓"
        self.indeterminate_symbol = "−"  # Symbol for indeterminate state
        self.font: Optional[IGUIFontInterface] = None

        # Image support - always use lists internally for consistency
        # This simplifies the code while maintaining backward compatibility in JSON
        self.normal_images: List[pygame.Surface] = []
        self.selected_images: List[pygame.Surface] = []
        self.hovered_images: List[pygame.Surface] = []
        self.disabled_images: List[pygame.Surface] = []

        # Position support for images - tuples of (x, y) where 0.0-1.0 represents relative position
        self.normal_image_positions: List[Tuple[float, float]] = []
        self.selected_image_positions: List[Tuple[float, float]] = []
        self.hovered_image_positions: List[Tuple[float, float]] = []
        self.disabled_image_positions: List[Tuple[float, float]] = []

        # Get text offset from theme
        self.text_offset = 5
        try:
            text_offset_data = self.ui_theme.get_misc_data(
                "text_offset", self.combined_element_ids
            )
            self.text_offset = (
                int(text_offset_data) if isinstance(text_offset_data, (str, int)) else 5
            )
        except (LookupError, ValueError):
            pass

        # Create the text label positioned to the right of the checkbox
        try:
            label_rect = pygame.Rect(
                self.rect.right + self.text_offset, self.rect.top, -1, self.rect.height
            )
            self.text_label = UILabel(
                label_rect,
                text=self.text,
                manager=self.ui_manager,
                container=self.ui_container,
                parent_element=self,
            )

            # Set the same tooltip on the text label as the checkbox
            if tool_tip_text is not None:
                self.text_label.set_tooltip(
                    tool_tip_text, tool_tip_object_id, tool_tip_text_kwargs
                )
        except (LookupError, ValueError) as e:
            # Log the error but don't crash
            print(f"Failed to create text label for checkbox: {e}")
            self.text_label = None

        # Set initial visibility to match parent
        if not visible:
            self.hide()

        # Load theme data
        self._load_theme_data()

        # Create the drawable shape with text parameters
        theming_parameters = {
            "normal_bg": self.colours["normal_bg"],
            "normal_border": self.colours["normal_border"],
            "disabled_bg": self.colours["disabled_bg"],
            "disabled_border": self.colours["disabled_border"],
            "selected_bg": self.colours["selected_bg"],
            "selected_border": self.colours["selected_border"],
            "hovered_bg": self.colours["hovered_bg"],
            "hovered_border": self.colours["hovered_border"],
            "normal_text": self.colours["normal_text"],
            "normal_text_shadow": self.colours["normal_text"],
            "hovered_text": self.colours["hovered_text"],
            "hovered_text_shadow": self.colours["hovered_text"],
            "disabled_text": self.colours["disabled_text"],
            "disabled_text_shadow": self.colours["disabled_text"],
            "selected_text": self.colours["selected_text"],
            "selected_text_shadow": self.colours["selected_text"],
            # Image support - always use lists internally
            "normal_images": self.normal_images,
            "selected_images": self.selected_images,
            "hovered_images": self.hovered_images,
            "disabled_images": self.disabled_images,
            "border_width": self.border_width,
            "shadow_width": self.shadow_width,
            "shape_corner_radius": self.shape_corner_radius,
            "border_overlap": self.border_overlap,
            "font": self.font,
            "text": self._get_display_symbol(),
            "text_horiz_alignment": "center",
            "text_vert_alignment": "center",
            # Position support for images
            "normal_image_positions": self.normal_image_positions,
            "selected_image_positions": self.selected_image_positions,
            "hovered_image_positions": self.hovered_image_positions,
            "disabled_image_positions": self.disabled_image_positions,
        }

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(
                self.rect,
                theming_parameters,
                ["normal", "hovered", "disabled", "selected"],
                self.ui_manager,
            )
        elif self.shape == "ellipse":
            self.drawable_shape = EllipseDrawableShape(
                self.rect,
                theming_parameters,
                ["normal", "hovered", "disabled", "selected"],
                self.ui_manager,
            )
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(
                self.rect,
                theming_parameters,
                ["normal", "hovered", "disabled", "selected"],
                self.ui_manager,
            )

        # Set initial state
        self._update_visual_state()

        # Set initial image
        self.on_fresh_drawable_shape_ready()

        # Update text label position after everything is set up
        self._update_text_label_position()

    def _get_display_symbol(self) -> str:
        """
        Get the symbol to display based on current state.

        :return: The symbol to display (check, indeterminate, or empty)
        """
        if self.is_indeterminate:
            return self.indeterminate_symbol
        elif self.is_checked:
            return self.check_symbol
        else:
            return ""

    def _update_visual_state(self):
        """
        Update the visual state of the checkbox based on current state.
        """
        if self.drawable_shape is not None:
            # Update the displayed symbol
            self.drawable_shape.set_text(self._get_display_symbol())

            # Update the visual state
            if not self.is_enabled:
                self.drawable_shape.set_active_state("disabled")
            elif self.is_checked or self.is_indeterminate:
                self.drawable_shape.set_active_state("selected")
            elif self.hovered:
                self.drawable_shape.set_active_state("hovered")
            else:
                self.drawable_shape.set_active_state("normal")

    def _load_theme_colour(
        self,
        colour_name: str,
        default_colour: Union[pygame.Color, IColourGradientInterface] = pygame.Color(
            0, 0, 0
        ),
    ) -> Union[pygame.Color, IColourGradientInterface]:
        """Helper method to load a colour from theme data.

        :param colour_name: The name of the colour to load
        :param default_colour: Default colour to return if not found in theme
        :return: The loaded colour or gradient
        """
        try:
            return self.ui_theme.get_colour_or_gradient(
                colour_name, self.combined_element_ids
            )
        except LookupError:
            return default_colour

    def _load_theme_misc_data(
        self,
        data_name: str,
        default_value: Any,
        casting_func: Optional[Callable] = None,
    ) -> Any:
        """Helper method to load miscellaneous theme data.

        :param data_name: The name of the data to load
        :param default_value: Default value to return if not found in theme
        :param casting_func: Optional function to cast the loaded value
        :return: The loaded and optionally cast value
        """
        try:
            value = self.ui_theme.get_misc_data(data_name, self.combined_element_ids)
            if casting_func and value is not None:
                return casting_func(value)
            return value
        except (LookupError, ValueError):
            return default_value

    def _load_theme_data(self):
        """
        Loads theming data from the UI theme.
        """
        # Load colours
        self.colours = {
            "normal_bg": self._load_theme_colour("normal_bg"),
            "normal_border": self._load_theme_colour("normal_border"),
            "hovered_bg": self._load_theme_colour("hovered_bg"),
            "hovered_border": self._load_theme_colour("hovered_border"),
            "disabled_bg": self._load_theme_colour("disabled_bg"),
            "disabled_border": self._load_theme_colour("disabled_border"),
            "selected_bg": self._load_theme_colour("selected_bg"),
            "selected_border": self._load_theme_colour("selected_border"),
            "normal_text": self._load_theme_colour("normal_text"),
            "hovered_text": self._load_theme_colour("hovered_text"),
            "disabled_text": self._load_theme_colour("disabled_text"),
            "selected_text": self._load_theme_colour("selected_text"),
        }

        # Load shape parameters
        self.shape = self._load_theme_misc_data("shape", "rectangle", str)
        if self.shape not in ["rectangle", "rounded_rectangle", "ellipse"]:
            self.shape = "rectangle"

        # Load border parameters
        border_width_data = self._load_theme_misc_data("border_width", 1)
        if isinstance(border_width_data, dict):
            self.border_width = {
                "left": int(border_width_data.get("left", 1)),
                "right": int(border_width_data.get("right", 1)),
                "top": int(border_width_data.get("top", 1)),
                "bottom": int(border_width_data.get("bottom", 1)),
            }
        else:
            # Handle legacy single integer format
            width = (
                int(border_width_data)
                if isinstance(border_width_data, (str, int))
                else 1
            )
            self.border_width = {
                "left": width,
                "right": width,
                "top": width,
                "bottom": width,
            }

        self.shadow_width = self._load_theme_misc_data("shadow_width", 2, int)
        self.border_overlap = self._load_theme_misc_data("border_overlap", 1, int)

        # Load corner radius
        corner_radius = self._load_theme_misc_data("shape_corner_radius", [2, 2, 2, 2])
        if isinstance(corner_radius, list):
            self.shape_corner_radius = [
                int(x) if isinstance(x, (str, int)) else 2 for x in corner_radius
            ]
        elif isinstance(corner_radius, (str, int)):
            radius_val = int(corner_radius)
            self.shape_corner_radius = [radius_val] * 4
        else:
            self.shape_corner_radius = [2, 2, 2, 2]

        # Load checkbox symbols
        self.check_symbol = self._load_theme_misc_data("check_symbol", "✓", str)
        self.indeterminate_symbol = self._load_theme_misc_data(
            "indeterminate_symbol", "−", str
        )

        # Load text offset
        self.text_offset = self._load_theme_misc_data("text_offset", 5, int)

        # Load font
        try:
            self.font = self.ui_theme.get_font(self.combined_element_ids)
            if self.font == self.ui_theme.get_font_dictionary().get_default_font():
                self.font = (
                    self.ui_theme.get_font_dictionary().get_default_symbol_font()
                )
        except LookupError:
            self.font = self.ui_theme.get_font_dictionary().get_default_symbol_font()

        # Load images
        self._load_images_from_theme()

    def _process_state_images(
        self,
        state_name: str,
        normal_images: List[pygame.Surface],
        normal_positions: List[Tuple[float, float]],
    ) -> Tuple[List[pygame.Surface], List[Tuple[float, float]]]:
        """Helper method to process images and positions for a given state.

        :param state_name: The name of the state to process images for (e.g. 'normal', 'hovered')
        :param normal_images: List of images from the normal state to use as fallback
        :param normal_positions: List of positions from the normal state to use as fallback
        :return: Tuple of (list of images, list of positions) for the state
        """
        new_images = []
        new_positions = []

        # Try multi-image format first
        try:
            image_details = self.ui_theme.get_image_details(
                f"{state_name}_images", self.combined_element_ids
            )
            new_images = [detail["surface"] for detail in image_details]
            new_positions = [detail["position"] for detail in image_details]
        except LookupError:
            # Fall back to single image format
            try:
                image_details = self.ui_theme.get_image_details(
                    f"{state_name}_image", self.combined_element_ids
                )
                if image_details:
                    new_images = [detail["surface"] for detail in image_details]
                    new_positions = [detail["position"] for detail in image_details]
            except LookupError:
                pass

        # Handle fallbacks and position defaults
        if not new_images:
            new_images = normal_images.copy()
            new_positions = normal_positions.copy()

        while len(new_positions) < len(new_images):
            new_positions.append((0.5, 0.5))

        return new_images, new_positions

    def _load_images_from_theme(self) -> bool:
        """
        Grabs images for this checkbox from the UI theme if any are set.
        Supports both single image format and multi-image format from JSON,
        but internally always uses lists for consistency.

        :return: True if any of the images have changed since last time they were set.
        """
        changed = False

        # Process normal state first to establish baseline for fallbacks
        normal_images = []
        normal_positions = []

        # First try to load multi-image format for normal state
        try:
            image_details = self.ui_theme.get_image_details(
                "normal_images", self.combined_element_ids
            )
            normal_images = [detail["surface"] for detail in image_details]
            normal_positions = [detail["position"] for detail in image_details]
        except LookupError:
            # Fall back to single image format for normal state
            try:
                image_details = self.ui_theme.get_image_details(
                    "normal_image", self.combined_element_ids
                )
                if image_details:
                    normal_images = [detail["surface"] for detail in image_details]
                    normal_positions = [detail["position"] for detail in image_details]
            except LookupError:
                pass

        # Ensure we have positions for all normal images (default to center if missing)
        while len(normal_positions) < len(normal_images):
            normal_positions.append((0.5, 0.5))

        # Check if normal images have changed
        if (
            normal_images != self.normal_images
            or normal_positions != self.normal_image_positions
        ):
            self.normal_images = normal_images
            self.normal_image_positions = normal_positions
            changed = True

        # Process other states with fallback to normal
        other_states = [
            ("hovered", "hovered_images", "hovered_image_positions"),
            ("selected", "selected_images", "selected_image_positions"),
            ("disabled", "disabled_images", "disabled_image_positions"),
        ]

        for state_name, images_attr_name, positions_attr_name in other_states:
            new_images, new_positions = self._process_state_images(
                state_name, normal_images, normal_positions
            )

            # Check if images have changed
            current_images = getattr(self, images_attr_name)
            current_positions = getattr(self, positions_attr_name, [])
            if new_images != current_images or new_positions != current_positions:
                setattr(self, images_attr_name, new_images)
                setattr(self, positions_attr_name, new_positions)
                changed = True

        return changed

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles processing of events.

        :param event: The event to process.
        :return: Return True if we want to consume this event so it is not passed on to the rest
                 of the UI.
        """
        consumed_event = False

        # Handle mouse clicks with proper scaling
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and hasattr(event, "button")
            and event.button == pygame.BUTTON_LEFT
            and hasattr(event, "pos")
        ):
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(
                event.pos
            )
            if (
                self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1])
                and self.is_enabled
            ):
                self._toggle_state()
                consumed_event = True

        # Handle keyboard events for accessibility
        elif (
            event.type == pygame.KEYDOWN
            and self.is_focused
            and self.is_enabled
            and hasattr(event, "key")
            and event.key in [pygame.K_SPACE, pygame.K_RETURN]
        ):
            self._toggle_state()
            consumed_event = True

        return consumed_event

    def _toggle_state(self):
        """
        Toggles the checkbox state and posts the appropriate event.
        For three-state checkboxes: unchecked -> checked -> unchecked
        For indeterminate checkboxes: indeterminate -> checked -> unchecked -> indeterminate
        """
        if self.is_indeterminate:
            # From indeterminate to checked
            self.is_indeterminate = False
            self.is_checked = True
        elif self.is_checked:
            # From checked to unchecked
            self.is_checked = False
        else:
            # From unchecked to checked
            self.is_checked = True

        self._update_visual_state()

        # Post event only for definitive states (not indeterminate)
        if not self.is_indeterminate:
            event_type = (
                UI_CHECK_BOX_CHECKED if self.is_checked else UI_CHECK_BOX_UNCHECKED
            )
            event_data = {
                "ui_element": self,
                "ui_object_id": self.most_specific_combined_id,
            }
            pygame.event.post(pygame.event.Event(event_type, event_data))

    def get_state(self) -> Union[bool, str]:
        """
        Gets the state of the checkbox.

        :return: True if checked, False if unchecked, 'indeterminate' if indeterminate.
        """
        if self.is_indeterminate:
            return "indeterminate"
        return self.is_checked

    def set_state(self, new_state: Union[bool, str]):
        """
        Sets the state of the checkbox.

        :param new_state: True for checked, False for unchecked, 'indeterminate' for indeterminate state.
        """
        old_checked = self.is_checked
        old_indeterminate = self.is_indeterminate

        if new_state == "indeterminate":
            self.is_checked = False
            self.is_indeterminate = True
        elif isinstance(new_state, bool):
            self.is_checked = new_state
            self.is_indeterminate = False
        else:
            raise ValueError("State must be True, False, or 'indeterminate'")

        # Only update if state actually changed
        if old_checked != self.is_checked or old_indeterminate != self.is_indeterminate:
            self._update_visual_state()

            # Post event only for definitive state changes (not indeterminate)
            if not self.is_indeterminate:
                event_type = (
                    UI_CHECK_BOX_CHECKED if self.is_checked else UI_CHECK_BOX_UNCHECKED
                )
                event_data = {
                    "ui_element": self,
                    "ui_object_id": self.most_specific_combined_id,
                }
                pygame.event.post(pygame.event.Event(event_type, event_data))

    def set_indeterminate(self, indeterminate: bool = True):
        """
        Sets the checkbox to indeterminate state.

        :param indeterminate: True to set indeterminate, False to clear indeterminate state.
        """
        if indeterminate:
            self.set_state("indeterminate")
        else:
            # If clearing indeterminate, default to unchecked
            self.set_state(False)

    def is_state_indeterminate(self) -> bool:
        """
        Check if the checkbox is in indeterminate state.

        :return: True if indeterminate, False otherwise.
        """
        return self.is_indeterminate

    def set_text(self, text: str) -> None:
        """
        Sets the text displayed next to the checkbox.

        :param text: The text to display.
        """
        if not isinstance(text, str):
            raise ValueError("Checkbox text must be a string")

        self.text = text
        if self.text_label is not None:
            self.text_label.set_text(text)

    def set_check_symbol(self, symbol: str) -> None:
        """
        Sets the symbol used to indicate a checked state.

        :param symbol: The symbol to use for checked state.
        """
        if symbol != self.check_symbol:
            self.check_symbol = symbol
            # Update display if currently checked
            if self.is_checked and self.drawable_shape is not None:
                self.drawable_shape.set_text(self._get_display_symbol())

    def set_indeterminate_symbol(self, symbol: str) -> None:
        """
        Sets the symbol used to indicate an indeterminate state.

        :param symbol: The symbol to use for indeterminate state.
        """
        if symbol != self.indeterminate_symbol:
            self.indeterminate_symbol = symbol
            # Update display if currently indeterminate
            if self.is_indeterminate and self.drawable_shape is not None:
                self.drawable_shape.set_text(self._get_display_symbol())

    def set_tooltip(
        self,
        text: Optional[str] = None,
        object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        delay: Optional[float] = None,
        wrap_width: Optional[int] = None,
    ):
        """
        Setup floating tool tip data for this UI element and its text label.

        :param text: the text for the tool tip.
        :param object_id: an object ID for the tooltip - useful for theming
        :param text_kwargs: key word arguments for the tool tip text
        :param delay: how long it takes the tooltip to appear when statically hovering the UI element
        :param wrap_width: how wide the tooltip will grow before wrapping.
        """
        # Set tooltip on the checkbox itself
        super().set_tooltip(text, object_id, text_kwargs, delay, wrap_width)

        # Also set the same tooltip on the text label
        if self.text_label is not None:
            self.text_label.set_tooltip(text, object_id, text_kwargs, delay, wrap_width)

    def show(self):
        """
        Shows the checkbox and its text label if they were hidden.
        """
        super().show()
        if self.text_label is not None:
            self.text_label.show()

    def hide(self):
        """
        Hides the checkbox and its text label.
        """
        super().hide()
        if self.text_label is not None:
            self.text_label.hide()

    def disable(self):
        """
        Disables the checkbox and its text label, preventing interaction.
        """
        if self.is_enabled and self.drawable_shape is not None:
            self.drawable_shape.set_active_state("disabled")
        super().disable()
        if self.text_label is not None:
            self.text_label.disable()

    def enable(self):
        """
        Enables the checkbox and its text label, allowing interaction.
        """
        if not self.is_enabled and self.drawable_shape is not None:
            if self.is_checked or self.is_indeterminate:
                self.drawable_shape.set_active_state("selected")
            else:
                self.drawable_shape.set_active_state("normal")
        super().enable()
        if self.text_label is not None:
            self.text_label.enable()

    def on_hovered(self):
        """
        Called when this element is hovered. Updates the hover state.
        """
        super().on_hovered()  # This handles tooltip creation and hover_time
        if self.is_enabled and not self.is_checked and self.drawable_shape is not None:
            self.drawable_shape.set_active_state("hovered")

    def on_unhovered(self):
        """
        Called when this element is no longer hovered. Updates the hover state.
        """
        super().on_unhovered()  # This handles tooltip cleanup
        if self.is_enabled and self.drawable_shape is not None:
            if self.is_checked or self.is_indeterminate:
                self.drawable_shape.set_active_state("selected")
            else:
                self.drawable_shape.set_active_state("normal")

    def can_hover(self) -> bool:
        """
        Tests whether we can trigger the hover state for this checkbox.

        :return: True if we are able to hover this checkbox.
        """
        return self.is_enabled and self.alive()

    def focus(self):
        """
        Called when this element is focused.
        """
        self.is_focused = True

    def unfocus(self):
        """
        Called when this element loses focus.
        """
        self.is_focused = False

    def can_focus(self) -> bool:
        """
        Tests whether this checkbox can be focused.

        :return: True if this checkbox can be focused.
        """
        return self.is_enabled and self.alive()

    def get_focus_set(self) -> Set[Any]:
        """
        Gets the focus set for this checkbox, which includes both the checkbox and its text label.

        :return: A set containing this checkbox and its text label.
        """
        focus_set: Set[Any] = {self}
        if self.text_label is not None:
            focus_set = focus_set.union({self.text_label})
        return focus_set

    def kill(self):
        """
        Overrides the standard kill method to also kill the text label.
        """
        if self.text_label is not None:
            self.text_label.kill()
        super().kill()

    def on_fresh_drawable_shape_ready(self):
        """
        Called when our drawable shape has finished rebuilding the active surface.
        """
        if self.drawable_shape is not None:
            self._set_image(self.drawable_shape.get_fresh_surface())

    def get_object_id(self) -> Union[str, None]:
        """
        Gets the object ID of the checkbox.

        :return: The object ID or None if no ID is set.
        """
        return self.object_ids[-1] if self.object_ids else None

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        # Check for shape changes
        if self._check_misc_theme_data_changed(
            attribute_name="shape",
            default_value="rectangle",
            casting_func=str,
            allowed_values=["rectangle", "rounded_rectangle"],
        ):
            has_any_changed = True

        # Check for shape theming changes
        if self._check_shape_theming_changed(
            defaults={
                "border_width": {"left": 1, "right": 1, "top": 1, "bottom": 1},
                "shadow_width": 2,
                "border_overlap": 1,
                "shape_corner_radius": [2, 2, 2, 2],
            }
        ):
            has_any_changed = True

        # Check for tool tip delay changes
        if self._check_misc_theme_data_changed(
            attribute_name="tool_tip_delay", default_value=1.0, casting_func=float
        ):
            has_any_changed = True

        # Check for text positioning changes
        if self._check_misc_theme_data_changed(
            attribute_name="text_offset", default_value=5, casting_func=int
        ):
            has_any_changed = True

        # Check for checkbox size changes
        if self._check_misc_theme_data_changed(
            attribute_name="checkbox_height", default_value=-1, casting_func=int
        ):
            has_any_changed = True

        # Check colour changes
        colours = {
            "normal_bg": self.ui_theme.get_colour_or_gradient(
                "normal_bg", self.combined_element_ids
            ),
            "normal_border": self.ui_theme.get_colour_or_gradient(
                "normal_border", self.combined_element_ids
            ),
            "hovered_bg": self.ui_theme.get_colour_or_gradient(
                "hovered_bg", self.combined_element_ids
            ),
            "hovered_border": self.ui_theme.get_colour_or_gradient(
                "hovered_border", self.combined_element_ids
            ),
            "disabled_bg": self.ui_theme.get_colour_or_gradient(
                "disabled_bg", self.combined_element_ids
            ),
            "disabled_border": self.ui_theme.get_colour_or_gradient(
                "disabled_border", self.combined_element_ids
            ),
            "selected_bg": self.ui_theme.get_colour_or_gradient(
                "selected_bg", self.combined_element_ids
            ),
            "selected_border": self.ui_theme.get_colour_or_gradient(
                "selected_border", self.combined_element_ids
            ),
            "normal_text": self.ui_theme.get_colour_or_gradient(
                "normal_text", self.combined_element_ids
            ),
            "hovered_text": self.ui_theme.get_colour_or_gradient(
                "hovered_text", self.combined_element_ids
            ),
            "disabled_text": self.ui_theme.get_colour_or_gradient(
                "disabled_text", self.combined_element_ids
            ),
            "selected_text": self.ui_theme.get_colour_or_gradient(
                "selected_text", self.combined_element_ids
            ),
        }

        if not hasattr(self, "colours") or colours != getattr(self, "colours", {}):
            self.colours = colours
            has_any_changed = True

        # Check font changes
        try:
            font = self.ui_theme.get_font(self.combined_element_ids)
            if font == self.ui_theme.get_font_dictionary().get_default_font():
                font = self.ui_theme.get_font_dictionary().get_default_symbol_font()
            if not hasattr(self, "font") or font != getattr(self, "font", None):
                self.font = font
                has_any_changed = True
        except LookupError:
            default_font = self.ui_theme.get_font_dictionary().get_default_symbol_font()
            if not hasattr(self, "font") or default_font != getattr(self, "font", None):
                self.font = default_font
                has_any_changed = True

        # Check for image changes
        if self._load_images_from_theme():
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def set_position(self, position):
        """
        Sets the absolute screen position of this checkbox, updating the text label at the same time.

        :param position: The absolute screen position to set.
        """
        super().set_position(position)
        self._update_text_label_position()

    def set_relative_position(self, position):
        """
        Sets the relative screen position of this checkbox, updating the text label at the same time.

        :param position: The relative screen position to set.
        """
        super().set_relative_position(position)
        self._update_text_label_position()

    def set_dimensions(self, dimensions, clamp_to_container=False):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        super().set_dimensions(dimensions, clamp_to_container)
        self._update_text_label_position()

    def _update_text_label_position(self):
        """
        Updates the text label position based on the current checkbox position and text offset.
        """
        if self.text_label is not None:
            # Position the label to the right of the checkbox
            label_x = self.rect.right + self.text_offset
            label_y = self.rect.top

            # Convert to relative position within the container
            if self.ui_container:
                label_x -= self.ui_container.rect.left
                label_y -= self.ui_container.rect.top

            self.text_label.set_relative_position((label_x, label_y))

    def _create_drawable_shape(
        self, shape_type: str, rect: pygame.Rect, theming_parameters: Dict
    ) -> Union[RectDrawableShape, RoundedRectangleShape, EllipseDrawableShape]:
        """
        Factory method to create the appropriate drawable shape based on shape type.

        :param shape_type: The type of shape to create ('rectangle', 'ellipse', or 'rounded_rectangle')
        :param rect: The rectangle defining the shape's dimensions
        :param theming_parameters: Dictionary of theming parameters for the shape
        :return: The created drawable shape
        """
        shape_classes: Dict[
            str,
            Type[Union[RectDrawableShape, RoundedRectangleShape, EllipseDrawableShape]],
        ] = {
            "rectangle": RectDrawableShape,
            "ellipse": EllipseDrawableShape,
            "rounded_rectangle": RoundedRectangleShape,
        }

        shape_class = shape_classes.get(shape_type)
        if shape_class is None:
            shape_class = RectDrawableShape  # Default fallback

        return shape_class(
            rect,
            theming_parameters,
            ["normal", "hovered", "disabled", "selected"],
            self.ui_manager,
        )

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this checkbox.
        """
        # Get theming parameters
        theming_parameters = {
            "normal_bg": self.colours.get(
                "normal_bg",
                self.ui_theme.get_colour_or_gradient(
                    "normal_bg", self.combined_element_ids
                ),
            ),
            "normal_border": self.colours.get(
                "normal_border",
                self.ui_theme.get_colour_or_gradient(
                    "normal_border", self.combined_element_ids
                ),
            ),
            "disabled_bg": self.colours.get(
                "disabled_bg",
                self.ui_theme.get_colour_or_gradient(
                    "disabled_bg", self.combined_element_ids
                ),
            ),
            "disabled_border": self.colours.get(
                "disabled_border",
                self.ui_theme.get_colour_or_gradient(
                    "disabled_border", self.combined_element_ids
                ),
            ),
            "selected_bg": self.colours.get(
                "selected_bg",
                self.ui_theme.get_colour_or_gradient(
                    "selected_bg", self.combined_element_ids
                ),
            ),
            "selected_border": self.colours.get(
                "selected_border",
                self.ui_theme.get_colour_or_gradient(
                    "selected_border", self.combined_element_ids
                ),
            ),
            "hovered_bg": self.colours.get(
                "hovered_bg",
                self.ui_theme.get_colour_or_gradient(
                    "hovered_bg", self.combined_element_ids
                ),
            ),
            "hovered_border": self.colours.get(
                "hovered_border",
                self.ui_theme.get_colour_or_gradient(
                    "hovered_border", self.combined_element_ids
                ),
            ),
            "normal_text": self.colours.get(
                "normal_text",
                self.ui_theme.get_colour_or_gradient(
                    "normal_text", self.combined_element_ids
                ),
            ),
            "normal_text_shadow": self.colours.get(
                "normal_text",
                self.ui_theme.get_colour_or_gradient(
                    "normal_text", self.combined_element_ids
                ),
            ),
            "hovered_text": self.colours.get(
                "hovered_text",
                self.ui_theme.get_colour_or_gradient(
                    "hovered_text", self.combined_element_ids
                ),
            ),
            "hovered_text_shadow": self.colours.get(
                "hovered_text",
                self.ui_theme.get_colour_or_gradient(
                    "hovered_text", self.combined_element_ids
                ),
            ),
            "disabled_text": self.colours.get(
                "disabled_text",
                self.ui_theme.get_colour_or_gradient(
                    "disabled_text", self.combined_element_ids
                ),
            ),
            "disabled_text_shadow": self.colours.get(
                "disabled_text",
                self.ui_theme.get_colour_or_gradient(
                    "disabled_text", self.combined_element_ids
                ),
            ),
            "selected_text": self.colours.get(
                "selected_text",
                self.ui_theme.get_colour_or_gradient(
                    "selected_text", self.combined_element_ids
                ),
            ),
            "selected_text_shadow": self.colours.get(
                "selected_text",
                self.ui_theme.get_colour_or_gradient(
                    "selected_text", self.combined_element_ids
                ),
            ),
            # Image support - always use lists internally
            "normal_images": self.normal_images,
            "selected_images": self.selected_images,
            "hovered_images": self.hovered_images,
            "disabled_images": self.disabled_images,
            # Position support for images
            "normal_image_positions": self.normal_image_positions,
            "selected_image_positions": self.selected_image_positions,
            "hovered_image_positions": self.hovered_image_positions,
            "disabled_image_positions": self.disabled_image_positions,
            "border_width": getattr(self, "border_width", 1),
            "shadow_width": getattr(self, "shadow_width", 2),
            "shape_corner_radius": getattr(self, "shape_corner_radius", [2, 2, 2, 2]),
            "border_overlap": getattr(self, "border_overlap", 1),
            "font": getattr(self, "font", None),
            "text": self._get_display_symbol(),
            "text_horiz_alignment": "center",
            "text_vert_alignment": "center",
        }

        # Create appropriate drawable shape using factory method
        self.drawable_shape = self._create_drawable_shape(
            self.shape, self.rect, theming_parameters
        )

        # Set initial state
        self._update_visual_state()

        # Update image
        self.on_fresh_drawable_shape_ready()

    def get_current_images(self) -> List[pygame.Surface]:
        """
        Get the current images for the checkbox's current state.
        Returns a list of surfaces.

        :return: List of pygame.Surface objects for the current state
        """
        if not self.is_enabled:
            return self.disabled_images
        elif self.is_checked or self.is_indeterminate:
            return self.selected_images
        elif self.hovered:
            return self.hovered_images
        else:
            return self.normal_images

    def is_multi_image_mode(self) -> bool:
        """
        Check if the checkbox is currently using multi-image mode.

        :return: True if using multiple images per state, False if using single images
        """
        # Check if any state has more than one image
        return (
            len(self.normal_images) > 1
            or len(self.hovered_images) > 1
            or len(self.selected_images) > 1
            or len(self.disabled_images) > 1
        )

    def get_image_count(self) -> int:
        """
        Get the number of images in the current state.

        :return: Number of images for the current checkbox state
        """
        return len(self.get_current_images())

    def get_images_by_state(self, state: str) -> List[pygame.Surface]:
        """
        Get images for a specific checkbox state.

        :param state: The state to get images for ('normal', 'hovered', 'selected', 'disabled')
        :return: List of pygame.Surface objects for the specified state
        """
        state_mapping = {
            "normal": self.normal_images,
            "hovered": self.hovered_images,
            "selected": self.selected_images,
            "disabled": self.disabled_images,
        }
        return state_mapping.get(state, [])
