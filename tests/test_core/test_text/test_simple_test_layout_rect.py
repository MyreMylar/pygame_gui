import pygame
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import SimpleTestLayoutRect


class TestSimpleTestLayoutRect:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))

        assert simple_rect.width == 200
        assert simple_rect.height == 30

    def test_gen_random_colour(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        colour_1 = SimpleTestLayoutRect.gen_random_colour()
        colour_2 = SimpleTestLayoutRect.gen_random_colour()
        colour_3 = SimpleTestLayoutRect.gen_random_colour()
        colour_4 = SimpleTestLayoutRect.gen_random_colour()

        assert not (colour_1 == colour_2 and colour_1 == colour_2 and
                    colour_1 == colour_3 and colour_1 == colour_4)

    def test_finalise(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))

        rendered_chunk_surf = pygame.Surface((200, 30))
        rendered_chunk_surf.fill((0, 0, 0))
        simple_rect.finalise(target_surface=rendered_chunk_surf,
                             target_area=pygame.Rect(0, 0, 200, 30),
                             row_chunk_origin=0,
                             row_chunk_height=20,
                             row_bg_height=20)

        assert rendered_chunk_surf.get_at((1, 5)) != pygame.Color(0, 0, 0)
        assert simple_rect.width == 200
        assert simple_rect.height == 30

    def test_split(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))

        assert simple_rect.width == 200
        assert simple_rect.height == 30

        new_rect = simple_rect.split(requested_x=100, line_width=120, row_start_x=0)

        assert simple_rect.width == 66
        assert simple_rect.height == 30
        assert new_rect.width == 134
        assert new_rect.height == 30

        another_rect = simple_rect.split(requested_x=10, line_width=120, row_start_x=0)

        assert simple_rect.width == 10
        assert simple_rect.height == 30
        assert another_rect.width == 56
        assert another_rect.height == 30

        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30), create_split_points=False)

        assert simple_rect.split_points == []

        with pytest.raises(ValueError, match="Line width is too narrow"):
            simple_rect.split(requested_x=10, line_width=0, row_start_x=0)


if __name__ == '__main__':
    pytest.console_main()
