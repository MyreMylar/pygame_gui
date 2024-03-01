from typing import Union, Tuple, Dict, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIContainerInterface
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core import UIElement, UIContainer

from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar
from pygame_gui.elements.ui_horizontal_scroll_bar import UIHorizontalScrollBar


class UIScrollingContainer(UIElement, IContainerLikeInterface):
    """
    A container like UI element that lets users scroll around a larger container of content with
    scroll bars.

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
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor
        self._root_container = None
        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=starting_height,
                         layer_thickness=2,
                         anchors=anchors,
                         visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['scrolling_container'])

        # self.parent_element = parent_element

        self.need_to_sort_out_scrollbars = False

        self.allow_scroll_x = allow_scroll_x
        self.allow_scroll_y = allow_scroll_y

        self._set_image(self.ui_manager.get_universal_empty_surface())

        # this contains the scroll bars and the 'view' container
        self._root_container = UIContainer(relative_rect=relative_rect,
                                           manager=manager,
                                           starting_height=starting_height,
                                           container=container,
                                           parent_element=parent_element,
                                           object_id=ObjectID(object_id='#root_container',
                                                              class_id=None),
                                           anchors=anchors,
                                           visible=self.visible)

        scroll_bar_rect = pygame.Rect(-20, 0, 20, relative_rect.height)
        self.vert_scroll_bar = UIVerticalScrollBar(relative_rect=scroll_bar_rect,
                                                   visible_percentage=1.0,
                                                   manager=self.ui_manager,
                                                   container=self._root_container,
                                                   parent_element=self,
                                                   anchors={'left': 'right',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'bottom'})

        self.vert_scroll_bar.set_dimensions((0, relative_rect.height))  # Remove these when anchoring is fixed
        self.vert_scroll_bar.set_relative_position((0, 0))  # Without this, they look off-centered
        self.join_focus_sets(self.vert_scroll_bar)

        scroll_bar_rect = pygame.Rect(0, -20, relative_rect.width, 20)
        self.horiz_scroll_bar = UIHorizontalScrollBar(relative_rect=scroll_bar_rect,
                                                      visible_percentage=1.0,
                                                      manager=self.ui_manager,
                                                      container=self._root_container,
                                                      parent_element=self,
                                                      anchors={'left': 'left',
                                                               'right': 'right',
                                                               'top': 'bottom',
                                                               'bottom': 'bottom'})

        self.horiz_scroll_bar.set_dimensions((relative_rect.width, 0))
        self.horiz_scroll_bar.set_relative_position((0, 0))
        self.join_focus_sets(self.horiz_scroll_bar)

        # This container is the view on to the scrollable container it's size is determined by
        # the size of the root container and whether there are any scroll bars or not.
        view_rect = pygame.Rect(0, 0, relative_rect.width, relative_rect.height)
        self._view_container = UIContainer(relative_rect=view_rect,
                                           manager=manager,
                                           starting_height=0,
                                           container=self._root_container,
                                           parent_element=parent_element,
                                           object_id=ObjectID(object_id='#view_container',
                                                              class_id=None),
                                           anchors={'left': 'left',
                                                    'right': 'right',
                                                    'top': 'top',
                                                    'bottom': 'bottom',
                                                    'right_target': self.vert_scroll_bar,
                                                    'bottom_target': self.horiz_scroll_bar})

        # This container is what we actually put other stuff in.
        # It is aligned to the top left corner but that isn't that important for a container that
        # can be much larger than it's view
        scrollable_rect = pygame.Rect(0, 0, relative_rect.width, relative_rect.height)
        self.scrollable_container = UIContainer(relative_rect=scrollable_rect,
                                                manager=manager,
                                                starting_height=0,
                                                container=self._view_container,
                                                parent_element=parent_element,
                                                object_id=ObjectID(
                                                    object_id='#scrollable_container',
                                                    class_id=None),
                                                anchors={'left': 'left',
                                                         'right': 'left',
                                                         'top': 'top',
                                                         'bottom': 'top'})

        self.scroll_bar_width = 0
        self.scroll_bar_height = 0

        self.scrolling_height = 0
        self.scrolling_width = 0

        self.scrolling_bottom = 0
        self.scrolling_right = 0
        self._calculate_scrolling_dimensions()

    def get_container(self) -> IUIContainerInterface:
        """
        Gets the scrollable container area (the one that moves around with the scrollbars)
        from this container-like UI element.

        :return: the scrolling container.
        """
        return self.scrollable_container

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this panel.

        """
        self._root_container.kill()
        super().kill()

    def set_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """

        super().set_position(position)
        self._root_container.set_position(position)

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        super().set_relative_position(position)
        self._root_container.set_relative_position(position)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]],
                       clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.

        NOTE: Using this on elements inside containers with non-default anchoring arrangements
        may make a mess of them.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        super().set_dimensions(dimensions)
        self._root_container.set_dimensions(dimensions)

        self._calculate_scrolling_dimensions()
        self._sort_out_element_container_scroll_bars()

    def set_scrollable_area_dimensions(self,
                                       dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the size of the scrollable area container. It starts the same size as the view
        container, but often you want to expand it, or why have a scrollable container?

        :param dimensions: The new dimensions.
        """
        self.scrollable_container.set_dimensions(dimensions)

        self._calculate_scrolling_dimensions()
        self._sort_out_element_container_scroll_bars()

    def update(self, time_delta: float):
        """
        Updates the scrolling container's position based upon the scroll bars and updates the
        scrollbar's visible percentage as well if that has changed.

        :param time_delta: The time passed between frames, measured in seconds.

        """
        super().update(time_delta)

        # Both scroll bars are the sole cause for each other's existence, terminate them both
        self._calculate_scrolling_dimensions()
        if (self.scrolling_width == self._view_container.rect.width + self.scroll_bar_width
                and self.scrolling_height == self._view_container.rect.height + self.scroll_bar_height):
            self._remove_vert_scrollbar()
            self._remove_horiz_scrollbar()

        if (self.vert_scroll_bar is not None and
                self.vert_scroll_bar.check_has_moved_recently()):

            self._calculate_scrolling_dimensions()
            vis_percent = self._view_container.rect.height / self.scrolling_height
            if self.vert_scroll_bar.start_percentage <= 0.5:
                start_height = int(self.vert_scroll_bar.start_percentage *
                                   self.scrolling_height)
            else:
                button_percent_height = (self.vert_scroll_bar.sliding_button.rect.height /
                                         self.vert_scroll_bar.scrollable_height)
                button_bottom_percent = (self.vert_scroll_bar.start_percentage +
                                         button_percent_height)
                start_height = (int(button_bottom_percent * self.scrolling_height) -
                                self._view_container.rect.height)

            if vis_percent < 1.0:
                self.vert_scroll_bar.set_visible_percentage(vis_percent)
            else:
                self._remove_vert_scrollbar()

            # Think this code is unreachable due to clamping
            # if self.scrolling_bottom < self._view_container.rect.bottom:
            #     start_height = min(start_height, self._view_container.rect.height)

            new_pos = (self.scrollable_container.relative_rect.x,
                       -start_height)
            self.scrollable_container.set_relative_position(new_pos)

        if (self.horiz_scroll_bar is not None and
                self.horiz_scroll_bar.check_has_moved_recently()):

            self._calculate_scrolling_dimensions()
            vis_percent = self._view_container.rect.width / self.scrolling_width
            if self.horiz_scroll_bar.start_percentage <= 0.5:
                start_width = int(self.horiz_scroll_bar.start_percentage *
                                  self.scrolling_width)
            else:
                button_percent_width = (self.horiz_scroll_bar.sliding_button.rect.width /
                                        self.horiz_scroll_bar.scrollable_width)
                button_right_percent = (self.horiz_scroll_bar.start_percentage +
                                        button_percent_width)
                start_width = (int(button_right_percent * self.scrolling_width) -
                               self._view_container.rect.width)
            if vis_percent < 1.0:
                self.horiz_scroll_bar.set_visible_percentage(vis_percent)
            else:
                self._remove_horiz_scrollbar()

            # Think this code is unreachable due to clamping
            # if self.scrolling_right < self._view_container.rect.right:
            #     start_width = min(start_width, self._view_container.rect.width)
            new_pos = (-start_width,
                       self.scrollable_container.relative_rect.y)
            self.scrollable_container.set_relative_position(new_pos)

    def _calculate_scrolling_dimensions(self):
        """
        Calculate all the variables we need to scroll the container correctly.

        This is a bit of a fiddly process since we can resize our viewing area, the scrollable
        area, and we generally don't want to yank the area you are looking at too much either.

        Plus, the scrollbars only have somewhat limited accuracy so need clamping...
        """
        scrolling_top = min(self.scrollable_container.rect.top,
                            self._view_container.rect.top)

        scrolling_left = min(self.scrollable_container.rect.left,
                             self._view_container.rect.left)
        # used for clamping
        self.scrolling_bottom = max(self.scrollable_container.rect.bottom,
                                    self._view_container.rect.bottom)
        self.scrolling_right = max(self.scrollable_container.rect.right,
                                   self._view_container.rect.right)

        self.scrolling_height = self.scrolling_bottom - scrolling_top
        self.scrolling_width = self.scrolling_right - scrolling_left

    def _sort_out_element_container_scroll_bars(self):
        """
        This creates, re-sizes or removes the scrollbars after resizing, but not after the scroll
        bar has been moved. Instead, it tries to keep the scrollbars in the same approximate position
        they were in before resizing
        """
        self._check_scroll_bars_and_adjust()
        need_horiz_scroll_bar, need_vert_scroll_bar = self._check_scroll_bars_and_adjust()

        if need_vert_scroll_bar:
            vis_percent = self._view_container.rect.height / self.scrolling_height
            start_percent = ((self._view_container.rect.top -
                              self.scrollable_container.rect.top)
                             / self.scrolling_height)
            self.vert_scroll_bar.start_percentage = start_percent
            self.vert_scroll_bar.set_visible_percentage(vis_percent)
            self.vert_scroll_bar.set_relative_position((-self.scroll_bar_width, 0))
            self.vert_scroll_bar.set_dimensions((self.scroll_bar_width,
                                                 self._view_container.rect.height))
        else:
            self._remove_vert_scrollbar()

        if need_horiz_scroll_bar:
            vis_percent = self._view_container.rect.width / self.scrolling_width
            start_percent = ((self._view_container.rect.left -
                              self.scrollable_container.rect.left)
                             / self.scrolling_width)
            self.horiz_scroll_bar.start_percentage = start_percent
            self.horiz_scroll_bar.set_visible_percentage(vis_percent)
            self.horiz_scroll_bar.set_relative_position((0, -self.scroll_bar_height))
            self.horiz_scroll_bar.set_dimensions((self._view_container.rect.width,
                                                  self.scroll_bar_height))
        else:
            self._remove_horiz_scrollbar()

    def _check_scroll_bars_and_adjust(self):
        """
        Check if we need a horizontal or vertical scrollbar and adjust the containers if we do.

        Adjusting the containers for a scrollbar, may mean we now need a scrollbar in the other
        dimension, so we need to call this twice.
        """
        self.scroll_bar_width = 0
        self.scroll_bar_height = 0
        need_horiz_scroll_bar = False
        need_vert_scroll_bar = False
        if (self.scrolling_height > self._view_container.rect.height or
                self.scrollable_container.relative_rect.top != 0) and self.allow_scroll_y:
            need_vert_scroll_bar = True
            self.scroll_bar_width = 20
        if (self.scrolling_width > self._view_container.rect.width or
                self.scrollable_container.relative_rect.left != 0) and self.allow_scroll_x:
            need_horiz_scroll_bar = True
            self.scroll_bar_height = 20
        self._calculate_scrolling_dimensions()
        return need_horiz_scroll_bar, need_vert_scroll_bar

    def _remove_vert_scrollbar(self):
        """
        Doesn't delete the vert scroll bar, instead just resizes it to (0, height of the view container).
        """
        if self.vert_scroll_bar is not None:
            self.scroll_bar_width = 0
            self.vert_scroll_bar.set_dimensions((0, self._view_container.rect.height))
            self.vert_scroll_bar.set_relative_position((0, 0))

            self._calculate_scrolling_dimensions()
            if self.horiz_scroll_bar is not None:
                self.horiz_scroll_bar.set_dimensions((self._view_container.rect.width,
                                                      self.scroll_bar_height))

    def _remove_horiz_scrollbar(self):
        """
        Doesn't delete the horiz scroll bar, instead just resizes it to (width of the view container, 0).
        """
        if self.horiz_scroll_bar is not None:
            self.scroll_bar_height = 0
            self.horiz_scroll_bar.set_dimensions((self._view_container.rect.width, 0))
            self.horiz_scroll_bar.set_relative_position((0, 0))

            self._calculate_scrolling_dimensions()
            if self.vert_scroll_bar is not None:
                self.vert_scroll_bar.set_dimensions((self.scroll_bar_width,
                                                     self._view_container.rect.height))

    def disable(self):
        """
        Disables all elements in the container, so they are no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self._root_container is not None:
                self._root_container.disable()

    def enable(self):
        """
        Enables all elements in the container, so they are interactive again.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self._root_container is not None:
                self._root_container.enable()

    def show(self):
        """
        In addition to the base UIElement.show() - call show() of owned container - _root_container.
        All other sub-elements (view_container, scrollbars) are children of _root_container, so
        it's visibility will propagate to them - there is no need to call their show() methods
        separately.
        """
        super().show()
        if self._root_container is not None:
            self._root_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - call hide() of owned container - _root_container.
        All other sub-elements (view_container, scrollbars) are children of _root_container, so
        it's visibility will propagate to them - there is no need to call their hide() methods
        separately.
        """
        if self._root_container is not None:
            self._root_container.hide()
        super().hide()
