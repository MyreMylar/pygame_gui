import os
import pygame
import pytest
from pygame_gui.ui_manager import UIManager


@pytest.fixture(scope="module")
def _init_pygame():
    # Enable these variables to test in same environment as Travis.
    # os.environ['SDL_VIDEODRIVER'] = 'dummy'
    # os.environ['SDL_AUDIODRIVER'] = 'disk'
    pygame.init()


@pytest.fixture()
def default_ui_manager():
    return UIManager((800, 600))


@pytest.fixture()
def default_display_surface():
    display = pygame.display.set_mode((10, 10), depth=32)
    yield display
    pygame.display.quit()
