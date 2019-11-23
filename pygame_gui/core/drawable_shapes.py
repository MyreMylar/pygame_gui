import math
import warnings
from collections import deque
from typing import Dict, List, Union, Tuple

import pygame
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.ui_appearance_theme import ColourGradient, ShapeCache
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

    def redraw_state(self, state_str):
        pass

    def clean_up_temp_shapes(self):
        pass

    def update(self):
        if len(self.states_to_redraw_queue) > 0:
            state = self.states_to_redraw_queue.popleft()
            self.redraw_state(state)
            if len(self.states_to_redraw_queue) == 0:
                # last state so clean up
                self.clean_up_temp_shapes()

    def redraw_all_states(self):
        self.states_to_redraw_queue = deque([state for state in self.states])
        initial_state = self.states_to_redraw_queue.popleft()
        self.redraw_state(initial_state)

    def compute_aligned_text_rect(self):
        """
        Aligns the text drawing position correctly according to our theming options.
        """
        if 'text' in self.theming and len(self.theming['text']) > 0:
            # first we need to create rectangle the size of the text, if there is any text to draw
            self.aligned_text_rect = pygame.Rect((0, 0), self.theming['font'].size(self.theming['text']))

            # horizontal
            if self.theming['text_horiz_alignment'] == 'center':
                self.aligned_text_rect.centerx = self.containing_rect.width / 2
            elif self.theming['text_horiz_alignment'] == 'left':
                self.aligned_text_rect.x = (self.theming['text_horiz_alignment_padding'] +
                                            self.theming['shadow_width'] + self.theming['border_width'])
            elif self.theming['text_horiz_alignment'] == 'right':
                x_pos = (self.click_area_shape.width - self.theming['text_horiz_alignment_padding'] -
                         self.aligned_text_rect.width - self.theming['shadow_width'] - self.theming['border_width'])
                self.aligned_text_rect.x = x_pos
            else:
                self.aligned_text_rect.centerx = self.containing_rect.width / 2
            # vertical
            if self.theming['text_vert_alignment'] == 'center':
                self.aligned_text_rect.centery = int(self.containing_rect.height / 2)
            elif self.theming['text_vert_alignment'] == 'top':
                self.aligned_text_rect.y = (self.theming['text_vert_alignment_padding'] +
                                            self.theming['shadow_width'] + self.theming['border_width'])
            elif self.theming['text_vert_alignment'] == 'bottom':
                self.aligned_text_rect.y = (self.containing_rect.height - self.aligned_text_rect.height
                                            - self.theming['text_vert_alignment_padding'] -
                                            self.theming['shadow_width'] - self.theming['border_width'])
            else:
                self.aligned_text_rect.centery = int(self.containing_rect.height / 2)

    def collide_point(self, point: Union[pygame.math.Vector2, Tuple[int, int]]):
        pass

    def get_surface(self, surface_name):
        if surface_name in self.surfaces:
            if self.surfaces[surface_name] is not None:
                return self.surfaces[surface_name]
            elif self.surfaces['normal'] is not None:
                return self.surfaces['normal']
            else:
                return pygame.Surface((0, 0))
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
            colour_surface = pygame.Surface(rect.size, flags=pygame.SRCALPHA)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, rect, special_flags=pygame.BLEND_RGBA_MULT)
        else:
            colour_surface = pygame.Surface(shape_surface.get_size(), flags=pygame.SRCALPHA)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def rebuild_images_and_text(self, image_state_str, state_str, text_colour_state_str):
        # Draw any themed images
        if image_state_str in self.theming and self.theming[image_state_str] is not None:
            image_rect = self.theming[image_state_str].get_rect()
            image_rect.center = (self.containing_rect.width / 2, self.containing_rect.height / 2)
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
            self.base_surface = self.ui_manager.get_shadow(self.containing_rect.size)
        else:
            self.click_area_shape = self.containing_rect.copy()
            self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA)

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
        return self.click_area_shape.collidepoint(point[0], point[1])

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

        self.surfaces[state_str] = self.base_surface.copy()

        if self.theming['border_width'] > 0:

            if type(self.theming[border_colour_state_str]) == ColourGradient:
                border_shape_surface = pygame.Surface(self.border_rect.size, flags=pygame.SRCALPHA)
                border_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                self.surfaces[state_str].blit(border_shape_surface,
                                              self.border_rect, special_flags=pygame.BLEND_RGBA_SUB)
                self.theming[border_colour_state_str].apply_gradient_to_surface(border_shape_surface)
                self.surfaces[state_str].blit(border_shape_surface, self.border_rect)
            else:
                self.surfaces[state_str].fill(self.theming[border_colour_state_str], self.border_rect)

        if type(self.theming[bg_colour_state_str]) == ColourGradient:
            background_shape_surface = pygame.Surface(self.background_rect.size, flags=pygame.SRCALPHA)
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
                bar_shape_surface = pygame.Surface(bar_rect.size, flags=pygame.SRCALPHA)
                bar_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                self.surfaces[state_str].blit(bar_shape_surface, bar_rect, special_flags=pygame.BLEND_RGBA_SUB)
                self.theming['filled_bar'].apply_gradient_to_surface(bar_shape_surface)
                self.surfaces[state_str].blit(bar_shape_surface, bar_rect)
            else:
                self.surfaces[state_str].fill(self.theming['filled_bar'], bar_rect)

        self.rebuild_images_and_text(image_state_str, state_str, text_colour_state_str)


class EllipseDrawableShape(DrawableShape):
    """
    A drawable ellipse shape for the UI, has theming options for a border, a shadow, colour gradients and text.

    :param containing_rect: The layout rectangle that surrounds and controls the size of this shape.
    :param theming_parameters: Various styling parameters that control the final look of the shape.
    :param states: The different UI states the shape can be in. Shapes have different surfaces for each state.
    :param manager: The UI manager.
    """

    def __init__(self, containing_rect: pygame.Rect, theming_parameters: Dict, states: List,
                 manager: UIManager):
        super().__init__(containing_rect, theming_parameters, states, manager)

        self.ellipse_center = containing_rect.center
        self.ellipse_half_diameters = (0.5 * containing_rect.width, 0.5 * containing_rect.height)

        self.click_area_shape = None
        self.border_rect = None
        self.background_rect = None
        self.aligned_text_rect = None
        self.base_surface = None

        self.full_rebuild_on_size_change()

    def full_rebuild_on_size_change(self):
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
            self.base_surface = self.ui_manager.get_shadow(self.containing_rect.size,
                                                           self.theming['shadow_width'], 'ellipse')
        else:
            self.click_area_shape = self.containing_rect.copy()
            self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA)

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
        Checks collision between a point and this ellipse.

        :param point:
        :return: If the point is inside the shape.
        """
        collided = False
        x_val = ((point[0] - self.ellipse_center[0]) ** 2) / (self.ellipse_half_diameters[0] ** 2)
        y_val = ((point[1] - self.ellipse_center[1]) ** 2) / (self.ellipse_half_diameters[1] ** 2)
        if (x_val + y_val) < 1:
            collided = True

        return collided

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

        self.ellipse_half_diameters = (0.5 * self.containing_rect.width, 0.5 * self.containing_rect.height)

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

        self.ellipse_center = self.click_area_shape.center

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

        self.surfaces[state_str] = self.base_surface.copy()

        # Try one AA call method
        aa = 4
        self.border_rect = pygame.Rect((self.theming['shadow_width'] * aa,
                                        self.theming['shadow_width'] * aa),
                                       (self.click_area_shape.width * aa, self.click_area_shape.height * aa))

        self.background_rect = pygame.Rect(((self.theming['border_width'] + self.theming['shadow_width']) * aa,
                                            (self.theming['border_width'] + self.theming['shadow_width']) * aa),
                                           (self.border_rect.width - (2 * self.theming['border_width'] * aa),
                                            self.border_rect.height - (2 * self.theming['border_width'] * aa)))

        bab_surface = pygame.Surface((self.containing_rect.width * aa,
                                      self.containing_rect.height * aa), flags=pygame.SRCALPHA)
        bab_surface.fill(pygame.Color('#00000000'))
        if self.theming['border_width'] > 0:
            # If we have a border, draw it
            # Two paths here, 1. Drawing with a colour gradient or 2. With a single colour.
            if type(self.theming[border_colour_state_str]) == ColourGradient:
                shape_surface = self.clear_and_create_shape_surface(bab_surface, self.border_rect,
                                                                    0, aa_amount=aa, clear=False)
                self.theming[border_colour_state_str].apply_gradient_to_surface(shape_surface)
                bab_surface.blit(shape_surface, self.border_rect)
            else:
                shape_surface = self.clear_and_create_shape_surface(bab_surface, self.border_rect,
                                                                    0, aa_amount=aa, clear=False)
                self.apply_colour_to_surface(self.theming[border_colour_state_str], shape_surface)
                bab_surface.blit(shape_surface, self.border_rect)

        # Next we draw the main background colour of the shape
        # Two paths here, 1. Drawing with a colour gradient or 2. With a single colour.
        if type(self.theming[bg_colour_state_str]) == ColourGradient:
            shape_surface = self.clear_and_create_shape_surface(bab_surface, self.background_rect, 1, aa_amount=aa)
            self.theming[bg_colour_state_str].apply_gradient_to_surface(shape_surface)
            bab_surface.blit(shape_surface, self.background_rect)
        else:
            shape_surface = self.clear_and_create_shape_surface(bab_surface, self.background_rect, 1, aa_amount=aa)
            self.apply_colour_to_surface(self.theming[bg_colour_state_str], shape_surface)
            bab_surface.blit(shape_surface, self.background_rect)

        # apply AA to background
        bab_surface = pygame.transform.smoothscale(bab_surface, self.containing_rect.size)

        # cut a hole in shadow, then blit background into it
        sub_surface = pygame.Surface(((self.containing_rect.width - (2 * self.theming['shadow_width'])) * aa,
                                      (self.containing_rect.height - (2 * self.theming['shadow_width'])) * aa),
                                     flags=pygame.SRCALPHA)
        sub_surface.fill(pygame.Color('#00000000'))
        pygame.draw.ellipse(sub_surface, pygame.Color("#FFFFFFFF"), sub_surface.get_rect())
        small_sub = pygame.transform.smoothscale(sub_surface,
                                                 (self.containing_rect.width - (2 * self.theming['shadow_width']),
                                                  self.containing_rect.height - (2 * self.theming['shadow_width'])))
        self.surfaces[state_str].blit(small_sub, pygame.Rect((self.theming['shadow_width'],
                                                              self.theming['shadow_width']),
                                                             sub_surface.get_size()),
                                      special_flags=pygame.BLEND_RGBA_SUB)

        self.surfaces[state_str].blit(bab_surface, (0, 0))

        self.rebuild_images_and_text(image_state_str, state_str, text_colour_state_str)

    @staticmethod
    def clear_and_create_shape_surface(surface, rect, overlap, aa_amount, clear=True) -> pygame.Surface:
        """
        Clear a space for a new shape surface on the main state surface for this state. The surface created will be
        plain white so that it can be easily multiplied with a colour surface.

        :param surface: The surface we are working on.
        :param rect: Used to size and position the new shape.
        :param overlap: The amount of overlap between this surface and the one below.
        :param aa_amount: The amount of Anti Aliasing to use for this shape.
        :param clear: Whether we should clear our surface.
        :return: The new shape surface.
        """

        # For the visible AA shape surface we only want to blend in the alpha channel
        large_shape_surface = pygame.Surface((rect.width, rect.height), flags=pygame.SRCALPHA)
        large_shape_surface.fill(pygame.Color('#FFFFFF00'))
        pygame.draw.ellipse(large_shape_surface, pygame.Color("#FFFFFFFF"), large_shape_surface.get_rect())

        if clear:
            # before we draw a shape we clear a space for it, to allow for transparency.
            # This works best if we leave a small overlap between the old background and the new shape
            subtract_rect = pygame.Rect(rect.x + (overlap * aa_amount),
                                        rect.y + (overlap * aa_amount),
                                        rect.width - 2 * (overlap * aa_amount),
                                        rect.height - 2 * (overlap * aa_amount))
            # for the subtract surface we want to blend in all RGBA channels to clear correctly for our new shape
            large_sub_surface = pygame.Surface((subtract_rect.width, subtract_rect.height), flags=pygame.SRCALPHA)
            large_sub_surface.fill(pygame.Color('#00000000'))
            pygame.draw.ellipse(large_sub_surface, pygame.Color("#FFFFFFFF"), large_sub_surface.get_rect())

            surface.blit(large_sub_surface, subtract_rect, special_flags=pygame.BLEND_RGBA_SUB)
        return large_shape_surface


class RoundedRectangleShape(DrawableShape):
    """
    A drawable rounded rectangle shape for the UI, has theming options for a border, a shadow, colour gradients
    and text.

    :param containing_rect: The layout rectangle that surrounds and controls the size of this shape.
    :param theming_parameters: Various styling parameters that control the final look of the shape.
    :param states: The different UI states the shape can be in. Shapes have different surfaces for each state.
    :param manager: The UI manager.
    """

    def __init__(self, containing_rect: pygame.Rect, theming_parameters: Dict, states: List,
                 manager: UIManager):
        super().__init__(containing_rect, theming_parameters, states, manager)

        self.click_area_shape = None
        self.border_rect = None
        self.background_rect = None
        self.aligned_text_rect = None
        self.base_surface = None
        self.corner_radius = None
        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None
        self.full_rebuild_on_size_change()

    def clean_up_temp_shapes(self):
        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None

    def full_rebuild_on_size_change(self):
        # clamping border, shadow widths and corner radii so we can't form impossible shapes
        # having impossible values here will also mean the shadow pre-generating system fails leading to
        # slow down when creating elements
        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None
        if self.theming['shadow_width'] > min(math.floor(self.containing_rect.width / 2),
                                              math.floor(self.containing_rect.height / 2)):
            old_width = self.theming['shadow_width']
            self.theming['shadow_width'] = min(math.floor(self.containing_rect.width / 2),
                                               math.floor(self.containing_rect.height / 2))
            warnings.warn('Clamping shadow_width of: ' + str(old_width) + ', to: ' + str(self.theming['shadow_width']))

        if self.theming['shadow_width'] < 0:
            old_width = self.theming['shadow_width']
            self.theming['shadow_width'] = 0
            warnings.warn('Clamping shadow_width of: ' + str(old_width) + ', to: ' + str(0))

        if self.theming['border_width'] > min(math.floor((self.containing_rect.width -
                                                          (self.theming['shadow_width'] * 2)) / 2),
                                              math.floor((self.containing_rect.height -
                                                          (self.theming['shadow_width'] * 2)) / 2)):
            old_width = self.theming['border_width']
            self.theming['border_width'] = min(math.floor((self.containing_rect.width -
                                                           (self.theming['shadow_width'] * 2)) / 2),
                                               math.floor((self.containing_rect.height -
                                                           (self.theming['shadow_width'] * 2)) / 2))
            warnings.warn('Clamping border_width of: ' + str(old_width) + ', to: ' + str(self.theming['border_width']))
        if self.theming['border_width'] < 0:
            old_width = self.theming['border_width']
            self.theming['border_width'] = 0
            warnings.warn('Clamping border_width of: ' + str(old_width) + ', to: ' + str(0))

        if self.theming['shadow_width'] > 0:

            self.click_area_shape = pygame.Rect((self.containing_rect.x + self.theming['shadow_width'],
                                                 self.containing_rect.y + self.theming['shadow_width']),
                                                (self.containing_rect.width - (2 * self.theming['shadow_width']),
                                                 self.containing_rect.height - (2 * self.theming['shadow_width'])))

            corner_radius = self.theming['shape_corner_radius']
            old_radius = self.theming['shape_corner_radius']
            if corner_radius > min(self.click_area_shape.width / 2, self.click_area_shape.height / 2):
                corner_radius = int(min(self.click_area_shape.width / 2, self.click_area_shape.height / 2))
                warnings.warn('Clamping shape_corner_radius of: ' + str(old_radius) + ', to: ' + str(corner_radius))
            if corner_radius < 0:
                corner_radius = 0
                warnings.warn('Clamping shape_corner_radius of: ' + str(old_radius) + ', to: ' + str(0))
            self.corner_radius = corner_radius

            self.base_surface = self.ui_manager.get_shadow(self.containing_rect.size,
                                                           self.theming['shadow_width'],
                                                           'rectangle',
                                                           corner_radius=(self.corner_radius +
                                                                          self.theming['shadow_width']))
        else:
            self.click_area_shape = self.containing_rect.copy()

            corner_radius = self.theming['shape_corner_radius']
            if corner_radius > min(self.click_area_shape.width / 2, self.click_area_shape.height / 2):
                corner_radius = int(min(self.click_area_shape.width / 2, self.click_area_shape.height / 2))
            if corner_radius < 0:
                corner_radius = 0
            self.corner_radius = corner_radius

            self.base_surface = pygame.Surface(self.containing_rect.size, flags=pygame.SRCALPHA)

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
        Checks collision between a point and this rounded rectangle.

        :param point:
        :return: If the point is inside the shape.
        """
        collided = False
        if self.click_area_shape.collidepoint(point[0], point[1]):
            # inside shape so do more accurate collision
            # check if we are inside the body of the shape first
            center_rect = pygame.Rect(self.click_area_shape.x + self.corner_radius,
                                      self.click_area_shape.y,
                                      self.click_area_shape.width - (2 * self.corner_radius),
                                      self.click_area_shape.height)

            edge_rect_left = pygame.Rect(self.click_area_shape.x,
                                         self.click_area_shape.y + self.corner_radius,
                                         self.corner_radius,
                                         self.click_area_shape.height - (2 * self.corner_radius))

            edge_rect_right = pygame.Rect(self.click_area_shape.x + self.click_area_shape.width - self.corner_radius,
                                          self.click_area_shape.y + self.corner_radius,
                                          self.corner_radius,
                                          self.click_area_shape.height - (2 * self.corner_radius))

            # Split the collision test to test first the middle of the rectangle, then the left and right edges and
            # finally the circular corners.
            if center_rect.collidepoint(point[0], point[1]):
                collided = True
            elif edge_rect_left.collidepoint(point[0], point[1]) or edge_rect_right:
                collided = True
            else:
                point_vec = Vector2(point)
                corner_centers = [Vector2(self.click_area_shape.x + self.corner_radius,
                                          self.click_area_shape.y + self.corner_radius),
                                  Vector2(self.click_area_shape.x + self.click_area_shape.width - self.corner_radius,
                                          self.click_area_shape.y + self.corner_radius),
                                  Vector2(self.click_area_shape.x + self.click_area_shape.width - self.corner_radius,
                                          self.click_area_shape.y + self.click_area_shape.height - self.corner_radius),
                                  Vector2(self.click_area_shape.x + self.corner_radius,
                                          self.click_area_shape.y + self.click_area_shape.height - self.corner_radius)]
                corner_center_distances = [point_vec.distance_to(center) for center in corner_centers]
                for distance in corner_center_distances:
                    if distance < self.corner_radius:
                        collided = True

        return collided

    def set_position(self, point: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Move the shape. Only really impacts the position of the 'click_area' hot spot.

        :param point: The new position to move it to.
        """
        self.containing_rect.x = point[0]
        self.containing_rect.y = point[1]
        self.click_area_shape.x = point[0] + self.theming['shadow_width']
        self.click_area_shape.y = point[1] + self.theming['shadow_width']

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
            shape_id = self.shape_cache.build_cache_id('rounded_rectangle', self.containing_rect.size,
                                                       self.theming['shadow_width'],
                                                       self.theming['border_width'],
                                                       self.theming[border_colour_state_str],
                                                       self.theming[bg_colour_state_str], self.corner_radius)

            found_shape = self.shape_cache.find_surface_in_cache(shape_id)
        if found_shape is not None:
            self.surfaces[state_str] = found_shape.copy()
        else:
            corner_radius = self.corner_radius
            border_corner_radius = corner_radius

            self.surfaces[state_str] = self.base_surface.copy()

            # Try one AA call method
            aa = 4
            self.border_rect = pygame.Rect((self.theming['shadow_width'] * aa,
                                            self.theming['shadow_width'] * aa),
                                           (self.click_area_shape.width * aa, self.click_area_shape.height * aa))

            self.background_rect = pygame.Rect(((self.theming['border_width'] + self.theming['shadow_width']) * aa,
                                                (self.theming['border_width'] + self.theming['shadow_width']) * aa),
                                               (self.border_rect.width - (2 * self.theming['border_width'] * aa),
                                                self.border_rect.height - (2 * self.theming['border_width'] * aa)))

            dimension_scale = min(self.background_rect.width/self.border_rect.width,
                                  self.background_rect.height/self.border_rect.height)
            bg_corner_radius = int(border_corner_radius * dimension_scale)

            bab_surface = pygame.Surface((self.containing_rect.width * aa,
                                          self.containing_rect.height * aa), flags=pygame.SRCALPHA)
            bab_surface.fill(pygame.Color('#00000000'))
            if self.theming['border_width'] > 0:
                # If we have a border, draw it
                # Two paths here, 1. Drawing with a colour gradient or 2. With a single colour.
                if type(self.theming[border_colour_state_str]) == ColourGradient:
                    shape_surface = self.clear_and_create_shape_surface(bab_surface, self.border_rect,
                                                                        0, border_corner_radius, aa_amount=aa, clear=False)
                    self.theming[border_colour_state_str].apply_gradient_to_surface(shape_surface)
                    bab_surface.blit(shape_surface, self.border_rect)
                else:
                    shape_surface = self.clear_and_create_shape_surface(bab_surface, self.border_rect,
                                                                        0, border_corner_radius, aa_amount=aa, clear=False)
                    self.apply_colour_to_surface(self.theming[border_colour_state_str], shape_surface)
                    bab_surface.blit(shape_surface, self.border_rect)

            # Next we draw the main background colour of the shape
            # four paths here, 1. Drawing with a colour gradient 2. With a single colour.
            # 3. Drawing bars with gradients. 4. Drawing bars with single colours.
            if type(self.theming[bg_colour_state_str]) == ColourGradient:
                shape_surface = self.clear_and_create_shape_surface(bab_surface, self.background_rect,
                                                                    0, bg_corner_radius, aa_amount=aa)

                if 'filled_bar' in self.theming and 'filled_bar_width' in self.theming:
                    bar_rect = pygame.Rect((0, 0), (self.theming['filled_bar_width'] * aa, self.background_rect.height))
                    unfilled_bar_rect = pygame.Rect((self.theming['filled_bar_width'] * aa, 0),
                                                    (self.background_rect.width - (self.theming['filled_bar_width'] * aa),
                                                     self.background_rect.height))

                    if type(self.theming['filled_bar']) == ColourGradient:
                        self.theming[bg_colour_state_str].apply_gradient_to_surface(shape_surface, unfilled_bar_rect)
                        self.theming['filled_bar'].apply_gradient_to_surface(shape_surface, bar_rect)
                    else:
                        self.theming[bg_colour_state_str].apply_gradient_to_surface(shape_surface, unfilled_bar_rect)
                        self.apply_colour_to_surface(self.theming['filled_bar'], shape_surface, bar_rect)
                else:
                    self.theming[bg_colour_state_str].apply_gradient_to_surface(shape_surface)
                bab_surface.blit(shape_surface, self.background_rect)
            else:
                shape_surface = self.clear_and_create_shape_surface(bab_surface, self.background_rect,
                                                                    0, bg_corner_radius, aa_amount=aa)
                if 'filled_bar' in self.theming and 'filled_bar_width' in self.theming:
                    bar_rect = pygame.Rect((0, 0), (self.theming['filled_bar_width'] * aa, self.background_rect.height))
                    unfilled_bar_rect = pygame.Rect((self.theming['filled_bar_width'] * aa, 0),
                                                    (self.background_rect.width - (self.theming['filled_bar_width'] * aa),
                                                     self.background_rect.height))

                    if type(self.theming['filled_bar']) == ColourGradient:
                        self.apply_colour_to_surface(self.theming[bg_colour_state_str], shape_surface, unfilled_bar_rect)
                        self.theming['filled_bar'].apply_gradient_to_surface(shape_surface, bar_rect)
                    else:
                        self.apply_colour_to_surface(self.theming[bg_colour_state_str], shape_surface, unfilled_bar_rect)
                        self.apply_colour_to_surface(self.theming['filled_bar'], shape_surface, bar_rect)
                else:
                    self.apply_colour_to_surface(self.theming[bg_colour_state_str], shape_surface)
                bab_surface.blit(shape_surface, self.background_rect)

            # clear space in shadow for background
            if self.theming['shadow_width'] > 0:
                # we want our shadow clear shape to be a little bigger than the background ideally at the curvy parts
                large_sub = self.create_shadow_subtract_surface(self.border_rect.size, corner_radius * aa, aa)
                small_sub = pygame.transform.smoothscale(large_sub, self.click_area_shape.size)

                if small_sub is not None:
                    self.surfaces[state_str].blit(small_sub, (self.theming['shadow_width'],
                                                              self.theming['shadow_width']),
                                                  special_flags=pygame.BLEND_RGBA_SUB)

            # apply AA to background
            bab_surface = pygame.transform.smoothscale(bab_surface, self.containing_rect.size)
            self.surfaces[state_str].blit(bab_surface, (0, 0))

            if shape_id is not None:
                self.shape_cache.add_surface_to_cache(self.surfaces[state_str].copy(), shape_id)

        self.rebuild_images_and_text(image_state_str, state_str, text_colour_state_str)

    def clear_and_create_shape_surface(self, surface, rect, overlap, corner_radius, aa_amount, clear=True) -> pygame.Surface:
        """
        Clear a space for a new shape surface on the main state surface for this state. The surface created will be
        plain white so that it can be easily multiplied with a colour surface.

        :param surface: The surface we are working on.
        :param rect: Used to size and position the new shape.
        :param overlap: The amount of overlap between this surface and the one below.
        :param corner_radius: The radius of the rounded corners.
        :param aa_amount: The amount of Anti Aliasing to use for this shape.
        :param clear: Whether we should clear our surface.
        :return: The new shape surface.
        """

        # lock the corner radius to a maximum size of half the smallest dimension and greater than 0
        if corner_radius > min(rect.width / 2, rect.height / 2):
            corner_radius = min(rect.width / 2, rect.height / 2)
        if corner_radius < 0:
            corner_radius = 0
        large_corner_radius = corner_radius * aa_amount

        # For the visible AA shape surface we only want to blend in the alpha channel
        if self.temp_additive_shape is None:
            large_shape_surface = pygame.Surface((rect.width, rect.height), flags=pygame.SRCALPHA)
            large_shape_surface.fill(pygame.Color('#FFFFFF00'))  # was:
            RoundedRectangleShape.draw_colourless_rounded_rectangle(large_corner_radius, large_shape_surface)
            self.temp_additive_shape = large_shape_surface.copy()
        else:
            large_shape_surface = pygame.transform.scale(self.temp_additive_shape, (rect.width, rect.height))

        if clear:
            # before we draw a shape we clear a space for it, to allow for transparency.
            # This works best if we leave a small overlap between the old background and the new shape
            subtract_rect = pygame.Rect(rect.x + (overlap * aa_amount),
                                        rect.y + (overlap * aa_amount),
                                        rect.width - (2 * overlap * aa_amount),
                                        rect.height - (2 * overlap * aa_amount))

            if subtract_rect.width > 0 and subtract_rect.height > 0:
                if self.temp_subtractive_shape is None:
                    large_sub_surface = self.create_subtract_surface(subtract_rect.size,
                                                                     large_corner_radius, aa_amount)
                    self.temp_subtractive_shape = large_sub_surface
                else:
                    large_sub_surface = pygame.transform.scale(self.temp_subtractive_shape, subtract_rect.size)

                if large_sub_surface is not None:
                    surface.blit(large_sub_surface, subtract_rect, special_flags=pygame.BLEND_RGBA_SUB)

        return large_shape_surface

    def create_subtract_surface(self, subtract_size, corner_radius, aa_amount):
        if subtract_size[0] > 0 and subtract_size[1] > 0:
            if self.temp_subtractive_shape is None:
                # for the subtract surface we want to blend in all RGBA channels to clear correctly for our new shape
                self.temp_subtractive_shape = pygame.Surface(subtract_size, flags=pygame.SRCALPHA)
                self.temp_subtractive_shape.fill(pygame.Color('#00000000'))
                RoundedRectangleShape.draw_colourless_rounded_rectangle(corner_radius,
                                                                        self.temp_subtractive_shape,
                                                                        clear_colour_string='#00000000',
                                                                        corner_offset=int(aa_amount/2))
                large_sub_surface = self.temp_subtractive_shape
            else:
                large_sub_surface = pygame.transform.scale(self.temp_subtractive_shape, subtract_size)

            return large_sub_surface
        return None

    def create_shadow_subtract_surface(self, subtract_size, corner_radius, aa_amount):
        if subtract_size[0] > 0 and subtract_size[1] > 0:
            if self.temp_shadow_subtractive_shape is None:
                # for the subtract surface we want to blend in all RGBA channels to clear correctly for our new shape
                self.temp_shadow_subtractive_shape = pygame.Surface(subtract_size, flags=pygame.SRCALPHA)
                self.temp_shadow_subtractive_shape.fill(pygame.Color('#00000000'))
                RoundedRectangleShape.draw_colourless_rounded_rectangle(corner_radius,
                                                                        self.temp_shadow_subtractive_shape,
                                                                        clear_colour_string='#00000000',
                                                                        corner_offset=int(-aa_amount/4))
                large_sub_surface = self.temp_shadow_subtractive_shape
            else:
                large_sub_surface = pygame.transform.scale(self.temp_shadow_subtractive_shape, subtract_size)

            return large_sub_surface
        return None

    @staticmethod
    def draw_colourless_rounded_rectangle(large_corner_radius, large_shape_surface,
                                          clear_colour_string='#FFFFFF00', corner_offset=0):
        """
        TODO: We should be able to make this faster in Pygame 2 with the new rounded rectangle drawing functions.

        :param large_corner_radius: The radius of the corners.
        :param large_shape_surface: The surface to draw onto, the shape fills the surface.
        :return:
        """
        pygame.draw.circle(large_shape_surface, pygame.Color('#FFFFFFFF'),
                           (large_corner_radius + corner_offset,
                            large_corner_radius + corner_offset), large_corner_radius)
        if corner_offset > 0:
            large_shape_surface.fill(pygame.Color(clear_colour_string),
                                     pygame.Rect(0,
                                                 int(large_shape_surface.get_height()/2),
                                                 large_shape_surface.get_width(),
                                                 int(large_shape_surface.get_height()/2)))
            large_shape_surface.fill(pygame.Color(clear_colour_string),
                                     pygame.Rect(int(large_shape_surface.get_width() / 2),
                                                 0,
                                                 int(large_shape_surface.get_width() / 2),
                                                 large_shape_surface.get_height()))

        x_flip = pygame.transform.flip(large_shape_surface, True, False)
        large_shape_surface.blit(x_flip, (0, 0))
        y_flip = pygame.transform.flip(large_shape_surface, False, True)
        large_shape_surface.blit(y_flip, (0, 0))
        large_shape_surface.fill(pygame.Color("#FFFFFFFF"),
                                 pygame.Rect((large_corner_radius, 0),
                                             (large_shape_surface.get_width() - (2 * large_corner_radius),
                                              large_shape_surface.get_height())))
        large_shape_surface.fill(pygame.Color("#FFFFFFFF"),
                                 pygame.Rect((0, large_corner_radius),
                                             (large_shape_surface.get_width(),
                                              large_shape_surface.get_height() - (2 * large_corner_radius))))
