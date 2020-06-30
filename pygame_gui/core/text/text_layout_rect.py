from typing import Tuple, Union
from abc import abstractmethod

from pygame.rect import Rect
from pygame.surface import Surface


class TextLayoutRect(Rect):
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

    @abstractmethod
    def finalise(self, target_surface: Surface):
        """
        Bake the contents of this layout rect onto a surface.

        :param target_surface:
        """

    def can_split(self):
        return self._can_split

    def should_span(self):
        return self._should_span

    def float_pos(self) -> int:
        return self._float_pos

    def split(self, requested_x: int) -> Union['TextLayoutRect', None]:  # noqa
        return None

    def vertical_overlap(self, other_rect: Rect) -> bool:
        """
        Test if two rectangles overlap one another in the y axis.
        :param other_rect:
        :return: True if they overlap.
        """
        above = self.bottom <= other_rect.top
        below = self.top > other_rect.bottom

        return not (above or below)
