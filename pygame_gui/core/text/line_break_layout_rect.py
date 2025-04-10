from typing import Tuple, Optional

import pygame
from pygame.surface import Surface
from pygame.rect import Rect
from pygame import Color

from pygame_gui.core.interfaces import IColourGradientInterface
from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.colour_gradient import ColourGradient


class LineBreakLayoutRect(TextLayoutRect):
    """
    Represents a line break, or new line, instruction in the text to the text layout system.

    :param dimensions: The dimensions of the 'line break', the height is the important thing
                       so the new lines are spaced correctly for the last active font.
    """

    def __init__(self, dimensions: Tuple[int, int], font):
        super().__init__(dimensions)
        self.letter_count = 1
        self.is_selected = False
        self.selection_colour: pygame.Color | IColourGradientInterface = Color(
            128, 128, 128, 255
        )
        self.selection_chunk_width = 4
        self.select_surf: Optional[Surface] = None
        self.font = font

    def __repr__(self):
        return f"<LineBreakLayoutRect {super().__repr__()} >"

    def finalise(
        self,
        target_surface: Surface,
        target_area: Rect,
        row_chunk_origin: int,
        row_chunk_height: int,
        row_bg_height: int,
        row_line_spacing_height: int,
        x_scroll_offset: int = 0,
        letter_end: Optional[int] = None,
    ):
        self.height = row_bg_height
        if self.is_selected:
            self.select_surf = Surface(
                (self.selection_chunk_width, self.height), flags=pygame.SRCALPHA
            )
            if isinstance(self.selection_colour, ColourGradient):
                self.select_surf.fill(Color("#FFFFFFFF"))
                self.selection_colour.apply_gradient_to_surface(self.select_surf)
            elif isinstance(self.selection_colour, Color):
                self.select_surf.fill(self.selection_colour)
            target_surface.blit(
                self.select_surf, self.topleft, special_flags=pygame.BLEND_PREMULTIPLIED
            )
        # should be cleared by row
