import pytest
import pygame

from pygame_gui.core.surface_cache import SurfaceCache


class TestSurfaceCache:
    def test_creation(self, _init_pygame, _display_surface_return_none):
        SurfaceCache()

    def test_add_surface_to_cache(self, _init_pygame, _display_surface_return_none):
        cache = SurfaceCache()
        cache.add_surface_to_cache(pygame.Surface((64, 64)), 'doop')

        assert isinstance(cache.find_surface_in_cache('doop'), pygame.Surface)
        assert cache.find_surface_in_cache('doop').get_width() == 64

    def test_update(self, _init_pygame, _display_surface_return_none):
        cache = SurfaceCache()
        cache.add_surface_to_cache(pygame.Surface((64, 64)), 'doop')

        assert len(cache.cache_short_term_lookup) == 1
        assert len(cache.cache_long_term_lookup) == 0
        cache.update()
        assert len(cache.cache_short_term_lookup) == 0
        assert len(cache.cache_long_term_lookup) == 1

        cache.low_on_space = True
        cache.cache_long_term_lookup['doop']['current_uses'] = 0
        cache.consider_purging_list.append('doop')

        cache.update()
        assert len(cache.consider_purging_list) == 0
        assert len(cache.cache_long_term_lookup) == 0
        assert not cache.low_on_space

    def test_add_surface_to_long_term_cache_too_large(self, _init_pygame,
                                                      _display_surface_return_none):
        cache = SurfaceCache()
        with pytest.warns(UserWarning, match="Unable to cache surfaces larger than"):
            cache.add_surface_to_long_term_cache([pygame.Surface((2048, 2048)), 1],
                                                 string_id="test_surface")

    def test_add_surface_to_long_term_cache(self, _init_pygame, _display_surface_return_none):
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

    def test_find_surface_in_cache(self, _init_pygame, _display_surface_return_none):
        cache = SurfaceCache()
        cache.add_surface_to_cache(pygame.Surface((64, 64)), 'doop')

        assert isinstance(cache.find_surface_in_cache('doop'), pygame.Surface)

        cache.update()
        assert isinstance(cache.find_surface_in_cache('doop'), pygame.Surface)

        assert cache.find_surface_in_cache('derp') is None

    def test_remove_user_from_cache_item(self, _init_pygame, _display_surface_return_none):
        cache = SurfaceCache()
        cache.add_surface_to_cache(pygame.Surface((64, 64)), 'doop')
        cache.update()

        assert cache.cache_long_term_lookup['doop']['current_uses'] == 1
        assert len(cache.consider_purging_list) == 0

        cache.remove_user_from_cache_item('doop')
        assert cache.cache_long_term_lookup['doop']['current_uses'] == 0
        assert len(cache.consider_purging_list) == 1

    def test_remove_user_and_request_clean_up_of_cached_item(self, _init_pygame,
                                                             _display_surface_return_none):
        cache = SurfaceCache()
        cache.add_surface_to_cache(pygame.Surface((64, 64)), 'doop')
        cache.update()

        assert cache.cache_long_term_lookup['doop']['current_uses'] == 1
        assert len(cache.consider_purging_list) == 0

        cache.remove_user_and_request_clean_up_of_cached_item('doop')

        assert cache.find_surface_in_cache('doop') is None

        # remove item not in cache
        cache.remove_user_and_request_clean_up_of_cached_item('Blep')

    def test_build_cache_id(self, _init_pygame):

        cache_id = SurfaceCache.build_cache_id(shape='rectangle',
                                               size=(64, 64),
                                               shadow_width=1,
                                               border_width=1,
                                               border_colour=pygame.Color(255, 0, 0, 255),
                                               bg_colour=pygame.Color(100, 200, 100, 180),
                                               corner_radius=5)

        assert cache_id == 'rectangle_64_64_1_1_5_255_0_0_255_100_200_100_180'

    def test_expand_lt_cache(self, _init_pygame):
        cache = SurfaceCache()
        assert not cache.low_on_space
        cache.cache_surfaces = [1, 2, 3, 4, 5]
        cache._expand_lt_cache()
        assert cache.low_on_space


if __name__ == '__main__':
    pytest.console_main()

