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
from typing import Optional, Union, Tuple

import pygame.freetype

from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core import ColourGradient


class TextLineChunkFTFont(TextLayoutRect):
    """
    A Text line chunk (text on the same horizontal line in the same style) using pygame's freetype
    module.
    """

    def __init__(self, text: str,
                 font: pygame.freetype.Font,
                 underlined: bool,
                 text_height: int,
                 line_spacing: float,
                 colour: Color,
                 bg_colour: Color,
                 text_shadow_data: Optional[Tuple[int, int, int, pygame.Color]] = None):

        text_rect = font.get_rect(text)
        dimensions = (text_rect.x + text_rect.width, int(round(text_height * line_spacing)))
        super().__init__(dimensions, can_split=True)

        self.text = text
        self.font = font
        self.underlined = underlined
        self.colour = colour
        self.bg_colour = bg_colour
        self.target_surface = None
        self.text_height = text_height
        self.line_spacing = line_spacing
        self.y_origin = (self.text_height + (self.font.get_sized_descender() + 1))
        self.text_shadow_data = text_shadow_data

        # we split text stings based on spaces
        self.split_points = [pos+1 for pos, char in enumerate(self.text) if char == ' ']
        self.letter_count = len(self.text)

    def style_match(self, other_text_chunk: 'TextLineChunkFTFont'):
        """
        Do two layout rectangles have matching styles (generally applies only to actual text).
        """
        match_fonts = self.font == other_text_chunk.font
        match_underlined = self.underlined == other_text_chunk.underlined
        match_colour = self.colour == other_text_chunk.colour
        match_bg_color = self.bg_colour == other_text_chunk.bg_colour

        return match_fonts and match_underlined and match_colour and match_bg_color

    def finalise(self,
                 target_surface: Surface,
                 row_origin: int,
                 row_height: int,
                 letter_end: Optional[int] = None):

        final_str_text = self.text if letter_end is None else self.text[:letter_end]
        # update chunk width for drawing only, need to include the text origin offset
        # to make the surface wide enough
        draw_text_rect = self.font.get_rect(final_str_text)
        chunk_draw_width = draw_text_rect.x + draw_text_rect.width
        chunk_draw_height = int(round(row_height/self.line_spacing))
        chunk_x_origin = 0
        if self.text_shadow_data is not None and self.text_shadow_data[0] != 0:
            # expand our text chunk if we have a text shadow
            chunk_x_origin += self.text_shadow_data[0]
            chunk_draw_width += (self.text_shadow_data[0] * 2)
            chunk_draw_height += (self.text_shadow_data[0] * 2)

        self.font.underline = self.underlined  # set underlined state
        if self.underlined:
            self.font.underline_adjustment = 0.5
        if isinstance(self.colour, ColourGradient):
            # draw the text first
            # Anti-aliasing on text is not done with pre-multiplied alpha so we need to bake
            # this text onto a surface with a normal blit before it can enter the pre-multipled
            # blitting pipeline. This current setup may be a bit wrong but it works OK for gradients
            # on the normal text colour.

            text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                          flags=pygame.SRCALPHA, depth=32)

            self.font.render_to(text_surface, (chunk_x_origin, row_origin),
                                final_str_text, fgcolor=Color('#FFFFFFFF'))
            self.colour.apply_gradient_to_surface(text_surface)

            # then make the background
            surface = Surface((chunk_draw_width, row_height), flags=pygame.SRCALPHA, depth=32)
            if isinstance(self.bg_colour, ColourGradient):
                surface.fill(Color('#FFFFFFFF'))
                self.bg_colour.apply_gradient_to_surface(surface)
            else:
                surface.fill(self.bg_colour)

            # center the text in the line
            text_rect = text_surface.get_rect()
            text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self.apply_shadow_effect(surface, text_rect, final_str_text, text_surface, (chunk_x_origin, row_origin))

            # then apply the text to the background deliberately not pre-multiplied
            # to bake the text anti-aliasing,
            surface.blit(text_surface, text_rect)

        elif isinstance(self.bg_colour, ColourGradient):
            # draw the text first
            text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                          flags=pygame.SRCALPHA, depth=32)

            self.font.render_to(text_surface, (chunk_x_origin, row_origin),
                                final_str_text, fgcolor=self.colour)

            # then make the background
            surface = Surface((chunk_draw_width, row_height),
                              flags=pygame.SRCALPHA, depth=32)
            surface.fill(Color('#FFFFFFFF'))
            self.bg_colour.apply_gradient_to_surface(surface)

            # center the text in the line
            text_rect = text_surface.get_rect()
            text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self.apply_shadow_effect(surface, text_rect, final_str_text, text_surface, (chunk_x_origin, row_origin))

            # then apply the text to the background deliberately not pre-multiplied
            # to bake the text anti-aliasing,
            surface.blit(text_surface, text_rect)
        else:
            text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                          flags=pygame.SRCALPHA, depth=32)
            self.font.render_to(text_surface, (chunk_x_origin, row_origin),
                                final_str_text,
                                fgcolor=self.colour)

            surface = Surface((chunk_draw_width, row_height), flags=pygame.SRCALPHA, depth=32)
            surface.fill(self.bg_colour)

            # center the text in the line
            text_rect = text_surface.get_rect()
            text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self.apply_shadow_effect(surface, text_rect, final_str_text, text_surface, (chunk_x_origin, row_origin))

            # then apply the text to the background deliberately not pre-multiplied
            # to bake the text anti-aliasing,
            surface.blit(text_surface, text_rect)

        target_surface.blit(surface, self.topleft,
                            special_flags=pygame.BLEND_PREMULTIPLIED)
        self.target_surface = target_surface

    def apply_shadow_effect(self, surface, text_rect, text_str, text_surface, origin):
        if self.text_shadow_data is not None and self.text_shadow_data[0] != 0:

            shadow_size = self.text_shadow_data[0]
            shadow_offset = (self.text_shadow_data[1], self.text_shadow_data[2])
            shadow_colour = self.text_shadow_data[3]
            # we have a shadow
            shadow_surface = text_surface.copy()
            shadow_surface.fill('#00000000')
            shadow_rect = text_rect.copy()
            self.font.render_to(shadow_surface, origin,
                                text_str,
                                fgcolor=shadow_colour)

            for y_pos in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_rect.x + shadow_offset[0],
                                                text_rect.y + shadow_offset[1]
                                                + y_pos),
                                               text_rect.size)

                surface.blit(shadow_surface, shadow_text_rect)
            for x_pos in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_rect.x + shadow_offset[0]
                                                + x_pos,
                                                text_rect.y + shadow_offset[1]),
                                               text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect)
            for x_and_y in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_rect.x + shadow_offset[0] + x_and_y,
                     text_rect.y + shadow_offset[1] + x_and_y),
                    text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect)
            for x_and_y in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_rect.x + shadow_offset[0] - x_and_y,
                     text_rect.y + shadow_offset[1] + x_and_y),
                    text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect)

    def split(self, requested_x: int, line_width: int) -> Union['TextLayoutRect', None]:
        # starting heuristic: find the percentage through the chunk width of this split request
        percentage_split = float(requested_x)/float(self.width)

        # Now we need to search for the perfect split point
        # perfect split point is a) less than or equal requested x, b) as close to it as possible
        # because split points will be in order we can test and decided to move left or right until
        # we find the optimum point.
        current_split_point_index = int(percentage_split *
                                        len(self.split_points))  # start with approximate position
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

        split_text_ok = False
        if optimum_split_point != 0:
            # split the text
            left_side = self.text[:optimum_split_point]
            right_side = self.text[optimum_split_point:]
            split_text_ok = True

        elif self.x == 0 and self.width > line_width:
            # we have a chunk with no breaks (one long word usually) longer than a line
            # split it at the word
            optimum_split_point = max(0, int(percentage_split * len(self.text)) - 1)
            if optimum_split_point != 0:
                left_side = self.text[:optimum_split_point] + '-'
                right_side = '-' + self.text[optimum_split_point:]
                split_text_ok = True
            else:
                raise ValueError('line width too small')

        if split_text_ok:
            # update the data for this chunk
            self.text = left_side
            self.letter_count = len(self.text)
            self.size = (self.font.get_rect(self.text).width, self.height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return self._split_at(right_side)
        else:
            return None

    def _split_at(self, right_side):
        return TextLineChunkFTFont(right_side, self.font, self.underlined,
                                   self.text_height, self.line_spacing,
                                   self.colour,
                                   self.bg_colour,
                                   self.text_shadow_data)

    def clear(self):
        if self.target_surface is not None:
            self.target_surface.fill(pygame.Color('#00000000'), self)

    def insert_text(self, input_text: str, index: int):
        """
        Insert a new string of text into this chunk and update the chunk's data.

        NOTE: We don't redraw the text immediately here as this size of this chunk
        changing may affect the position of other chunks later in the layout.

        :param input_text: the new text to insert.
        :param index: the index we are sticking the new text at.
        """
        self.clear()
        self.text = self.text[:index] + input_text + self.text[index:]
        # we split text stings based on spaces
        self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']
        self.letter_count = len(self.text)

        self.size = (self.font.get_rect(self.text).width, self.height) # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
