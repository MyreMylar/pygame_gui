import pytest
import pygame

from pygame_gui.core.ui_shadow import ShadowGenerator


class TestShadowGenerator:
    def test_creation(self, _init_pygame, _display_surface_return_none):
        ShadowGenerator()

    def test_clear_short_term_caches(self, _init_pygame, _display_surface_return_none):
        generator = ShadowGenerator()
        generator.clear_short_term_caches()

        assert generator.short_term_rect_cache == {}

    def test_find_closest_shadow_scale_to_size_invalid(
        self, _init_pygame, _display_surface_return_none
    ):
        generator = ShadowGenerator()
        assert (
            generator.find_closest_shadow_scale_to_size(
                size=(100, 100), shape="triangle"
            )
            is None
        )

    def test_create_new_rectangle_shadow_invalid(
        self, _init_pygame, _display_surface_return_none
    ):
        generator = ShadowGenerator()
        assert (
            generator.create_new_rectangle_shadow(
                width=10,
                height=10,
                corner_radii=[20, 20, 20, 20],
                shadow_width_param=20,
            )
            is None
        )

    def test_create_new_rectangle_shadow(
        self, _init_pygame, _display_surface_return_none
    ):
        generator = ShadowGenerator()
        assert isinstance(
            generator.create_new_rectangle_shadow(50, 50, 1, [1, 1, 1, 1]),
            pygame.Surface,
        )

    def test_create_new_ellipse_shadow(
        self, _init_pygame, _display_surface_return_none
    ):
        generator = ShadowGenerator()
        assert isinstance(
            generator.create_new_ellipse_shadow(50, 50, 1), pygame.Surface
        )

    def test_create_shadow_corners(self):
        generator = ShadowGenerator()
        with pytest.warns(UserWarning, match="Tried to make shadow with width <= 0"):
            generator.create_shadow_corners(
                shadow_width_param=-1, corner_radii=[2, 2, 2, 2]
            )


if __name__ == "__main__":
    pytest.console_main()
