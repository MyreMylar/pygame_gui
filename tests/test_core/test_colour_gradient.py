import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.colour_gradient import ColourGradient


class TestColourGradient:
    def test_creation(self, _init_pygame):
        gradient = ColourGradient(angle_direction=90,
                                  colour_1=pygame.Color("#FF0000"),
                                  colour_2=pygame.Color("#00FF00"),
                                  colour_3=pygame.Color("#0000FF"))

        assert str(gradient) == "90_255_0_0_255_0_255_0_255_0_0_255_255"
