import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine

from pygame_gui.core.utility import clipboard_paste


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

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_3(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_non_default_2.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
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

    def test_process_event_text_entered_success(self, _init_pygame: None, default_ui_manager: UIManager,
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

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_text_entered_too_long(self, _init_pygame: None, default_ui_manager: UIManager,
                                                 _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(3)
        text_entry.select()

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t, 'mod': 0,
                                                                     'unicode': 't'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_e, 'mod': 0,
                                                                     'unicode': 'e'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s, 'mod': 0,
                                                                     'unicode': 's'}))
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_s, 'mod': 0,
                                                                           'unicode': 't'}))

        assert processed_key_event is False and text_entry.get_text() == 'tes'

    def test_process_event_text_ctrl_c(self, _init_pygame: None,
                                       _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text('dan')
        text_entry.select()
        text_entry.select_range = [0, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_c, 'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'c'}))

        text_entry.redraw_cursor()

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_text_ctrl_v(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.select()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c, 'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 0]
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v, 'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'danan'

    def test_process_event_text_ctrl_a(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.select()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a, 'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c, 'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))

        text_entry.select_range = [0, 0]
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v, 'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dandan'

    def test_process_event_text_ctrl_x(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.select()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a, 'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_x, 'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'x'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v, 'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_mouse_buttons(self, _init_pygame: None, default_ui_manager: UIManager,
                                         _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1, 'pos': (30, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                         {'button': 1, 'pos': (80, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [3, 9])

    def test_process_event_text_return(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.select()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RETURN}))

        assert processed_key_event

    def test_set_allowed_characters_numbers(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_allowed_characters('numbers')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid characters on text entry element"):
            text_entry.set_text("one two three")
            assert text_entry.get_text() == ""

    def test_set_allowed_characters_anything(self, _init_pygame, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_allowed_characters(['D','A','N'])
        with pytest.warns(UserWarning, match="Tried to set text string with invalid characters on text entry element"):
            text_entry.set_text("HORSE")
            assert text_entry.get_text() == ""

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
