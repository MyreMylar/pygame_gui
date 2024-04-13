import pytest
import pygame

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

    def test_add_window_always_on_top(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_always_on_top = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                                        manager=default_ui_manager, element_id='test_window',
                                        always_on_top=True)
        stack.add_new_window(window)
        stack.add_new_window(window_always_on_top)

        assert len(stack.stack) == 1
        assert len(stack.top_stack) == 1

    def test_clear_with_always_on_top(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_always_on_top = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                                        manager=default_ui_manager, element_id='test_window',
                                        always_on_top=True)
        stack.add_new_window(window)
        stack.add_new_window(window_always_on_top)

        assert len(stack.stack) == 1
        assert len(stack.top_stack) == 1

        stack.clear()

        assert len(stack.stack) == 0
        assert len(stack.top_stack) == 0

    def test_remove_window_with_always_on_top(self, _init_pygame, default_ui_manager,
                                              _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window_always_on_top = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                                        manager=default_ui_manager, element_id='test_window',
                                        always_on_top=True)
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_2 = UIWindow(pygame.Rect(50, 50, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_3 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_always_on_top_2 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                                          manager=default_ui_manager, element_id='test_window',
                                          always_on_top=True)
        stack.add_new_window(window_always_on_top)
        stack.add_new_window(window)
        stack.add_new_window(window_2)
        stack.add_new_window(window_3)
        stack.add_new_window(window_always_on_top_2)
        assert len(stack.stack) == 3
        assert len(stack.top_stack) == 2
        assert stack.is_window_at_top(window_3)
        assert stack.is_window_at_top_of_top(window_always_on_top_2)
        stack.remove_window(window)
        stack.remove_window(window_always_on_top)
        stack.remove_window(window_2)
        stack.remove_window(window_3)
        stack.remove_window(window_always_on_top_2)

        assert len(stack.top_stack) == 0
        assert len(stack.stack) == 0

    def test_move_window_to_front_with_always_on_top(self, _init_pygame, default_ui_manager,
                                                     _display_surface_return_none):
        stack = UIWindowStack((800, 600), default_ui_manager.get_root_container())
        window_always_on_top = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                                        manager=default_ui_manager, element_id='test_window',
                                        always_on_top=True)
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        window_2 = UIWindow(pygame.Rect(50, 50, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')
        window_3 = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                            manager=default_ui_manager, element_id='test_window')

        stack.add_new_window(window_always_on_top)
        stack.add_new_window(window)
        stack.add_new_window(window_2)
        stack.add_new_window(window_3)
        stack.move_window_to_front(window)
        stack.move_window_to_front(window_3)
        stack.move_window_to_front(window_2)

        assert stack.stack[0] == window
        assert stack.stack[2] == window_2
        assert stack.top_stack[0] == window_always_on_top
        assert window_always_on_top.layer > window_2.layer


if __name__ == '__main__':
    pytest.console_main()
