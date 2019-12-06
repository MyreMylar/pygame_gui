import os
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_image import UIImage


class TestUIButton:
    def test_creation(self, _init_pygame: None, default_ui_manager: UIManager,
                      default_display_surface: pygame.Surface):

        loaded_image = pygame.image.load(os.path.join('tests', 'data', 'images', 'splat.png'))
        ui_image = UIImage(relative_rect=pygame.Rect(100, 100, 150, 30),
                           image_surface=loaded_image,
                           manager=default_ui_manager)
        assert ui_image.image is not None
