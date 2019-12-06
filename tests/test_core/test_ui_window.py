import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_window_stack import UIWindowStack
from pygame_gui.core.ui_window import UIWindow


class TestWindowStack:
    def test_creation(self, _init_pygame, default_ui_manager):
        UIWindow(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, element_ids=[])

    def test_stub_methods(self, _init_pygame, default_ui_manager):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, element_ids=[])

        window.select()
        window.unselect()

    def test_process_event(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), manager=default_ui_manager, element_ids=[])
        processed_down_event = window.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                       {'button': 1, 'pos': (100, 100)}))

        assert processed_down_event is True

    def test_check_clicked_inside(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), manager=default_ui_manager, element_ids=[])
        clicked_inside = window.check_clicked_inside(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                        {'button': 1, 'pos': (100, 100)}))

        assert clicked_inside is True