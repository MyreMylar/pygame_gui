# import os
import pygame
import pytest
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.interfaces import IUIManagerInterface


@pytest.fixture(scope="module", autouse=True)
def _init_pygame():
    # Enable these variables to test in same environment as Travis.
    # os.environ['SDL_VIDEODRIVER'] = 'dummy'
    # os.environ['SDL_AUDIODRIVER'] = 'disk'
    pygame.init()

@pytest.fixture()
def default_ui_manager() -> IUIManagerInterface:
    return UIManager((800, 600))


@pytest.fixture()
def default_display_surface():
    display = pygame.display.set_mode((10, 10), 0, 32)
    yield display
    pygame.display.quit()


@pytest.fixture()
def _display_surface_return_none():
    pygame.display.set_mode((10, 10), 0, 32)
    yield None
    pygame.display.quit()
