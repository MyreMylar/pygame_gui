import pygame
from typing import Tuple, Union
import warnings


class ShadowGenerator:
    """
    A class to generate surfaces that work as a 'shadow' for rectangular UI elements. Base shadow surface are generated
    with an algorithm, then when one is requested at a specific size the closest pre-generated shadow surface is
    picked and then scaled to the exact size requested.

    By default it creates a four base shadows in a small range of sizes. If you find the shadow appearance
    unsatisfactory then it is possible to create more closer to the size of the elements you are having trouble with.
    """

    def __init__(self):
        self.created_rectangle_shadows = {}
        self.created_ellipse_shadows = {}
        self.preloaded_shadow_corners = {}

    def shadow_edges_and_corners_to_preload(self, list_of_corners, list_of_edges):
        # corners = {corner_radius: 10, shadow_width: 10}
        pass

    def create_shadow_corners(self, shadow_width_param, corner_radius_param, aa_amount=4):

        if shadow_width_param <= 0:
            shadow_width_param = 1
            warnings.warn("Tried to make shadow with width <= 0")
        final_corner_surface = pygame.Surface((corner_radius_param * aa_amount,
                                               corner_radius_param * aa_amount),
                                              flags=pygame.SRCALPHA, depth=32)
        final_corner_surface.fill(pygame.Color('#00000000'))

        final_edge_surface = pygame.Surface((shadow_width_param * aa_amount,
                                             shadow_width_param * aa_amount),
                                            flags=pygame.SRCALPHA, depth=32)
        final_edge_surface.fill(pygame.Color('#00000000'))

        alpha_increment = 20.0 / (shadow_width_param ** 1.5)
        shadow_alpha = alpha_increment

        corner_shadow_width = corner_radius_param * aa_amount
        corner_shadow_height = corner_radius_param * aa_amount
        corner_radius = corner_radius_param * aa_amount
        corner_center = (corner_radius, corner_radius)

        edge_shadow_width = shadow_width_param * aa_amount
        edge_shadow_height = shadow_width_param * aa_amount
        edge_shadow_fade_height = edge_shadow_width

        for i in range(0, shadow_width_param):
            if corner_shadow_width > 0 and corner_shadow_height > 0 and corner_radius > 0:
                # Edge
                edge_shadow_rect = pygame.Rect(0, 0, edge_shadow_width, edge_shadow_height)
                edge_shadow_surface = pygame.Surface(edge_shadow_rect.size, flags=pygame.SRCALPHA, depth=32)
                edge_shadow_surface.fill(pygame.Color('#00000000'))

                edge_shadow_surface.fill(pygame.Color(0, 0, 0, int(shadow_alpha)),
                                         pygame.Rect(0, edge_shadow_height - edge_shadow_fade_height,
                                                     edge_shadow_width,
                                                     edge_shadow_fade_height))

                final_edge_surface.blit(edge_shadow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

                # corner
                corner_shadow_rect = pygame.Rect(0, 0, corner_shadow_width, corner_shadow_height)
                corner_shadow_surface = pygame.Surface(corner_shadow_rect.size, flags=pygame.SRCALPHA, depth=32)
                corner_shadow_surface.fill(pygame.Color('#00000000'))

                pygame.draw.circle(corner_shadow_surface, pygame.Color(0, 0, 0, int(shadow_alpha)),
                                   corner_center,
                                   corner_radius)

                final_corner_surface.blit(corner_shadow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

                # increments/decrements
                shadow_alpha += alpha_increment
                corner_radius -= aa_amount
                edge_shadow_fade_height -= aa_amount

        top_edge = pygame.transform.smoothscale(final_edge_surface, (shadow_width_param, shadow_width_param))
        bottom_edge = pygame.transform.flip(top_edge, False, True)
        left_edge = pygame.transform.rotate(top_edge, 90)
        right_edge = pygame.transform.flip(left_edge, True, False)

        tl_corner = pygame.transform.smoothscale(final_corner_surface, (corner_radius_param, corner_radius_param))
        tr_corner = pygame.transform.flip(tl_corner, True, False)
        bl_corner = pygame.transform.flip(tl_corner, False, True)
        br_corner = pygame.transform.flip(tl_corner, True, True)

        corners_and_edges = {"top": top_edge,
                             "bottom": bottom_edge,
                             "left": left_edge,
                             "right": right_edge,
                             "top_left": tl_corner,
                             "top_right": tr_corner,
                             "bottom_left": bl_corner,
                             "bottom_right": br_corner}
        self.preloaded_shadow_corners[str(shadow_width_param) + 'x' + str(corner_radius_param)] = corners_and_edges

        return corners_and_edges

    def create_new_rectangle_shadow(self, width: int, height: int,
                                    shadow_width_param: int, corner_radius_param: int, ):
        """
        Creates a rectangular shadow surface at the specified size and stores it for later use.

        :param width: The width of the base shadow to create.
        :param height: The height of the base shadow to create.
        :param shadow_width_param: The width of the shadowed edge.
        :param corner_radius_param: The radius of the rectangular shadow's corners.
        """

        if width >= corner_radius_param and height >= corner_radius_param:
            final_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA, depth=32)

            corner_index_id = str(shadow_width_param) + 'x' + str(corner_radius_param)
            if corner_index_id in self.preloaded_shadow_corners:
                edges_and_corners = self.preloaded_shadow_corners[corner_index_id]
            else:
                edges_and_corners = self.create_shadow_corners(shadow_width_param, corner_radius_param)

            final_surface.blit(edges_and_corners["top_left"], (0, 0))
            final_surface.blit(edges_and_corners["top_right"], (width - corner_radius_param, 0))

            final_surface.blit(edges_and_corners["bottom_left"],
                               (0, height - corner_radius_param))
            final_surface.blit(edges_and_corners["bottom_right"],
                               (width - corner_radius_param, height - corner_radius_param))

            if width - (2 * corner_radius_param) > 0:
                top_edge = pygame.transform.scale(edges_and_corners["top"],
                                                  (width - (2 * corner_radius_param), shadow_width_param))
                bottom_edge = pygame.transform.scale(edges_and_corners["bottom"],
                                                     (width - (2 * corner_radius_param), shadow_width_param))
                final_surface.blit(top_edge, (corner_radius_param, 0))
                final_surface.blit(bottom_edge, (corner_radius_param, height - shadow_width_param))

            if height - (2 * corner_radius_param) > 0:
                left_edge = pygame.transform.scale(edges_and_corners["left"],
                                                   (shadow_width_param, height - (2 * corner_radius_param)))
                right_edge = pygame.transform.scale(edges_and_corners["right"],
                                                    (shadow_width_param, height - (2 * corner_radius_param)))

                final_surface.blit(left_edge, (0, corner_radius_param))
                final_surface.blit(right_edge, (width - shadow_width_param, corner_radius_param))

            self.created_rectangle_shadows[str(width) + 'x' + str(height) +
                                           'x' + str(corner_radius_param) + 'x' + str(shadow_width_param)] = final_surface
            return final_surface
        else:
            return None

    def create_new_ellipse_shadow(self, width: int, height: int, shadow_width_param: int, aa_amount: int = 4):
        """
        Creates a ellipse shaped shadow surface at the specified size and stores it for later use.

        :param width: The width of the shadow to create.
        :param height: The height of the shadow to create.
        :param shadow_width_param: The width of the shadowed edge.
        :param aa_amount: The amount of anti-aliasing to use, defaults to 4.
        """
        shadow_surface = pygame.Surface((width * aa_amount, height * aa_amount), flags=pygame.SRCALPHA, depth=32)
        shadow_surface.fill(pygame.Color('#00000000'))

        alpha_increment = max(1, int(20 / shadow_width_param))
        shadow_alpha = alpha_increment
        shadow_width = width * aa_amount
        shadow_height = height * aa_amount
        for i in range(0, shadow_width_param):
            if shadow_width > 0 and shadow_height > 0:
                shadow_rect = pygame.Rect(i * aa_amount, i * aa_amount, shadow_width, shadow_height)
                pygame.draw.ellipse(shadow_surface, pygame.Color(0, 0, 0, shadow_alpha), shadow_rect)
                shadow_width -= (2 * aa_amount)
                shadow_height -= (2 * aa_amount)
                shadow_alpha += alpha_increment

        final_surface = pygame.transform.smoothscale(shadow_surface, (width, height))
        self.created_ellipse_shadows[str(width) + 'x' + str(height) + 'x' + str(shadow_width_param)] = final_surface
        return final_surface

    def find_closest_shadow_scale_to_size(self, size: Tuple[int, int],
                                          shadow_width: int = 2,
                                          shape: str = "rectangle",
                                          corner_radius: int = 2) -> Union[pygame.Surface, None]:
        """
        This function searches through our dictionary of created shadows, grabs the closest one to the size
        we request and then scales that shadow to the exact size we need.



        :param size: The size of the element we are finding a shadow for.
        :param shadow_width: The width of the shadow to find.
        :param shape: The shape of the shadow to find.
        :param corner_radius: The radius of the corners if this is a rectangular shadow.
        :return: The shadow surface we asked for scaled to the size we requested, or None if no shadows exist.
        """
        lowest_diff = 1000000000000
        closest_key = None
        if shape == 'rectangle':
            for key in self.created_rectangle_shadows.keys():
                dimension_strings = key.split('x')
                width = int(dimension_strings[0])
                height = int(dimension_strings[1])
                corner_rad = int(dimension_strings[2])
                shadow_size = int(dimension_strings[3])

                key_aspect_ratio = float(width / height)
                request_aspect_ratio = float(size[0] / size[1])
                ratio_diff = abs(key_aspect_ratio - request_aspect_ratio)
                width_diff = abs(width - size[0])
                height_diff = abs(height - size[1])
                corner_diff = abs(corner_rad - corner_radius)
                shadow_diff = abs(shadow_size - shadow_width)
                total_diff = width_diff + height_diff + shadow_diff + corner_diff + ratio_diff
                if corner_diff < 2 and shadow_diff < 2 and ratio_diff < 0.75 and total_diff < lowest_diff:
                    lowest_diff = total_diff
                    closest_key = key

            if closest_key is not None:
                return pygame.transform.smoothscale(self.created_rectangle_shadows[closest_key], size)
            else:
                return self.create_new_rectangle_shadow(size[0], size[1], shadow_width, corner_radius)

        if shape == 'ellipse':
            for key in self.created_ellipse_shadows.keys():
                dimension_strings = key.split('x')
                width = int(dimension_strings[0])
                height = int(dimension_strings[1])
                shadow_size = int(dimension_strings[2])

                width_diff = abs(width - size[0])
                height_diff = abs(height - size[1])
                ratio_diff = max(width_diff, height_diff)
                shadow_diff = abs(shadow_size - shadow_width) * 50
                total_diff = width_diff + height_diff + shadow_diff
                if total_diff < lowest_diff:
                    lowest_diff = total_diff
                    if ratio_diff < 10:
                        closest_key = key

            if closest_key is not None:
                return pygame.transform.smoothscale(self.created_ellipse_shadows[closest_key], size)
            else:
                return self.create_new_ellipse_shadow(size[0], size[1], shadow_width)

        return None
