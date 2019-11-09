from typing import Dict, List, Union, Tuple

import pygame
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.ui_appearance_theme import ColourGradient


class DrawableShape:
    def __init__(self, containing_rect: pygame.Rect,
                 theming_parameters: Dict, states: List,
                 manager: UIManager):
        self.containing_rect = containing_rect
        self.theming = theming_parameters
        self.states = states
        self.ui_manager = manager

        self.surfaces = {'normal': None,
                         'hovered': None,
                         'disabled': None,
                         'selected': None,
                         'active': None}  # type: Dict[str,pygame.Surface]

    def redraw_state(self, state_str):
        pass

    def redraw_all_states(self):
        for state in self.states:
            self.redraw_state(state)

    def collide_point(self, point: Union[pygame.math.Vector2, Tuple[int, int]]):
        pass

    def get_surface(self, surface_name):
        return self.surfaces[surface_name]


class RectDrawableShape(DrawableShape):
    def __init__(self, containing_rect: pygame.Rect, theming_parameters: Dict, states: List,
                 manager: UIManager):
        super().__init__(containing_rect, theming_parameters, states, manager)

        if self.theming['shadow_width'] > 0:
            self.click_area_shape = pygame.Rect((self.containing_rect.x + self.theming['shadow_width'],
                                                 self.containing_rect.y + self.theming['shadow_width']),
                                                (self.containing_rect.width - (2 * self.theming['shadow_width']),
                                                 self.containing_rect.height - (2 * self.theming['shadow_width'])))
            self.base_surface = self.ui_manager.get_shadow(self.containing_rect.size)
        else:
            self.click_area_shape = self.containing_rect.copy()
            self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA)

        self.border_rect = pygame.Rect((self.theming['shadow_width'],
                                        self.theming['shadow_width']),
                                       (self.click_area_shape.width, self.click_area_shape.height))

        self.background_rect = pygame.Rect((self.theming['border_width'] + self.theming['shadow_width'],
                                            self.theming['border_width'] + self.theming['shadow_width']),
                                           (self.click_area_shape.width - (2 * self.theming['border_width']),
                                            self.click_area_shape.height - (2 * self.theming['border_width'])))
        self.redraw_all_states()

    def collide_point(self, point: Union[pygame.math.Vector2, Tuple[int, int]]):
        return self.click_area_shape.collidepoint(point[0], point[1])

    def redraw_state(self, state_str):
        state_str = state_str
        border_colour_state_str = state_str + '_border'
        bg_colour_state_str = state_str + '_bg'
        text_colour_state_str = state_str + '_text'
        image_state_str = state_str + '_image'

        self.surfaces[state_str] = self.base_surface.copy()

        if self.theming['border_width'] > 0:

            if type(self.theming[border_colour_state_str]) == ColourGradient:
                border_shape_surface = pygame.Surface(self.border_rect.size)
                border_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                gradient_surface = self.theming[border_colour_state_str].apply_gradient_to_surface(border_shape_surface)
                self.surfaces[state_str].blit(border_shape_surface, self.border_rect,
                                              special_flags=pygame.BLEND_RGBA_SUB)
                self.surfaces[state_str].blit(gradient_surface, self.border_rect)
            else:
                self.surfaces[state_str].fill(self.theming[border_colour_state_str], self.border_rect)

        if type(self.theming[bg_colour_state_str]) == ColourGradient:
            background_shape_surface = pygame.Surface(self.background_rect.size)
            background_shape_surface.fill(pygame.Color('#FFFFFFFF'))
            gradient_surface = self.theming[bg_colour_state_str].apply_gradient_to_surface(background_shape_surface)
            self.surfaces[state_str].blit(background_shape_surface,
                                          self.background_rect, special_flags=pygame.BLEND_RGBA_SUB)
            self.surfaces[state_str].blit(gradient_surface, self.background_rect)
        else:
            self.surfaces[state_str].fill(self.theming[bg_colour_state_str], self.background_rect)

        if self.theming[image_state_str] is not None:
            image_rect = self.theming[image_state_str].get_rect()
            image_rect.center = (self.containing_rect.width/2, self.containing_rect.height/2)
            self.surfaces[state_str].blit(self.theming[image_state_str], image_rect)

        if self.theming['text'] is not None:
            if len(self.theming['text']) > 0:
                text_surface = self.theming['font'].render(self.theming['text'], True,
                                                           self.theming[text_colour_state_str])
            else:
                text_surface = None

            if text_surface is not None and self.theming['aligned_text_rect'] is not None:
                self.surfaces[state_str].blit(text_surface, self.theming['aligned_text_rect'])
