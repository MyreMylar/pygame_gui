from collections import deque
import pygame
import pygame.freetype
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from pygame_gui.ui_manager import UIManager

from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.text import SimpleTestLayoutRect, TextLineChunkFTFont, HyperlinkTextChunk
from pygame_gui.core.text import TextBoxLayoutRow
from pygame_gui.core.text import HorizRuleLayoutRect


class TestHorizRuleLayoutRect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        HorizRuleLayoutRect(height=20,
                            colour_or_gradient=pygame.Color('#FFFFFF'))

    def test_finalise(self):
        horiz_rule = HorizRuleLayoutRect(height=20,
                                         rule_dimensions=(-1, 1),
                                         colour_or_gradient=pygame.Color('#FFFFFF'))

        assert horiz_rule.width == -1

        horiz_rule.width = 200
        assert horiz_rule.width == 200

        rule_surface = pygame.Surface((200, 20), flags=pygame.SRCALPHA)
        rule_surface.fill(pygame.Color(0, 0, 0, 0))
        horiz_rule.finalise(target_surface=rule_surface,
                            target_area=None,
                            row_chunk_origin=0,
                            row_chunk_height=20,
                            row_bg_height=20)

        assert rule_surface.get_at((10, 2)) == pygame.Color(0, 0, 0, 0)
        assert rule_surface.get_at((10, 10)) == pygame.Color(255, 255, 255, 255)
        assert rule_surface.get_at((10, 11)) == pygame.Color(255, 255, 255, 63)


if __name__ == '__main__':
    pytest.console_main()
