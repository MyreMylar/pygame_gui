from collections import deque
from typing import Dict, List, Union, Tuple

import pygame
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.colour_gradient import ColourGradient
from pygame.math import Vector2


class DrawableShape:
    def __init__(self, containing_rect: pygame.Rect, theming_parameters: Dict, states: List, manager: UIManager):
        self.containing_rect = containing_rect
        self.theming = theming_parameters
        self.states = states
        self.ui_manager = manager
        self.shape_cache = self.ui_manager.ui_theme.shape_cache

        self.aligned_text_rect = None
        self.click_area_shape = None

        self.surfaces = {'normal': None,
                         'hovered': None,
                         'disabled': None,
                         'selected': None,
                         'active': None}  # type: Dict[str,Union[pygame.Surface, None]]

        self.states_to_redraw_queue = deque([])
        self.need_to_clean_up = True

    def redraw_state(self, state_str):
        pass

    def clean_up_temp_shapes(self):
        pass

    def update(self):
        if len(self.states_to_redraw_queue) > 0:
            state = self.states_to_redraw_queue.popleft()
            self.redraw_state(state)
        if self.need_to_clean_up and len(self.states_to_redraw_queue) == 0:
            # last state so clean up
            self.clean_up_temp_shapes()
            self.need_to_clean_up = False

    def redraw_all_states(self):
        self.states_to_redraw_queue = deque([state for state in self.states])
        initial_state = self.states_to_redraw_queue.popleft()
        self.redraw_state(initial_state)

    def compute_aligned_text_rect(self):
        """
        Aligns the text drawing position correctly according to our theming options.
        """
        if 'text' not in self.theming or len(self.theming['text']) <= 0:
            return
        # first we need to create rectangle the size of the text, if there is any text to draw
        self.aligned_text_rect = pygame.Rect((0, 0), self.theming['font'].size(self.theming['text']))

        if (self.theming['text_horiz_alignment'] == 'center' or
                not self.theming['text_horiz_alignment'] in ['left', 'right']):
            self.aligned_text_rect.centerx = int(self.containing_rect.width / 2)
        elif self.theming['text_horiz_alignment'] == 'left':
            self.aligned_text_rect.x = (self.theming['text_horiz_alignment_padding'] +
                                        self.theming['shadow_width'] + self.theming['border_width'])
        else:
            x_pos = (self.containing_rect.width - self.theming['text_horiz_alignment_padding'] -
                     self.aligned_text_rect.width - self.theming['shadow_width'] - self.theming['border_width'])
            self.aligned_text_rect.x = x_pos
        if (self.theming['text_vert_alignment'] == 'center' or
                not self.theming['text_vert_alignment'] in ['top', 'bottom']):
            self.aligned_text_rect.centery = int(self.containing_rect.height / 2)
        elif self.theming['text_vert_alignment'] == 'top':
            self.aligned_text_rect.y = (self.theming['text_vert_alignment_padding'] +
                                        self.theming['shadow_width'] + self.theming['border_width'])
        else:
            self.aligned_text_rect.y = (self.containing_rect.height - self.aligned_text_rect.height
                                        - self.theming['text_vert_alignment_padding'] -
                                        self.theming['shadow_width'] - self.theming['border_width'])

    def collide_point(self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        pass

    def get_surface(self, surface_name):
        if surface_name in self.surfaces and self.surfaces[surface_name] is not None:
            return self.surfaces[surface_name]
        elif surface_name in self.surfaces and self.surfaces['normal'] is not None:
            return self.surfaces['normal']
        else:
            return pygame.Surface((0, 0))

    def set_position(self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        pass

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        pass

    @staticmethod
    def apply_colour_to_surface(colour, shape_surface, rect=None):
        """
        Apply a colour to a shape surface by multiplication blend. This works best when the shape surface is
        predominantly white.

        :param colour: The colour to apply.
        :param shape_surface: The shape surface to apply the colour to.
        :param rect: A rectangle to apply the colour inside of.
        """
        if rect is not None:
            colour_surface = pygame.Surface(rect.size, flags=pygame.SRCALPHA, depth=32)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, rect, special_flags=pygame.BLEND_RGBA_MULT)
        else:
            colour_surface = pygame.Surface(shape_surface.get_size(), flags=pygame.SRCALPHA, depth=32)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def rebuild_images_and_text(self, image_state_str, state_str, text_colour_state_str):
        # Draw any themed images
        if image_state_str in self.theming and self.theming[image_state_str] is not None:
            image_rect = self.theming[image_state_str].get_rect()
            image_rect.center = (int(self.containing_rect.width / 2), int(self.containing_rect.height / 2))
            self.surfaces[state_str].blit(self.theming[image_state_str], image_rect)
        # Draw any text
        if 'text' in self.theming and 'font' in self.theming and self.theming['text'] is not None:
            if len(self.theming['text']) > 0 and text_colour_state_str in self.theming:
                if type(self.theming[text_colour_state_str]) != ColourGradient:
                    text_surface = self.theming['font'].render(self.theming['text'], True,
                                                               self.theming[text_colour_state_str])
                else:
                    text_surface = self.theming['font'].render(self.theming['text'], True,
                                                               pygame.Color('#FFFFFFFF'))
                    self.theming[text_colour_state_str].apply_gradient_to_surface(text_surface)
            else:
                text_surface = None

            if text_surface is not None and self.aligned_text_rect is not None:
                self.surfaces[state_str].blit(text_surface, self.aligned_text_rect)
