import pytest
import pygame

from pygame_gui.core.colour_gradient import ColourGradient


class TestColourGradient:
    def test_creation(self, _init_pygame):
        gradient = ColourGradient(
            angle_direction=90,
            colour_1=pygame.Color("#FF0000"),
            colour_2=pygame.Color("#00FF00"),
            colour_3=pygame.Color("#0000FF"),
        )

        assert str(gradient) == "90_255_0_0_255_0_255_0_255_0_0_255_255"

    def test_apply_gradient_to_surface(self, _init_pygame):
        gradient = ColourGradient(
            angle_direction=90,
            colour_1=pygame.Color("#FF0000"),
            colour_2=pygame.Color("#00FF00"),
            colour_3=pygame.Color("#0000FF"),
        )

        test_surface = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        test_surface.fill(pygame.Color(255, 255, 255, 255))

        gradient.apply_gradient_to_surface(test_surface)

        after_application_colour = test_surface.get_at((0, 0))
        if pygame.vernum.major >= 2 and pygame.vernum.minor >= 2:
            # The scaling algorithm changed slightly in 2.2, this affects the gradient color
            assert after_application_colour == pygame.Color(0, 5, 249, 255)
        else:
            assert after_application_colour == pygame.Color(0, 11, 243, 255)


if __name__ == "__main__":
    pytest.console_main()
