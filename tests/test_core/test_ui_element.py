import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.ui_window import UIWindow
from pygame_gui.core.ui_container import UIContainer


class TestUIElement:
    def test_creation(self, _init_pygame, default_ui_manager):
        UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1)

    def test_stub_methods(self, _init_pygame, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        element.on_hovered()
        element.on_unhovered()
        element.while_hovering(0.5, pygame.math.Vector2(0.0, 0.0))
        assert element.can_hover() is True
        assert element.process_event(pygame.event.Event(pygame.USEREVENT, {})) is False
        element.select()
        element.unselect()
        element.rebuild_from_changed_theme_data()

    def test_hover_point(self, _init_pygame, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.hover_point(25, 25) is True
        assert element.hover_point(100, 100) is False

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager)
        element = UIElement(relative_rect=pygame.Rect(100, 100, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_height=0,
                            layer_thickness=1)

        element.set_relative_position(pygame.math.Vector2(150.0, 30.0))

        assert element.rect.topleft == (250, 130)

    def test_set_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager)
        element = UIElement(relative_rect=pygame.Rect(100, 100, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_height=0,
                            layer_thickness=1)

        element.set_position(pygame.math.Vector2(150.0, 30.0))

        assert (element.relative_rect.topleft == (50, -70))

    def test_create_invalid_id(self, _init_pygame, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)
        with pytest.raises(ValueError, match="Object ID cannot contain fullstops or spaces"):
            element.create_valid_ids(None, None, ". .", 'none')

    def test_check_hover(self, _init_pygame, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        default_ui_manager.mouse_position = (25, 25)
        assert element.check_hover(0.5, False) is True

        default_ui_manager.mouse_position = (100, 200)

        assert element.check_hover(0.5, False) is False
