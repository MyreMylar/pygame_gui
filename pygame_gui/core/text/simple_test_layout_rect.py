from typing import Tuple, Optional
import random

import pygame

from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect, TextFloatPosition


class SimpleTestLayoutRect(TextLayoutRect):
    """
    Useful class for testing layout generation. Multi coloured boxes make it easy to distinguish
    different layout Rects from one another and it's possible to set all the layout options in the
    constructor/initializer to represent different types of layout rect.
    """

    def __init__(self,
                 dimensions: Tuple[int, int], *,
                 create_split_points=True,
                 float_pos=TextFloatPosition.none):

        super().__init__(dimensions, can_split=create_split_points, float_pos=float_pos)
        self.colour = self.gen_random_colour()

        self.smallest_split_size = 1

        if create_split_points:
            self.split_points = [int(dimensions[0] / 3),
                                 int(dimensions[0] / 3) * 2]
        else:
            self.split_points = []

    @staticmethod
    def gen_random_colour():
        """
        Creates a random colour using the golden ratio method.

        Helps make the test layout rects reasonably distinctive from each other.
        """
        golden_ratio = ((5 ** 0.5) - 1) / 2
        colour = Color("#000000")
        colour.hsla = 360 * ((random.uniform(1.0, 500.0) * golden_ratio) % 1), 50, 70, 100
        return colour

    def finalise(self,
                 target_surface: Surface,
                 target_area: pygame.Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 letter_end: Optional[int] = None):
        surface = Surface(self.size, depth=32, flags=pygame.SRCALPHA)
        surface.fill(self.colour)
        target_surface.blit(surface, self, area=target_area)

    def split(self, requested_x: int, line_width: int, row_start_x: int):

        if line_width < self.smallest_split_size:
            raise ValueError('Line width is too narrow')

        # find closest split point less than the request
        current_split_point = 0
        found_any_split_point = False
        for point in self.split_points:
            if requested_x > point > self.left + current_split_point:
                current_split_point = point
                found_any_split_point = True

        if self.x == row_start_x and not found_any_split_point:
            # no nice split point and we are at start of a line so force a split.
            current_split_point = requested_x

        if current_split_point != 0:
            new_rect = SimpleTestLayoutRect(dimensions=(self.width - current_split_point, # noqa pylint: disable=no-member
                                                        self.height),
                                            create_split_points=True)
            self.width -= new_rect.width  # pylint: disable=no-member
            return new_rect
        else:
            return None
