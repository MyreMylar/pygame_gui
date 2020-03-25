import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface


class TestUIContainer:
    def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

    def test_get_container(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                           _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        assert container.get_container() == container

    def test_add_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                         _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button)
        container.add_element(button)
        assert len(container.elements) == 1

    def test_remove_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager,
                          container=container)

        container.remove_element(button)
        assert len(container.elements) == 0

    def test_recalculate_container_layer_thickness(self, _init_pygame,
                                                   default_ui_manager: IUIManagerInterface,
                                                   _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager,
                 container=container)

        container.recalculate_container_layer_thickness()

        assert container.layer_thickness == 2

    def test_change_container_layer(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        container.change_layer(2)
        assert container.get_top_layer() == 4

    def test_get_top_layer(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        assert container.get_top_layer() == 3

    def test_update_containing_rect_position(self, _init_pygame, default_ui_manager,
                                             _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.rect.topleft = (0, 0)
        container.relative_rect.topleft = (0, 0)
        container_2.update_containing_rect_position()

        assert button.rect.topleft == (70, 70)

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container)

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (125, 125)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        container.set_dimensions((50, 50))

        assert container.rect.size == (50, 50)

    def test_kill(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.kill()

        assert not button.alive()
        assert not container_2.alive()
        assert not container.alive()

    def test_clear(self, _init_pygame, default_ui_manager,
                   _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.clear()

        assert not button.alive()
        assert not container_2.alive()
        assert len(container.elements) == 0

    def test_check_hover_when_not_able_to_hover(self, _init_pygame, default_ui_manager,
                                                _display_surface_return_none):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container.hovered = True
        assert container.check_hover(0.5, True) is True  # already hovering
        container.hovered = True
        container.kill()
        assert container.check_hover(0.5, False) is False  # dead so can't hover any more

