import pytest
import pytest_benchmark

import pygame

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox


def create_new_text_box(default_ui_manager):
    UITextBox(
        html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                  "<i>styles</i>.",
        relative_rect=pygame.Rect(100, 100, 200, 300),
        manager=default_ui_manager)


def test_new_style_text_box_performance(benchmark, _init_pygame,
                                        default_ui_manager: UIManager,
                                        _display_surface_return_none):

    default_ui_manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                                      {"name": "fira_code", "size:": 14, "style": "italic"}])

    benchmark(create_new_text_box, default_ui_manager)


if __name__ == '__main__':
    pytest.console_main()
