import warnings

import pygame

from pygame_gui.core.colour_gradient import ColourGradient


class SurfaceCache:
    def __init__(self):
        self.cache_surface_size = (1024, 1024)
        self.cache_surfaces = []
        starting_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
        starting_surface.fill(pygame.Color('#00000000'))
        self.cache_surfaces.append({'surface': starting_surface,
                                    'free_space_rectangles': [pygame.Rect((0, 0), self.cache_surface_size)]})

        self.cache_long_term_lookup = {}
        self.cache_short_term_lookup = {}

        self.consider_purging_list = []

    def add_surface_to_cache(self, surface, string_id):
        self.cache_short_term_lookup[string_id] = surface.copy()

    def update(self):
        if any(self.cache_short_term_lookup):
            string_id, surface = self.cache_short_term_lookup.popitem()
            self.add_surface_to_long_term_cache(surface, string_id)

        # don't bother considering any purging until we've filled up at least a few textures
        if len(self.cache_surfaces) > 3:
            for cache_id in self.consider_purging_list:
                cached_item = self.cache_long_term_lookup[cache_id]
                # check our item to be purged takes up more space than 200x200 and is not being used right now.
                cached_item_area = cached_item.get_width() * cached_item.get_height()
                if cached_item[1] == 0 and cached_item_area >= 40000:
                    # purge
                    self.free_cached_surface(cache_id)

            self.consider_purging_list.clear()

    def add_surface_to_long_term_cache(self, surface, string_id):
        surface_size = surface.get_size()
        if surface_size > self.cache_surface_size:
            warnings.warn('Unable to cache surfaces larger than ' + str(self.cache_surface_size))
            return None
        else:

            found_rectangle_cache = None

            while found_rectangle_cache is None:
                for cache_surface in self.cache_surfaces:
                    found_rectangle_to_split = None
                    if found_rectangle_cache is None:
                        free_space_rectangles = cache_surface['free_space_rectangles']
                        current_surface = cache_surface['surface']
                        for free_rectangle in free_space_rectangles:
                            if free_rectangle.width >= surface_size[0] and free_rectangle.height >= surface_size[1]:
                                # we fits, so we sits
                                found_rectangle_to_split = free_rectangle
                                found_rectangle_cache = pygame.Rect(free_rectangle.topleft, surface_size)
                                current_surface.blit(surface, free_rectangle.topleft)
                                self.cache_long_term_lookup[string_id] = [current_surface.subsurface(found_rectangle_cache),
                                                                          1]
                                break

                        if found_rectangle_to_split is not None and found_rectangle_cache is not None:
                            self.split_rect(found_rectangle_to_split, found_rectangle_cache,
                                            cache_surface['free_space_rectangles'])
                            rects_to_split = [rect for rect in free_space_rectangles
                                              if rect.colliderect(found_rectangle_cache)]
                            for split_rect in rects_to_split:
                                self.split_rect(split_rect, found_rectangle_cache, cache_surface['free_space_rectangles'])

                            # clean up rectangles entirely inside other rectangles
                            rects_to_remove = []
                            rectangles_to_check = [rectangle for rectangle in free_space_rectangles]
                            for free_rectangle in free_space_rectangles:
                                for check_rect in rectangles_to_check:
                                    if free_rectangle != check_rect and check_rect.contains(free_rectangle):
                                        rects_to_remove.append(free_rectangle)
                            cache_surface['free_space_rectangles'] = [rect for rect in free_space_rectangles
                                                                      if rect not in rects_to_remove]

                if found_rectangle_cache is None:
                    # create a new cache surface
                    new_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
                    new_surface.fill(pygame.Color('#00000000'))
                    self.cache_surfaces.append({'surface': new_surface,
                                                'free_space_rectangles': [
                                                    pygame.Rect((0, 0), self.cache_surface_size)]})

            return True

    @staticmethod
    def split_rect(found_rectangle_to_split, dividing_rect, free_space_rectangles):
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

    def find_surface_in_cache(self, lookup_id):
        # check short term
        if lookup_id in self.cache_short_term_lookup:
            return self.cache_short_term_lookup[lookup_id]
        # check long term
        if lookup_id in self.cache_long_term_lookup:
            self.cache_long_term_lookup[lookup_id][1] += 1
            return self.cache_long_term_lookup[lookup_id][0]
        else:
            return None

    def remove_user_from_cache_item(self, string_id):
        if string_id in self.cache_long_term_lookup:
            self.cache_long_term_lookup[string_id][1] -= 1

            if self.cache_long_term_lookup[string_id][1] == 0:
                self.consider_purging_list.append(string_id)

    def remove_user_and_request_clean_up_of_cached_item(self, string_id):
        self.remove_user_from_cache_item(string_id)
        self.free_cached_surface(string_id)

    def free_cached_surface(self, string_id):
        if string_id not in self.cache_long_term_lookup or self.cache_long_term_lookup[string_id][1] != 0:
            return
        # check item to be removed is unused
        cache_to_clear = self.cache_long_term_lookup.pop(string_id)
        cache_surface_to_clear = cache_to_clear[0]

        for cache_surface in self.cache_surfaces:
            if cache_surface['surface'] == cache_surface_to_clear.get_parent():
                freed_space = pygame.Rect(cache_surface_to_clear.get_offset(),
                                          cache_surface_to_clear.get_size())
                cache_surface['free_space_rectangles'].append(freed_space)
                break

        if string_id in self.consider_purging_list:
            self.consider_purging_list.remove(string_id)

    @staticmethod
    def build_cache_id(shape, size, shadow_width, border_width, border_colour, bg_colour, corner_radius=None):

        id_string = (shape + '_' + str(size[0]) + '_' + str(size[1]) + '_' +
                     str(shadow_width) + '_' + str(border_width))

        if corner_radius is not None:
            id_string += '_' + str(corner_radius)

        if type(border_colour) == ColourGradient:
            id_string += '_' + str(border_colour)
        else:
            id_string += ('_' + str(border_colour.r) + '_' + str(border_colour.g) +
                          '_' + str(border_colour.b) + '_' + str(border_colour.a))

        if type(bg_colour) == ColourGradient:
            id_string += '_' + str(bg_colour)
        else:
            id_string += ('_' + str(bg_colour.r) + '_' + str(bg_colour.g) +
                          '_' + str(bg_colour.b) + '_' + str(bg_colour.a))

        return id_string
