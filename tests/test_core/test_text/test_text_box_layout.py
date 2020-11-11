from collections import deque
import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from pygame_gui.ui_manager import UIManager

from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.text import SimpleTestLayoutRect


class TestTextBoxLayout:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        TextBoxLayout(input_data_queue=input_data,
                      layout_rect=pygame.Rect(0, 0, 200, 300),
                      view_rect=pygame.Rect(0, 0, 200, 150),
                      line_spacing=1.0)

    def test_creation_with_data(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        assert len(layout.layout_rows) > 0

    def test_reprocess_layout_queue(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        assert len(layout.layout_rows) == 4
        layout.reprocess_layout_queue(pygame.Rect(0, 0, 100, 300))
        assert len(layout.layout_rows) == 8


if __name__ == '__main__':
    pytest.console_main()
