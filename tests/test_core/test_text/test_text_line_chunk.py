from collections import deque

import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TextBoxLayout, TextLineChunkFTFont, TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.ui_manager import UIManager


class TestTextLineChunkFTFont:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#00000000'))

        assert chunk.text == 'test'


if __name__ == '__main__':
    pytest.console_main()
