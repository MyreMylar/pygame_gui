import pygame
import pygame.freetype
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import SimpleTestLayoutRect


class TestSimpleTestLayoutRect:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(100, 30))

        assert simple_rect.width == 100
        assert simple_rect.height == 30

    def test_gen_random_colour(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        colour_1 = SimpleTestLayoutRect.gen_random_colour()
        colour_2 = SimpleTestLayoutRect.gen_random_colour()
        colour_3 = SimpleTestLayoutRect.gen_random_colour()
        colour_4 = SimpleTestLayoutRect.gen_random_colour()

        assert (
            colour_1 != colour_2
            or colour_1 != colour_2
            or colour_1 != colour_3
            or colour_1 != colour_4
        )

    def test_finalise(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))

        rendered_chunk_surf = pygame.Surface((200, 30))
        rendered_chunk_surf.fill((0, 0, 0))
        simple_rect.finalise(target_surface=rendered_chunk_surf,
                             target_area=pygame.Rect(0, 0, 200, 30),
                             row_chunk_origin=0,
                             row_chunk_height=20,
                             row_bg_height=20,
                             row_line_spacing_height=20)

        assert rendered_chunk_surf.get_at((1, 5)) != pygame.Color(0, 0, 0)
        assert simple_rect.width == 200
        assert simple_rect.height == 30

    def test_split(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))

        assert simple_rect.width == 200
        assert simple_rect.height == 30

        self._split_and_check_result(simple_rect, 100, 66, 134)
        self._split_and_check_result(simple_rect, 10, 10, 56)
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30), create_split_points=False)

        assert simple_rect.split_points == []

        with pytest.raises(ValueError, match="Line width is too narrow"):
            simple_rect.split(requested_x=10, line_width=0, row_start_x=0)

    # TODO Rename this here and in `test_split`
    @staticmethod
    def _split_and_check_result(simple_rect, requested_x, arg2, arg3):
        new_rect = simple_rect.split(
            requested_x=requested_x, line_width=120, row_start_x=0
        )

        assert simple_rect.width == arg2
        assert simple_rect.height == 30
        assert new_rect.width == arg3
        assert new_rect.height == 30

    def test_split_line_width_too_narrow(self):

        # Arrange
        rect = SimpleTestLayoutRect(dimensions=(100, 20), create_split_points=True)
        rect.smallest_split_size = 50
        requested_x = 60
        line_width = 40  # Too narrow
        row_start_x = 10

        # Act & Assert
        with pytest.raises(ValueError, match='Line width is too narrow'):
            rect.split(requested_x, line_width, row_start_x)

    @pytest.mark.parametrize("requested_x, line_width, row_start_x, split_points, expected_width", [
        # Happy path tests
        (60, 100, 10, [25, 50, 75], 50),  # id: split_at_50
        (40, 100, 10, [25, 50, 75], 25),  # id: split_at_25
        (90, 100, 10, [25, 50, 75], 75),  # id: split_at_75
        (20, 100, 10, [25, 50, 75], 20),  # id: no split point so split_at_20

        # Edge cases
        (100, 100, 10, [25, 50, 75], 75),  # id: requested_x_at_edge
        (25, 100, 10, [25, 50, 75], 25),  # id: requested_x_on_split_point
        (60, 100, 10, [], 60),  # id: no_split_points so split_at_60
        (60, 100, 10, [10, 20], 20),  # id: split_points_less_than_requested
        (10, 100, 10, [25, 50, 75], 10),  # id: requested_x_before_split_points

        # Force split at start of line
        (60, 100, 10, [], 60),  # id: force_split_at_start
        (20, 100, 10, [], 20),  # id: force_split_at_start_small_x
    ])
    def test_split_various_cases(self, requested_x, line_width, row_start_x, split_points, expected_width):

        # Arrange
        rect = SimpleTestLayoutRect(dimensions=(100, 20), create_split_points=True)
        rect.split_points = split_points
        rect.x = row_start_x

        # Act
        new_rect = rect.split(requested_x, line_width, row_start_x)

        # Assert
# sourcery skip: no-conditionals-in-tests
        if expected_width > 0:
            assert new_rect is not None
            assert new_rect.width == 100 - expected_width
            assert rect.width == expected_width
        else:
            assert new_rect is None
            assert rect.width == 100

    def test_split_allow_split_dashes_false(self):
        # Arrange
        rect = SimpleTestLayoutRect(dimensions=(100, 20), create_split_points=True)
        rect.split_points = [25, 50, 75]
        rect.x = 10
        rect.left = 0
        requested_x = 60
        line_width = 100
        row_start_x = 10
        allow_split_dashes = False

        # Act
        new_rect = rect.split(requested_x, line_width, row_start_x, allow_split_dashes)

        # Assert
        assert new_rect is not None
        assert new_rect.width == 100 - 50
        assert rect.width == 50


if __name__ == '__main__':
    pytest.console_main()
