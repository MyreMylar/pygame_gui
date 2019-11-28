import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager

from pygame_gui.windows.ui_message_window import UIMessageWindow


class TestUIMessageWindow:

    def test_creation(self, _init_pygame, default_ui_manager):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        UIMessageWindow(message_window_rect=pygame.Rect(100, 100, 200, 300),
                        message_title="Test Message",
                        html_message="This is a <b>bold</b> test of the message box functionality.",
                        manager=default_ui_manager)
