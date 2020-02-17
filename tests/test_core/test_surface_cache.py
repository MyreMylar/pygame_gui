import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.surface_cache import SurfaceCache


class TestSurfaceCache:
    def test_creation(self, _init_pygame):
        SurfaceCache()

    def test_add_surface_to_long_term_cache_too_large(self, _init_pygame):
        cache = SurfaceCache()
        with pytest.warns(UserWarning, match="Unable to cache surfaces larger than"):
            cache.add_surface_to_long_term_cache([pygame.Surface((2048, 2048)), 1],
                                                 string_id="test_surface")

    def test_add_surface_to_long_term_cache(self, _init_pygame):
        cache = SurfaceCache()
        cache.add_surface_to_long_term_cache([pygame.Surface((256, 256)), 1],
                                             string_id="test_surface_1")
        cache.add_surface_to_long_term_cache([pygame.Surface((512, 256)), 1],
                                             string_id="test_surface_2")
        cache.add_surface_to_long_term_cache([pygame.Surface((256, 512)), 1],
                                             string_id="test_surface_3")
        cache.add_surface_to_long_term_cache([pygame.Surface((256, 128)), 1],
                                             string_id="test_surface_4")
        cache.add_surface_to_long_term_cache([pygame.Surface((128, 256)), 1],
                                             string_id="test_surface_5")
        cache.add_surface_to_long_term_cache([pygame.Surface((256, 256)), 1],
                                             string_id="test_surface_6")
        cache.add_surface_to_long_term_cache([pygame.Surface((128, 128)), 1],
                                             string_id="test_surface_7")
        cache.add_surface_to_long_term_cache([pygame.Surface((640, 64)), 1],
                                             string_id="test_surface_8")
        cache.add_surface_to_long_term_cache([pygame.Surface((640, 32)), 1],
                                             string_id="test_surface_9")
        cache.add_surface_to_long_term_cache([pygame.Surface((784, 784)), 1],
                                             string_id="test_surface_10")

        assert type(cache.find_surface_in_cache("test_surface_1")) == pygame.Surface
