import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface , _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.ui_container import UIContainer
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

    def test_update(self, _init_pygame, default_ui_manager,
                    _display_surface_return_none):
        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        container.set_scrollable_area_dimensions((500, 600))

        container.horiz_scroll_bar.scroll_wheel_right = True
        container.horiz_scroll_bar.update(0.02)

        container.update(0.02)

        assert container.get_container().relative_rect.x == -18

    def test_show(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIScrollingContainer(relative_rect=pygame.Rect(100, 100, 400, 400),
                                         manager=default_ui_manager, visible=0)
        container.set_scrollable_area_dimensions((500, 600))

        assert container.visible == 0
        assert container.dirty == 1

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

        container.show()

        assert container.visible == 1
        assert container.dirty == 2

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
        assert container.dirty == 2

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.horiz_scroll_bar.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

        container.hide()

        assert container.visible == 0
        assert container.dirty == 1

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0
