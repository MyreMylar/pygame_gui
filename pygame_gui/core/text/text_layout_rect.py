from typing import Tuple, Union, Optional
from abc import abstractmethod
from enum import Enum
from collections import namedtuple

import pygame
from pygame.surface import Surface


Padding = namedtuple('Padding', "top right bottom left")


class TextFloatPosition(Enum):
    """
    An enumeration covering the three possible 'float' positions of a layout rect in a text layout.

    'NONE' is the normal case. This rectangle will be treated as one in a row of rectangles

    'LEFT' will allow other rectangles to flow around this one on the right hand side with
           potentially multiple rows of shorter rectangles taking up its vertical height.

    'RIGHT' the same as left except on the other side.

    Generally we use this to embed images into the flow of a text box.
    """
    NONE = 0
    LEFT = 1
    RIGHT = 2


class TextLayoutRect(pygame.rect.Rect):
    """
    A base class for use in Layouts.
    """

    def __init__(self, dimensions: Tuple[int, int],
                 *,
                 can_split=False,
                 float_pos: TextFloatPosition = TextFloatPosition.NONE,
                 should_span=False):
        super().__init__((0, 0), dimensions)
        self._can_split = can_split
        self._float_pos = float_pos
        self._should_span = should_span
        self.letter_count = 0
        self.descender = 0
        self.smallest_split_size = 1

    @abstractmethod
    def finalise(self,
                 target_surface: Surface,
                 target_area: pygame.Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 x_scroll_offset: int = 0,
                 letter_end: Optional[int] = None):
        """
        Bake the contents of this layout rect onto a surface.

        :param target_surface:
        :param target_area:
        :param row_chunk_origin:
        :param row_chunk_height:
        :param row_bg_height:
        :param x_scroll_offset:
        :param letter_end:
        """

    def clear(self, optional_rect: Optional[pygame.Rect] = None):
        """
        Clear the space this rect takes up on the finalised surface.

        :param optional_rect: A rect to clear instead of the default self rect, useful for effects.
        """

    def can_split(self):
        """
        Return True if this rectangle can be split into smaller rectangles by a layout.

        :return: True if splittable, False otherwise.
        """
        return self._can_split

    def should_span(self):
        """
        Return True if this rectangle should be expanded/shrunk to fit the available
        width in a layout.

        :return: True if should span the width, False otherwise.
        """
        return self._should_span

    def float_pos(self) -> TextFloatPosition:
        """
        Return the 'floating' status of this rectangle. can be TextFloatPosition.left,
        TextFloatPosition.right or TextFloatPosition.none and the default, used by most
        rectangles, is TextFloatPosition.none.

        Used to make text flow around images.

        :return: returns the float status of this rectangle.
        """
        return self._float_pos

    def split(self,
              requested_x: int,
              line_width: int,
              row_start_x: int) -> Union['TextLayoutRect', None]:  # noqa
        """
        Try to perform a split operation on this rectangle. Often rectangles will be split at the
        nearest point that is still less than the request (i.e. to the left of the request in
        the common left-to-right text layout case) .

        :param requested_x: the requested place to split this rectangle along it's width.
        :param line_width: the width of the current line.
        :param row_start_x: the x start position of the row.

        """
        if line_width < self.smallest_split_size:
            raise ValueError('Line width is too narrow')

        if row_start_x < -1:
            raise ValueError('Row start must be 0 or greater')

        original_width = self.width  # noqa: pylint: disable=access-member-before-definition,attribute-defined-outside-init
        self.width = requested_x  # noqa: pylint: disable=attribute-defined-outside-init
        return TextLayoutRect((original_width - requested_x, self.height))

    def vertical_overlap(self, other_rect: pygame.Rect) -> bool:
        """
        Test if two rectangles overlap one another in the y axis.

        :param other_rect:
        :return: True if they overlap.
        """
        above = self.bottom <= other_rect.top
        below = self.top > other_rect.bottom

        return not (above or below)
