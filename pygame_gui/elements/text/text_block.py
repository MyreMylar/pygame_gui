import warnings
from typing import Union, List, Dict, Any

import pygame

from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.ui_font_dictionary import UIFontDictionary

from pygame_gui.elements.text.text_effects import TextBoxEffect
from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.html_parser import TextLineContext


class TextBlock:
    """
    Handles turning parsed HTML in TextLineContexts into surfaces in StyledChunks and deals with word wrapping.

    :param text: Raw text to be styled with TextLineContext objects.
    :param rect: The rectangle to wrap the text to.
    :param indexed_styles: Text styles stored by their index in the raw text.
    :param font_dict: The UI's font dictionary.
    :param link_style: The link style for this text block (so we can do several bits of styling at once in an <a> block.
    :param bg_colour: The background colour or gradient for the whole block.
    :param wrap_to_height: Whether we should wrap the text to our block height. Not sure if this works.
    """
    class TextLine:
        """
        TODO: move this out of the TextBlock class if it still needs to exist.
        """
        def __init__(self):
            self.chunks = []
            self.max_line_char_height = 0
            self.max_line_ascent = 0

    def __init__(self,
                 text: str,
                 rect: pygame.Rect,
                 indexed_styles: Dict[int, TextLineContext],
                 font_dict: UIFontDictionary,
                 link_style: Dict[str, Any],
                 bg_colour: Union[pygame.Color, ColourGradient],
                 wrap_to_height: bool = False):

        self.characters = text

        self.position = (rect[0], rect[1])
        self.width = rect[2]
        self.height = rect[3] if wrap_to_height else -1
        self.indexed_styles = indexed_styles
        self.block_sprite = None
        self.font_dict = font_dict

        self.final_dimensions = (rect[2], rect[3])

        self.link_style = link_style

        self.bg_colour = bg_colour

        self.lines = []
        self.redraw(None)

    def redraw(self, text_effect: Union[TextBoxEffect, None]):
        """
        Takes our parsed text and the styles generated from that parsing and builds rendered 'chunks' out of them
        that are then blitted onto a final surface containing all our drawn text.

        :param text_effect: The text effect to apply when drawing the text.
        """
        self.lines = []
        if text_effect:
            end_text_position = text_effect.get_end_text_pos()
        else:
            end_text_position = len(self.characters)

        lines_of_chunks = []
        chunk_line = []
        start_style_key = 0
        keys = [key for key in list(self.indexed_styles.keys()) if key <= end_text_position]
        keys.sort()
        keys.append(end_text_position)
        max_line_ascent = 0
        for end_style_key in keys:
            if end_style_key != 0:
                text = self.characters[start_style_key:end_style_key]
                chunk = [text, self.indexed_styles[start_style_key]]
                chunk_font = self.font_dict.find_font(chunk[1].font_size,
                                                      chunk[1].font_name,
                                                      chunk[1].style.bold,
                                                      chunk[1].style.italic)
                chunk_ascent = chunk_font.get_ascent()
                if chunk_ascent > max_line_ascent:
                    max_line_ascent = chunk_ascent
                if chunk[0] == '\n':
                    if not chunk_line:
                        lines_of_chunks.append([max_line_ascent, [['', chunk[1]]]])
                    else:
                        lines_of_chunks.append([max_line_ascent, chunk_line])
                    chunk_line = []
                    max_line_ascent = 0
                else:
                    chunk_line.append(chunk)

            start_style_key = end_style_key

        if len(chunk_line) > 0:
            lines_of_chunks.append([max_line_ascent, chunk_line])

        if self.width != -1:
            line_index = 0
            while line_index < len(lines_of_chunks):
                line = lines_of_chunks[line_index][1]
                line_render_length = 0
                split_point = -1
                chunk_index = 0
                chunk_to_split_index = 0
                chunk_length = 0
                for chunk in line:
                    font = self.font_dict.find_font(chunk[1].font_size,
                                                    chunk[1].font_name,
                                                    chunk[1].style.bold,
                                                    chunk[1].style.italic)

                    metrics = font.metrics(chunk[0])
                    chunk_length = font.size(chunk[0])[0]
                    line_render_length += chunk_length
                    if line_render_length > self.width:
                        char_line_length = line_render_length - chunk_length
                        for i in range(len(metrics)):
                            advance = metrics[i][4]
                            char_line_length += advance
                            if char_line_length > self.width:
                                # splitting time
                                chunk_to_split_index = chunk_index
                                split_point = i
                                break
                    if split_point != -1:
                        break
                    chunk_index += 1

                if split_point != -1:
                    word_split_point = 0
                    chunk_to_split = line[chunk_to_split_index]
                    for i in range(split_point, 0, -1):
                        if chunk_to_split[0][i] == ' ':
                            word_split_point = i
                            break
                    if word_split_point == 0 and chunk_to_split_index == 0 and chunk_length > self.width:
                        # our chunk is one word, at the start of the line, and the split point is in it, so split the
                        # word instead of hunting for a word split point

                        if split_point > 1:
                            chunk_2_font = self.font_dict.find_font(chunk_to_split[1].font_size,
                                                                    chunk_to_split[1].font_name,
                                                                    chunk_to_split[1].style.bold,
                                                                    chunk_to_split[1].style.italic)

                            # If available space is less than three characters wide,
                            # we won't be able to split words with hyphens
                            if self.width < chunk_2_font.size('-W-')[0]:
                                chunk_1 = [chunk_to_split[0][:split_point - 1], chunk_to_split[1]]
                                chunk_2 = [chunk_to_split[0][split_point - 1:].lstrip(' '), chunk_to_split[1]]
                            else:
                                chunk_1 = [chunk_to_split[0][:split_point - 1] + '-', chunk_to_split[1]]
                                chunk_2 = ["-" + chunk_to_split[0][split_point - 1:].lstrip(' '), chunk_to_split[1]]

                            chunk_2_ascent = chunk_2_font.get_ascent()

                            lines_of_chunks[line_index][1][chunk_to_split_index] = chunk_1
                            new_line = [chunk_2_ascent, [chunk_2]]

                            chunk_length_of_line = len(lines_of_chunks[line_index][1])
                            for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                                remaining_chunk = lines_of_chunks[line_index][1][remaining_chunk_index]
                                new_line[1].append(remaining_chunk)

                                remaining_chunk_font = self.font_dict.find_font(remaining_chunk[1].font_size,
                                                                                remaining_chunk[1].font_name,
                                                                                remaining_chunk[1].style.bold,
                                                                                remaining_chunk[1].style.italic)
                                remaining_chunk_ascent = remaining_chunk_font.get_ascent()
                                if remaining_chunk_ascent > new_line[0]:
                                    new_line[0] = remaining_chunk_ascent

                            for _ in range(chunk_to_split_index + 1, chunk_length_of_line):
                                lines_of_chunks[line_index][1].pop()

                            lines_of_chunks.insert(line_index + 1, new_line)

                        else:
                            warnings.warn('Unable to split word into chunks because text box is too narrow')

                    else:
                        chunk_1 = [chunk_to_split[0][:word_split_point], chunk_to_split[1]]
                        chunk_2 = [chunk_to_split[0][word_split_point:].lstrip(' '), chunk_to_split[1]]

                        chunk_2_font = self.font_dict.find_font(chunk_2[1].font_size,
                                                                chunk_2[1].font_name,
                                                                chunk_2[1].style.bold,
                                                                chunk_2[1].style.italic)
                        chunk_2_ascent = chunk_2_font.get_ascent()

                        lines_of_chunks[line_index][1][chunk_to_split_index] = chunk_1
                        new_line = [chunk_2_ascent, [chunk_2]]

                        chunk_length_of_line = len(lines_of_chunks[line_index][1])
                        for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                            remaining_chunk = lines_of_chunks[line_index][1][remaining_chunk_index]
                            new_line[1].append(remaining_chunk)

                            remaining_chunk_font = self.font_dict.find_font(remaining_chunk[1].font_size,
                                                                            remaining_chunk[1].font_name,
                                                                            remaining_chunk[1].style.bold,
                                                                            remaining_chunk[1].style.italic)
                            remaining_chunk_ascent = remaining_chunk_font.get_ascent()
                            if remaining_chunk_ascent > new_line[0]:
                                new_line[0] = remaining_chunk_ascent

                        for _ in range(chunk_to_split_index + 1, chunk_length_of_line):
                            lines_of_chunks[line_index][1].pop()

                        lines_of_chunks.insert(line_index + 1, new_line)
                line_index += 1

        surface = None
        surface_width = self.width
        surface_height = self.height
        if not (self.height == -1 or self.width == -1):
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, depth=32)

        position = [0, 0]
        line_height_acc = 0
        max_line_length = 0
        for line in lines_of_chunks:
            line_chunks = []
            max_line_char_height = 0
            max_line_ascent = 0
            for chunk in line[1]:
                new_chunk = StyledChunk(chunk[1].font_size,
                                        chunk[1].font_name,
                                        chunk[0],
                                        chunk[1].style,
                                        chunk[1].color,
                                        chunk[1].bg_color,
                                        chunk[1].is_link,
                                        chunk[1].link_href,
                                        self.link_style,
                                        (position[0], position[1]),
                                        self.font_dict)
                position[0] += new_chunk.advance
                if new_chunk.height > max_line_char_height:
                    max_line_char_height = new_chunk.height
                if new_chunk.ascent > max_line_ascent:
                    max_line_ascent = new_chunk.ascent
                line_chunks.append(new_chunk)

                if surface is not None:
                    # need to adjust y start pos based on ascents
                    chunk_rect = new_chunk.rect
                    adjust = line[0] - new_chunk.ascent
                    chunk_rect.y += adjust
                    surface.blit(new_chunk.rendered_chunk, chunk_rect)

            text_line = TextBlock.TextLine()
            text_line.chunks = line_chunks
            text_line.max_line_ascent = max_line_ascent
            self.lines.append(text_line)

            if position[0] > max_line_length:
                max_line_length = position[0]
            position[0] = 0
            position[1] += max_line_char_height
            line_height_acc += max_line_char_height

        if surface is None:
            surface_width = max_line_length if self.width == -1 else self.width
            surface_height = line_height_acc if self.height == -1 else self.height
            surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA, depth=32)

            for line in self.lines:
                for chunk in line.chunks:
                    # need to adjust y start pos based on ascents
                    chunk_rect = chunk.rect
                    adjust = line.max_line_ascent - chunk.ascent
                    chunk_rect.y += adjust
                    surface.blit(chunk.rendered_chunk, chunk_rect)

        self.block_sprite = surface
        self.final_dimensions = [surface_width, surface_height]
        self.width = surface_width
        self.height = surface_height

    def redraw_from_chunks(self, text_effect: Union[TextBoxEffect, None]):
        """
        Redraw only the last part of text block starting from the already complete styled and word wrapped StyledChunks.

        :param text_effect: The text effect to use when redrawing.
        """
        final_alpha = text_effect.get_final_alpha() if text_effect else 255
        self.block_sprite = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA, depth=32)

        if type(self.bg_colour) == ColourGradient:
            self.block_sprite.fill(pygame.Color("#FFFFFFFF"))
            self.bg_colour.apply_gradient_to_surface(self.block_sprite)
        else:
            self.block_sprite.fill(self.bg_colour)

        for text_line in self.lines:
            for chunk in text_line.chunks:
                if self.block_sprite is not None:
                    self.block_sprite.blit(chunk.rendered_chunk, chunk.rect)
        self.block_sprite.set_alpha(final_alpha)

    def add_chunks_to_hover_group(self, hover_group: List[StyledChunk]):
        """
        Grab the StyledChunks that are hyperlinks and add them to a passed in 'hover group' so they can be checked
        By the UITextBox for mouse over and mouse click events.

        :param hover_group: The group to add our hyperlink StyledChunks to.
        """
        for line in self.lines:
            for chunk in line.chunks:
                if chunk.is_link:
                    hover_group.append(chunk)
