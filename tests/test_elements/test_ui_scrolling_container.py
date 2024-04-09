import pytest
import pygame

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface


class TestUIScrollingContainer:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UIScrollingContainer(relative_rect=pygame.Rect(100, 100, 400, 400),
                             manager=default_ui_manager)

    def test_get_container(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                           _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)
        assert container.get_container() == container.scrollable_container

    def test_add_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                         _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button)
        container.get_container().add_element(button)
        assert len(container.get_container().elements) == 1

    def test_remove_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager,
                          container=container)

        container.get_container().remove_element(button)
        assert len(container.get_container().elements) == 0

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)
        assert container._root_container.rect.size == (200, 200)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)
        container_2 = UIScrollingContainer(pygame.Rect(50, 50, 50, 50),
                                           manager=default_ui_manager,
                                           container=container)

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (125, 125)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_dimensions((50, 50))

        assert container.rect.size == (50, 50)

        container.set_scrollable_area_dimensions((500, 600))

        container.set_dimensions((400, 500))

        assert container.rect.size == (400, 500)

        container.set_dimensions((500, 600))

        assert container.rect.size == (500, 600)

    def test_kill(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)
        container_2 = UIScrollingContainer(pygame.Rect(50, 50, 50, 50),
                                           manager=default_ui_manager,
                                           container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.kill()

        assert not button.alive()
        assert not container_2.alive()
        assert not container.alive()

    def test_set_scrollable_area_dimensions(self, _init_pygame, default_ui_manager,
                                            _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_scrollable_area_dimensions((500, 600))

        assert container.vert_scroll_bar is not None
        assert container.horiz_scroll_bar is not None
        assert container.scrollable_container.rect.size == (500, 600)
        assert container._view_container.rect.size == (200-container.vert_scroll_bar.rect.width,
                                                       200-container.horiz_scroll_bar.rect.height)

    def test_set_scrollable_area_dimensions_constrained_x_axis(self, _init_pygame, default_ui_manager,
                                                               _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager,
                                         allow_scroll_x=False)

        assert container.vert_scroll_bar.rect.width == 0
        assert container.horiz_scroll_bar is None
        assert container.scrollable_container.rect.size == (200, 200)

        container.set_scrollable_area_dimensions((200, 600))

        assert container.vert_scroll_bar is not None
        assert container.horiz_scroll_bar is None
        assert container._view_container.rect.size == (200 - container.vert_scroll_bar.rect.width,
                                                       200)
        assert container.scrollable_container.rect.size == (200 - container.vert_scroll_bar.rect.width, 600)

    def test_set_scrollable_area_dimensions_constrained_y_axis(self, _init_pygame, default_ui_manager,
                                                               _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager,
                                         allow_scroll_y=False)

        assert container.vert_scroll_bar is None
        assert container.horiz_scroll_bar.rect.height == 0
        assert container.scrollable_container.rect.size == (200, 200)

        container.set_scrollable_area_dimensions((600, 200))

        assert container.vert_scroll_bar is None
        assert container.horiz_scroll_bar is not None
        assert container._view_container.rect.size == (200,
                                                       200 - container.horiz_scroll_bar.rect.height)
        assert container.scrollable_container.rect.size == (600,
                                                            200 - container.horiz_scroll_bar.rect.height)

    def test_update(self, _init_pygame, default_ui_manager,
                    _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_scrollable_area_dimensions((500, 600))

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -1.0
        container.horiz_scroll_bar.update(0.02)

        container.update(0.02)

        assert container.get_container().get_relative_rect().x == -15

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -1.0
        container.vert_scroll_bar.update(0.02)

        container.update(0.02)

        assert container.get_container().get_relative_rect().y == -12

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.horiz_scroll_bar.start_percentage = 0.6
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.scrolling_right = container._view_container.rect.right - 1
        container.update(0.02)

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)

        container.scrollable_container.set_dimensions((150, 600))
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        container.scrollable_container.set_dimensions((150, 150))

        container.update(0.02)
        container.update(0.02)
        container.update(0.02)

        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_scrollable_area_dimensions((500, 600))

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)

        container.scrollable_container.rect.top = -500  # scroll it too high and then update
        container.update(0.02)

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=container)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=container)

        container.disable()

        assert container.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=container)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=container)

        container.disable()
        container.enable()

        assert container.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is True

    def test_show(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIScrollingContainer(relative_rect=pygame.Rect(100, 100, 400, 400),
                                         manager=default_ui_manager, visible=0)
        container.set_scrollable_area_dimensions((500, 600))

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

        container.show()

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.horiz_scroll_bar.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIScrollingContainer(relative_rect=pygame.Rect(100, 100, 400, 400),
                                         manager=default_ui_manager)
        container.set_scrollable_area_dimensions((500, 600))

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.horiz_scroll_bar.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

        container.hide()

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        container = UIScrollingContainer(relative_rect=pygame.Rect(100, 100, 200, 100),
                                         manager=manager,
                                         visible=0)
        container.set_scrollable_area_dimensions((600, 600))
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_iteration(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                       _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(50, 50, 50, 50), text="1",
                            manager=default_ui_manager, container=container)
        button_2 = UIButton(relative_rect=pygame.Rect(150, 50, 50, 50), text="2",
                            manager=default_ui_manager, container=container)
        
        assert button_1 in container
        assert button_2 in container
        count = 0
        for button in container:
            button.get_relative_rect()
            count += 1
        assert count == 2

    def test_are_contents_hovered(self,  _init_pygame, default_ui_manager: IUIManagerInterface,
                                  _display_surface_return_none):
        manager = UIManager((800, 600))
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200), manager=manager)
        container.set_scrollable_area_dimensions((400, 400))
        button_1 = UIButton(relative_rect=pygame.Rect(50, 50, 50, 50), text="1",
                            manager=manager, container=container)
        button_2 = UIButton(relative_rect=pygame.Rect(50, 300, 50, 50), text="2",
                            manager=manager, container=container)
        manager.mouse_position = (155, 155)
        button_1.check_hover(0.1, False)
        button_2.check_hover(0.1, False)

        assert container.are_contents_hovered()
        assert container.vert_scroll_bar is not None

        container.vert_scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'y': -0.5}))

        assert container.vert_scroll_bar.scroll_wheel_moved

        assert container.horiz_scroll_bar is not None

        container.horiz_scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'x': -0.5}))

        assert container.horiz_scroll_bar.scroll_wheel_moved


if __name__ == '__main__':
    pytest.console_main()
