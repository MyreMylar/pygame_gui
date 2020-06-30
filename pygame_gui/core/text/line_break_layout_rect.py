from typing import Tuple

from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class LineBreakLayoutRect(TextLayoutRect):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)

    def finalise(self, target_surface: Surface):
        pass
