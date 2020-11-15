from typing import Tuple, Optional

from pygame.surface import Surface
from pygame.rect import Rect

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class LineBreakLayoutRect(TextLayoutRect):
    """
    Represents a line break, or new line, instruction in the text to the text layout system.

    :param dimensions: The dimensions of the 'line break', the height is the important thing
                       so the new lines are spaced correctly for the last active font.
    """
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)

    def finalise(self,
                 target_surface: Surface,
                 target_area: Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 letter_end: Optional[int] = None):
        pass
