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

    def test_set_text_forbidden_characters(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_forbidden_characters('numbers')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid characters on text entry element"):
            text_entry.set_text("1,2,3,4,5")

    def test_rebuild_select_area_1(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_2(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_non_default.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_set_text_rebuild_select_area_3(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_redraw_cursor(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.cursor_on = True
        text_entry.edit_position = 1
        text_entry.redraw_cursor()

        assert text_entry.image is not None

    def test_select(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.select()

        assert text_entry.image is not None

    def test_unselect(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.unselect()

        assert text_entry.image is not None

    def test_process_event_text_entered(self, _init_pygame: None, default_ui_manager: UIManager,
                                        _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.select()
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d, 'mod': 0,
                                                                           'unicode': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        assert text_entry.get_text() == 'dan'

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
