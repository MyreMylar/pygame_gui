import warnings

from typing import List, Union, Tuple

import pygame

from pygame_gui.core.utility import basic_blit
from pygame_gui.core.colour_gradient import ColourGradient


class SurfaceCache:
    """
    A cache for surfaces that we estimate the UI may want to reuse to save constantly remaking
    almost identical drawable shapes.

    """
    def __init__(self):
        self.cache_surface_size = (1024, 1024)
        self.cache_surfaces = []
        starting_surface = pygame.surface.Surface(self.cache_surface_size,
                                                  flags=pygame.SRCALPHA, depth=32)
        starting_surface.fill(pygame.Color('#00000000'))
        self.cache_surfaces.append({'surface': starting_surface,
                                    'free_space_rectangles':
                                        [pygame.Rect((0, 0), self.cache_surface_size)]})

        self.cache_long_term_lookup = {}
        self.cache_short_term_lookup = {}

        self.consider_purging_list = []

        self.low_on_space = False

    def add_surface_to_cache(self, surface: pygame.surface.Surface, string_id: str):
        """
        Adds a surface to the cache. There are two levels to the cache, the short term level
        just keeps hold of the surface until we have time to add it to the long term level.

        :param surface: The surface to add to the cache.
        :param string_id: An ID to store the surface under to make it easy to recall later.
        """
        self.cache_short_term_lookup[string_id] = [surface.copy(), 1]

    def update(self):
        """
        Takes care of steadily moving surfaces from the short term cache into the long term.
        Long term caching takes a while so we limit it to adding one surface a frame.

        We also purge some lesser used surfaces from the long term cache when we run out of space.
        """
        if any(self.cache_short_term_lookup):
            string_id, cached_item = self.cache_short_term_lookup.popitem()
            self.add_surface_to_long_term_cache(cached_item, string_id)

        if self.low_on_space:
            self.low_on_space = False
            for cache_id in self.consider_purging_list:
                cached_item = self.cache_long_term_lookup[cache_id]
                if cached_item['current_uses'] == 0 and cached_item['total_uses'] == 1:
                    self._free_cached_surface(cache_id)

            self.consider_purging_list.clear()

    def add_surface_to_long_term_cache(self,
                                       cached_item: List[Union[pygame.surface.Surface, int]],
                                       string_id: str):
        """
        Move a surface from the short term cache into the long term one.

        :param cached_item: The surface to move into the long term cache.
        :param string_id: The ID of the surface in the cache.
        """

        if cached_item[0].get_size() > self.cache_surface_size:
            warnings.warn('Unable to cache surfaces larger than ' + str(self.cache_surface_size))
            return None
        else:

            found_rectangle_cache = None

            while found_rectangle_cache is None and not self.low_on_space:
                for cache_surface in self.cache_surfaces:
                    if found_rectangle_cache is None:
                        result = self._find_spot_in_lt_cache(cache_surface, cached_item, string_id)
                        found_rectangle_cache = result[0]
                        found_rectangle_to_split = result[1]
                        self._divide_lt_cache(cache_surface, found_rectangle_cache,
                                              found_rectangle_to_split)

                if found_rectangle_cache is None:
                    self._expand_lt_cache()

            return True

    def _divide_lt_cache(self, cache_surface, found_rectangle_cache, found_rectangle_to_split):
        """
        Having reserved a spot in one of our long term cache surfaces, divide up the rest of
        the cache surface to correctly ascertain the new set of free spaces.

        :param cache_surface: The long term cache surface we are dividing.
        :param found_rectangle_cache: The newly reserved space.
        :param found_rectangle_to_split: The old rectangle the newly reserved space is in.
        """
        if (found_rectangle_to_split is not None and
                found_rectangle_cache is not None):
            free_space_rectangles = cache_surface['free_space_rectangles']
            self.split_rect(found_rectangle_to_split, found_rectangle_cache,
                            cache_surface['free_space_rectangles'])
            rects_to_split = [rect for rect in free_space_rectangles
                              if rect.colliderect(found_rectangle_cache)]
            for split_rect in rects_to_split:
                self.split_rect(split_rect, found_rectangle_cache,
                                cache_surface['free_space_rectangles'])

            self._clean_up_lt_cache(cache_surface, free_space_rectangles)

    @staticmethod
    def _clean_up_lt_cache(cache_surface, free_space_rectangles):
        """
        Clean up rectangles entirely inside other rectangles.

        :param cache_surface:
        :param free_space_rectangles:

        """
        rects_to_remove = []
        rectangles_to_check = free_space_rectangles[:]
        for free_rectangle in free_space_rectangles:
            for check_rect in rectangles_to_check:
                if (free_rectangle != check_rect and
                        check_rect.contains(free_rectangle)):
                    rects_to_remove.append(free_rectangle)
        cache_surface['free_space_rectangles'] = [rect
                                                  for rect in
                                                  free_space_rectangles
                                                  if rect not in
                                                  rects_to_remove]

    def _find_spot_in_lt_cache(self, cache_surface, new_item, string_id):
        """
        Find a place in a long term cache surface for our new item from the short term cache.

        :param cache_surface: the surface to search.
        :param new_item: the item to cache.
        :param string_id: the look up id.
        :return: A tuple of the new rect we are reserving, and the rectangle it's inside of.
        """
        found_rectangle_cache = None
        found_rectangle_to_split = None
        current_surface = cache_surface['surface']
        surface_size = new_item[0].get_size()
        for free_rectangle in cache_surface['free_space_rectangles']:
            if (free_rectangle.width >= surface_size[0] and
                    free_rectangle.height >= surface_size[1]):
                # we fits, so we sits
                found_rectangle_to_split = free_rectangle
                found_rectangle_cache = pygame.Rect(free_rectangle.topleft,
                                                    surface_size)
                basic_blit(current_surface, new_item[0], free_rectangle.topleft)
                self.cache_long_term_lookup[string_id] = {
                    'surface': current_surface.subsurface(found_rectangle_cache),
                    'current_uses': new_item[1],
                    'total_uses': new_item[1]}
                break
        return found_rectangle_cache, found_rectangle_to_split

    def _expand_lt_cache(self):
        """
        Try to expand the long term cache by adding more surfaces, until we hit the limit.
        """
        if len(self.cache_surfaces) < 3:
            # create a new cache surface
            new_surface = pygame.surface.Surface(self.cache_surface_size,
                                                 flags=pygame.SRCALPHA,
                                                 depth=32)
            new_surface.fill(pygame.Color('#00000000'))
            self.cache_surfaces.append({'surface': new_surface,
                                        'free_space_rectangles':
                                            [pygame.Rect((0, 0),
                                                         self.cache_surface_size)]})
        else:
            self.low_on_space = True

    @staticmethod
    def split_rect(found_rectangle_to_split: pygame.Rect,
                   dividing_rect: pygame.Rect,
                   free_space_rectangles: List[pygame.Rect]):
        """
        Takes an existing free space rectangle that we are placing a new surface inside of and
        then divides up the remaining space into new, smaller free space rectangles.

        :param found_rectangle_to_split: The rectangle we are spliting.
        :param dividing_rect: The rectangle dividing up the split rectangle.
        :param free_space_rectangles: A list of all free space rectangles for a particular surface.
        """
        free_space_rectangles.remove(found_rectangle_to_split)

        # create new rectangles
        if (found_rectangle_to_split.right - dividing_rect.right) > 0:
            rect_1 = pygame.Rect(dividing_rect.right,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.right - dividing_rect.right,
                                 found_rectangle_to_split.height)
            free_space_rectangles.append(rect_1)
        if (found_rectangle_to_split.bottom - dividing_rect.bottom) > 0:
            rect_2 = pygame.Rect(found_rectangle_to_split.left,
                                 dividing_rect.bottom,
                                 found_rectangle_to_split.width,
                                 found_rectangle_to_split.bottom - dividing_rect.bottom)
            free_space_rectangles.append(rect_2)
        if (dividing_rect.top - found_rectangle_to_split.top) > 0:
            rect_3 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.width,
                                 dividing_rect.top - found_rectangle_to_split.top)
            free_space_rectangles.append(rect_3)
        if (dividing_rect.left - found_rectangle_to_split.left) > 0:
            rect_4 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 dividing_rect.left - found_rectangle_to_split.left,
                                 found_rectangle_to_split.height)
            free_space_rectangles.append(rect_4)

    def find_surface_in_cache(self, lookup_id: str) -> Union[pygame.surface.Surface, None]:
        """
        Looks for a surface in the cache by an ID and returns it if found.

        :param lookup_id: ID of the surface to look for in the cache.

        :return The found surface, or None.

        """
        # check short term
        if lookup_id in self.cache_short_term_lookup:
            cached_item = self.cache_short_term_lookup[lookup_id]
            cached_item[1] += 1
            return cached_item[0]
        # check long term
        if lookup_id in self.cache_long_term_lookup:
            self.cache_long_term_lookup[lookup_id]['current_uses'] += 1
            self.cache_long_term_lookup[lookup_id]['total_uses'] += 1
            return self.cache_long_term_lookup[lookup_id]['surface']
        else:
            return None

    def remove_user_from_cache_item(self, string_id: str):
        """
        Deduct a 'user' from a particular cache surface. The number of users of a cache surface
        over the lifetime of a program would be a decent measure of how 'valuable' it is to
        keep a surface in the cache.

        :param string_id: The ID of the cached surface to deduct a user from.
        """
        if string_id in self.cache_long_term_lookup:
            self.cache_long_term_lookup[string_id]['current_uses'] -= 1

            if (self.cache_long_term_lookup[string_id]['current_uses'] == 0 and
                    self.cache_long_term_lookup[string_id]['total_uses'] == 1):
                self.consider_purging_list.append(string_id)

    def remove_user_and_request_clean_up_of_cached_item(self, string_id: str):
        """
        If we are certain that a cached surface won't be used again anytime soon we can request
        it is removed from the cache directly.

        :param string_id: the ID of the cached surface to remove from the cache.
        """
        self.remove_user_from_cache_item(string_id)
        self._free_cached_surface(string_id)

    def _free_cached_surface(self, string_id: str):
        """
        Directly remove an unused surface from the long term cache.

        :param string_id: the ID of the cached surface to remove from the cache.

        """
        if (string_id not in self.cache_long_term_lookup or
                self.cache_long_term_lookup[string_id]['current_uses'] != 0):
            return
        # check item to be removed is unused
        cache_to_clear = self.cache_long_term_lookup.pop(string_id)
        cache_surface_to_clear = cache_to_clear['surface']

        for cache_surface in self.cache_surfaces:
            if cache_surface['surface'] == cache_surface_to_clear.get_parent():
                freed_space = pygame.Rect(cache_surface_to_clear.get_offset(),
                                          cache_surface_to_clear.get_size())
                cache_surface['free_space_rectangles'].append(freed_space)
                break

        if string_id in self.consider_purging_list:
            self.consider_purging_list.remove(string_id)

    @staticmethod
    def build_cache_id(shape: str,
                       size: Tuple[int, int],
                       shadow_width: int,
                       border_width: int,
                       border_colour: pygame.Color,
                       bg_colour: pygame.Color,
                       corner_radius: Union[int, None] = None) -> str:
        """
        Create an ID string for a surface based on it's dimensions and parameters. The idea is
        that any surface in the cache with the same values in this ID should be identical.

        :param shape: A string for the overall shape of the surface (rounded rectangle,
         rectangle, etc).
        :param size: The dimensions of the surface.
        :param shadow_width: The thickness of the shadow around the shape.
        :param border_width: The thickness of the border around the shape.
        :param border_colour: The colour of the border.
        :param bg_colour: The background, or main colour of the surface.
        :param corner_radius: Optional corner radius parameter, only used for rounded rectangles.

        :return: A assembled string ID from the provided data.

        """

        id_string = (shape + '_' + str(size[0]) + '_' + str(size[1]) + '_' +
                     str(shadow_width) + '_' + str(border_width))

        if corner_radius is not None:
            id_string += '_' + str(corner_radius)

        if isinstance(border_colour, ColourGradient):
            id_string += '_' + str(border_colour)
        else:
            id_string += ('_' + str(border_colour.r) + '_' + str(border_colour.g) +
                          '_' + str(border_colour.b) + '_' + str(border_colour.a))

        if isinstance(bg_colour, ColourGradient):
            id_string += '_' + str(bg_colour)
        else:
            id_string += ('_' + str(bg_colour.r) + '_' + str(bg_colour.g) +
                          '_' + str(bg_colour.b) + '_' + str(bg_colour.a))

        return id_string
