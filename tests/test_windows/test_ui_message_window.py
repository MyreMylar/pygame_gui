import os
import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows.ui_message_window import UIMessageWindow

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIMessageWindow:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'fira_code',
                                           'point_size': 14,
                                           'style': 'bold'}])
        UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                        window_title="Test Message",
                        html_message="This is a <b>bold</b> test "
                                     "of the message box functionality.",
                        manager=default_ui_manager)

    def test_create_too_small(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'fira_code',
                                           'point_size': 14,
                                           'style': 'bold'}])

        with pytest.warns(UserWarning, match="Initial size"):
            UIMessageWindow(rect=pygame.Rect(100, 100, 50, 50),
                            window_title="Test Message",
                            html_message="This is a <b>bold</b> test of the "
                                         "message box functionality.",
                            manager=default_ui_manager)

    def test_press_close_window_button(self, _init_pygame, default_ui_manager,
                                       _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        is_alive_pre_process_event = message_window.alive()

        close_button_x = message_window.close_window_button.rect.centerx
        close_button_y = message_window.close_window_button.rect.centery

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (close_button_x,
                                                                      close_button_y)}))

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (close_button_x,
                                                                      close_button_y)}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        is_dead_post_process_event = not message_window.alive()

        assert is_alive_pre_process_event is True and is_dead_post_process_event is True

    def test_update_dismiss_button(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        is_alive_pre_events = message_window.alive()
        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': message_window.dismiss_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             event_data))
        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': message_window.dismiss_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             event_data))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)
        is_dead_post_events = not message_window.alive()

        assert is_alive_pre_events is True and is_dead_post_events is True

    def test_update_menu_bar_grab(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        message_window.title_bar.held = True
        message_window.update(0.01)

        assert message_window.grabbed_window is True

    def test_rebuild(self, _init_pygame, default_ui_manager,
                     _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        message_window.rebuild()

        assert message_window.image is not None

    def test_rebuild_rounded_rectangle(self, _init_pygame, default_ui_manager,
                                       _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        message_window.shape_corner_radius = 15
        message_window.shape = 'rounded_rectangle'
        message_window.rebuild()

        assert message_window.image is not None

    def test_non_default_theme_build(self, _init_pygame,
                                     _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_message_window_non_default.json"))
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=manager)

        assert message_window.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    def test_bad_values_theme_build(self, _init_pygame,
                                    _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_message_window_bad_values.json"))
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=manager)

        assert message_window.image is not None

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager,
                                         visible=0)

        assert message_window.visible == 0

        assert message_window.close_window_button.visible == 0
        assert message_window.dismiss_button.visible == 0
        assert message_window.text_block.visible == 0

        message_window.show()

        assert message_window.visible == 1

        assert message_window.close_window_button.visible == 1
        assert message_window.dismiss_button.visible == 1
        assert message_window.text_block.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=default_ui_manager)

        assert message_window.visible == 1

        assert message_window.close_window_button.visible == 1
        assert message_window.dismiss_button.visible == 1
        assert message_window.text_block.visible == 1

        message_window.hide()

        assert message_window.visible == 0

        assert message_window.close_window_button.visible == 0
        assert message_window.dismiss_button.visible == 0
        assert message_window.text_block.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (600, 600)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        message_window = UIMessageWindow(rect=pygame.Rect(100, 100, 250, 300),
                                         window_title="Test Message",
                                         html_message="This is a bold test of the "
                                                      "message box functionality.",
                                         manager=manager,
                                         visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        message_window.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        message_window.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

