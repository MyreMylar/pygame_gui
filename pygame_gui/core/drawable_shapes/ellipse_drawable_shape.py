import math
from typing import Dict, List, Union, Tuple, Any

import pygame

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape
from pygame_gui.core.utility import apply_colour_to_surface, basic_blit


class EllipseDrawableShape(DrawableShape):
    """
    A drawable ellipse shape for the UI, has theming options for a border, a shadow, colour
    gradients and text.

    :param containing_rect: The layout rectangle that surrounds and controls the size of this shape.
    :param theming_parameters: Various styling parameters that control the final look of the shape.
    :param states: The different UI states the shape can be in. Shapes have different surfaces
                   for each state.
    :param manager: The UI manager.

    """

    def __init__(self, containing_rect: pygame.Rect,
                 theming_parameters: Dict[str, Any],
                 states: List[str],
                 manager: IUIManagerInterface):
        super().__init__(containing_rect, theming_parameters, states, manager)

        self.ellipse_center = containing_rect.center
        self.ellipse_half_diameters = (0.5 * containing_rect.width, 0.5 * containing_rect.height)

        self.full_rebuild_on_size_change()

    def full_rebuild_on_size_change(self):
        """
        Completely redraw the shape from it's theming parameters and dimensions.

        """
        super().full_rebuild_on_size_change()
        # clamping border and shadow widths so we can't form impossible negative sized surfaces
        if self.shadow_width > min(math.floor(self.containing_rect.width / 2),
                                   math.floor(self.containing_rect.height / 2)):
            self.shadow_width = min(math.floor(self.containing_rect.width / 2),
                                    math.floor(self.containing_rect.height / 2))

        self.shadow_width = max(self.shadow_width, 0)

        if self.border_width > min(math.floor((self.containing_rect.width -
                                               (self.shadow_width * 2)) / 2),
                                   math.floor((self.containing_rect.height -
                                               (self.shadow_width * 2)) / 2)):
            self.border_width = min(math.floor((self.containing_rect.width -
                                                (self.shadow_width * 2)) / 2),
                                    math.floor((self.containing_rect.height -
                                                (self.shadow_width * 2)) / 2))

        self.border_width = max(self.border_width, 0)

        if self.shadow_width > 0:
            self.click_area_shape = pygame.Rect((self.containing_rect.x + self.shadow_width,
                                                 self.containing_rect.y + self.shadow_width),
                                                (self.containing_rect.width -
                                                 (2 * self.shadow_width),
                                                 self.containing_rect.height -
                                                 (2 * self.shadow_width)))
            self.base_surface = self.ui_manager.get_shadow(self.containing_rect.size,
                                                           self.shadow_width, 'ellipse')
        else:
            self.click_area_shape = self.containing_rect.copy()
            self.base_surface = pygame.surface.Surface(self.containing_rect.size,
                                                       flags=pygame.SRCALPHA,
                                                       depth=32)
            self.base_surface.fill(pygame.Color('#00000000'))

        self.border_rect = pygame.Rect((self.shadow_width,
                                        self.shadow_width),
                                       (self.click_area_shape.width, self.click_area_shape.height))

        self.background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                            self.border_width + self.shadow_width),
                                           (self.click_area_shape.width - (2 * self.border_width),
                                            self.click_area_shape.height - (2 * self.border_width)))
        if 'disabled' in self.states and self.active_state == self.states['disabled']:
            self.redraw_all_states(force_full_redraw=True)
        else:
            self.redraw_all_states()

    def collide_point(self, point: Union[pygame.math.Vector2,
                                         Tuple[int, int],
                                         Tuple[float, float]]) -> bool:
        """
        Checks collision between a point and this ellipse.

        :param point: The point to test against the shape.

        :return: True if the point is inside the shape.

        """
        collided = False
        x_val = ((point[0] - self.ellipse_center[0]) ** 2) / (self.ellipse_half_diameters[0] ** 2)
        y_val = ((point[1] - self.ellipse_center[1]) ** 2) / (self.ellipse_half_diameters[1] ** 2)
        if (x_val + y_val) < 1:
            collided = True

        return collided

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Expensive size change of the ellipse shape.

        :param dimensions: The new size to set the shape to.

        """
        if (dimensions[0] == self.containing_rect.width and
                dimensions[1] == self.containing_rect.height):
            return False
        self.containing_rect.width = int(dimensions[0])
        self.containing_rect.height = int(dimensions[1])
        self.click_area_shape.width = int(dimensions[0]) - (2 * self.shadow_width)
        self.click_area_shape.height = int(dimensions[1]) - (2 * self.shadow_width)

        self.ellipse_half_diameters = (0.5 * self.containing_rect.width,
                                       0.5 * self.containing_rect.height)

        self.full_rebuild_on_size_change()

        return True

    def set_position(self, point: Union[pygame.math.Vector2,
                                        Tuple[int, int],
                                        Tuple[float, float]]):
        """
        Move the shape. Only really impacts the position of the 'click_area' hot spot.

        :param point: The new position to move it to.

        """
        self.containing_rect.x = int(point[0])
        self.containing_rect.y = int(point[1])
        self.click_area_shape.x = int(point[0]) + self.shadow_width
        self.click_area_shape.y = int(point[1]) + self.shadow_width

        self.ellipse_center = self.click_area_shape.center

    def redraw_state(self, state_str: str, add_text: bool = True):
        """
        Redraws the shape's surface for a given UI state.

        :param add_text: Whether to add the text to the shape in this redraw.
        :param state_str: The ID string of the state to rebuild.

        """
        if self.containing_rect.width <= 0 or self.containing_rect.height <= 0:
            self.states[state_str] = self.ui_manager.get_universal_empty_surface()
        else:

            border_colour_state_str = state_str + '_border'
            bg_colour_state_str = state_str + '_bg'
            text_colour_state_str = state_str + '_text'
            text_shadow_colour_state_str = state_str + '_text_shadow'
            image_state_str = state_str + '_image'

            found_shape = None
            shape_id = None
            if 'filled_bar' not in self.theming and 'filled_bar_width_percentage' not in self.theming:
                shape_id = self.shape_cache.build_cache_id('ellipse',
                                                           self.containing_rect.size,
                                                           self.shadow_width,
                                                           self.border_width,
                                                           self.theming[border_colour_state_str],
                                                           self.theming[bg_colour_state_str])

                found_shape = self.shape_cache.find_surface_in_cache(shape_id)
            if found_shape is not None:
                self.states[state_str].surface = found_shape.copy()
            else:
                self.states[state_str].surface = self.base_surface.copy()

                # Try one AA call method
                aa_amount = 4
                self.border_rect = pygame.Rect((self.shadow_width * aa_amount,
                                                self.shadow_width * aa_amount),
                                               (self.click_area_shape.width * aa_amount,
                                                self.click_area_shape.height * aa_amount))

                self.background_rect = pygame.Rect(((self.border_width +
                                                     self.shadow_width) * aa_amount,
                                                    (self.border_width +
                                                     self.shadow_width) * aa_amount),
                                                   (self.border_rect.width -
                                                    (2 * self.border_width * aa_amount),
                                                    self.border_rect.height -
                                                    (2 * self.border_width * aa_amount)))

                bab_surface = pygame.surface.Surface((self.containing_rect.width * aa_amount,
                                                      self.containing_rect.height * aa_amount),
                                                     flags=pygame.SRCALPHA,
                                                     depth=32)
                bab_surface.fill(pygame.Color('#00000000'))
                if self.border_width > 0:
                    if isinstance(self.theming[border_colour_state_str], ColourGradient):
                        shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                            self.border_rect,
                                                                            0, aa_amount=aa_amount,
                                                                            clear=False)
                        self.theming[border_colour_state_str].apply_gradient_to_surface(shape_surface)
                    else:
                        shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                            self.border_rect,
                                                                            0, aa_amount=aa_amount,
                                                                            clear=False)
                        apply_colour_to_surface(self.theming[border_colour_state_str],
                                                shape_surface)
                    basic_blit(bab_surface, shape_surface, self.border_rect)
                if isinstance(self.theming[bg_colour_state_str], ColourGradient):
                    shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                        self.background_rect, 1,
                                                                        aa_amount=aa_amount)
                    self.theming[bg_colour_state_str].apply_gradient_to_surface(shape_surface)
                else:
                    shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                        self.background_rect, 1,
                                                                        aa_amount=aa_amount)
                    apply_colour_to_surface(self.theming[bg_colour_state_str], shape_surface)

                basic_blit(bab_surface, shape_surface, self.background_rect)
                # apply AA to background
                bab_surface = pygame.transform.smoothscale(bab_surface, self.containing_rect.size)

                # cut a hole in shadow, then blit background into it
                sub_surface = pygame.surface.Surface(
                    ((self.containing_rect.width - (2 * self.shadow_width)) * aa_amount,
                     (self.containing_rect.height - (2 * self.shadow_width)) * aa_amount),
                    flags=pygame.SRCALPHA, depth=32)
                sub_surface.fill(pygame.Color('#00000000'))
                pygame.draw.ellipse(sub_surface, pygame.Color("#FFFFFFFF"), sub_surface.get_rect())
                small_sub = pygame.transform.smoothscale(sub_surface,
                                                         (self.containing_rect.width -
                                                          (2 * self.shadow_width),
                                                          self.containing_rect.height -
                                                          (2 * self.shadow_width)))
                self.states[state_str].surface.blit(small_sub, pygame.Rect((self.shadow_width,
                                                                            self.shadow_width),
                                                                           sub_surface.get_size()),
                                                    special_flags=pygame.BLEND_RGBA_SUB)
                basic_blit(self.states[state_str].surface, bab_surface, (0, 0))

                if (shape_id is not None and
                        self.states[state_str].surface.get_width() <= 1024 and
                        self.states[state_str].surface.get_height() <= 1024):
                    self.shape_cache.add_surface_to_cache(self.states[state_str].surface.copy(),
                                                          shape_id)

            self.finalise_images_and_text(image_state_str, state_str,
                                          text_colour_state_str,
                                          text_shadow_colour_state_str,
                                          add_text)

        self.states[state_str].has_fresh_surface = True
        self.states[state_str].generated = True

    @staticmethod
    def clear_and_create_shape_surface(surface: pygame.surface.Surface,
                                       rect: pygame.Rect,
                                       overlap: int,
                                       aa_amount: int,
                                       clear: bool = True) -> pygame.surface.Surface:
        """
        Clear a space for a new shape surface on the main state surface for this state. The
        surface created will be plain white so that it can be easily multiplied with a colour
        surface.

        :param surface: The surface we are working on.
        :param rect: Used to size and position the new shape.
        :param overlap: The amount of overlap between this surface and the one below.
        :param aa_amount: The amount of Anti Aliasing to use for this shape.
        :param clear: Whether we should clear our surface.

        :return: The new shape surface.

        """

        # For the visible AA shape surface we only want to blend in the alpha channel
        large_shape_surface = pygame.surface.Surface((rect.width, rect.height),
                                                     flags=pygame.SRCALPHA,
                                                     depth=32)
        large_shape_surface.fill(pygame.Color('#00000000'))
        pygame.draw.ellipse(large_shape_surface, pygame.Color("#FFFFFFFF"),
                            large_shape_surface.get_rect())

        if clear:
            # before we draw a shape we clear a space for it, to allow for transparency.
            # This works best if we leave a small overlap between the old background
            # and the new shape
            subtract_rect = pygame.Rect(rect.x + (overlap * aa_amount),
                                        rect.y + (overlap * aa_amount),
                                        max(0, rect.width - 2 * (overlap * aa_amount)),
                                        max(0, rect.height - 2 * (overlap * aa_amount)))
            # for the subtract surface we want to blend in all RGBA channels to clear correctly
            # for our new shape
            large_sub_surface = pygame.surface.Surface((subtract_rect.width,
                                                        subtract_rect.height),
                                                       flags=pygame.SRCALPHA, depth=32)
            large_sub_surface.fill(pygame.Color('#00000000'))
            pygame.draw.ellipse(large_sub_surface, pygame.Color("#FFFFFFFF"),
                                large_sub_surface.get_rect())

            surface.blit(large_sub_surface, subtract_rect, special_flags=pygame.BLEND_RGBA_SUB)
        return large_shape_surface
