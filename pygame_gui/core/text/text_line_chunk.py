"""
A bit of renderable text that fits on a single line and all in the same style.

Blocks of text are made up of many text chunks. At the simplest level there would be one per line.

On creation a text chunk calculates how much space it will take up when rendered to a surface and
stores this size information in a rectangle. These rectangles can then be used in layout
calculations.

Once a layout for the text chunk is finalised the chunk's render function can be called to add the
chunk onto it's final destination.

TODO:
  - Experiment with being font type agnostic as much as possible. I have a suspicion that freetype
    font might be more useful here because of render_to() and maybe the background colour default
    but it's worth testing all these assumptions and the speed of both.
  - Do we need an intermediate type that links together - chunks, the html parser and the layout
    managers? Mainly thinking about new lines like <br> and /n. Seems unlikely so far?
  - Performance comparison tests & functionality comparison tests between current system and new.
    Need to set these up early.
"""

import pygame.freetype

from pygame.font import Font
from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect

from pygame_gui.core import ColourGradient
from pygame_gui.core.utility import render_white_text_alpha_black_bg, apply_colour_to_surface
from pygame_gui.core.utility import basic_blit


class TextLineChunkFont(TextLayoutRect):
    """
    A Text line chunk (text on the same horizontal line in the same style) using pygame's font
    module.
    """

    def __init__(self, text: str, font: Font, colour: Color, bg_colour: Color):

        dimensions = font.size(text)
        super().__init__(dimensions, can_split=True)

        self.text = text
        self.font = font
        self.colour = colour
        self.bg_color = bg_colour

        # we split text stings based on spaces
        self.split_points = [pos+1 for pos, char in enumerate(self.text) if char == ' ']

    def finalise(self, target_surface: Surface):
        surface = self.font.render(self.text, True, self.colour, self.bg_color)
        target_surface.blit(surface, self)

    def split(self, requested_x: int):
        # starting heuristic: find the percentage through the chunk width of this split request
        percentage_split = float(requested_x)/float(self.width)
        closest_split_index = int(percentage_split * len(self.split_points))

        # Now we need to search for the perfect split point
        # perfect split point is a) less than or equal requested x, b) as close to it as possible
        # because split points will be in order we can test and decided to move left or right until
        # we find the optimum point.
        current_split_point_index = closest_split_index
        tested_points = []
        valid_points = []
        found_optimum = False

        optimum_split_point = 0
        max_split_point_index = len(self.split_points) - 1

        while not found_optimum and len(self.split_points) > 0:
            optimum_split_point = self.split_points[current_split_point_index]

            if optimum_split_point in tested_points:
                # already tested this one so we must have changed direction after crossing the
                # requested_x line. the last valid point must be the optimum split point.
                if not valid_points:
                    raise RuntimeError('Unable to find valid split point for text layout')
                found_optimum = True
                optimum_split_point = valid_points[-1]
            else:
                width, _ = self.font.size(self.text[:optimum_split_point])
                if width < requested_x and current_split_point_index <= max_split_point_index:
                    # we are below the required width so we move right
                    valid_points.append(optimum_split_point)
                    if current_split_point_index < max_split_point_index:
                        current_split_point_index += 1
                elif width > requested_x and current_split_point_index > 0:
                    current_split_point_index -= 1
                elif width == requested_x:
                    # the split point is right on the requested width
                    found_optimum = True
                else:
                    # no valid point
                    found_optimum = True
                    optimum_split_point = 0
                tested_points.append(optimum_split_point)

        # What we need to consider is the case when there are no split points in a chunk and the
        # chunk is wider than the maximum width, in that case moving the chunk to the next line
        # will not work
        if optimum_split_point != 0:
            # split the text
            left_side = self.text[:optimum_split_point]
            right_side = self.text[optimum_split_point:]

            # update the data for this chunk
            self.text = left_side
            self.size = self.font.size(self.text)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return TextLineChunkFont(right_side, self.font, self.colour, self.bg_color)
        else:
            return None


class TextLineChunkFTFont(TextLayoutRect):
    """
    A Text line chunk (text on the same horizontal line in the same style) using pygame's freetype
    module.
    """

    def __init__(self, text: str,
                 font: pygame.freetype.Font,
                 line_height: int,
                 colour: Color,
                 bg_colour: Color):

        dimensions = (font.get_rect(text).width, line_height)
        super().__init__(dimensions, can_split=True)

        self.text = text
        self.font = font
        self.line_height = line_height
        self.colour = colour
        self.bg_color = bg_colour

        # we split text stings based on spaces
        self.split_points = [pos+1 for pos, char in enumerate(self.text) if char == ' ']

    def finalise(self, target_surface: Surface):

        if isinstance(self.colour, ColourGradient):
            # draw the text first
            # Anti-aliasing on text is not done with pre-multiplied alpha so we need to bake
            # this text onto a surface with a normal blit before it can enter the pre-multipled
            # blitting pipeline. This current setup may be a bit wrong but it works OK for gradients
            # on the normal text colour.
            text_surface, render_rect = self.font.render(self.text, fgcolor=Color('#FFFFFFFF'))
            self.colour.apply_gradient_to_surface(text_surface)

            # then make the background
            surface = Surface(render_rect.size, flags=pygame.SRCALPHA, depth=32)
            if isinstance(self.bg_color, ColourGradient):
                surface.fill(Color('#FFFFFFFF'))
                self.bg_color.apply_gradient_to_surface(surface)
            else:
                surface.fill(self.bg_color)

            # then apply the text to the background deliberately not pre-multiplied to bake the
            # text anti-aliasing
            surface.blit(text_surface, (0, 0))
        elif isinstance(self.bg_color, ColourGradient):
            # draw the text first
            text_surface, render_rect = self.font.render(self.text, fgcolor=self.colour)

            # then make the background
            surface = Surface(render_rect.size, flags=pygame.SRCALPHA, depth=32)
            surface.fill(Color('#FFFFFFFF'))
            self.bg_color.apply_gradient_to_surface(surface)

            # then apply the text to the background, deliberately not pre-multiplied to bake the
            # text anti-aliasing
            surface.blit(text_surface, (0, 0))
        else:

            surface, render_rect = self.font.render(self.text,
                                                    fgcolor=self.colour,
                                                    bgcolor=self.bg_color)
        # using padding on freetype fonts adds three pixels above and below
        # the ascender/descender height of the font. Not using padding shrinks
        # the bounds to the actual height of whatever letters are drawn which
        # means variable height render surface. The strategy I'm using here
        # starts with padded rects, that are at least of equal height, and
        # then removes the padding.
        render_rect.height -= 6
        render_rect.topleft = self.topleft
        target_surface.blit(surface, render_rect,
                            area=pygame.Rect((0, 3), render_rect.size),
                            special_flags=pygame.BLEND_PREMULTIPLIED)

    def split(self, requested_x: int):
        # starting heuristic: find the percentage through the chunk width of this split request
        percentage_split = float(requested_x)/float(self.width)
        closest_split_index = int(percentage_split * len(self.split_points))

        # Now we need to search for the perfect split point
        # perfect split point is a) less than or equal requested x, b) as close to it as possible
        # because split points will be in order we can test and decided to move left or right until
        # we find the optimum point.
        current_split_point_index = closest_split_index
        tested_points = []
        valid_points = []
        found_optimum = False

        optimum_split_point = 0
        max_split_point_index = len(self.split_points) - 1

        while not found_optimum and len(self.split_points) > 0:
            optimum_split_point = self.split_points[current_split_point_index]

            if optimum_split_point in tested_points:
                # already tested this one so we must have changed direction after crossing the
                # requested_x line. the last valid point must be the optimum split point.
                if not valid_points:
                    raise RuntimeError('Unable to find valid split point for text layout')
                found_optimum = True
                optimum_split_point = valid_points[-1]
            else:
                width, _ = self.font.get_rect(self.text[:optimum_split_point]).size
                if width < requested_x and current_split_point_index <= max_split_point_index:
                    # we are below the required width so we move right
                    valid_points.append(optimum_split_point)
                    if current_split_point_index < max_split_point_index:
                        current_split_point_index += 1
                elif width > requested_x and current_split_point_index > 0:
                    current_split_point_index -= 1
                elif width == requested_x:
                    # the split point is right on the requested width
                    found_optimum = True
                else:
                    # no valid point
                    found_optimum = True
                    optimum_split_point = 0
                tested_points.append(optimum_split_point)

        # What we need to consider is the case when there are no split points in a chunk and the
        # chunk is wider than the maximum width, in that case moving the chunk to the next line
        # will not work
        if optimum_split_point != 0:
            # split the text
            left_side = self.text[:optimum_split_point]
            right_side = self.text[optimum_split_point:]

            # update the data for this chunk
            self.text = left_side
            self.size = (self.font.get_rect(self.text).width, self.line_height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return TextLineChunkFTFont(right_side, self.font,
                                       self.line_height, self.colour, self.bg_color)
        else:
            return None
