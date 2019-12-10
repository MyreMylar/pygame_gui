import warnings

import pygame

from pygame_gui.core.colour_gradient import ColourGradient


class SurfaceCache:
    def __init__(self):
        self.cache_surface_size = (1024, 1024)
        self.cache_surfaces = []
        self.current_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
        self.current_surface.fill(pygame.Color('#00000000'))
        self.cache_surfaces.append(self.current_surface)

        self.free_space_rectangles = [pygame.Rect((0, 0), self.cache_surface_size)]

        self.cache_long_term_lookup = {}
        self.cache_short_term_lookup = {}

    def add_surface_to_cache(self, surface, string_id):
        self.cache_short_term_lookup[string_id] = surface.copy()

    def update(self):
        if any(self.cache_short_term_lookup):
            string_id, surface = self.cache_short_term_lookup.popitem()
            self.add_surface_to_long_term_cache(surface, string_id)

    def add_surface_to_long_term_cache(self, surface, string_id):
        surface_size = surface.get_size()
        if surface_size > self.cache_surface_size:
            warnings.warn('Unable to cache surfaces larger than ' + str(self.cache_surface_size))
            return None
        else:
            found_rectangle_to_split = None
            found_rectangle_cache = None

            while found_rectangle_cache is None:
                for free_rectangle in self.free_space_rectangles:
                    if free_rectangle.width >= surface_size[0] and free_rectangle.height >= surface_size[1]:
                        # we fits, so we sits
                        found_rectangle_to_split = free_rectangle
                        found_rectangle_cache = pygame.Rect(free_rectangle.topleft, surface_size)
                        self.current_surface.blit(surface, free_rectangle.topleft)
                        self.cache_long_term_lookup[string_id] = self.current_surface.subsurface(found_rectangle_cache)
                        break

                if found_rectangle_to_split is not None and found_rectangle_cache is not None:
                    self.split_rect(found_rectangle_to_split, found_rectangle_cache)
                    rects_to_split = [rect for rect in self.free_space_rectangles if rect.colliderect(found_rectangle_cache)]
                    for split_rect in rects_to_split:
                        self.split_rect(split_rect, found_rectangle_cache)

                    # clean up rectangles entirely inside other rectangles
                    rects_to_remove = []
                    rectangles_to_check = [rectangle for rectangle in self.free_space_rectangles]
                    for free_rectangle in self.free_space_rectangles:
                        for check_rect in rectangles_to_check:
                            if free_rectangle != check_rect and check_rect.contains(free_rectangle):
                                rects_to_remove.append(free_rectangle)
                    self.free_space_rectangles = [rect for rect in self.free_space_rectangles
                                                  if rect not in rects_to_remove]

                elif found_rectangle_to_split is None:
                    # create a new cache surface
                    self.current_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
                    self.current_surface.fill(pygame.Color('#00000000'))
                    self.cache_surfaces.append(self.current_surface)
                    self.free_space_rectangles = [pygame.Rect((0, 0), self.cache_surface_size)]

            return True

    def split_rect(self, found_rectangle_to_split, dividing_rect):
        self.free_space_rectangles.remove(found_rectangle_to_split)

        # create new rectangles
        if (found_rectangle_to_split.right - dividing_rect.right) > 0:
            rect_1 = pygame.Rect(dividing_rect.right,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.right - dividing_rect.right,
                                 found_rectangle_to_split.height)
            self.free_space_rectangles.append(rect_1)
        if (found_rectangle_to_split.bottom - dividing_rect.bottom) > 0:
            rect_2 = pygame.Rect(found_rectangle_to_split.left,
                                 dividing_rect.bottom,
                                 found_rectangle_to_split.width,
                                 found_rectangle_to_split.bottom - dividing_rect.bottom)
            self.free_space_rectangles.append(rect_2)
        if (dividing_rect.top - found_rectangle_to_split.top) > 0:
            rect_3 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.width,
                                 dividing_rect.top - found_rectangle_to_split.top)
            self.free_space_rectangles.append(rect_3)
        if (dividing_rect.left - found_rectangle_to_split.left) > 0:
            rect_4 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 dividing_rect.left - found_rectangle_to_split.left,
                                 found_rectangle_to_split.height)
            self.free_space_rectangles.append(rect_4)

    def find_surface_in_cache(self, lookup_id):
        # check short term
        if lookup_id in self.cache_short_term_lookup:
            return self.cache_short_term_lookup[lookup_id]
        # check long term
        if lookup_id in self.cache_long_term_lookup:
            return self.cache_long_term_lookup[lookup_id]
        else:
            return None

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
