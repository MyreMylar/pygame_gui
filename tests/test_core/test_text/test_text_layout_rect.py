from collections import deque

import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TextLayoutRect, TextFloatPosition, TextLineChunkFTFont, TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.ui_manager import UIManager


class TestTextLayoutRect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_layout_rect = TextLayoutRect(dimensions=(100, 50),
                                          can_split=True,
                                          float_pos=TextFloatPosition.none,
                                          should_span=False)

        assert text_layout_rect.size == (100, 50)


if __name__ == '__main__':
    pytest.console_main()
