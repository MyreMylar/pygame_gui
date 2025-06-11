import pytest

from pygame_gui.core.text import TextLayoutRect, TextFloatPosition
from pygame_gui.ui_manager import UIManager


class TestTextLayoutRect:
    def test_creation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        text_layout_rect = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )

        assert text_layout_rect.size == (100, 50)

    def test_can_split(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        text_layout_rect = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )

        assert text_layout_rect.can_split()

        text_layout_rect_no_split = TextLayoutRect(
            dimensions=(100, 50),
            can_split=False,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )

        assert not text_layout_rect_no_split.can_split()

    def test_should_span(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        text_layout_rect = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=True,
        )

        assert text_layout_rect.should_span()

        text_layout_rect_no_span = TextLayoutRect(
            dimensions=(100, 50),
            can_split=False,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )

        assert not text_layout_rect_no_span.should_span()

    def test_float_pos(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        rect_float_none = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=True,
        )

        assert rect_float_none.float_pos() == TextFloatPosition.NONE

        rect_float_left = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.LEFT,
            should_span=True,
        )

        assert rect_float_left.float_pos() == TextFloatPosition.LEFT

        rect_float_right = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.RIGHT,
            should_span=True,
        )

        assert rect_float_right.float_pos() == TextFloatPosition.RIGHT

    def test_split(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        layout_rect = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )

        with pytest.raises(ValueError, match="Line width is too narrow"):
            layout_rect.split(requested_x=0, line_width=0, row_start_x=0)

        with pytest.raises(ValueError, match="Row start must be 0 or greater"):
            layout_rect.split(requested_x=50, line_width=50, row_start_x=-20)

        new_rect = layout_rect.split(requested_x=50, line_width=50, row_start_x=0)

        assert layout_rect.width == 50
        assert new_rect.width == 50
        assert layout_rect.height == new_rect.height

    def test_vertical_overlap(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        layout_rect_1 = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )
        layout_rect_1.topleft = (0, 0)

        layout_rect_2 = TextLayoutRect(
            dimensions=(100, 50),
            can_split=True,
            float_pos=TextFloatPosition.NONE,
            should_span=False,
        )
        layout_rect_2.topleft = (0, 45)

        assert layout_rect_1.vertical_overlap(layout_rect_2)

        layout_rect_2.topleft = (0, 65)

        assert not layout_rect_1.vertical_overlap(layout_rect_2)

        layout_rect_2.topleft = (120, 65)

        assert not layout_rect_1.vertical_overlap(layout_rect_2)

        layout_rect_2.topleft = (120, 25)

        assert layout_rect_1.vertical_overlap(layout_rect_2)


if __name__ == "__main__":
    pytest.console_main()
