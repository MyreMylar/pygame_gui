import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox


class TestUITextBox:

    def test_creation(self, _init_pygame: None, default_ui_manager: UIManager):
        default_ui_manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                                          {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_non_default.json"))

        manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                               {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=fira_code>Some text in a <b>bold box</b> using "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        assert text_box.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_bad_values.json"))

        manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                               {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=fira_code>Some text in a <b>bold box</b> using "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        assert text_box.image is not None
