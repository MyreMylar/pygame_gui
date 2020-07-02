from typing import Tuple

from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class LineBreakLayoutRect(TextLayoutRect):
    """
    Represents a line break, or new line, instruction in the text to the text layout system.

    :param dimensions: The dimensions of the 'line break', the height is the important thing
                       so the new lines are spaced correctly for the last active font.
    """
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)

    def finalise(self, target_surface: Surface):
        pass
