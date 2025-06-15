from typing import Optional, Union, Dict, List, Tuple

import pygame

from pygame_gui.core import UIElement, UIContainer, ObjectID
from pygame_gui.core.gui_type_hints import Coordinate
from pygame_gui.core.interfaces import (
    IUIElementInterface,
    IUIManagerInterface,
    IContainerLikeInterface,
)
from pygame_gui.core.gui_type_hints import RectLike


class UIAutoResizingContainer(UIContainer):
    """
    A container like UI element that updates its size as elements within it change size, or new elements are added

    :param relative_rect: The starting size and relative position of the container.
    :param min_dimensions: The values which define the minimum dimensions for the container.
                           Defaults to the None (current rect)
    :param max_dimensions: The values which define the maximum dimensions for the container.
                           Defaults to the None (unbounded)
    :param resize_left: Should the left side be resized?
    :param resize_right: Should the right side be resized?
    :param resize_top: Should the top side be resized?
    :param resize_bottom: Should the bottom side be resized?
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param parent_element: A parent element for this container. Defaults to None, or the
                           container if you've set that.
    :param object_id: An object ID for this element.
    :param anchors: Layout anchors in a dictionary.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        min_dimensions: Optional[Union[pygame.Rect, Tuple[int, int]]] = None,
        max_dimensions: Optional[Union[pygame.Rect, Tuple[int, int]]] = None,
        resize_left: bool = True,
        resize_right: bool = True,
        resize_top: bool = True,
        resize_bottom: bool = True,
        manager: Optional[IUIManagerInterface] = None,
        *,
        starting_height: int = 1,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
        include_min_dimension_sized_root_pos_element: bool = True,
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            element_id=["auto_resizing_container"],
        )

        if min_dimensions is None:
            self.min_dimensions: Union[Tuple[int, int], Tuple[float, float]] = (
                self.get_relative_rect().size
            )

        else:
            if isinstance(min_dimensions, pygame.Rect):
                self.min_dimensions = min_dimensions.size
            else:
                self.min_dimensions = min_dimensions

        if isinstance(max_dimensions, pygame.Rect):
            self.max_dimensions: Optional[
                Union[Tuple[int, int], Tuple[float, float]]
            ] = max_dimensions.size
        else:
            self.max_dimensions = max_dimensions

        self.resize_left = resize_left
        self.resize_right = resize_right
        self.resize_top = resize_top
        self.resize_bottom = resize_bottom

        # Elements which affect the corresponding edge of the container
        self.left_element: Optional[IUIElementInterface] = None
        self.right_element: Optional[IUIElementInterface] = None
        self.top_element: Optional[IUIElementInterface] = None
        self.bottom_element: Optional[IUIElementInterface] = None

        # Right to left is not the inverse of left to right because of varying sizes of elements
        self.left_to_right_elements: List[IUIElementInterface] = []
        self.right_to_left_elements: List[IUIElementInterface] = []
        self.top_to_bottom_elements: List[IUIElementInterface] = []
        self.bottom_to_top_elements: List[IUIElementInterface] = []

        self.should_update_sorting = False
        self.should_update_rect_edges = False
        self.has_recently_updated_dimensions = False

        self._container_root_element: Optional[UIElement] = None
        if include_min_dimension_sized_root_pos_element:
            self._container_root_element = UIElement(
                pygame.Rect((0, 0), self.min_dimensions),
                manager,
                self,
                starting_height=starting_height,
                layer_thickness=0,
            )

    def add_element(self, element: IUIElementInterface) -> None:
        """
        Add a UIElement to the container. The UIElement's relative_rect parameter will be relative to
        this container. Overridden to also update dimensions.

        :param element: A UIElement to add to this container.
        :return: None
        """

        # Add the element
        super().add_element(element)

        # Update sorting and dimensions
        self.should_update_sorting = True
        self.should_update_rect_edges = True

    def remove_element(self, element: IUIElementInterface) -> None:
        """
        Remove a UIElement from this container. Overridden to handle auto-resizing.

        :param element: A UIElement to remove from this container.
        :return: None
        """
        # Store element's rect for later comparison
        element_rect = element.get_abs_rect()

        # Remove the element from all tracking lists
        if element in self.left_to_right_elements:
            self.left_to_right_elements.remove(element)

        if element in self.right_to_left_elements:
            self.right_to_left_elements.remove(element)

        if element in self.top_to_bottom_elements:
            self.top_to_bottom_elements.remove(element)

        if element in self.bottom_to_top_elements:
            self.bottom_to_top_elements.remove(element)

        # Update extreme elements before calling super's remove_element
        if element in (
            self.left_element,
            self.right_element,
            self.top_element,
            self.bottom_element,
        ):
            # Remove the element from extreme elements
            if element == self.left_element:
                self.left_element = None
            if element == self.right_element:
                self.right_element = None
            if element == self.top_element:
                self.top_element = None
            if element == self.bottom_element:
                self.bottom_element = None

            # Update extreme elements after removal
            self._update_extreme_elements()

        # Call super's remove_element
        super().remove_element(element)

        # Update dimensions to handle auto-resizing
        self.should_update_rect_edges = True

        # Update dimensions immediately if element was at the edges
        if element_rect is not None:
            container_rect = self.get_abs_rect()
            if (
                element_rect.left <= container_rect.left
                or element_rect.right >= container_rect.right
                or element_rect.top <= container_rect.top
                or element_rect.bottom >= container_rect.bottom
            ):
                self._update_sorting()
                self._update_rect_edges()

    def _get_left_most_point(self) -> int:
        """
        Gets the minimum x value any element has.

        :return: An integer
        """
        # Start with current left edge
        left = int(self.get_abs_rect().left)

        # Check elements
        if self.left_element:
            left = int(self.left_element.get_abs_rect().left)

        return left

    def _get_right_most_point(self) -> int:
        """
        Gets the maximum x value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        # Start with current rect's right edge
        right = int(self.get_abs_rect().right)

        # Check elements
        if self.right_element:
            right = int(self.right_element.get_abs_rect().right)

        return right

    def _get_top_most_point(self) -> int:
        """
        Gets the minimum y value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        top = int(self.get_abs_rect().top)

        if self.top_element:
            top = int(self.top_element.get_abs_rect().top)

        return top

    def _get_bottom_most_point(self) -> int:
        """
        Gets the maximum y value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        # Start with current rect's bottom edge
        bottom = int(self.get_abs_rect().bottom)

        # Check elements
        if self.bottom_element:
            bottom = int(self.bottom_element.get_abs_rect().bottom)

        return bottom

    def _update_sorting(self) -> None:
        """
        Updates the sorting of elements by their positions.

        :return: None
        """
        # Only sort elements that have been fully initialized
        elements = [
            element for element in self.elements if element.get_abs_rect() is not None
        ]

        # Sort elements by their positions
        self.left_to_right_elements = sorted(
            elements, key=(lambda element: element.get_abs_rect().left)
        )
        self.right_to_left_elements = sorted(
            elements, key=(lambda element: element.get_abs_rect().right), reverse=True
        )
        self.top_to_bottom_elements = sorted(
            elements, key=(lambda element: element.get_abs_rect().top)
        )
        self.bottom_to_top_elements = sorted(
            elements, key=(lambda element: element.get_abs_rect().bottom), reverse=True
        )

        # Update extreme elements
        self._update_extreme_elements()

    def _update_extreme_elements(self) -> None:
        """
        Updates which elements are currently responsible for preventing the container from collapsing on each side

        :return: None
        """
        # Store old extreme elements
        old_left = self.left_element
        old_right = self.right_element
        old_top = self.top_element
        old_bottom = self.bottom_element

        # Update extreme elements
        self.left_element = (
            self.left_to_right_elements[0] if self.left_to_right_elements else None
        )
        self.right_element = (
            self.right_to_left_elements[0] if self.right_to_left_elements else None
        )
        self.top_element = (
            self.top_to_bottom_elements[0] if self.top_to_bottom_elements else None
        )
        self.bottom_element = (
            self.bottom_to_top_elements[0] if self.bottom_to_top_elements else None
        )

        # If any extreme elements changed, trigger a dimension update
        if (
            old_left != self.left_element
            or old_right != self.right_element
            or old_top != self.top_element
            or old_bottom != self.bottom_element
        ):
            self.should_update_rect_edges = True

    def _update_rect_edges(self) -> None:
        """
        Updates the sizes of the container

        :return: None
        """
        rect = self.get_abs_rect()

        # Calculate extensions needed
        left_ext: int = (
            int(rect.left - self._get_left_most_point()) if self.resize_left else 0
        )
        right_ext: int = int(
            self._get_right_most_point() - rect.right if self.resize_right else 0
        )
        top_ext: int = (
            int(rect.top - self._get_top_most_point()) if self.resize_top else 0
        )
        bottom_ext: int = int(
            self._get_bottom_most_point() - rect.bottom if self.resize_bottom else 0
        )

        # Calculate total width/height needed
        width = int(rect.width + right_ext + left_ext)
        height = int(rect.height + bottom_ext + top_ext)

        # Handle left and top expansion first
        if left_ext != 0:  # Only expand if we need to move left
            self.width_change_left(left_ext)

        if top_ext != 0:  # Only expand if we need to move up
            self.height_change_top(top_ext)

        # Apply min/max constraints
        if self.min_dimensions is not None:
            width = max(width, int(self.min_dimensions[0]))
            height = max(height, int(self.min_dimensions[1]))

        if self.max_dimensions is not None:
            width = min(width, int(self.max_dimensions[0]))
            height = min(height, int(self.max_dimensions[1]))

        # Only set dimensions if they've changed
        if (width, height) != rect.size:
            self.set_dimensions((width, height))

    def on_contained_elements_changed(self, target: IUIElementInterface) -> None:
        """
        Update the positioning of the contained elements of this container. To be called when one of the contained
        elements may have moved, been resized or changed its anchors.

        :param target: the UI element that has been benn moved resized or changed its anchors.
        :return: None
        """
        super().on_contained_elements_changed(target)

        self._update_sorting()
        self._update_extreme_elements()

        self.should_update_rect_edges = True

    def update(self, time_delta: float) -> None:
        """
        Updates the container's size based upon the elements inside.

        Call this function if you have added or removed an element from this container and want
        to update the size in the same frame, otherwise it will update in the next frame.

        :param time_delta: The time passed between frames, measured in seconds.
        :return: None
        """
        self.has_recently_updated_dimensions = False
        super().update(time_delta)

        if self.should_update_sorting:  # Only used when adding elements as their rects aren't accurate during creation
            self._update_sorting()
            self._update_extreme_elements()
            self.should_update_sorting = False

        if self.should_update_rect_edges:
            self._update_rect_edges()
            self.should_update_rect_edges = False

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Sets the dimensions of the container, clamped to min_edges_rect and max_edges_rect constraints
        if they are set and different from the current rect.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether to clamp the dimensions to the container.
        """
        width, height = dimensions

        # Call super's set_dimensions with the constrained dimensions
        super().set_dimensions((width, height), clamp_to_container)

        # Mark that rect edges need updating, but don't update immediately to avoid recursion
        self.should_update_rect_edges = True
        self.has_recently_updated_dimensions = True
