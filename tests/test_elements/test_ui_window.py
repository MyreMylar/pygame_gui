import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.ui_window import UIWindow


class TestWindowStack:
    def test_creation(self, _init_pygame, default_ui_manager):
        UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                 manager=default_ui_manager, element_id='test_window')

    def test_stub_methods(self, _init_pygame, default_ui_manager):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        window.focus()
        window.unfocus()

    def test_process_event(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        processed_down_event = window.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                       {'button': 1, 'pos': (100, 100)}))

        assert processed_down_event is True

    def test_check_clicked_inside(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        clicked_inside = window.check_clicked_inside_or_blocking(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                        {'button': 1, 'pos': (100, 100)}))

        assert clicked_inside is True
