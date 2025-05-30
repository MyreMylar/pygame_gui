from typing import Union, Dict, Optional, Iterator, List, Tuple

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IContainerAndContainerLike,
    IColourGradientInterface,
)

from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.core.gui_type_hints import Coordinate, RectLike


class UIPanel(UIElement, IContainerLikeInterface):
    """
    A rectangular panel that holds a UI container and is designed to overlap other elements. It
    acts a little like a window that is not shuffled about in a stack - instead remaining at the
    same layer distance from the container it was initially placed in.

    It's primary purpose is for things like involved HUDs in games that want to always sit on top
    of UI elements that may be present 'inside' the game world (e.g. player health bars). By
    creating a UI Panel at a height above the highest layer used by the game world's UI elements
    we can ensure that all elements added to the panel are always above the fray.

    :param relative_rect: The positioning and sizing rectangle for the panel. See the layout
                          guide for details.
    :param starting_height: How many layers above its container to place this panel on.
    :param manager: The GUI manager that handles drawing and updating the UI and interactions
                    between elements. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param margins: Controls the distance between the edge of the panel and where it's
                    container should begin.
    :param container: The container this panel is inside - distinct from this panel's own
                      container.
    :param parent_element: A hierarchical 'parent' used for signifying belonging and used in
                           theming and events.
    :param object_id: An identifier that can be used to help distinguish this particular panel
                      from others.
    :param anchors: Used to layout elements and dictate what the relative_rect is relative to.
                    Defaults to the top left.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        starting_height: int = 1,
        manager: Optional[IUIManagerInterface] = None,
        *,
        element_id: str = "panel",
        margins: Optional[Dict[str, int]] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
    ):
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor - set the container size later
        self.panel_container = UIContainer(
            pygame.Rect(0, 0, 0, 0),
            manager,
            starting_height=starting_height,
            container=container,
            parent_element=None,
            object_id=ObjectID(object_id="#panel_container", class_id=None),
            anchors=anchors,
            visible=visible,
        )
        super().__init__(
            relative_rect,
            manager,
            container,
            starting_height=starting_height,
            layer_thickness=1,
            anchors=anchors,
            visible=visible,
            parent_element=parent_element,
            object_id=object_id,
            element_id=[element_id],
        )

        # need to reset ids after building panel to include panel as parent element
        # shouldn't affect theming as this container has no theming
        self.panel_container.parent_element = self
        self.panel_container._create_valid_ids(
            container,
            self,
            ObjectID(object_id="#panel_container", class_id=None),
            "container",
        )

        self.background_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            0, 0, 0, 0
        )
        self.border_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            0, 0, 0, 0
        )

        # Image support - always use lists internally for consistency
        self.background_images: List[pygame.Surface] = []

        # Position support for images - tuples of (x, y) where 0.0-1.0 represents relative position
        self.background_image_positions: List[Tuple[float, float]] = []

        self.background_image = None
        self.border_width = {"left": 1, "right": 1, "top": 1, "bottom": 1}
        self.shadow_width = 2
        self.shape = "rectangle"
        self.shape_corner_radius = [2, 2, 2, 2]

        # Auto-scale images theming parameter
        self.auto_scale_images = False

        self.rebuild_from_changed_theme_data()

        if margins is None:
            self.container_margins = {
                "left": self.shadow_width + self.border_width["left"],
                "right": self.shadow_width + self.border_width["right"],
                "top": self.shadow_width + self.border_width["top"],
                "bottom": self.shadow_width + self.border_width["bottom"],
            }
        else:
            self.container_margins = margins

        container_rect = pygame.Rect(
            self.relative_rect.left + self.container_margins["left"],
            self.relative_rect.top + self.container_margins["top"],
            self.relative_rect.width
            - (self.container_margins["left"] + self.container_margins["right"]),
            self.relative_rect.height
            - (self.container_margins["top"] + self.container_margins["bottom"]),
        )

        self.panel_container.set_dimensions(container_rect.size)
        self.panel_container.set_relative_position(container_rect.topleft)

    @staticmethod
    def _scale_image_to_fit(
        image: pygame.Surface, target_size: Tuple[int, int]
    ) -> pygame.Surface:
        """
        Scale an image to fit within the target size while maintaining aspect ratio.
        The image will be scaled to the largest size that fits within the target dimensions.

        :param image: The image surface to scale.
        :param target_size: The target size (width, height) to fit the image within.
        :return: The scaled image surface.
        """
        if image is None:
            return None

        image_width, image_height = image.get_size()
        target_width, target_height = target_size

        # Calculate scale factors for both dimensions
        scale_x = target_width / image_width
        scale_y = target_height / image_height

        # Use the smaller scale factor to ensure the image fits within the target size
        scale = min(scale_x, scale_y)

        # Calculate new dimensions
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # Scale the image
        if new_width > 0 and new_height > 0:
            return pygame.transform.smoothscale(image, (new_width, new_height))
        else:
            return image

    def _set_any_images_from_theme(self) -> bool:
        """
        Grabs background images for this panel from the UI theme if any are set.
        Supports both single image format and multi-image format from JSON,
        but internally always uses lists for consistency.

        :return: True if any of the images have changed since last time they were set.
        """
        changed = False
        new_images = []
        new_positions = []

        # First try to load multi-image format (background_images)
        try:
            image_details = self.ui_theme.get_image_details(
                "background_images", self.combined_element_ids
            )
            new_images = [detail["surface"] for detail in image_details]
            new_positions = [
                detail.get("position", (0.5, 0.5)) for detail in image_details
            ]
        except LookupError:
            # Fall back to single image format (background_image)
            try:
                image_details = self.ui_theme.get_image_details(
                    "background_image", self.combined_element_ids
                )
                if image_details:
                    new_images = [detail["surface"] for detail in image_details]
                    new_positions = [
                        detail.get("position", (0.5, 0.5)) for detail in image_details
                    ]
            except LookupError:
                # No image found for this state
                pass

        # Apply auto-scaling if enabled
        if new_images and self.auto_scale_images:
            scaled_images = []
            for img in new_images:
                scaled_img = self._scale_image_to_fit(img, self.rect.size)
                scaled_images.append(scaled_img)
            new_images = scaled_images

        # Ensure we have positions for all images (default to center if missing)
        while len(new_positions) < len(new_images):
            new_positions.append((0.5, 0.5))

        # Check if images or positions have changed
        if (
            new_images != self.background_images
            or new_positions != self.background_image_positions
        ):
            self.background_images = new_images
            self.background_image_positions = new_positions
            changed = True

        return changed

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived
        classes but also has a little functionality to make sure the panel's layer 'thickness' is
        accurate and to handle window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if self.get_container().get_thickness() != self.layer_thickness:
            self.layer_thickness = self.get_container().get_thickness()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.

        :return: Should return True if this element consumes this event.

        """
        consumed_event = False
        if (
            self is not None
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button
            in [pygame.BUTTON_LEFT, pygame.BUTTON_RIGHT, pygame.BUTTON_MIDDLE]
        ):
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(
                event.pos
            )
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                consumed_event = True

        return consumed_event

    def get_container(self) -> IContainerAndContainerLike:
        """
        Returns the container that should contain all the UI elements in this panel.

        :return UIContainer: The panel's container.

        """

        return self.panel_container

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this panel.

        """
        self.get_container().kill()
        super().kill()

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Set the size of this panel and then re-sizes and shifts the contents of the panel container
        to fit the new size.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        # Don't use a basic gate on this set dimensions method because the container may be a
        # different size to the window
        super().set_dimensions(dimensions)

        # Handle auto-scaling of background images when panel size changes
        if self.auto_scale_images and self.background_images:
            scaled_images = []
            for img in self.background_images:
                scaled_img = self._scale_image_to_fit(img, self.rect.size)
                scaled_images.append(scaled_img)
            self.background_images = scaled_images
            self.rebuild()

        new_container_dimensions = (
            self.relative_rect.width
            - (self.container_margins["left"] + self.container_margins["right"]),
            self.relative_rect.height
            - (self.container_margins["top"] + self.container_margins["bottom"]),
        )
        if new_container_dimensions != self.get_container().get_size():
            self.get_container().set_dimensions(new_container_dimensions)

    def set_relative_position(self, position: Coordinate):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        super().set_relative_position(position)

        container_top_left = (
            self.relative_rect.left + self.container_margins["left"],
            self.relative_rect.top + self.container_margins["top"],
        )

        self.get_container().set_relative_position(container_top_left)

    def set_position(self, position: Coordinate):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """
        super().set_position(position)

        container_top_left = (
            self.relative_rect.left + self.container_margins["left"],
            self.relative_rect.top + self.container_margins["top"],
        )

        self.get_container().set_relative_position(container_top_left)

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the
        panel's drawable shape.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

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

        def parse_to_bool(str_data: str):
            return bool(int(str_data))

        # Load auto_scale_images parameter BEFORE loading images so scaling can be applied
        if self._check_misc_theme_data_changed(
            attribute_name="auto_scale_images",
            default_value=False,
            casting_func=parse_to_bool,
        ):
            has_any_changed = True

        # Use the enhanced image loading system
        if self._set_any_images_from_theme():
            has_any_changed = True

        # misc
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

        if has_any_changed:
            self.rebuild()

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this panel.
        """
        theming_parameters = {
            "normal_bg": self.background_colour,
            "normal_border": self.border_colour,
            "normal_images": self.background_images,
            "normal_image_positions": self.background_image_positions,  # Add positions
            "border_width": self.border_width,
            "shadow_width": self.shadow_width,
            "shape_corner_radius": self.shape_corner_radius,
            "border_overlap": self.border_overlap,
        }

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )

        self.on_fresh_drawable_shape_ready()

    def disable(self):
        """
        Disables all elements in the panel, so they are no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self.panel_container is not None:
                self.panel_container.disable()

    def enable(self):
        """
        Enables all elements in the panel, so they are interactive again.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.panel_container is not None:
                self.panel_container.enable()

    def show(self, show_contents: bool = True):
        """
        In addition to the base UIElement.show() - call show() of owned container - panel_container.

        :param show_contents: whether to also show the contents of the panel. Defaults to True.
        """
        super().show()
        if self.panel_container is not None:
            self.panel_container.show(show_contents)

    def hide(self, hide_contents: bool = True):
        """
        In addition to the base UIElement.hide() - call hide() of owned container - panel_container.

        :param hide_contents: whether to also hide the contents of the panel. Defaults to True.
        """
        if not self.visible:
            return

        if self.panel_container is not None:
            self.panel_container.hide(hide_contents)
        super().hide()

    def __iter__(self) -> Iterator[IUIElementInterface]:
        """
        Iterates over the elements within the container.
        :return Iterator: An iterator over the elements within the container.
        """
        return iter(self.get_container())

    def __contains__(self, item: IUIElementInterface) -> bool:
        """
        Checks if the given element is contained within the container.
        :param item: The element to check for containment.
        :return bool: Return True if the element is found, False otherwise.
        """
        return item in self.get_container()

    def are_contents_hovered(self) -> bool:
        """
        Are any of the elements in the container hovered? Used for handling mousewheel events.

        :return: True if one of the elements is hovered, False otherwise.
        """
        any_hovered = False
        for element in self:
            element_focus_set = element.get_focus_set()
            if element_focus_set is not None and any(
                sub_element.hovered for sub_element in element_focus_set
            ):
                any_hovered = True
            elif isinstance(element, IContainerLikeInterface):
                any_hovered = element.are_contents_hovered()

            if any_hovered:
                break
        return any_hovered

    def set_anchors(
        self, anchors: Optional[Dict[str, Union[str, IUIElementInterface]]]
    ) -> None:
        super().set_anchors(anchors)
        if self.panel_container is not None:
            self.panel_container.set_anchors(anchors)

    def get_current_images(self) -> List[pygame.Surface]:
        """
        Get the current background images for the panel.
        Returns a list of surfaces.

        :return: List of pygame.Surface objects for the panel background
        """
        return self.background_images

    def is_multi_image_mode(self) -> bool:
        """
        Check if the panel is currently using multi-image mode.

        :return: True if using multiple background images, False if using single image
        """
        return len(self.background_images) > 1

    def get_image_count(self) -> int:
        """
        Get the number of background images.

        :return: Number of background images for the panel
        """
        return len(self.background_images)

    def set_background_images(self, images: List[pygame.Surface]):
        """
        Set the background images for the panel.

        :param images: List of pygame.Surface objects to use as background images
        """
        if images != self.background_images:
            self.background_images = images.copy() if images else []

            # Apply auto-scaling if enabled
            if self.background_images and self.auto_scale_images:
                scaled_images = []
                for img in self.background_images:
                    scaled_img = self._scale_image_to_fit(img, self.rect.size)
                    scaled_images.append(scaled_img)
                self.background_images = scaled_images

            self.rebuild()

    def add_background_image(self, image: pygame.Surface):
        """
        Add a background image to the panel's image list.

        :param image: pygame.Surface object to add to the background images
        """
        if image is not None:
            # Apply auto-scaling if enabled
            if self.auto_scale_images:
                image = self._scale_image_to_fit(image, self.rect.size)

            self.background_images.append(image)
            self.rebuild()

    def remove_background_image(self, index: int) -> bool:
        """
        Remove a background image at the specified index.

        :param index: Index of the image to remove
        :return: True if image was removed, False if index was invalid
        """
        if 0 <= index < len(self.background_images):
            self.background_images.pop(index)
            self.rebuild()
            return True
        return False

    def clear_background_images(self):
        """
        Remove all background images from the panel.
        """
        if self.background_images:
            self.background_images.clear()
            self.rebuild()

    def get_background_image_at_index(self, index: int) -> Optional[pygame.Surface]:
        """
        Get a specific background image by index.

        :param index: Index of the image to retrieve
        :return: pygame.Surface object at the specified index, or None if index is invalid
        """
        if 0 <= index < len(self.background_images):
            return self.background_images[index]
        return None

    def set_auto_scale_images(self, auto_scale: bool):
        """
        Enable or disable automatic scaling of background images to fit the panel size.

        :param auto_scale: True to enable auto-scaling, False to disable
        """
        if auto_scale != self.auto_scale_images:
            self.auto_scale_images = auto_scale

            # If enabling auto-scale, rescale existing images
            if auto_scale and self.background_images:
                scaled_images = []
                for img in self.background_images:
                    scaled_img = self._scale_image_to_fit(img, self.rect.size)
                    scaled_images.append(scaled_img)
                self.background_images = scaled_images
                self.rebuild()

    def get_auto_scale_images(self) -> bool:
        """
        Get the current auto-scale images setting.

        :return: True if auto-scaling is enabled, False otherwise
        """
        return self.auto_scale_images

    def get_current_image_positions(self) -> List[Tuple[float, float]]:
        """
        Get the current image positions for the panel.
        Returns a list of position tuples.

        :return: List of (x, y) position tuples for the background images
        """
        return self.background_image_positions

    def set_image_positions(self, positions: List[Tuple[float, float]]):
        """
        Set the positions for all background images.

        :param positions: List of (x, y) tuples where x and y are between 0.0 and 1.0
        """
        # Only keep positions up to the number of images we have
        if len(positions) > len(self.background_images):
            positions = positions[: len(self.background_images)]

        self.background_image_positions = positions.copy()
        # Ensure we have positions for all images
        while len(self.background_image_positions) < len(self.background_images):
            self.background_image_positions.append((0.5, 0.5))
        self.rebuild()

    def set_image_position(self, index: int, position: Tuple[float, float]) -> bool:
        """
        Set the position of a specific background image.

        :param index: Index of the image to position
        :param position: (x, y) tuple where x and y are between 0.0 and 1.0
        :return: True if position was set, False if index was invalid
        """
        if 0 <= index < len(self.background_images):
            while len(self.background_image_positions) <= index:
                self.background_image_positions.append((0.5, 0.5))
            self.background_image_positions[index] = position
            self.rebuild()
            return True
        return False
