import pygame
from pygame_gui.core import UIElement, UIContainer, ObjectID
from pygame_gui.core.interfaces import IUIElementInterface, IUIManagerInterface, IContainerLikeInterface

from typing import *


class UIAutoResizingContainer(UIContainer):
    """
    A container like UI element that updates its size as elements within it change size, or new elements are added

    :param relative_rect: The starting size and relative position of the container.
    :param min_edges_rect: The Rect which defines the maximum values for the left and top,
     and the minimum values for the right and bottom edges of the container. Defaults to the None (current rect)
    :param max_edges_rect: The Rect which defines the minimum values for the left and top,
     and the maximum values for the right and bottom edges of the container. Defaults to the None (unbounded)
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

    def __init__(self,
                 relative_rect: pygame.Rect,
                 min_edges_rect: pygame.Rect = None,
                 max_edges_rect: pygame.Rect = None,
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
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager,
                         starting_height=starting_height,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='auto_resizing_container')

        self.min_edges_rect = min_edges_rect

        if self.min_edges_rect is None:
            self.min_edges_rect = self.get_relative_rect()

        self.max_edges_rect = max_edges_rect

        self.abs_min_edges_rect = None
        self.abs_max_edges_rect = None
        self.recalculate_abs_edges_rect()

        self.resize_left = resize_left
        self.resize_right = resize_right
        self.resize_top = resize_top
        self.resize_bottom = resize_bottom

        # Elements which affect the corresponding edge of the container
        self.left_element: Optional[UIElement] = None
        self.right_element: Optional[UIElement] = None
        self.top_element: Optional[UIElement] = None
        self.bottom_element: Optional[UIElement] = None

        # Right to left is not the inverse of left to right because of varying sizes of elements
        self.left_to_right_elements: List[IUIElementInterface] = []
        self.right_to_left_elements: List[IUIElementInterface] = []
        self.top_to_bottom_elements: List[IUIElementInterface] = []
        self.bottom_to_top_elements: List[IUIElementInterface] = []

        # An element which is anchored to the left shouldn't expand the container to the left
        self.left_anchor_elements: List[IUIElementInterface] = []
        self.right_anchor_elements: List[IUIElementInterface] = []
        self.top_anchor_elements: List[IUIElementInterface] = []
        self.bottom_anchor_elements: List[IUIElementInterface] = []

        self.should_update_sorting = False
        self.should_update_dimensions = False

        self.has_recently_updated_dimensions = False
    
    def add_element(self, element: IUIElementInterface) -> None:
        """
        Add a UIElement to the container. The UIElement's relative_rect parameter will be relative to
        this container. Overridden to also update dimensions.

        :param element: A UIElement to add to this container.
        :return: None
        """
        super().add_element(element)

        self._update_anchors_from_element(element)

        self.should_update_sorting = True  # Currently, the rect is just a copy of relative rect so cannot do sorting
        self.should_update_dimensions = True

    def remove_element(self, element: IUIElementInterface) -> None:
        """
        Remove a UIElement from this container.

        :param element: A UIElement to remove from this container.
        :return: None
        """
        super().remove_element(element)

        if element in self.left_anchor_elements:
            self.left_anchor_elements.remove(element)
        if element in self.right_anchor_elements:
            self.right_anchor_elements.remove(element)
        if element in self.top_anchor_elements:
            self.top_anchor_elements.remove(element)
        if element in self.bottom_anchor_elements:
            self.bottom_anchor_elements.remove(element)

        self.left_to_right_elements.remove(element)
        self.right_to_left_elements.remove(element)
        self.top_to_bottom_elements.remove(element)
        self.bottom_to_top_elements.remove(element)

        if element in (self.left_element, self.right_element, self.top_element, self.bottom_element):
            self._update_extreme_elements()

        self.should_update_dimensions = True

    def _get_left_most_point(self) -> int:
        """
        Gets the minimum x value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        left = self.abs_min_edges_rect.left
        if self.left_element:
            left = min(left, self.left_element.get_abs_rect().left)
        if self.abs_max_edges_rect is not None:
            left = max(left, self.abs_max_edges_rect.left)
        return left

    def _get_right_most_point(self) -> int:
        """
        Gets the maximum x value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        right = self.abs_min_edges_rect.right
        if self.right_element:
            right = max(right, self.right_element.get_abs_rect().right)
        if self.abs_max_edges_rect is not None:
            right = min(right, self.abs_max_edges_rect.right)
        return right

    def _get_top_most_point(self) -> int:
        """
        Gets the minimum y value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        top = self.abs_min_edges_rect.top
        if self.top_element:
            top = min(top, self.top_element.get_abs_rect().top)
        if self.abs_max_edges_rect is not None:
            top = max(top, self.abs_max_edges_rect.top)
        return top

    def _get_bottom_most_point(self) -> int:
        """
        Gets the maximum y value any element has clamped to the min_edges_rect and max_edges_rect
        :return: An integer
        """
        bottom = self.abs_min_edges_rect.bottom
        if self.bottom_element:
            bottom = max(bottom, self.bottom_element.get_abs_rect().bottom)
        if self.abs_max_edges_rect is not None:
            bottom = min(bottom, self.abs_max_edges_rect.bottom)
        return bottom

    def recalculate_abs_edges_rect(self) -> None:
        """
        Used to recalculate the absolute rects from the min and max edges rect which control the minimum and maximum
        sizes of the container. Usually called when the container of this container has moved, or the minimum or
        maximum rects have changed.

        :return: None
        """
        self.abs_min_edges_rect = self._calc_abs_rect_pos_from_rel_rect(relative_rect=self.min_edges_rect,
                                                                        container=self.ui_container,
                                                                        anchors=self.anchors)

        if self.max_edges_rect:
            self.abs_max_edges_rect = self._calc_abs_rect_pos_from_rel_rect(relative_rect=self.min_edges_rect,
                                                                            container=self.ui_container,
                                                                            anchors=self.anchors)

    def update_containing_rect_position(self) -> None:
        """
        Overriden to also recalculate the absolute rects which control the minimum and maximum sizes of the container

        :return: None
        """
        super().update_containing_rect_position()
        self.recalculate_abs_edges_rect()

    def update_min_edges_rect(self, new_rect: pygame.Rect) -> None:
        """
        Updates the container's maximum values for the left and top, and the minimum value for
        the right and bottom edges based upon the edges of the new rect.

        Call the update function if you want to update the elements contained in the same frame,
        otherwise the elements contained within will update in the next frame.

        :param new_rect: Rect to update the min_edges_rect with
        :return: None
        """
        if not isinstance(new_rect, pygame.Rect):
            raise ValueError("Argument passed is not a pygame.Rect object")
        if new_rect != self.min_edges_rect:
            self.min_edges_rect = new_rect
            self.recalculate_abs_edges_rect()

    def update_max_edges_rect(self, new_rect: pygame.Rect) -> None:
        """
        Updates the container's minimum values for the left and top, and the maximum value for
        the right and bottom edges based upon the edges of the new rect.

        Call the update function if you want to update the elements contained in the same frame,
        otherwise the elements contained within will update in the next frame.

        :param new_rect: Rect to update the max_edges_rect with
        :return: None
        """
        if not isinstance(new_rect, pygame.Rect):
            raise ValueError("Argument passed is not a pygame.Rect object")
        if new_rect != self.max_edges_rect:
            self.max_edges_rect = new_rect
            self.recalculate_abs_edges_rect()
    
    def _update_anchors_from_element(self, element: IUIElementInterface) -> bool:
        """
        Updates the element's anchors which affect which side it's allowed to resize based on its anchors.
        This is needed to avoid endlessly expanding the container to accommodate elements which will always be out of
        bounds.

        :return: None
        """

        has_any_changed = False

        anchors = element.anchors.values()  # Only the values are important
        for attr in ["left", "right", "top", "bottom"]:

            anchor_elements = getattr(self, f"{attr}_anchor_elements")
            element_contained = element in anchor_elements

            if attr in anchors:
                if not element_contained:
                    anchor_elements.append(element)
                    has_any_changed = True

            elif element_contained:
                anchor_elements.remove(element)
                has_any_changed = True

        return has_any_changed

    def _update_anchor_elements(self) -> None:
        """
        Updates the elements which affect which side they are allowed to resize based on their anchors.
        This is needed to avoid endlessly expanding the container to accommodate elements which will always be out of
        bounds.

        :return: None
        """
        self.left_anchor_elements = []
        self.right_anchor_elements = []
        self.top_anchor_elements = []
        self.bottom_anchor_elements = []
        for element in self.elements:
            anchors = element.anchors.values()
            if "left" in anchors:
                self.left_anchor_elements.append(element)
            if "right" in anchors:
                self.right_anchor_elements.append(element)
            if "top" in anchors:
                self.top_anchor_elements.append(element)
            if "bottom" in anchors:
                self.bottom_anchor_elements.append(element)

    def _update_sorting(self) -> None:
        """
        Updates the sorting of the elements from left to right, top to bottom etc.

        :return: None
        """
        elements = self.elements

        self.left_to_right_elements = sorted(elements, key=(lambda element: element.get_abs_rect().left))
        self.right_to_left_elements = sorted(elements, key=(lambda element: element.get_abs_rect().right), reverse=True)
        self.top_to_bottom_elements = sorted(elements, key=(lambda element: element.get_abs_rect().top))
        self.bottom_to_top_elements = sorted(elements, key=(lambda element: element.get_abs_rect().bottom),
                                             reverse=True)

    def _update_extreme_elements(self) -> None:
        """
        Updates which elements are currently responsible for preventing the container from collapsing on each side

        :return: None
        """
        self.left_element = next(
            (element for element in self.left_to_right_elements if element not in self.left_anchor_elements), None)
        self.right_element = next(
            (element for element in self.right_to_left_elements if element not in self.right_anchor_elements), None)
        self.top_element = next(
            (element for element in self.top_to_bottom_elements if element not in self.top_anchor_elements), None)
        self.bottom_element = next(
            (element for element in self.bottom_to_top_elements if element not in self.bottom_anchor_elements), None)

    def _update_dimensions(self) -> None:
        """
        Updates the sizes of the container

        :return: None
        """
        rect = self.get_abs_rect()

        left_ext = rect.left - self._get_left_most_point() if self.resize_left else 0
        right_ext = self._get_right_most_point() - rect.right if self.resize_right else 0
        top_ext = rect.top - self._get_top_most_point() if self.resize_top else 0
        bottom_ext = self._get_bottom_most_point() - rect.bottom if self.resize_bottom else 0

        if left_ext or top_ext:
            self.set_position(pygame.Vector2(rect.topleft) - pygame.Vector2(left_ext, top_ext))

        width = left_ext + rect.width + right_ext
        height = top_ext + rect.height + bottom_ext

        if left_ext or right_ext or top_ext or bottom_ext:
            self.set_dimensions((width, height))
    
    def on_contained_elements_changed(self, target: UIElement) -> None:
        """
        Update the positioning of the contained elements of this container. To be called when one of the contained
        elements may have moved, or been resized.

        :param target: the UI element that has been benn moved or resized.
        """
        super().on_contained_elements_changed(target)

        self._update_anchors_from_element(target)
        self._update_sorting()
        self._update_extreme_elements()
        
        self.should_update_dimensions = True

    def update(self, time_delta: float) -> None:
        """
        Updates the container's size based upon the elements inside.

        Call this function if you have added or removed an element from this container and want
        to update the size in the same frame, otherwise it will update in the next frame.

        :param time_delta: The time passed between frames, measured in seconds.
        :return: None
        """
        super().update(time_delta)

        if self.has_recently_updated_dimensions:
            self.has_recently_updated_dimensions = False

        if self.should_update_sorting:
            self._update_sorting()
            self._update_extreme_elements()
            self.should_update_sorting = False

        if self.should_update_dimensions:
            self._update_dimensions()
            self.should_update_dimensions = False
            self.has_recently_updated_dimensions = True
