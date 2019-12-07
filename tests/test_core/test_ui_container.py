import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_button import UIButton


class TestUIContainer:
    def test_creation(self, _init_pygame, default_ui_manager):
        UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

    def test_change_container_layer(self, _init_pygame, default_ui_manager):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        container.change_container_layer(2)
        assert container.get_top_layer() == 4

    def test_get_top_layer(self, _init_pygame, default_ui_manager):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        assert container.get_top_layer() == 3

    def test_check_hover_when_not_able_to_hover(self, _init_pygame, default_ui_manager):
        container = UIContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container.hovered = True
        assert container.check_hover(0.5, True) is True  # already hovering
        container.hovered = True
        container.kill()
        assert container.check_hover(0.5, False) is False  # dead so can't hover any more

