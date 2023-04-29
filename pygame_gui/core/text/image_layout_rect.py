from typing import Optional

import pygame
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.image import load

from pygame_gui.core.text.text_layout_rect import TextLayoutRect, Padding


class ImageLayoutRect(TextLayoutRect):
    """
    Represents an image that sits in the text.
    """
    def __init__(self, image_path, float_position, padding: Padding):
        self.image_path = image_path
        self.image_surf = load(image_path).convert_alpha().premul_alpha()
        self.padding = padding
        self.size_with_padding = (self.image_surf.get_width() + padding.left + padding.right,
                                  self.image_surf.get_height() + padding.top + padding.bottom)
        super().__init__(self.size_with_padding, float_pos=float_position)

    def finalise(self,
                 target_surface: Surface,
                 target_area: Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 x_scroll_offset: int = 0,
                 letter_end: Optional[int] = None):
        blit_rect = self.copy()
        blit_rect.width -= (self.padding.left + self.padding.right)
        blit_rect.height -= (self.padding.top + self.padding.bottom)
        blit_rect.left += self.padding.left
        blit_rect.top += self.padding.top
        target_surface.blit(self.image_surf, blit_rect, target_area, special_flags=pygame.BLEND_PREMULTIPLIED)
