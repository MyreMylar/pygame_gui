import os
import pytest
import pygame

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_status_bar import UIStatusBar


class HealthySprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.current_health = 50
        self.health_capacity = 100
        self.rect = pygame.Rect(0, 0, 32, 64)

    def health_percent(self):
        return self.current_health / self.health_capacity


class TestUIStatusBar:

    def test_creation(self, _init_pygame, default_ui_manager):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)
        assert health_bar.image is not None

    def test_update(self, _init_pygame, default_ui_manager):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)
        healthy_sprite.current_health = 10
        health_bar.update(0.01)
        assert health_bar.image is not None

        health_bar.percent_full = 50

        assert health_bar.percent_full == 0.5

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_status_bar_non_default.json"))
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=manager)
        assert health_bar.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_status_bar_bad_values.json"))
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=manager)
        assert health_bar.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)

        health_bar.set_position((150.0, 30.0))

        assert health_bar.rect.topleft == (150, 30)

        other_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                manager=default_ui_manager)

        assert other_bar.position == (100, 100)

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)

        health_bar.set_relative_position((150.0, 30.0))

        assert health_bar.rect.topleft == (150, 30)

    def test_set_dimensions(self, _init_pygame, default_ui_manager):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)

        health_bar.set_dimensions((250.0, 60.0))

        assert health_bar.drawable_shape.containing_rect.size == (250, 60)
        assert health_bar.rect.size == (250, 60)
        assert health_bar.relative_rect.size == (250, 60)

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager,
                                 visible=0)

        assert health_bar.visible == 0
        health_bar.show()
        assert health_bar.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                 sprite=healthy_sprite,
                                 manager=default_ui_manager)

        assert health_bar.visible == 1
        health_bar.hide()
        assert health_bar.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        healthy_sprite = HealthySprite()
        health_bar = UIStatusBar(relative_rect=pygame.Rect(100, 100, 400, 400),
                                 sprite=healthy_sprite,
                                 manager=manager,
                                 visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        health_bar.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        health_bar.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)


if __name__ == '__main__':
    pytest.console_main()
