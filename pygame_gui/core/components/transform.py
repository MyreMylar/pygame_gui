import warnings

from typing import List, Union, Tuple, Dict
from typing import TYPE_CHECKING

import pygame

'from pygame_gui.core import UIElement'
from pygame_gui.core.components import Component

class Transform(Component):
    def __init__(self, element: 'UIElement',
                 relative_rect: Union[pygame.Rect, Tuple[int, int, int, int]],
                 anchors: Dict[str, Union[str, 'UIElement']] = None,
                 dynamic_size_calculator = None):
        super().__init__(element)

        self.minimum_dimensions = (-1, -1)
        relative_rect.size = self._get_clamped_to_minimum_dimensions(relative_rect.size)

        if isinstance(relative_rect, pygame.Rect):
            self.relative_rect = relative_rect.copy()
        else:
            self.relative_rect = pygame.Rect(relative_rect)
        self.rect = self.relative_rect.copy()

        self.dynamic_width = True if self.relative_rect.width == -1 else False
        self.dynamic_height = True if self.relative_rect.height == -1 else False

        self.anchors = {}
        if anchors is not None:
            if 'center' in anchors and anchors['center'] == 'center':
                self.anchors.update({'center': 'center'})
            else:
                if self._validate_horizontal_anchors(anchors):
                    if 'left' in anchors:
                        self.anchors['left'] = anchors['left']
                    if 'right' in anchors:
                        self.anchors['right'] = anchors['right']
                    if 'centerx' in anchors:
                        self.anchors['centerx'] = anchors['centerx']
                else:
                    self.anchors.update({'left': 'left'})

                if self._validate_vertical_anchors(anchors):
                    if 'top' in anchors:
                        self.anchors['top'] = anchors['top']
                    if 'bottom' in anchors:
                        self.anchors['bottom'] = anchors['bottom']
                    if 'centery' in anchors:
                        self.anchors['centery'] = anchors['centery']
                else:
                    self.anchors.update({'top': 'top'})

            if 'left_target' in anchors:
                self.anchors['left_target'] = anchors['left_target']
            if 'right_target' in anchors:
                self.anchors['right_target'] = anchors['right_target']
            if 'top_target' in anchors:
                self.anchors['top_target'] = anchors['top_target']
            if 'bottom_target' in anchors:
                self.anchors['bottom_target'] = anchors['bottom_target']
            if 'centerx_target' in anchors:
                self.anchors['centerx_target'] = anchors['centerx_target']
            if 'centery_target' in anchors:
                self.anchors['centery_target'] = anchors['centery_target']
        else:
            self.anchors = {'left': 'left',
                            'top': 'top'}

        self.relative_bottom_margin = None
        self.relative_right_margin = None
        
        self.dynamic_size_calculator = dynamic_size_calculator
        
    @property
    def rect(self):
        return self.element.rect

    @rect.setter
    def rect(self, rect):
        self.element.rect = rect

    @staticmethod
    def _validate_horizontal_anchors(anchors: Dict[str, Union[str, 'UIElement']]):
        # first make a dictionary of just the horizontal anchors
        horizontal_anchors = {}

        if 'left' in anchors:
            horizontal_anchors.update({'left': anchors['left']})
        if 'right' in anchors:
            horizontal_anchors.update({'right': anchors['right']})
        if 'centerx' in anchors:
            horizontal_anchors.update({'centerx': anchors['centerx']})

        valid_anchor_set = [{'left': 'left', 'right': 'left'},
                            {'left': 'right', 'right': 'right'},
                            {'left': 'left', 'right': 'right'},
                            {'left': 'left'},
                            {'right': 'right'},
                            {'left': 'right'},
                            {'right': 'left'},
                            {'centerx': 'centerx'}
                            ]

        if horizontal_anchors in valid_anchor_set:
            return True
        elif len(horizontal_anchors) == 0:
            return False  # no horizontal anchors so just use defaults
        else:
            warnings.warn("Supplied horizontal anchors are invalid, defaulting to left", category=UserWarning)
            return False

    @staticmethod
    def _validate_vertical_anchors(anchors: Dict[str, Union[str, 'UIElement']]):
        # first make a dictionary of just the vertical anchors
        vertical_anchors = {}

        if 'top' in anchors:
            vertical_anchors.update({'top': anchors['top']})
        if 'bottom' in anchors:
            vertical_anchors.update({'bottom': anchors['bottom']})
        if 'centery' in anchors:
            vertical_anchors.update({'centery': anchors['centery']})

        valid_anchor_set = [{'top': 'top', 'bottom': 'top'},
                            {'top': 'bottom', 'bottom': 'bottom'},
                            {'top': 'top', 'bottom': 'bottom'},
                            {'top': 'top'},
                            {'bottom': 'bottom'},
                            {'top': 'bottom'},
                            {'bottom': 'top'},
                            {'centery': 'centery'}
                            ]

        if vertical_anchors in valid_anchor_set:
            return True
        elif len(vertical_anchors) == 0:
            return False  # no vertical anchors so just use defaults
        else:
            warnings.warn("Supplied vertical anchors are invalid, defaulting to top", category=UserWarning)
            return False
    
    def _set_dynamic_width(self, is_dynamic: bool = True):
        self.dynamic_width = is_dynamic
        if self.element.drawable_shape is not None:
            self.element.drawable_shape.dynamic_width = is_dynamic
    
    def _set_dynamic_height(self, is_dynamic: bool = True):
        self.dynamic_height = is_dynamic
        if self.element.drawable_shape is not None:
            self.element.drawable_shape.dynamic_height = is_dynamic

    def _get_clamped_to_minimum_dimensions(self, dimensions, clamp_to_container=False):
        container = self.element.ui_container
        if container is not None and clamp_to_container:
            dimensions = (min(container.rect.width,
                              max(self.minimum_dimensions[0],
                                  int(dimensions[0]))),
                          min(container.rect.height,
                              max(self.minimum_dimensions[1],
                                  int(dimensions[1]))))
        else:
            dimensions = (max(self.minimum_dimensions[0], int(dimensions[0])),
                          max(self.minimum_dimensions[1], int(dimensions[1])))
        return dimensions

    def _calc_top_offset(self) -> int:
        return (self.anchors['top_target'].get_abs_rect().bottom
                if 'top_target' in self.anchors
                else self.element.ui_container.get_abs_rect().top)

    def _calc_bottom_offset(self) -> int:
        return (self.anchors['bottom_target'].get_abs_rect().top
                if 'bottom_target' in self.anchors
                else self.element.ui_container.get_abs_rect().bottom)

    def _calc_centery_offset(self) -> int:
        return (self.anchors['centery_target'].get_abs_rect().centery
                if 'centery_target' in self.anchors
                else self.element.ui_container.get_abs_rect().centery)

    def _calc_left_offset(self) -> int:
        return (self.anchors['left_target'].get_abs_rect().right
                if 'left_target' in self.anchors
                else self.element.ui_container.get_abs_rect().left)

    def _calc_right_offset(self) -> int:
        return (self.anchors['right_target'].get_abs_rect().left
                if 'right_target' in self.anchors
                else self.element.ui_container.get_abs_rect().right)

    def _calc_centerx_offset(self) -> int:
        return (self.anchors['centerx_target'].get_abs_rect().centerx
                if 'centerx_target' in self.anchors
                else self.element.ui_container.get_abs_rect().centerx)

    def update_absolute_rect_position_from_anchors(self, recalculate_margins=False):
        """
        Called when our element's relative position has changed.
        """
        new_top = 0
        new_bottom = 0
        top_offset = self._calc_top_offset()
        bottom_offset = self._calc_bottom_offset()

        center_x_and_y = False

        if 'center' in self.anchors:
            if self.anchors['center'] == 'center':
                center_x_and_y = True

        if ('centery' in self.anchors and self.anchors['centery'] == 'centery') or center_x_and_y:
            centery_offset = self._calc_centery_offset()
            new_top = self.relative_rect.top - self.relative_rect.height//2 + centery_offset
            new_bottom = self.relative_rect.bottom - self.relative_rect.height//2 + centery_offset

        if 'top' in self.anchors:
            if self.anchors['top'] == 'top':
                new_top = self.relative_rect.top + top_offset
                new_bottom = self.relative_rect.bottom + top_offset
            elif self.anchors['top'] == 'bottom':
                new_top = self.relative_rect.top + bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = (bottom_offset -
                                                   (new_top + self.relative_rect.height))
                new_bottom = bottom_offset - self.relative_bottom_margin

        if 'bottom' in self.anchors:
            if self.anchors['bottom'] == 'top':
                new_top = self.relative_rect.top + top_offset
                new_bottom = self.relative_rect.bottom + top_offset
            elif self.anchors['bottom'] == 'bottom':
                if not ('top' in self.anchors and self.anchors['top'] == 'top'):
                    new_top = self.relative_rect.top + bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = (bottom_offset -
                                                   (new_top + self.relative_rect.height))
                new_bottom = bottom_offset - self.relative_bottom_margin

        new_left = 0
        new_right = 0
        left_offset = self._calc_left_offset()
        right_offset = self._calc_right_offset()

        if ('centerx' in self.anchors and self.anchors['centerx'] == 'centerx') or center_x_and_y:
            centerx_offset = self._calc_centerx_offset()
            new_left = self.relative_rect.left - self.relative_rect.width//2 + centerx_offset
            new_right = self.relative_rect.right - self.relative_rect.width//2 + centerx_offset

        if 'left' in self.anchors:
            if self.anchors['left'] == 'left':
                new_left = self.relative_rect.left + left_offset
                new_right = self.relative_rect.right + left_offset
            elif self.anchors['left'] == 'right':
                new_left = self.relative_rect.left + right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = (right_offset - (new_left + self.relative_rect.width))
                new_right = right_offset - self.relative_right_margin

        if 'right' in self.anchors:
            if self.anchors['right'] == 'left':
                new_left = self.relative_rect.left + left_offset
                new_right = self.relative_rect.right + left_offset
            elif self.anchors['right'] == 'right':
                if not ('left' in self.anchors and self.anchors['left'] == 'left'):
                    new_left = self.relative_rect.left + right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = (right_offset - (new_left + self.relative_rect.width))
                new_right = right_offset - self.relative_right_margin

        self.rect.left = new_left
        self.rect.top = new_top
        if self.dynamic_height:
            new_height = new_bottom - new_top
        else:
            new_height = max(0, new_bottom - new_top)

        if self.dynamic_width:
            new_width = new_right - new_left
        else:
            new_width = max(0, new_right - new_left)

        new_width, new_height = self._get_clamped_to_minimum_dimensions((new_width, new_height))
        if (new_height != self.relative_rect.height) or (new_width != self.relative_rect.width):
            self.element.set_dimensions((new_width, new_height))

    def _update_relative_rect_position_from_anchors(self, recalculate_margins=False):
        """
        Called when our element's absolute position has been forcibly changed.
        """

        # This is a bit easier to calculate than getting the absolute position from the
        # relative one, because the absolute position rectangle is always relative to the top
        # left of the screen.

        # Setting these to None means we are always recalculating the margins in here.
        self.relative_bottom_margin = None
        self.relative_right_margin = None

        new_top = 0
        new_bottom = 0
        top_offset = self._calc_top_offset()
        bottom_offset = self._calc_bottom_offset()

        center_x_and_y = False
        if 'center' in self.anchors:
            if self.anchors['center'] == 'center':
                center_x_and_y = True

        if ('centery' in self.anchors and self.anchors['centery'] == 'centery') or center_x_and_y:
            centery_offset = self._calc_centery_offset()
            new_top = self.rect.top + self.relative_rect.height//2 - centery_offset
            new_bottom = self.rect.bottom + self.relative_rect.height//2 - centery_offset

        if 'top' in self.anchors:
            if self.anchors['top'] == 'top':
                new_top = self.rect.top - top_offset
                new_bottom = self.rect.bottom - top_offset
            elif self.anchors['top'] == 'bottom':
                new_top = self.rect.top - bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = bottom_offset - self.rect.bottom
                new_bottom = self.rect.bottom - bottom_offset

        if 'bottom' in self.anchors:
            if self.anchors['bottom'] == 'top':
                new_top = self.rect.top - top_offset
                new_bottom = self.rect.bottom - top_offset
            elif self.anchors['bottom'] == 'bottom':
                if not ('top' in self.anchors and self.anchors['top'] == 'top'):
                    new_top = self.rect.top - bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = bottom_offset - self.rect.bottom
                new_bottom = self.rect.bottom - bottom_offset

        new_left = 0
        new_right = 0
        left_offset = self._calc_left_offset()
        right_offset = self._calc_right_offset()

        if ('centerx' in self.anchors and self.anchors['centerx'] == 'centerx') or center_x_and_y:
            centerx_offset = self._calc_centerx_offset()
            new_left = self.rect.left + self.relative_rect.width//2 - centerx_offset
            new_right = self.rect.right + self.relative_rect.width//2 - centerx_offset

        if 'left' in self.anchors:
            if self.anchors['left'] == 'left':
                new_left = self.rect.left - left_offset
                new_right = self.rect.right - left_offset
            elif self.anchors['left'] == 'right':
                new_left = self.rect.left - right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = right_offset - self.rect.right
                new_right = self.rect.right - right_offset

        if 'right' in self.anchors:
            if self.anchors['right'] == 'left':
                new_left = self.rect.left - left_offset
                new_right = self.rect.right - left_offset
            elif self.anchors['right'] == 'right':
                if not ('left' in self.anchors and self.anchors['left'] == 'left'):
                    new_left = self.rect.left - right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = right_offset - self.rect.right
                new_right = self.rect.right - right_offset

        # set bottom and right first in case these are only anchors available
        self.relative_rect.bottom = new_bottom
        self.relative_rect.right = new_right

        # set top and left last to give these priority, in most cases where all anchors are set
        # we want relative_rect parameters to be correct for whatever the top & left sides are
        # anchored to. The data for the bottom and right in cases where left is anchored
        # differently to right and/or top is anchored differently to bottom should be captured by
        # the bottom and right margins.
        self.relative_rect.left = new_left
        self.relative_rect.top = new_top

    def _calc_dynamic_size(self):
        if self.dynamic_size_calculator is None:
            return

        if self.dynamic_width or self.dynamic_height:
            self._set_dimensions(self.dynamic_size_calculator())

            # if we have anchored the left side of our button to the right of its container then
            # changing the width is going to mess up the horiz position as well.
            new_left = self.relative_rect.left
            new_top = self.relative_rect.top
            if 'left' in self.anchors and self.anchors['left'] == 'right' and self.dynamic_width:
                left_offset = self.dynamic_dimensions_orig_top_left[0]
                new_left = left_offset - self.relative_rect.width
            # if we have anchored the top side of our button to the bottom of it's container then
            # changing the height is going to mess up the vert position as well.
            if 'top' in self.anchors and self.anchors['top'] == 'bottom' and self.dynamic_height:
                top_offset = self.dynamic_dimensions_orig_top_left[1]
                new_top = top_offset - self.relative_rect.height

            self.element.set_relative_position((new_left, new_top))
        
    def on_set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        self.relative_rect.x = int(position[0])
        self.relative_rect.y = int(position[1])

        self.update_absolute_rect_position_from_anchors(recalculate_margins=True)
        
    def on_set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """
        self.rect.x = int(position[0])
        self.rect.y = int(position[1])
        self._update_relative_rect_position_from_anchors(recalculate_margins=True)

    def on_set_minimum_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                                       Tuple[int, int],
                                                       Tuple[float, float]]):
        """
        If this window is resizable, then the dimensions we set here will be the minimum that
        users can change the window to. They are also used as the minimum size when
        'set_dimensions' is called.

        :param dimensions: The new minimum dimension for the window.

        """
        self.minimum_dimensions = (min(self.element.ui_container.rect.width, int(dimensions[0])),
                                   min(self.element.ui_container.rect.height, int(dimensions[1])))

        if ((self.rect.width < self.minimum_dimensions[0]) or
                (self.rect.height < self.minimum_dimensions[1])):
            new_width = max(self.minimum_dimensions[0], self.rect.width)
            new_height = max(self.minimum_dimensions[1], self.rect.height)
            self.element.set_dimensions((new_width, new_height))
            
    def on_set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]],
                       clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element. And set whether the elements are dynamic.

        NOTE: Using this on elements inside containers with non-default anchoring arrangements
        may make a mess of them.

        :param dimensions: The new dimensions to set. If it is a negative value, the element will become
                            dynamically sized, otherwise it will become statically sized.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        is_dynamic = False
        if dimensions[0] < 0:
            self._set_dynamic_width()
            is_dynamic = True
        else:
            self._set_dynamic_width(False)
            
        if dimensions[1] < 0:
            self._set_dynamic_height()
            is_dynamic = True
        else:
            self._set_dynamic_height(False)
            
        if is_dynamic:
            self.element.rebuild()
        else:
            self._set_dimensions(dimensions, clamp_to_container)

    def _set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                                Tuple[int, int],
                                                Tuple[float, float]],
                        clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.
        Dimensions must be positive values.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        dimensions = self._get_clamped_to_minimum_dimensions(dimensions, clamp_to_container)
        self.relative_rect.width = int(dimensions[0])
        self.relative_rect.height = int(dimensions[1])
        self.rect.size = self.relative_rect.size

        if dimensions[0] >= 0 and dimensions[1] >= 0:
            self.update_absolute_rect_position_from_anchors(recalculate_margins=True)

            if self.element.drawable_shape is not None:
                if self.element.drawable_shape.set_dimensions(self.relative_rect.size):
                    # needed to stop resizing 'lag'
                    self.element._set_image(self.element.drawable_shape.get_fresh_surface())

            self.element._update_container_clip()
            self.element.ui_container.on_anchor_target_changed(self)

    def get_anchor_targets(self) -> list:
        targets = []
        if 'left_target' in self.anchors:
            targets.append(self.anchors['left_target'])
        if 'right_target' in self.anchors:
            targets.append(self.anchors['right_target'])
        if 'top_target' in self.anchors:
            targets.append(self.anchors['top_target'])
        if 'bottom_target' in self.anchors:
            targets.append(self.anchors['bottom_target'])

        return targets
