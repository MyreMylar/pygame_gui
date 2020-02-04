import math
import warnings
from typing import Dict, List, Union, Tuple

import pygame

from pygame_gui import UIManager
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape


class RectDrawableShape(DrawableShape):
    """
    A rectangle shape for UI elements has theming options for a border, a shadow, colour gradients and text.

    :param containing_rect: The layout rectangle that surrounds and controls the size of this shape.
    :param theming_parameters: Various styling parameters that control the final look of the shape.
    :param states: The different UI states the shape can be in. Shapes have different surfaces for each state.
    :param manager: The UI manager.
    """

    def __init__(self, containing_rect: pygame.Rect, theming_parameters: Dict, states: List, manager: UIManager):
        super().__init__(containing_rect, theming_parameters, states, manager)

        self.click_area_shape = None
        self.border_rect = None
        self.background_rect = None
        self.aligned_text_rect = None
        self.base_surface = None
        self.full_rebuild_on_size_change()

    def full_rebuild_on_size_change(self):
        """
        Everything needs rebuilding if we change the size of the containing rectangle.
        """
        # clamping border and shadow widths so we can't form impossible negative sized surfaces
        if self.theming['shadow_width'] > min(math.floor(self.containing_rect.width / 2),
                                              math.floor(self.containing_rect.height / 2)):
            self.theming['shadow_width'] = min(math.floor(self.containing_rect.width / 2),
                                               math.floor(self.containing_rect.height / 2))
        if self.theming['shadow_width'] < 0:
            self.theming['shadow_width'] = 0

        if self.theming['border_width'] > min(math.floor((self.containing_rect.width -
                                                          (self.theming['shadow_width'] * 2)) / 2),
                                              math.floor((self.containing_rect.height -
                                                          (self.theming['shadow_width'] * 2)) / 2)):
            self.theming['border_width'] = min(math.floor((self.containing_rect.width -
                                                           (self.theming['shadow_width'] * 2)) / 2),
                                               math.floor((self.containing_rect.height -
                                                           (self.theming['shadow_width'] * 2)) / 2))
        if self.theming['border_width'] < 0:
            self.theming['border_width'] = 0

        if self.theming['shadow_width'] > 0:
            self.click_area_shape = pygame.Rect((self.containing_rect.x + self.theming['shadow_width'],
                                                 self.containing_rect.y + self.theming['shadow_width']),
                                                (self.containing_rect.width - (2 * self.theming['shadow_width']),
                                                 self.containing_rect.height - (2 * self.theming['shadow_width'])))
            shadow = self.ui_manager.get_shadow(self.containing_rect.size,
                                                shadow_width=self.theming['shadow_width'],
                                                corner_radius=self.theming['shadow_width'])
            if shadow is not None:
                self.base_surface = shadow
            else:
                warnings.warn("shape created too small to fit in selected shadow width and corner radius")
                self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA, depth=32)
        else:
            self.click_area_shape = self.containing_rect.copy()
            self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA, depth=32)

        self.compute_aligned_text_rect()

        self.border_rect = pygame.Rect((self.theming['shadow_width'],
                                        self.theming['shadow_width']),
                                       (self.click_area_shape.width, self.click_area_shape.height))

        self.background_rect = pygame.Rect((self.theming['border_width'] + self.theming['shadow_width'],
                                            self.theming['border_width'] + self.theming['shadow_width']),
                                           (self.click_area_shape.width - (2 * self.theming['border_width']),
                                            self.click_area_shape.height - (2 * self.theming['border_width'])))
        self.redraw_all_states()

    def collide_point(self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Tests if a point is colliding with our Drawable shape's 'click area' hot spot.

        :param point: The point to test.
        :return: True if we are colliding.
        """
        return bool(self.click_area_shape.collidepoint(int(point[0]), int(point[1])))

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Expensive size change.

        :param dimensions:
        :return:
        """
        self.containing_rect.width = dimensions[0]
        self.containing_rect.height = dimensions[1]
        self.click_area_shape.width = dimensions[0] - (2 * self.theming['shadow_width'])
        self.click_area_shape.height = dimensions[1] - (2 * self.theming['shadow_width'])

        self.full_rebuild_on_size_change()

    def set_position(self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Move the shape. Only really impacts the position of the 'click_area' hot spot.

        :param point: The new position to move it to.
        """
        self.containing_rect.x = point[0]
        self.containing_rect.y = point[1]
        self.click_area_shape.x = point[0] + self.theming['shadow_width']
        self.click_area_shape.y = point[1] + self.theming['shadow_width']

    def redraw_state(self, state_str):
        """
        Redraws the shape's surface for a given UI state.

        :param state_str: The ID string of the state to rebuild.
        """
        state_str = state_str
        border_colour_state_str = state_str + '_border'
        bg_colour_state_str = state_str + '_bg'
        text_colour_state_str = state_str + '_text'
        image_state_str = state_str + '_image'

        found_shape = None
        shape_id = None
        if 'filled_bar' not in self.theming and 'filled_bar_width' not in self.theming:
            shape_id = self.shape_cache.build_cache_id('rectangle', self.containing_rect.size,
                                                       self.theming['shadow_width'],
                                                       self.theming['border_width'],
                                                       self.theming[border_colour_state_str],
                                                       self.theming[bg_colour_state_str])

            found_shape = self.shape_cache.find_surface_in_cache(shape_id)
        if found_shape is not None:
            self.surfaces[state_str] = found_shape.copy()
        else:
            self.surfaces[state_str] = self.base_surface.copy()

            if self.theming['border_width'] > 0:

                if type(self.theming[border_colour_state_str]) == ColourGradient:
                    border_shape_surface = pygame.Surface(self.border_rect.size, flags=pygame.SRCALPHA, depth=32)
                    border_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                    self.surfaces[state_str].blit(border_shape_surface,
                                                  self.border_rect, special_flags=pygame.BLEND_RGBA_SUB)
                    self.theming[border_colour_state_str].apply_gradient_to_surface(border_shape_surface)
                    self.surfaces[state_str].blit(border_shape_surface, self.border_rect)
                else:
                    self.surfaces[state_str].fill(self.theming[border_colour_state_str], self.border_rect)

            if type(self.theming[bg_colour_state_str]) == ColourGradient:
                background_shape_surface = pygame.Surface(self.background_rect.size, flags=pygame.SRCALPHA, depth=32)
                background_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                self.surfaces[state_str].blit(background_shape_surface,
                                              self.background_rect, special_flags=pygame.BLEND_RGBA_SUB)
                self.theming[bg_colour_state_str].apply_gradient_to_surface(background_shape_surface)
                self.surfaces[state_str].blit(background_shape_surface, self.background_rect)
            else:
                self.surfaces[state_str].fill(self.theming[bg_colour_state_str], self.background_rect)

            if 'filled_bar' in self.theming and 'filled_bar_width' in self.theming:
                bar_rect = pygame.Rect(self.background_rect.topleft, (self.theming['filled_bar_width'],
                                                                      self.background_rect.height))
                if type(self.theming['filled_bar']) == ColourGradient:
                    bar_shape_surface = pygame.Surface(bar_rect.size, flags=pygame.SRCALPHA, depth=32)
                    bar_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                    self.surfaces[state_str].blit(bar_shape_surface, bar_rect, special_flags=pygame.BLEND_RGBA_SUB)
                    self.theming['filled_bar'].apply_gradient_to_surface(bar_shape_surface)
                    self.surfaces[state_str].blit(bar_shape_surface, bar_rect)
                else:
                    self.surfaces[state_str].fill(self.theming['filled_bar'], bar_rect)

            if shape_id is not None:
                self.shape_cache.add_surface_to_cache(self.surfaces[state_str].copy(), shape_id)

        self.rebuild_images_and_text(image_state_str, state_str, text_colour_state_str)
