from typing import Tuple, Optional

from pygame.surface import Surface
from pygame.rect import Rect
from pygame.image import load

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class ImageLayoutRect(TextLayoutRect):
    """
    Represents an image that sits in the text.
    """
    def __init__(self, image_path, float_position):
        self.image_surf = load(image_path)
        super().__init__(self.image_surf.get_size(), float_pos=float_position)

    def finalise(self,
                 target_surface: Surface,
                 target_area: Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 x_scroll_offset: int = 0,
                 letter_end: Optional[int] = None):

        target_surface.blit(self.image_surf, self, target_area)
