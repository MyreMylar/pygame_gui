import os
import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows.ui_message_window import UIMessageWindow


class TestUIMessageWindow:

    def test_creation(self, _init_pygame, default_ui_manager):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                        message_title="Test Message",
                        html_message="This is a <b>bold</b> test of the message box functionality.",
                        manager=default_ui_manager)

    def test_update_close_button(self, _init_pygame, default_ui_manager):
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=default_ui_manager)

        message_window.close_window_button.pressed = True
        is_alive_pre_update = message_window.alive()
        message_window.update(0.01)
        is_dead_post_update = not message_window.alive()

        assert is_alive_pre_update is True and is_dead_post_update is True

    def test_update_dismiss_button(self, _init_pygame, default_ui_manager):
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=default_ui_manager)

        message_window.dismiss_button.pressed = True
        is_alive_pre_update = message_window.alive()
        message_window.update(0.01)
        is_dead_post_update = not message_window.alive()

        assert is_alive_pre_update is True and is_dead_post_update is True

    def test_update_menu_bar_grab(self, _init_pygame, default_ui_manager):
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=default_ui_manager)

        message_window.menu_bar.held = True
        message_window.update(0.01)

        assert message_window.grabbed_window is True

    def test_rebuild(self, _init_pygame, default_ui_manager):
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=default_ui_manager)

        message_window.rebuild()

        assert message_window.image is not None

    def test_rebuild_rounded_rectangle(self, _init_pygame, default_ui_manager):
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=default_ui_manager)

        message_window.shape_corner_radius = 15
        message_window.shape_type = 'rounded_rectangle'
        message_window.rebuild()

        assert message_window.image is not None

    def test_non_default_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_message_window_non_default.json"))
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=manager)

        assert message_window.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    def test_bad_values_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_message_window_bad_values.json"))
        message_window = UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                                         message_title="Test Message",
                                         html_message="This is a bold test of the message box functionality.",
                                         manager=manager)

        assert message_window.image is not None
