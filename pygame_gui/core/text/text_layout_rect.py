from typing import Tuple, Union, Optional
from abc import abstractmethod

import pygame
from pygame.surface import Surface


class TextLayoutRect(pygame.Rect):
    """
    A base class for use in Layouts.
    """
    FLOAT_NONE = 0
    FLOAT_LEFT = 1
    FLOAT_RIGHT = 2

    def __init__(self, dimensions: Tuple[int, int],
                 *,
                 can_split=False,
                 float_pos=FLOAT_NONE,
                 should_span=False):
        super().__init__((0, 0), dimensions)
        self._can_split = can_split
        self._float_pos = float_pos
        self._should_span = should_span
        self.letter_count = 0

    @abstractmethod
    def finalise(self, target_surface: Surface, letter_end: Optional[int] = None):
        """
        Bake the contents of this layout rect onto a surface.

        :param target_surface:
        :param letter_end:
        """

    def clear(self):
        """
        Clear the space this rect takes up on the finalised surface.
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

    def float_pos(self) -> int:
        """
        Return the 'floating' status of this rectangle. can be FLOAT_LEFT, FLOAT_RIGHT or
        FLOAT_NONE and the  default, used by most rectangles, is FLOAT_NONE.

        Used to make text flow around images.

        :return: returns the float status of this rectangle.
        """
        return self._float_pos

    def split(self, requested_x: int) -> Union['TextLayoutRect', None]:  # noqa
        """
        Try to perform a split operation on this rectangle. Often rectangles will be split at the
        nearest point that is still less than the request (i.e. to the left of the request in
        the common left-to-right text layout case) .

        :param requested_x: the requested place to split this rectangle along it's width.
        """
        super().width = requested_x
        return TextLayoutRect((self.width - requested_x, self.height))

    def vertical_overlap(self, other_rect: pygame.Rect) -> bool:
        """
        Test if two rectangles overlap one another in the y axis.

        :param other_rect:
        :return: True if they overlap.
        """
        above = self.bottom <= other_rect.top
        below = self.top > other_rect.bottom

        return not (above or below)

    def style_match(self, other_rect):
        return True

    def insert_text(self, input_text: str, index: int):
        pass
