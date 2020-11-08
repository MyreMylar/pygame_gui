import math
import warnings
from typing import Dict, List, Union, Tuple, Any

import pygame
from pygame.math import Vector2

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape
from pygame_gui.core.utility import apply_colour_to_surface, basic_blit
from pygame_gui.core.utility import USE_PREMULTIPLIED_ALPHA


class RoundedRectangleShape(DrawableShape):
    """
    A drawable rounded rectangle shape for the UI, has theming options for a border, a shadow,
    colour gradients and text.

    :param containing_rect: The layout rectangle that surrounds and controls the size of this shape.
    :param theming_parameters: Various styling parameters that control the final look of the shape.
    :param states: The different UI states the shape can be in. Shapes have different surfaces for
                   each state.
    :param manager: The UI manager.

    """

    def __init__(self, containing_rect: pygame.Rect,
                 theming_parameters: Dict[str, Any],
                 states: List[str],
                 manager: IUIManagerInterface):
        super().__init__(containing_rect, theming_parameters, states, manager)

        self.corner_radius = None
        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None
        self.has_been_resized = False

        self.full_rebuild_on_size_change()

    def clean_up_temp_shapes(self):
        """
        Clean up some temporary surfaces we use repeatedly when rebuilding multiple states of the
        shape but have no need of afterwards.

        """
        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None

    def full_rebuild_on_size_change(self):
        """
        Completely rebuilds the rounded rectangle shape from it's dimensions and parameters.

        Everything needs rebuilding if we change the size of the containing rectangle.

        """
        super().full_rebuild_on_size_change()

        self.temp_additive_shape = None
        self.temp_subtractive_shape = None
        self.temp_shadow_subtractive_shape = None

        # clamping border, shadow widths and corner radii so we can't form impossible shapes
        # having impossible values here will also mean the shadow pre-generating system fails
        # leading to slow down when creating elements
        if self.shadow_width > min(math.floor(self.containing_rect.width / 2),
                                   math.floor(self.containing_rect.height / 2)):
            old_width = self.shadow_width
            self.shadow_width = min(math.floor(self.containing_rect.width / 2),
                                    math.floor(self.containing_rect.height / 2))
            warnings.warn(
                'Clamping shadow_width of: ' + str(old_width) + ', to: ' + str(self.shadow_width))

        if self.shadow_width < 0:
            old_width = self.shadow_width
            self.shadow_width = 0
            warnings.warn('Clamping shadow_width of: ' + str(old_width) + ', to: ' + str(0))

        if self.border_width > min(math.floor((self.containing_rect.width -
                                               (self.shadow_width * 2)) / 2),
                                   math.floor((self.containing_rect.height -
                                               (self.shadow_width * 2)) / 2)):
            old_width = self.border_width
            self.border_width = min(math.floor((self.containing_rect.width -
                                                (self.shadow_width * 2)) / 2),
                                    math.floor((self.containing_rect.height -
                                                (self.shadow_width * 2)) / 2))
            warnings.warn('Clamping border_width of: ' +
                          str(old_width) + ', to: ' +
                          str(self.border_width))
        if self.border_width < 0:
            old_width = self.border_width
            self.border_width = 0
            warnings.warn('Clamping border_width of: ' + str(old_width) + ', to: ' + str(0))

        corner_radius = self.theming['shape_corner_radius']
        if self.shadow_width > 0:
            self.click_area_shape = pygame.Rect((self.containing_rect.x +
                                                 self.shadow_width,
                                                 self.containing_rect.y +
                                                 self.shadow_width),
                                                (self.containing_rect.width -
                                                 (2 * self.shadow_width),
                                                 self.containing_rect.height -
                                                 (2 * self.shadow_width)))

            old_radius = self.theming['shape_corner_radius']
            if corner_radius > min(self.click_area_shape.width / 2,
                                   self.click_area_shape.height / 2):
                corner_radius = int(min(self.click_area_shape.width / 2,
                                        self.click_area_shape.height / 2))
                warnings.warn('Clamping shape_corner_radius of: ' +
                              str(old_radius) + ', to: ' + str(corner_radius))
            if corner_radius < 0:
                corner_radius = 0
                warnings.warn('Clamping shape_corner_radius of: ' +
                              str(old_radius) + ', to: ' + str(0))
            self.corner_radius = corner_radius

            shadow = self.ui_manager.get_shadow(self.containing_rect.size,
                                                self.shadow_width,
                                                'rectangle',
                                                corner_radius=(self.corner_radius +
                                                               self.shadow_width))
            if shadow is not None:
                self.base_surface = shadow
            else:
                warnings.warn("shape created too small to fit in"
                              " selected shadow width and corner radius")
                self.base_surface = pygame.surface.Surface(self.containing_rect.size,
                                                           flags=pygame.SRCALPHA,
                                                           depth=32)
        else:
            self.click_area_shape = self.containing_rect.copy()

            if corner_radius > min(self.click_area_shape.width / 2,
                                   self.click_area_shape.height / 2):
                corner_radius = int(min(self.click_area_shape.width / 2,
                                        self.click_area_shape.height / 2))
            if corner_radius < 0:
                corner_radius = 0
            self.corner_radius = corner_radius

            self.base_surface = pygame.surface.Surface(self.containing_rect.size,
                                                       flags=pygame.SRCALPHA,
                                                       depth=32)

        self.border_rect = pygame.Rect((self.shadow_width,
                                        self.shadow_width),
                                       (self.click_area_shape.width, self.click_area_shape.height))

        self.background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                            self.border_width + self.shadow_width),
                                           (self.click_area_shape.width - (2 * self.border_width),
                                            self.click_area_shape.height - (2 * self.border_width)))
        self.redraw_all_states()

    def collide_point(self, point: Union[pygame.math.Vector2,
                                         Tuple[int, int],
                                         Tuple[float, float]]) -> bool:
        """
        Checks collision between a point and this rounded rectangle.

        :param point: The point to test collision with.

        :return: True, if the point is inside the shape.

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

            edge_rect_right = pygame.Rect(self.click_area_shape.x +
                                          self.click_area_shape.width -
                                          self.corner_radius,
                                          self.click_area_shape.y +
                                          self.corner_radius,
                                          self.corner_radius,
                                          self.click_area_shape.height - (2 * self.corner_radius))

            # Split the collision test to test first the middle of the rectangle, then the left and
            # right edges and finally the circular corners.
            if center_rect.collidepoint(point[0], point[1]):
                collided = True
            elif (edge_rect_left.collidepoint(point[0], point[1]) or
                  edge_rect_right.collidepoint(point[0], point[1])):
                collided = True
            else:
                point_vec = Vector2(point)
                corner_centers = [Vector2(self.click_area_shape.x +
                                          self.corner_radius,
                                          self.click_area_shape.y +
                                          self.corner_radius),
                                  Vector2(self.click_area_shape.x +
                                          self.click_area_shape.width -
                                          self.corner_radius,
                                          self.click_area_shape.y +
                                          self.corner_radius),
                                  Vector2(self.click_area_shape.x +
                                          self.click_area_shape.width -
                                          self.corner_radius,
                                          self.click_area_shape.y +
                                          self.click_area_shape.height -
                                          self.corner_radius),
                                  Vector2(self.click_area_shape.x +
                                          self.corner_radius,
                                          self.click_area_shape.y +
                                          self.click_area_shape.height -
                                          self.corner_radius)]
                corner_center_distances = [point_vec.distance_to(center)
                                           for center in corner_centers]
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
        self.click_area_shape.x = point[0] + self.shadow_width
        self.click_area_shape.y = point[1] + self.shadow_width

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Changes the size of the rounded rectangle shape. Relatively expensive to completely do so
        has support for 'temporary rapid resizing' while the dimensions are being changed
        frequently.

        :param dimensions: The new dimensions.

        """
        if (dimensions[0] == self.containing_rect.width and
                dimensions[1] == self.containing_rect.height):
            return
        self.containing_rect.width = dimensions[0]
        self.containing_rect.height = dimensions[1]
        self.click_area_shape.width = dimensions[0] - (2 * self.shadow_width)
        self.click_area_shape.height = dimensions[1] - (2 * self.shadow_width)

        if self.shadow_width > 0:
            quick_surf = self.ui_manager.get_shadow(self.containing_rect.size,
                                                    self.shadow_width,
                                                    'rectangle',
                                                    corner_radius=self.shadow_width + 2)
        else:
            quick_surf = pygame.surface.Surface(self.containing_rect.size,
                                                flags=pygame.SRCALPHA,
                                                depth=32)
            quick_surf.fill(pygame.Color('#00000000'))
        if isinstance(self.theming['normal_bg'], ColourGradient):
            grad_surf = pygame.surface.Surface(self.click_area_shape.size,
                                               flags=pygame.SRCALPHA,
                                               depth=32)
            grad_surf.fill(pygame.Color('#FFFFFFFF'))
            self.theming['normal_bg'].apply_gradient_to_surface(grad_surf)

            basic_blit(quick_surf, grad_surf,
                       pygame.Rect((self.shadow_width,
                                    self.shadow_width),
                                   self.click_area_shape.size))
        else:
            quick_surf.fill(self.theming['normal_bg'], pygame.Rect((self.shadow_width,
                                                                    self.shadow_width),
                                                                   self.click_area_shape.size))

        self.states['normal'].surface = quick_surf
        self.finalise_images_and_text('normal_image', 'normal', 'normal_text')
        self.states['normal'].has_fresh_surface = True

        self.has_been_resized = True
        self.should_trigger_full_rebuild = True
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def redraw_state(self, state_str: str):
        """
        Redraws the shape's surface for a given UI state.

        :param state_str: The ID string of the state to rebuild.

        """
        text_colour_state_str = state_str + '_text'
        image_state_str = state_str + '_image'
        bg_col = self.theming[state_str + '_bg']
        border_col = self.theming[state_str + '_border']

        found_shape = None
        shape_id = None
        if 'filled_bar' not in self.theming and 'filled_bar_width_percentage' not in self.theming:
            shape_id = self.shape_cache.build_cache_id('rounded_rectangle',
                                                       self.containing_rect.size,
                                                       self.shadow_width,
                                                       self.border_width,
                                                       border_col,
                                                       bg_col,
                                                       self.corner_radius)

            found_shape = self.shape_cache.find_surface_in_cache(shape_id)
        if found_shape is not None:
            self.states[state_str].surface = found_shape.copy()
        else:
            border_corner_radius = self.corner_radius

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

            dimension_scale = min(self.background_rect.width / max(self.border_rect.width, 1),
                                  self.background_rect.height / max(self.border_rect.height, 1))
            bg_corner_radius = int(border_corner_radius * dimension_scale)

            bab_surface = pygame.surface.Surface((self.containing_rect.width * aa_amount,
                                                  self.containing_rect.height * aa_amount),
                                                 flags=pygame.SRCALPHA, depth=32)
            bab_surface.fill(pygame.Color('#00000000'))
            if self.border_width > 0:
                shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                    self.border_rect,
                                                                    0,
                                                                    border_corner_radius,
                                                                    aa_amount=aa_amount,
                                                                    clear=False)
                if isinstance(border_col, ColourGradient):
                    border_col.apply_gradient_to_surface(shape_surface)
                else:
                    apply_colour_to_surface(border_col, shape_surface)

                basic_blit(bab_surface, shape_surface, self.border_rect)

            shape_surface = self.clear_and_create_shape_surface(bab_surface,
                                                                self.background_rect,
                                                                0,
                                                                bg_corner_radius,
                                                                aa_amount=aa_amount)

            if 'filled_bar' in self.theming and 'filled_bar_width_percentage' in self.theming:
                self._redraw_filled_bar(bg_col, shape_surface)
            else:
                if isinstance(bg_col, ColourGradient):
                    bg_col.apply_gradient_to_surface(shape_surface)
                else:
                    apply_colour_to_surface(bg_col, shape_surface)

            basic_blit(bab_surface, shape_surface, self.background_rect)

            # apply AA to background
            bab_surface = pygame.transform.smoothscale(bab_surface, self.containing_rect.size)

            basic_blit(self.states[state_str].surface, bab_surface, (0, 0))

            if self.states[state_str].cached_background_id is not None:
                cached_id = self.states[state_str].cached_background_id
                self.shape_cache.remove_user_from_cache_item(cached_id)
            if (not self.has_been_resized
                    and ((self.containing_rect.width * self.containing_rect.height) < 40000)
                    and (shape_id is not None
                         and self.states[state_str].surface.get_width() <= 1024
                         and self.states[state_str].surface.get_height() <= 1024)):
                self.shape_cache.add_surface_to_cache(self.states[state_str].surface.copy(),
                                                      shape_id)
                self.states[state_str].cached_background_id = shape_id

        self.finalise_images_and_text(image_state_str, state_str, text_colour_state_str)

        self.states[state_str].has_fresh_surface = True
        self.states[state_str].generated = True

    def _redraw_filled_bar(self,
                           bg_col: Union[pygame.Color, ColourGradient],
                           shape_surface: pygame.surface.Surface):
        """
        Draw a 'filled bar' onto our drawable shape, allows for things like loading bars,
        health bars etc.

        :param bg_col: the colour or gradient of the bar.
        :param shape_surface: the surface we are drawing on to.

        """
        filled_bar_width = int(self.background_rect.width *
                               self.theming['filled_bar_width_percentage'])
        bar_rect = pygame.Rect((0, 0), (filled_bar_width,
                                        self.background_rect.height))
        unfilled_bar_width = self.background_rect.width - filled_bar_width
        unfilled_bar_rect = pygame.Rect((filled_bar_width, 0),
                                        (unfilled_bar_width,
                                         self.background_rect.height))

        if isinstance(bg_col, ColourGradient):
            bg_col.apply_gradient_to_surface(shape_surface, unfilled_bar_rect)
        else:
            apply_colour_to_surface(bg_col, shape_surface, unfilled_bar_rect)
        if isinstance(self.theming['filled_bar'], ColourGradient):
            self.theming['filled_bar'].apply_gradient_to_surface(shape_surface, bar_rect)
        else:
            apply_colour_to_surface(self.theming['filled_bar'], shape_surface, bar_rect)

    def clear_and_create_shape_surface(self,
                                       surface: pygame.surface.Surface,
                                       rect: pygame.Rect,
                                       overlap: int,
                                       corner_radius: int,
                                       aa_amount: int,
                                       clear: bool = True) -> pygame.surface.Surface:
        """
        Clear a space for a new shape surface on the main state surface for this state. The
        surface created will be plain white so that it can be easily multiplied with a
        colour surface.

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
            large_shape_surface = pygame.surface.Surface((rect.width, rect.height),
                                                         flags=pygame.SRCALPHA, depth=32)
            clear_colour = '#00000000' if USE_PREMULTIPLIED_ALPHA else '#FFFFFF00'
            large_shape_surface.fill(pygame.Color(clear_colour))  # was:
            RoundedRectangleShape.draw_colourless_rounded_rectangle(large_corner_radius,
                                                                    large_shape_surface,
                                                                    clear_colour)
            self.temp_additive_shape = large_shape_surface.copy()
        else:
            large_shape_surface = pygame.transform.scale(self.temp_additive_shape,
                                                         (rect.width, rect.height))

        if clear:
            # before we draw a shape we clear a space for it, to allow for transparency.
            # This works best if we leave a small overlap between the old
            # background and the new shape
            subtract_rect = pygame.Rect(rect.x + (overlap * aa_amount),
                                        rect.y + (overlap * aa_amount),
                                        rect.width - (2 * overlap * aa_amount),
                                        rect.height - (2 * overlap * aa_amount))

            if subtract_rect.width > 0 and subtract_rect.height > 0:
                if self.temp_subtractive_shape is None:
                    large_sub_surface = self.create_subtract_surface(subtract_rect.size,
                                                                     large_corner_radius,
                                                                     aa_amount)
                    self.temp_subtractive_shape = large_sub_surface
                else:
                    large_sub_surface = pygame.transform.scale(self.temp_subtractive_shape,
                                                               subtract_rect.size)

                if large_sub_surface is not None:
                    surface.blit(large_sub_surface,
                                 subtract_rect,
                                 special_flags=pygame.BLEND_RGBA_SUB)

        return large_shape_surface

    def create_subtract_surface(self,
                                subtract_size: Tuple[int, int],
                                corner_radius: int,
                                aa_amount: int):
        """
        Create a rounded rectangle shaped surface that can be used to subtract everything from a
        surface to leave a transparent hole in it.

        """
        if subtract_size[0] > 0 and subtract_size[1] > 0:
            if self.temp_subtractive_shape is None:
                # for the subtract surface we want to blend in all RGBA channels to clear
                # correctly for our new shape
                self.temp_subtractive_shape = pygame.surface.Surface(subtract_size,
                                                                     flags=pygame.SRCALPHA,
                                                                     depth=32)
                self.temp_subtractive_shape.fill(pygame.Color('#00000000'))
                RoundedRectangleShape.draw_colourless_rounded_rectangle(corner_radius,
                                                                        self.temp_subtractive_shape,
                                                                        '#00000000',
                                                                        int(aa_amount / 2))
                large_sub_surface = self.temp_subtractive_shape
            else:
                large_sub_surface = pygame.transform.scale(self.temp_subtractive_shape,
                                                           subtract_size)

            return large_sub_surface
        return None

    @staticmethod
    def draw_colourless_rounded_rectangle(large_corner_radius: int,
                                          large_shape_surface: pygame.surface.Surface,
                                          clear_colour_string: str = '#00000000',
                                          corner_offset: int = 0):
        """
        Draw a rounded rectangle shape in pure white so it is ready to be multiplied by a colour
        or gradient.

        :param large_corner_radius: The radius of the corners.
        :param large_shape_surface: The surface to draw onto, the shape fills the surface.
        :param clear_colour_string: The colour to clear the background to.
        :param corner_offset: Offsets the corners, used to help avoid overlaps that look bad.

        """
        if pygame.version.vernum[0] >= 2:
            pygame.draw.rect(large_shape_surface, pygame.Color('#FFFFFFFF'),
                             pygame.Rect((corner_offset, corner_offset),
                                         (large_shape_surface.get_width() - corner_offset,
                                          large_shape_surface.get_height() - corner_offset)),
                             border_radius=large_corner_radius)
        else:
            pygame.draw.circle(large_shape_surface, pygame.Color('#FFFFFFFF'),
                               (large_corner_radius + corner_offset,
                                large_corner_radius + corner_offset), large_corner_radius)
            if corner_offset > 0:
                large_shape_surface.fill(pygame.Color(clear_colour_string),
                                         pygame.Rect(0,
                                                     int(large_shape_surface.get_height() / 2),
                                                     large_shape_surface.get_width(),
                                                     int(large_shape_surface.get_height() / 2)))
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
                                                 (large_shape_surface.get_width() -
                                                  (2 * large_corner_radius),
                                                  large_shape_surface.get_height())))
            large_shape_surface.fill(pygame.Color("#FFFFFFFF"),
                                     pygame.Rect((0, large_corner_radius),
                                                 (large_shape_surface.get_width(),
                                                  large_shape_surface.get_height() -
                                                  (2 * large_corner_radius))))
