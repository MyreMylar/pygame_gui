import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_window_stack import UIWindowStack
from pygame_gui.elements.ui_window import UIWindow


class TestWindowStack:
    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UIWindowStack((800, 600), default_ui_manager.get_root_container())

    def test_add_window(self, _init_pygame, default_ui_manager,
                        _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        stack.add_new_window(window)

        assert len(stack.stack) == 1

    def test_clear(self, _init_pygame, default_ui_manager,
                   _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        stack.add_new_window(window)

        assert len(stack.stack) == 1

        stack.clear()

        assert len(stack.stack) == 0

    def test_remove_window(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_2 = UIWindow(pygame.Rect(50, 50, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_3 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        stack.add_new_window(window)
        stack.add_new_window(window_2)
        stack.add_new_window(window_3)
        stack.remove_window(window)
        stack.remove_window(window_2)
        stack.remove_window(window_3)

        assert len(stack.stack) == 0

    def test_move_window_to_front(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_2 = UIWindow(pygame.Rect(50, 50, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_3 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        stack.add_new_window(window)
        stack.add_new_window(window_2)
        stack.add_new_window(window_3)
        stack.move_window_to_front(window)
        stack.move_window_to_front(window_3)
        stack.move_window_to_front(window_2)

        assert stack.stack[0] == window

    def test_is_window_at_top(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_2 = UIWindow(pygame.Rect(50, 50, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_3 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        stack.add_new_window(window)
        stack.add_new_window(window_2)
        stack.add_new_window(window_3)
        stack.move_window_to_front(window)
        stack.move_window_to_front(window_3)
        stack.move_window_to_front(window_2)

        assert stack.is_window_at_top(window_2) is True
        assert stack.is_window_at_top(window) is False
        assert stack.is_window_at_top(window_3) is False
