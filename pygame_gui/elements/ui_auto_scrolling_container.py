import pygame
from pygame_gui.core import UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.elements import UIScrollingContainer, UIAutoResizingContainer

from typing import *


class UIAutoScrollingContainer(UIScrollingContainer):
    """
    A container like UI element that lets users scroll around a larger container of content with
    scroll bars. Also allows to prevent adding scroll bars to the horizontal or vertical axis.

    :param relative_rect: The size and relative position of the container. This will also be the
                          starting size of the scrolling area.
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
                 manager: Optional[IUIManagerInterface] = None,
                 allow_scroll_x: bool = True,
                 allow_scroll_y: bool = True,
                 *,
                 starting_height: int = 1,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):
        super().__init__(relative_rect, manager,
                         allow_scroll_x=allow_scroll_x,
                         allow_scroll_y=allow_scroll_y,
                         starting_height=starting_height,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id="auto_scrolling_container")

        resize_left: bool = True
        resize_right: bool = True
        resize_top: bool = True
        resize_bottom: bool = True

        anchors = {"left": "left",
                   "right": "left",
                   "top": "top",
                   "bottom": "top"}

        if not self.allow_scroll_x:
            resize_left = False
            resize_right = False
            anchors["right"] = "right"

        if not self.allow_scroll_y:
            resize_top = False
            resize_bottom = False
            anchors["bottom"] = "bottom"

        self.scrollable_container.kill()
        scrollable_rect = pygame.Rect(0, 0, relative_rect.width, relative_rect.height)
        self.scrollable_container = UIAutoResizingContainer(relative_rect=scrollable_rect,
                                                            manager=manager,
                                                            resize_left=resize_left,
                                                            resize_right=resize_right,
                                                            resize_top=resize_top,
                                                            resize_bottom=resize_bottom,
                                                            starting_height=0,
                                                            container=self._view_container,
                                                            parent_element=parent_element,
                                                            object_id=ObjectID(
                                                                object_id="#scrollable_container",
                                                                class_id=None),
                                                            anchors=anchors)

    def update(self, time_delta: float):
        """
        Updates the scrolling container's position based upon the scroll bars and updates the
        scrollbar's visible percentage as well if that has changed.

        :param time_delta: The time passed between frames, measured in seconds.

        """
        super().update(time_delta)

        if self.scrollable_container.has_recently_updated_dimensions:
            self._calculate_scrolling_dimensions()
            self._sort_out_element_container_scroll_bars()
