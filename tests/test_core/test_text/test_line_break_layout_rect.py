import pygame
import pygame.freetype
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import LineBreakLayoutRect


class TestLineBreakLayoutRect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        line_break_rect = LineBreakLayoutRect(dimensions=(200, 30), font=default_font)

        assert line_break_rect.width == 200
        assert line_break_rect.height == 30

    def test_finalise(self, _init_pygame, default_ui_manager: UIManager):
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        line_break_rect = LineBreakLayoutRect(dimensions=(200, 30), font=default_font)

        rendered_chunk_surf = pygame.Surface((200, 30))
        rendered_chunk_surf.fill((0, 0, 0))
        line_break_rect.finalise(target_surface=rendered_chunk_surf,
                                 target_area=pygame.Rect(0, 0, 200, 30),
                                 row_chunk_origin=0,
                                 row_chunk_height=20,
                                 row_bg_height=20)

        assert rendered_chunk_surf.get_at((1, 5)) == pygame.Color(0, 0, 0)
        assert line_break_rect.width == 200
        assert line_break_rect.height == 30


if __name__ == '__main__':
    pytest.console_main()
