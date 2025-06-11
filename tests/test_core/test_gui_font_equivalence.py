import pytest
import pygame

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame_gui.core.gui_font_freetype import GUIFontFreetype
from pygame_gui.core.gui_font_pygame import GUIFontPygame


class TestFontEquivalence:
    def test_creation(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        assert ftfont_font.point_size == pygame_font.point_size

    def test_underline(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        ftfont_font.underline = True
        pygame_font.underline = True
        assert ftfont_font.underline == pygame_font.underline

        ftfont_font.underline = False
        pygame_font.underline = False
        assert ftfont_font.underline == pygame_font.underline

    def test_underline_adjustment(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        ftfont_font.underline_adjustment = 0.5
        pygame_font.underline_adjustment = 0.5
        assert ftfont_font.underline_adjustment == pygame_font.underline_adjustment

        ftfont_font.underline_adjustment = 0.0
        pygame_font.underline_adjustment = 0.0
        assert ftfont_font.underline_adjustment == pygame_font.underline_adjustment

    def test_get_point_size(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        assert ftfont_font.get_point_size() == pygame_font.get_point_size()

    def test_get_padding_height(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        assert ftfont_font.get_padding_height() == pygame_font.get_padding_height()

    def test_get_rect(self, _init_pygame):
        """
        As it turns out pygame.freetype's kerning support is more basic than SDL_ttf. As such the rectangles
        produced will not match exactly on some fonts where character pairs have kerning e.g. 'VA' or, as in
        this case 'Wo'.

        :param _init_pygame:
        :return:
        """
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        ftfont_rect = ftfont_font.get_rect("Hello World")
        pgfont_rect = pygame_font.get_rect("Hello World")
        assert ftfont_rect.width == pytest.approx(pgfont_rect.width, rel=1)
        assert ftfont_rect.height == pytest.approx(pgfont_rect.height, rel=2)
        assert ftfont_rect.top == pgfont_rect.top
        assert ftfont_rect.left == pgfont_rect.left

    def test_metrics(self, _init_pygame):
        ftfont_font = GUIFontFreetype(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )
        pygame_font = GUIFontPygame(
            "tests/data/Roboto-Regular.ttf", 20, force_style=False, style=None
        )

        ftfont_metrics = ftfont_font.get_metrics("Hello World")
        pgfont_metrics = pygame_font.get_metrics("Hello World")

        # pgfont: (minx, maxx, miny, maxy, advance)
        # ftfont: (min_x, max_x, min_y, max_y, horizontal_advance_x, horizontal_advance_y)
        for index, char in enumerate("Hello World"):
            assert ftfont_metrics[index][0] == pgfont_metrics[index][0]  # min x
            assert ftfont_metrics[index][1] == pgfont_metrics[index][1]  # max x
            assert ftfont_metrics[index][2] == pgfont_metrics[index][2]  # min y
            assert ftfont_metrics[index][3] == pgfont_metrics[index][3]  # max y
            assert (
                ftfont_metrics[index][4] == pgfont_metrics[index][4]
            )  # horizontal_advance_x
            # pg font does nto have vertical advance in the metrics (do we use it?)


if __name__ == "__main__":
    pytest.console_main()
