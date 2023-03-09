import os
import pytest
import pygame
import platform

import i18n

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine
from pygame_gui.core.ui_container import UIContainer

from pygame_gui.core.utility import clipboard_paste, clipboard_copy


class TestUITextEntryLine:

    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)
        assert text_entry.image is not None

    def test_placeholder_text(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager,
                                     placeholder_text="Enter name...")
        assert text_entry.image is not None
        assert text_entry.drawable_shape.theming['text'] == "Enter name..."

        text_entry.set_text("Dan")

        assert text_entry.drawable_shape.theming['text'] == "Dan"

        text_entry.set_text("")

        assert text_entry.drawable_shape.theming['text'] == "Enter name..."

        text_entry.focus()

        assert text_entry.drawable_shape.theming['text'] == ""

        text_entry.unfocus()

        assert text_entry.drawable_shape.theming['text'] == "Enter name..."

        i18n.add_translation('translation.enter_age', 'Enter age...')

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager,
                                     placeholder_text='translation.enter_age')
        assert text_entry.image is not None
        assert text_entry.drawable_shape.theming['text'] == "Enter age..."

    def test_initial_text(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager,
                                     initial_text="Bob")
        assert text_entry.image is not None
        assert text_entry.drawable_shape.theming['text'] == "Bob"

    def test_clear(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager,
                                     initial_text="Bob")
        assert text_entry.image is not None
        assert text_entry.drawable_shape.theming['text'] == "Bob"

        text_entry.clear()

        assert text_entry.image is not None
        assert text_entry.drawable_shape.theming['text'] == ""

    def test_set_text_length_limit(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(10)

        with pytest.warns(UserWarning, match="Tried to set text string that"
                                             " is too long on text entry element"):
            text_entry.set_text("GOLD PYJAMAS GOLD PYJAMAS")

    def test_set_text_success(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(10)
        text_entry.set_text("GOLD")

        assert text_entry.get_text() == "GOLD"

    def test_set_text_forbidden_characters(self, _init_pygame, _display_surface_return_none, default_ui_manager,):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_forbidden_characters('numbers')
        with pytest.warns(UserWarning,
                          match="Tried to set text string with invalid"
                                " characters on text entry element"):
            text_entry.set_text("1,2,3,4,5")

    def test_hidden_text(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_hidden(False)
        text_entry.set_text("Some basic text")
        text_entry.set_text_hidden(True)
        text_entry.set_text("Some other basic text")
        text_entry.set_text_hidden(False)
        text_entry.set_text_hidden(True)

        assert text_entry.image is not None

        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d, 'mod': 0,
                                                                     'unicode': 'd'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        text_entry.set_text_hidden(False)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.set_text_hidden(True)
        text_entry.select_range = [0, 0]
        text_entry.edit_position = 3
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                    {'key': pygame.K_v,
                                                     'mod': pygame.KMOD_CTRL,
                                                     'unicode': 'v'}))

        text_entry.select_range = [1, 3]
        text_entry.edit_position = 1
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                    {'key': pygame.K_v,
                                                     'mod': pygame.KMOD_CTRL,
                                                     'unicode': 'v'}))

        assert text_entry.image is not None

        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)
        text_entry.set_text('dan')
        text_entry.set_text_hidden(True)

        assert text_entry.image is not None

        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_symbol_font.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)
        text_entry.set_text('dan')
        with pytest.raises(ValueError, match='Selected font for UITextEntryLine'):
            text_entry.set_text_hidden(True)

    def test_rebuild_select_area_1(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_2(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_3(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
        text_entry.rebuild()

        assert text_entry.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_set_text_rebuild_select_area_3(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    # def test_redraw_cursor(self, _init_pygame, _display_surface_return_none, default_ui_manager):
    #     text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
    #                                  manager=default_ui_manager)
    #
    #     text_entry.set_text("GOLD")
    #     text_entry.select_range = [0, 2]
    #     text_entry.cursor_on = True
    #     text_entry.edit_position = 1
    #     text_entry.redraw_cursor()
    #
    #     assert text_entry.image is not None

    def test_focus(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.focus()

        assert text_entry.image is not None

    def test_unfocus(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.unfocus()

        assert text_entry.image is not None

    def test_process_event_text_entered_success(self, _init_pygame: None,
                                                default_ui_manager: UIManager,
                                                _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d,
                                                                           'mod': 0,
                                                                           'unicode': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_text_entered_forbidden(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.focus()

        text_entry.set_forbidden_characters(['d', 'a', 'n'])
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d,
                                                                           'mod': 0,
                                                                           'unicode': 'd'}))

        assert processed_key_event is False and text_entry.get_text() == ''

    def test_process_event_text_entered_not_allowed(self, _init_pygame: None,
                                                    default_ui_manager: UIManager,
                                                    _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.focus()

        text_entry.set_allowed_characters(['d', 'a', 'n'])
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_o,
                                                                           'mod': 0,
                                                                           'unicode': 'o'}))

        assert processed_key_event is False and text_entry.get_text() == ''

    def test_process_event_text_entered_with_select_range(self, _init_pygame: None,
                                                          default_ui_manager: UIManager,
                                                          _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('Hours and hours of fun writing tests')
        text_entry.focus()
        text_entry.select_range = [1, 9]

        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_o,
                                                                           'mod': 0,
                                                                           'unicode': 'o'}))

        assert (processed_key_event is True and
                text_entry.get_text() == 'Ho hours of fun writing tests')

    def test_process_event_text_entered_too_long(self, _init_pygame: None,
                                                 default_ui_manager: UIManager,
                                                 _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text_length_limit(3)
        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t, 'mod': 0,
                                                                     'unicode': 't'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_e, 'mod': 0,
                                                                     'unicode': 'e'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s, 'mod': 0,
                                                                     'unicode': 's'}))
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_s,
                                                                           'mod': 0,
                                                                           'unicode': 't'}))

        assert processed_key_event is False and text_entry.get_text() == 'tes'

    def test_process_event_text_ctrl_c(self, _init_pygame: None,
                                       _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_c,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'c'}))
        text_entry.cursor_on = True
        # text_entry.redraw_cursor()

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_text_ctrl_v(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 0]
        text_entry.edit_position = 3
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'danan'

    def test_process_event_text_ctrl_v_nothing(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        clipboard_copy('')
        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 0]
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_ctrl_v_over_limit(self, _init_pygame: None,
                                             default_ui_manager: UIManager,
                                             _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.length_limit = 3
        text_entry.select_range = [0, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 0]
        text_entry.edit_position = 3
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_ctrl_v_at_limit(self, _init_pygame: None, default_ui_manager: UIManager,
                                           _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.length_limit = 3
        text_entry.select_range = [0, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))

        text_entry.set_text('bob')
        text_entry.focus()
        text_entry.select_range = [0, 3]
        text_entry.edit_position = 0
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_ctrl_v_over_limit_select_range(self, _init_pygame: None,
                                                          default_ui_manager: UIManager,
                                                          _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.length_limit = 3
        text_entry.select_range = [0, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [2, 3]
        text_entry.edit_position = 3
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_text_ctrl_v_select_range(self, _init_pygame: None,
                                                    default_ui_manager: UIManager,
                                                    _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 3]
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event

        if not platform.system().upper() == "LINUX":
            # copy and paste is unreliable on linux, this part of the test fails fairly regularly there
            assert text_entry.get_text() == 'an'

    def test_process_event_text_ctrl_a(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))

        text_entry.select_range = [0, 0]
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dandan'

    def test_process_event_text_ctrl_x(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_x,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'x'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_mouse_buttons(self, _init_pygame: None, default_ui_manager: UIManager,
                                         _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (30, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                         {'button': 1,
                                                                          'pos': (80, 15)}))

        assert processed_down_event
        assert processed_up_event
        assert text_entry.select_range == [3, 9]

    def test_process_event_mouse_button_double_click(self, _init_pygame: None,
                                                     default_ui_manager: UIManager,
                                                     _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [7, 14])

        text_entry.set_text('')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 0])

    def test_process_event_mouse_button_double_click_in_empty_space(
            self, _init_pygame: None,
            default_ui_manager: UIManager,
            _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('                      dan')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 1])

    def test_process_event_mouse_button_double_click_first_word(self, _init_pygame: None,
                                                                default_ui_manager: UIManager,
                                                                _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': pygame.BUTTON_LEFT,
                                                        'pos': (15, 15)}))
        processed_up_event = text_entry.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': pygame.BUTTON_LEFT,
                                                        'pos': (15, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 3])

    def test_process_event_mouse_button_up_outside(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (30, 15)}))
        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                                           'pos': (80, 50)}))

        assert processed_down_event and text_entry.selection_in_progress is False

    def test_process_event_text_return(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RETURN}))

        assert processed_key_event

    def test_process_event_text_right(self, _init_pygame: None, default_ui_manager: UIManager,
                                      _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT}))

        assert processed_key_event

    def test_process_event_text_right_actually_move(self, _init_pygame: None,
                                                    default_ui_manager: UIManager,
                                                    _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.edit_position = 2
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT}))

        assert processed_key_event

    def test_process_event_text_left(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        assert text_entry.edit_position == 3

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT}))

        assert processed_key_event
        assert text_entry.edit_position == 2

    def test_process_event_home(self, _init_pygame: None, default_ui_manager: UIManager,
                                _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_HOME}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 0

    def test_process_event_end(self, _init_pygame: None, default_ui_manager: UIManager,
                               _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_END}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 3

    def test_process_event_text_right_select_range(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT}))

        assert processed_key_event

    def test_process_event_text_left_select_range(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT}))

        assert processed_key_event

    def test_process_event_delete_select_range(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DELETE}))

        assert processed_key_event

    def test_process_event_delete(self, _init_pygame: None, default_ui_manager: UIManager,
                                  _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.edit_position = 1

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DELETE}))

        assert processed_key_event

    def test_process_event_backspace(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.edit_position = 2
        text_entry.start_text_offset = 1

        processed_key_event = text_entry.process_event(
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE}))

        assert processed_key_event

    def test_process_event_backspace_select_range(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        processed_key_event = text_entry.process_event(
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE}))

        assert processed_key_event

    def test_set_allowed_characters_predefined(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_allowed_characters('numbers')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid"
                                             " characters on text entry element"):
            text_entry.set_text("one two three")
            assert text_entry.get_text() == ""

        text_entry.set_allowed_characters('letters')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid"
                                             " characters on text entry element"):
            text_entry.set_text("123")
            assert text_entry.get_text() == ""

        text_entry.set_allowed_characters('alpha_numeric')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid"
                                             " characters on text entry element"):
            text_entry.set_text("*&%")
            assert text_entry.get_text() == ""

        default_ui_manager.set_locale('jp')
        text_entry.set_allowed_characters('numbers')
        text_entry.set_allowed_characters('letters')
        text_entry.set_allowed_characters('alpha_numeric')

    def test_set_allowed_characters_anything(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_allowed_characters(['D', 'A', 'N'])
        with pytest.warns(UserWarning, match="Tried to set text string with invalid "
                                             "characters on text entry element"):
            text_entry.set_text("HORSE")
            assert text_entry.get_text() == ""

    def test_set_allowed_characters_invalid_id(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        with pytest.warns(UserWarning, match="Trying to set allowed characters by "
                                             "type string, but no match"):
            text_entry.set_allowed_characters('dan')

    def test_set_forbidden_characters_predefined(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_forbidden_characters('forbidden_file_path')
        with pytest.warns(UserWarning, match="Tried to set text string with invalid "
                                             "characters on text entry element"):
            text_entry.set_text(">:<")
            assert text_entry.get_text() == ""

        default_ui_manager.set_locale('jp')
        text_entry.set_forbidden_characters('forbidden_file_path')
        text_entry.set_forbidden_characters('numbers')

    def test_set_forbidden_characters_anything(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.set_forbidden_characters(['D', 'A', 'N'])
        with pytest.warns(UserWarning, match="Tried to set text string with invalid "
                                             "characters on text entry element"):
            text_entry.set_text("DAN")
            assert text_entry.get_text() == ""

    def test_set_forbidden_characters_invalid_id(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        with pytest.warns(UserWarning, match="Trying to set forbidden characters by type "
                                             "string, but no match"):
            text_entry.set_forbidden_characters('dan')

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_redraw_selected_text(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("Yellow su")
        text_entry.select_range = [3, 8]
        text_entry.start_text_offset = 500
        text_entry.redraw()

    def test_redraw_selected_text_different_them(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.set_text("Yellow su")
        text_entry.select_range = [3, 9]
        text_entry.redraw()

    def test_update(self,  _init_pygame, _display_surface_return_none):
        pygame.display.init()

        class MouselessManager(UIManager):
            fixed_mouse_pos = (0, 0)

            def _update_mouse_position(self):
                self.mouse_position = MouselessManager.fixed_mouse_pos

        manager = MouselessManager((800, 600), os.path.join("tests", "data",
                                                            "themes",
                                                            "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.update(0.01)

        assert text_entry.alive()
        assert not manager.text_input_hovered

        MouselessManager.fixed_mouse_pos = (200, 115)
        manager.update(0.01)
        assert manager.text_input_hovered

        text_entry.kill()

        text_entry.update(0.01)

        assert not text_entry.alive()

    def test_update_after_click(self,  _init_pygame, _display_surface_return_none: None, default_ui_manager):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=manager)

        text_entry.set_text('Wow testing is great so amazing')
        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                                             'pos': (30, 15)}))
        default_ui_manager.mouse_position = (70, 15)

        text_entry.update(0.01)

    def test_update_newline_after_click(self,  _init_pygame, _display_surface_return_none: None, default_ui_manager):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 200, 30),
                                     manager=manager)

        text_entry.set_text('Wow testing is great so amazing\n\n')
        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                                             'pos': (30, 15)}))
        default_ui_manager.mouse_position = (70, 15)

        text_entry.update(0.01)

    def test_update_after_long_wait(self,  _init_pygame):
        pygame.display.init()
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.update(0.01)
        text_entry.update(5.0)

    def test_update_cursor_blink(self,  _init_pygame, _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        text_entry.focus()
        text_entry.cursor_blink_delay_after_moving_acc = 10.0
        text_entry.update(0.01)
        text_entry.blink_cursor_time_acc = 10.0
        text_entry.update(0.01)
        text_entry.blink_cursor_time_acc = 10.0
        text_entry.update(0.01)

    def test_rebuild_from_theme_data_non_default(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)

        assert text_entry.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=manager)
        assert text_entry.image is not None

    def test_set_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 150, 30),
                                     container=test_container,
                                     manager=default_ui_manager)

        text_entry.set_position((150.0, 30.0))

        assert (text_entry.relative_rect.topleft == (50, -70) and
                text_entry.drawable_shape.containing_rect.topleft == (150, 30))

    def test_set_relative_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(50, 50, 300, 250),
                                     manager=default_ui_manager)
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 150, 30),
                                     container=test_container,
                                     manager=default_ui_manager)

        text_entry.set_relative_position((50.0, 30.0))

        assert text_entry.rect.topleft == (100, 80)

    def test_set_dimensions(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(0, 0, 150, 30),
                                     container=test_container,
                                     manager=default_ui_manager)

        assert text_entry.rect.right == 250

        text_entry.set_dimensions((200, 30))

        assert text_entry.rect.right == 300
        assert text_entry.drawable_shape.containing_rect.right == 300

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.focus()
        text_entry.disable()

        assert text_entry.is_enabled is False
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d,
                                                                           'mod': 0,
                                                                           'unicode': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        assert processed_key_event is False and text_entry.get_text() == ''

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        text_entry.disable()

        text_entry.focus()
        text_entry.enable()

        assert text_entry.is_enabled is True
        text_entry.focus()
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d,
                                                                           'mod': 0,
                                                                           'unicode': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        assert processed_key_event is True and text_entry.get_text() == 'dan'

    def test_show(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager, visible=0)

        assert text_entry.visible == 0
        text_entry.show()
        assert text_entry.visible == 1

    def test_hide(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)

        assert text_entry.visible == 1
        text_entry.hide()
        assert text_entry.visible == 0

    def test_show_hide_rendering(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 400, 400),
                                     manager=manager,
                                     visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        text_entry.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        text_entry.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_change_locale(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        text_entry = UITextEntryLine(relative_rect=pygame.Rect(100, 100, 200, 30),
                                     manager=default_ui_manager)
        text_entry.set_text("Some basic text")

        default_ui_manager.set_locale('fr')

        default_ui_manager.set_locale('ja')

        default_ui_manager.set_locale('en')
        text_entry.set_text_hidden(True)

        default_ui_manager.set_locale('fr')

        text_entry.set_text_hidden(False)

        assert text_entry.get_text() == "Some basic text"


if __name__ == '__main__':
    pytest.console_main()
