import os
import pygame
import pytest

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows.ui_console_window import UIConsoleWindow

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIConsoleWindow:
    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'fira_code',
                                           'point_size': 14,
                                           'style': 'bold'}])

        UIConsoleWindow(
            rect=pygame.rect.Rect((0, 0), (700, 500)),
            manager=default_ui_manager)
