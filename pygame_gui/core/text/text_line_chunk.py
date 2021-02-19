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
                 colour: Union[Color, ColourGradient],
                 using_default_text_colour: bool,
                 bg_colour: Union[Color, ColourGradient],
                 text_shadow_data: Optional[Tuple[int, int, int, pygame.Color, bool]] = None,
                 max_dimensions: Optional[Tuple[int, int]] = None):
        if len(text) == 0:
            text_rect = font.get_rect('A')
        else:
            text_rect = font.get_rect(text)
        text_width = sum([char_metric[4] for char_metric in font.get_metrics(text)])
        text_height = text_rect.height
        if max_dimensions is not None:
            if max_dimensions[0] != -1:
                text_width = min(max_dimensions[0], text_width)
            if max_dimensions[1] != -1:
                text_height = min(max_dimensions[1], text_height)
        super().__init__((text_width, text_height), can_split=True)

        self.text = text

        # style that needs to be matched to merge or insert chunks (are those basically the same operation?)
        self.font = font
        self.underlined = underlined
        self.colour = colour
        self.shadow_colour = pygame.Color('#000000')
        self.using_default_text_colour = using_default_text_colour
        self.using_default_text_shadow_colour = False
        self.bg_colour = bg_colour
        self.text_shadow_data = text_shadow_data
        if self.text_shadow_data is not None:
            self.using_default_text_shadow_colour = self.text_shadow_data[4]
            self.shadow_colour = self.text_shadow_data[3]

        self.max_dimensions = max_dimensions
        self.y_origin = text_rect.y
        self.font_y_padding = self._calc_font_padding()

        # we split text stings based on spaces, these variables need recalculating when splitting or merging chunks
        self.split_points = [pos+1 for pos, char in enumerate(self.text) if char == ' ']
        self.letter_count = len(self.text)

        self.target_surface = None
        self.target_surface_area = None
        self.row_chunk_origin = 0
        self.row_chunk_height = 0
        self.row_bg_height = 0
        self.layout_x_offset = 0
        self.letter_end = 0

        self.is_selected = False
        self.is_active = False
        self.selection_colour = pygame.Color(128, 128, 128, 255)

        self.should_centre_from_baseline = False

    def _calc_font_padding(self):
        # 'font padding' this determines the amount of padding that font.pad adds to the top of text excluding
        # any padding added to make glyphs even - this is useful for 'base-line centering' when we want to center text
        # that doesn't drop below the base line (no y's, g's, p's etc) but also don't want it to flicker on and off.
        # base-line centering is the default for chunks on a single style row.
        padding_state = self.font.pad

        self.font.pad = False
        no_pad_origin = self.font.get_rect('A').y

        self.font.pad = True
        pad_origin = self.font.get_rect('A').y

        self.font.pad = padding_state
        return pad_origin - no_pad_origin

    def style_match(self, other_text_chunk: 'TextLineChunkFTFont'):
        """
        Do two layout rectangles have matching styles (generally applies only to actual text).
        """
        match_fonts = self.font == other_text_chunk.font
        match_underlined = self.underlined == other_text_chunk.underlined
        match_colour = self.colour == other_text_chunk.colour
        match_bg_color = self.bg_colour == other_text_chunk.bg_colour
        match_shadow_data = self.text_shadow_data == other_text_chunk.text_shadow_data
        match_selected = self.is_selected == other_text_chunk.is_selected
        match_active = self.is_active == other_text_chunk.is_active

        return (match_fonts and match_underlined and match_colour and
                match_bg_color and match_shadow_data and match_selected and match_active)

    def finalise(self,
                 target_surface: Surface,
                 target_area: pygame.Rect,
                 row_chunk_origin: int,
                 row_chunk_height: int,
                 row_bg_height: int,
                 x_scroll_offset: int,
                 letter_end: Optional[int] = None):

        if self.is_selected:
            bg_col = self.selection_colour
        else:
            bg_col = self.bg_colour

        final_str_text = self.text if letter_end is None else self.text[:letter_end]
        # update chunk width for drawing only, need to include the text origin offset
        # to make the surface wide enough
        chunk_draw_width = sum([char_metric[4] for char_metric in self.font.get_metrics(final_str_text)])
        chunk_draw_height = row_chunk_height
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
            if pygame.version.vernum[0] >= 2:
                # This is a hacky way to convert text to pre-multiplied alpha with a SDL2 alpha blit
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                temp_text_surface = text_surface.copy()

                self.font.render_to(temp_text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=Color('#FFFFFFFF'))
                text_surface.blit(temp_text_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            else:
                # pygame 1 version is a bit rubbish
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                text_surface.fill((0, 0, 0, 1))
                self.font.render_to(text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=Color('#FFFFFFFF'))
            self.colour.apply_gradient_to_surface(text_surface)

            # then make the background
            surface = Surface((chunk_draw_width, row_bg_height), flags=pygame.SRCALPHA, depth=32)

            if isinstance(bg_col, ColourGradient):
                surface.fill(Color('#FFFFFFFF'))
                bg_col.apply_gradient_to_surface(surface)
            else:
                surface.fill(bg_col)

            # center the text in the line
            text_rect = text_surface.get_rect()
            if self.should_centre_from_baseline:
                padless_origin = self.y_origin - self.font_y_padding
                half_padless_origin = int(round(0.5 * padless_origin))
                text_rect.y = surface.get_rect().centery - self.font_y_padding - half_padless_origin
            else:
                text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self._apply_shadow_effect(surface, text_rect, final_str_text,
                                      text_surface, (chunk_x_origin, row_chunk_origin))

            surface.blit(text_surface, text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)

        elif isinstance(bg_col, ColourGradient):
            # draw the text first
            if pygame.version.vernum[0] >= 2:
                # This is a hacky way to convert text to pre-multiplied alpha with a SDL2 alpha blit
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                temp_text_surface = text_surface.copy()

                self.font.render_to(temp_text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=self.colour)
                text_surface.blit(temp_text_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            else:
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                text_surface.fill((0, 0, 0, 1))
                self.font.render_to(text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=self.colour)

            # then make the background
            surface = Surface((chunk_draw_width, row_bg_height),
                              flags=pygame.SRCALPHA, depth=32)
            surface.fill(Color('#FFFFFFFF'))
            bg_col.apply_gradient_to_surface(surface)

            # center the text in the line
            text_rect = text_surface.get_rect()
            if self.should_centre_from_baseline:
                padless_origin = self.y_origin - self.font_y_padding
                half_padless_origin = int(round(0.5 * padless_origin))
                text_rect.y = surface.get_rect().centery - self.font_y_padding - half_padless_origin
            else:
                text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self._apply_shadow_effect(surface, text_rect, final_str_text,
                                      text_surface, (chunk_x_origin, row_chunk_origin))

            surface.blit(text_surface, text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)
        else:
            if pygame.version.vernum[0] >= 2:
                # This is a hacky way to convert text to pre-multiplied alpha with a SDL2 alpha blit
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                temp_text_surface = text_surface.copy()

                self.font.render_to(temp_text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=self.colour)
                text_surface.blit(temp_text_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            else:
                text_surface = pygame.Surface((chunk_draw_width, chunk_draw_height),
                                              flags=pygame.SRCALPHA, depth=32)
                text_surface.fill((0, 0, 0, 1))
                self.font.render_to(text_surface, (chunk_x_origin, row_chunk_origin),
                                    final_str_text, fgcolor=self.colour)

            surface = Surface((chunk_draw_width, row_bg_height), flags=pygame.SRCALPHA, depth=32)
            surface.fill(bg_col)

            # center the text in the line
            text_rect = text_surface.get_rect()
            if self.should_centre_from_baseline:
                padless_origin = self.y_origin - self.font_y_padding
                half_padless_origin = int(round(0.5 * padless_origin))
                text_rect.y = surface.get_rect().centery - self.font_y_padding - half_padless_origin
            else:
                text_rect.centery = surface.get_rect().centery

            # apply any shadow effects
            self._apply_shadow_effect(surface, text_rect, final_str_text,
                                      text_surface, (chunk_x_origin, row_chunk_origin))

            surface.blit(text_surface, text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)

        # sort out horizontal scrolling
        final_pos = (max(target_area.left, self.left - x_scroll_offset), self.top)

        distance_to_lhs_overlap = self.left - target_area.left
        lhs_overlap = max(0, x_scroll_offset - distance_to_lhs_overlap)

        remaining_rhs_space = target_area.width - (final_pos[0] - target_area.left)
        rhs_overlap = max(0, ((self.width - lhs_overlap) - remaining_rhs_space))

        target_width = (self.width - lhs_overlap) - rhs_overlap

        final_target = pygame.Rect(lhs_overlap,
                                   target_area.top,
                                   min(target_width, target_area.width),  # we only want to grab as much as we can show
                                   target_area.height)

        if target_width > 0:
            target_surface.blit(surface, final_pos, area=final_target, special_flags=pygame.BLEND_PREMULTIPLIED)

        # In case we need to redraw this chunk, keep hold of the input parameters
        self.target_surface = target_surface
        self.target_surface_area = target_area
        self.row_chunk_origin = row_chunk_origin
        self.row_chunk_height = row_chunk_height
        self.row_bg_height = row_bg_height
        self.layout_x_offset = x_scroll_offset
        self.letter_end = letter_end

    def _apply_shadow_effect(self, surface, text_rect, text_str, text_surface, origin):
        if self.text_shadow_data is not None and self.text_shadow_data[0] != 0:

            shadow_size = self.text_shadow_data[0]
            shadow_offset = (self.text_shadow_data[1], self.text_shadow_data[2])
            shadow_colour = self.shadow_colour
            # we have a shadow
            if pygame.version.vernum[0] >= 2:
                # This is a hacky way to convert text to pre-multiplied alpha with a SDL2 alpha blit
                shadow_surface = text_surface.copy()
                temp_shadow_surface = shadow_surface.copy()

                self.font.render_to(temp_shadow_surface, origin,
                                    text_str,
                                    fgcolor=shadow_colour)
                shadow_surface.blit(temp_shadow_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            else:
                shadow_surface = text_surface.copy()
                shadow_surface.fill((0, 0, 0, 1))  # have to have 1 alpha here to fake convert to pre-multiplied alpha

                self.font.render_to(shadow_surface, origin,
                                    text_str,
                                    fgcolor=shadow_colour)

            for y_pos in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_rect.x + shadow_offset[0],
                                                text_rect.y + shadow_offset[1]
                                                + y_pos),
                                               text_rect.size)

                surface.blit(shadow_surface, shadow_text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)
            for x_pos in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_rect.x + shadow_offset[0]
                                                + x_pos,
                                                text_rect.y + shadow_offset[1]),
                                               text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)
            for x_and_y in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_rect.x + shadow_offset[0] + x_and_y,
                     text_rect.y + shadow_offset[1] + x_and_y),
                    text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)
            for x_and_y in range(-shadow_size, shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_rect.x + shadow_offset[0] - x_and_y,
                     text_rect.y + shadow_offset[1] + x_and_y),
                    text_rect.size)
                surface.blit(shadow_surface, shadow_text_rect, special_flags=pygame.BLEND_PREMULTIPLIED)

    def split(self, requested_x: int, line_width: int, row_start_x: int) -> Union['TextLayoutRect', None]:
        # starting heuristic: find the percentage through the chunk width of this split request
        percentage_split = 0
        if self.width != 0:
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
        left_side = ''
        right_side = ''
        if optimum_split_point != 0:
            # split the text
            left_side = self.text[:optimum_split_point]
            right_side = self.text[optimum_split_point:]
            split_text_ok = True

        elif self.x == row_start_x and self.right > line_width:
            # we have a chunk with no breaks (one long word usually) longer than a line
            # split it at the word
            optimum_split_point = max(1, int(percentage_split * len(self.text)) - 1)
            if optimum_split_point != 1:  # have to be at least wide enough to fit in a dash and another character
                left_side = self.text[:optimum_split_point] + '-'
                right_side = '-' + self.text[optimum_split_point:]
                split_text_ok = True
            else:
                raise ValueError('Line width is too narrow')

        if split_text_ok:
            # update the data for this chunk
            self.text = left_side
            self.letter_count = len(self.text)
            self.size = (sum([char_metric[4] for char_metric in self.font.get_metrics(self.text)]),
                         self.height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return self._split_at(right_side, self.topright, self.target_surface,
                                  self.target_surface_area, self.should_centre_from_baseline)
        else:
            return None

    def split_index(self, index):
        if 0 < index < len(self.text):
            left_side = self.text[:index]
            right_side = self.text[index:]

            self.text = left_side
            self.letter_count = len(self.text)
            self.size = (sum([char_metric[4] for char_metric in self.font.get_metrics(self.text)]),
                         self.height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return self._split_at(right_side, self.topright, self.target_surface,
                                  self.target_surface_area, self.should_centre_from_baseline)
        else:
            return None

    def _split_at(self, right_side, split_pos, target_surface, target_surface_area, baseline_centred):
        right_side_chunk = TextLineChunkFTFont(right_side, self.font, self.underlined,
                                               self.colour,
                                               self.using_default_text_colour,
                                               self.bg_colour,
                                               self.text_shadow_data)
        right_side_chunk.topleft = split_pos
        right_side_chunk.target_surface = target_surface
        right_side_chunk.target_surface_area = target_surface_area
        right_side_chunk.should_centre_from_baseline = baseline_centred
        return right_side_chunk

    def clear(self):
        if self.target_surface is not None:
            self.target_surface.fill(pygame.Color('#00000000'), self)

    def add_text(self, input_text: str):
        self.insert_text(input_text, len(self.text))

    def insert_text(self, input_text: str, index: int):
        """
        Insert a new string of text into this chunk and update the chunk's data.

        NOTE: We don't redraw the text immediately here as this size of this chunk
        changing may affect the position of other chunks later in the layout.

        :param input_text: the new text to insert.
        :param index: the index we are sticking the new text at.
        """
        self.text = self.text[:index] + input_text + self.text[index:]
        # we split text stings based on spaces
        self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']
        self.letter_count = len(self.text)

        if len(self.text) == 0:
            text_rect = self.font.get_rect('A')
        else:
            text_rect = self.font.get_rect(self.text)
        text_width = sum([char_metric[4] for char_metric in self.font.get_metrics(self.text)])
        text_height = text_rect.height
        if self.max_dimensions is not None:
            if self.max_dimensions[0] != -1:
                text_width = min(self.max_dimensions[0], text_width)
            if self.max_dimensions[1] != -1:
                text_height = min(self.max_dimensions[1], text_height)

        self.size = (text_width, text_height) # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

    def delete_letter_at_index(self, index):
        self.text = self.text[:index] + self.text[min(len(self.text), index+1):]

        self.letter_count = len(self.text)
        self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

        if len(self.text) == 0:
            text_rect = self.font.get_rect('A')
        else:
            text_rect = self.font.get_rect(self.text)
        text_width = sum([char_metric[4] for char_metric in self.font.get_metrics(self.text)])
        text_height = text_rect.height
        if self.max_dimensions is not None:
            if self.max_dimensions[0] != -1:
                text_width = min(self.max_dimensions[0], text_width)
            if self.max_dimensions[1] != -1:
                text_height = min(self.max_dimensions[1], text_height)

        self.size = (
        text_width, text_height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

    def backspace_letter_at_index(self, index):
        self.text = self.text[:max(0, index-1)] + self.text[index:]

        self.letter_count = len(self.text)
        self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

        if len(self.text) == 0:
            text_rect = self.font.get_rect('A')
        else:
            text_rect = self.font.get_rect(self.text)
        text_width = sum([char_metric[4] for char_metric in self.font.get_metrics(self.text)])
        text_height = text_rect.height
        if self.max_dimensions is not None:
            if self.max_dimensions[0] != -1:
                text_width = min(self.max_dimensions[0], text_width)
            if self.max_dimensions[1] != -1:
                text_height = min(self.max_dimensions[1], text_height)

        self.size = (
        text_width, text_height)  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

    def x_pos_to_letter_index(self, x_pos: int):
        chunk_space_x = x_pos - self.x
        percentage = chunk_space_x/self.width
        estimated_index = int(round(len(self.text) * percentage))
        best_index = estimated_index
        text_rect = self.font.get_rect(self.text[:best_index])
        width_to_index = text_rect.x + text_rect.width
        lowest_diff = abs(width_to_index - chunk_space_x)

        check_dir = -1
        changed_dir = 0
        step = 1
        # algorithm picks a good guess for the best letter index and then checks either side for better indexes
        while changed_dir < 2:
            new_index = best_index + (step * check_dir)
            curr_text_rect = self.font.get_rect(self.text[:max(estimated_index + (step * check_dir), 0)])
            new_diff = abs((curr_text_rect.x + curr_text_rect.width) - chunk_space_x)
            if new_diff < lowest_diff:
                lowest_diff = new_diff
                best_index = new_index
                step += 1
            else:
                check_dir *= -1
                changed_dir += 1
                step = 1

        return best_index

    def redraw(self):
        """
        Redraw a surface that has already been finalised once before.
        """
        if self.target_surface is not None:
            self.clear()
            self.finalise(self.target_surface, self.target_surface_area, self.row_chunk_origin,
                          self.row_chunk_height, self.row_bg_height, self.layout_x_offset, self.letter_end)
