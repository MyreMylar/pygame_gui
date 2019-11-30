import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine


class TestUITextEntryLine:

    def test_creation(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)
        assert text_entry.image is not None

    def test_set_text_length_limit(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(10)

        with pytest.warns(UserWarning, match="Tried to set text string that is too long on text entry element"):
            text_entry.set_text("GOLD PYJAMAS GOLD PYJAMAS")

    def test_set_text_success(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(10)
        text_entry.set_text("GOLD")

        assert text_entry.get_text() == "GOLD"

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_non_default.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        assert text_entry.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)
        assert text_entry.image is not None
