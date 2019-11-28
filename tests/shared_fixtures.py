import pygame
import pytest
from pygame_gui.ui_manager import UIManager


@pytest.fixture(scope="module")
def _init_pygame():
    pygame.init()


@pytest.fixture()
def default_ui_manager():
    return UIManager((800, 600))