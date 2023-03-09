import os
import pygame
import pytest

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer


class TestUIImage:
    def test_creation(self, _init_pygame: None, default_ui_manager: UIManager,
                      default_display_surface: pygame.Surface):

        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)
        assert ui_image.image is not None

    def test_set_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)

        ui_image.set_position((200, 200))

        assert ui_image.relative_rect.topleft == (200, 200)

    def test_set_relative_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)

        ui_image.set_relative_position((200, 200))

        assert ui_image.relative_rect.topleft == (200, 200)

    def test_set_dimensions(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)

        assert ui_image.image.get_size() == (150, 30) and ui_image.rect.size == (150, 30)

        ui_image.set_dimensions((200, 200))

        assert ui_image.image.get_size() == (200, 200) and ui_image.rect.size == (200, 200)

        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        ui_image = UIImage(relative_rect=pygame.Rect(10, 10, 128, 128),
                           image_surface=loaded_image,
                           manager=default_ui_manager,
                           container=container)

        ui_image.set_dimensions((350, 350))
        ui_image.set_dimensions((128, 128))

        container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                         manager=default_ui_manager)

        ui_image = UIImage(relative_rect=pygame.Rect(10, 10, 128, 128),
                           image_surface=loaded_image,
                           manager=default_ui_manager,
                           container=container)

        ui_image.set_dimensions((50, 50))
        ui_image.set_dimensions((128, 128))

        container.set_dimensions((50, 50))
        ui_image.set_dimensions((35, 35))
        container.set_dimensions((300, 300))
        ui_image.set_dimensions((128, 128))

        assert ui_image.image.get_size() == (128, 128) and ui_image.rect.size == (128, 128)

    def test_show(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager,
                           visible=0)

        assert ui_image.visible == 0
        ui_image.show()
        assert ui_image.visible == 1

    def test_hide(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)

        assert ui_image.visible == 1
        ui_image.hide()
        assert ui_image.visible == 0

    def test_show_hide_rendering(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)
        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(25, 25, 375, 150),
                           image_surface=loaded_image,
                           manager=manager,
                           visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        ui_image.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        ui_image.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)


if __name__ == '__main__':
    pytest.console_main()
