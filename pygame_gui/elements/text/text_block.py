import warnings
from typing import Union, List, Dict, Any

import pygame

from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.ui_font_dictionary import UIFontDictionary

from pygame_gui.elements.text.text_effects import TextBoxEffect
from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.html_parser import CharStyle


class TextBlock:
    """
    Handles turning parsed HTML in TextLineContexts into surfaces in StyledChunks and deals with
    word wrapping.

    :param text: Raw text to be styled with TextLineContext objects.
    :param rect: The rectangle to wrap the text to.
    :param indexed_styles: Text styles stored by their index in the raw text.
    :param font_dict: The UI's font dictionary.
    :param link_style: The link style for this text block (so we can do several bits of styling at
    once in an <a> block.
    :param bg_colour: The background colour or gradient for the whole block.
    :param wrap_to_height: Whether we should wrap the text to our block height. Not sure if this
    works.
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
                 indexed_styles: Dict[int, StyledChunk],
                 font_dict: UIFontDictionary,
                 link_style: CharStyle,
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
        Takes our parsed text and the styles generated from that parsing and builds rendered
        'chunks' out of them that are then blitted onto a final surface containing all our drawn
        text.

        :param text_effect: The text effect to apply when drawing the text.
        """
        self.lines = []
        if text_effect:
            end_text_position = text_effect.get_end_text_pos()
        else:
            end_text_position = len(self.characters)

        lines_of_chunks = []
        self._divide_text_into_styled_chunks(end_text_position, lines_of_chunks)
        self._wrap_chunks_to_fit_rect(lines_of_chunks)
        self._draw_chunks_to_surface(lines_of_chunks)

    def _divide_text_into_styled_chunks(self, end_text_position: int,
                                        lines_of_chunks: List):
        """
        Divide our text into chunks based on whatever styles are set on the text.
        This also splits the text into lines if the 'new line' character has ben used.

        :param end_text_position: How far we are intending to draw up to.
        :param lines_of_chunks: the resulting list of text divide up into lines of chunks.
        """
        chunk_line = []
        start_style_key = 0
        keys = [key for key in list(self.indexed_styles.keys()) if key <= end_text_position]
        keys.sort()
        keys.append(end_text_position)
        max_line_ascent = 0
        for end_style_key in keys:
            if end_style_key != 0:
                text = self.characters[start_style_key:end_style_key]
                style = self.indexed_styles[start_style_key]
                chunk_font = self.font_dict.find_font(style.font_size,
                                                      style.font_name,
                                                      style.style.bold,
                                                      style.style.italic)
                chunk_ascent = chunk_font.get_ascent()
                chunk = {'text': text,
                         'style': style,
                         'font': chunk_font,
                         'ascent': chunk_ascent}
                if chunk_ascent > max_line_ascent:
                    max_line_ascent = chunk_ascent
                if chunk['text'] == '\n':
                    if not chunk_line:
                        lines_of_chunks.append({'line_ascent': max_line_ascent,
                                                'chunks': [{'text': '',
                                                            'style': chunk['style'],
                                                            'font': chunk_font,
                                                            'ascent': chunk_ascent}]})
                    else:
                        lines_of_chunks.append({'line_ascent': max_line_ascent,
                                                'chunks': chunk_line})
                    chunk_line = []
                    max_line_ascent = 0
                else:
                    chunk_line.append(chunk)

            start_style_key = end_style_key
        if chunk_line:
            lines_of_chunks.append({'line_ascent': max_line_ascent,
                                    'chunks': chunk_line})

    def _wrap_chunks_to_fit_rect(self,
                                 lines_of_chunks: List[Dict[str,
                                                            Union[List[Dict[str, Any]], int]]]):
        """
        Takes a list of lines of chunks and tries to wrap it to fit the provided rectangle,
        assuming one has been provided with at least a usable width.

        :param lines_of_chunks: The list of lines of chunks.
        """
        if self.width == -1:
            return
        for line_index, line_data in enumerate(lines_of_chunks):
            line_render_length = 0
            split_point = -1
            chunk_index = 0
            chunk_to_split_index = 0
            chunk_length = 0
            for chunk in line_data['chunks']:
                metrics = chunk['font'].metrics(chunk['text'])
                chunk_length = chunk['font'].size(chunk['text'])[0]
                line_render_length += chunk_length
                if line_render_length > self.width:
                    char_line_length = line_render_length - chunk_length
                    for i, metric in enumerate(metrics):
                        advance = metric[4]
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
                self._split_chunk(chunk_length, chunk_to_split_index,
                                  line_data['chunks'], line_index,
                                  lines_of_chunks, split_point)

    def _split_chunk(self,
                     chunk_length: int,
                     chunk_to_split_index: int,
                     line: List[Dict[str, Any]],
                     line_index: int,
                     lines_of_chunks: List[Dict[str, Union[List[Dict[str, Any]], int]]],
                     split_point: int):
        """
        Split a chunk of text into two.

        :param chunk_length: The length of this chunk
        :param chunk_to_split_index: The index of our chunk to split.
        :param line_index: The line we are on in the block of text.
        :param lines_of_chunks: All the chunks in our block.
        :param split_point: The point we must split by.
        """
        word_split_point = 0
        chunk_to_split = line[chunk_to_split_index]
        for i in range(split_point, 0, -1):
            if chunk_to_split['text'][i] == ' ':
                word_split_point = i
                break
        if (word_split_point == 0 and chunk_to_split_index == 0 and
                chunk_length > self.width):
            # our chunk is one word, at the start of the line, and the split point is
            # in it, so split the word instead of hunting for a word split point
            self._split_single_word_chunk(chunk_to_split, chunk_to_split_index, line_index,
                                          lines_of_chunks, split_point)

        else:
            self._split_multi_word_chunk(chunk_to_split, chunk_to_split_index, line_index,
                                         lines_of_chunks, word_split_point)

    @staticmethod
    def _split_multi_word_chunk(chunk_to_split: Dict[str, Any],
                                chunk_to_split_index: int,
                                line_index: int,
                                lines_of_chunks: List[Dict[str, Union[List[Dict[str, Any]], int]]],
                                word_split_point: int):
        """
        Split a chunk of text in two at an appropriate point between words.

        :param chunk_to_split: The chunk to divide.
        :param chunk_to_split_index: The index of our chunk to split.
        :param line_index: The line we are on in the block of text.
        :param lines_of_chunks: All the chunks in our block.
        :param word_split_point: Index of the space character closest to where we want to split.
        :return:
        """

        chunk_1 = {'text': chunk_to_split['text'][:word_split_point],
                   'style': chunk_to_split['style'],
                   'font': chunk_to_split['font'],
                   'ascent': chunk_to_split['ascent']}

        chunk_2 = {'text': chunk_to_split['text'][word_split_point:].lstrip(' '),
                   'style': chunk_to_split['style'],
                   'font': chunk_to_split['font'],
                   'ascent': chunk_to_split['ascent']}

        # change the chunk we are splitting to equal chunk 1 (the left-hand piece)
        lines_of_chunks[line_index]['chunks'][chunk_to_split_index] = chunk_1

        # create a new line for chunk 2 (the right-hand piece)
        new_line = {'line_ascent': chunk_2['ascent'],
                    'chunks': [chunk_2]}

        remaining_chunks = lines_of_chunks[line_index]['chunks'][chunk_to_split_index + 1:]
        for remaining_chunk in remaining_chunks:
            new_line['chunks'].append(remaining_chunk)

            if remaining_chunk['ascent'] > new_line['line_ascent']:
                new_line['line_ascent'] = remaining_chunk['ascent']

            lines_of_chunks[line_index]['chunks'].pop()

        # reset the line ascent to zero and recalculate it
        lines_of_chunks[line_index]['line_ascent'] = 0
        for pre_split_chunk in lines_of_chunks[line_index]['chunks']:
            if pre_split_chunk['ascent'] > lines_of_chunks[line_index]['line_ascent']:
                lines_of_chunks[line_index]['line_ascent'] = pre_split_chunk['ascent']

        lines_of_chunks.insert(line_index + 1, new_line)

    def _split_single_word_chunk(self,
                                 chunk_to_split: Dict[str, Any],
                                 chunk_to_split_index: int,
                                 line_index: int,
                                 lines_of_chunks: List[Dict[str, Union[List[Dict[str, Any]], int]]],
                                 split_point: int):
        """
        Split a chunk of text that is just a single word spanning the whole line.
        We try to insert hyphens either side of the split to indicate that the word has been
        divided.

        :param chunk_to_split: The chunk to divide.
        :param chunk_to_split_index: The index of our chunk to split.
        :param line_index: The line we are on in the block of text.
        :param lines_of_chunks: All the chunks in our block.
        :param split_point: The precise point to split.
        """
        if split_point > 1:

            # If available space is less than three characters wide,
            # we won't be able to split words with hyphens
            if self.width < chunk_to_split['font'].size('-W-')[0]:
                chunk_1 = {'text': chunk_to_split['text'][:split_point - 1],
                           'style': chunk_to_split['style'],
                           'font': chunk_to_split['font'],
                           'ascent': chunk_to_split['ascent']}

                chunk_2 = {'text': chunk_to_split['text'][split_point - 1:].lstrip(' '),
                           'style': chunk_to_split['style'],
                           'font': chunk_to_split['font'],
                           'ascent': chunk_to_split['ascent']}
            else:
                chunk_1 = {'text': chunk_to_split['text'][:split_point - 1] + '-',
                           'style': chunk_to_split['style'],
                           'font': chunk_to_split['font'],
                           'ascent': chunk_to_split['ascent']}

                chunk_2 = {'text': "-" + chunk_to_split['text'][split_point - 1:].lstrip(' '),
                           'style': chunk_to_split['style'],
                           'font': chunk_to_split['font'],
                           'ascent': chunk_to_split['ascent']}

            # change the chunk we are splitting to equal chunk 1 (the left-hand piece)
            lines_of_chunks[line_index]['chunks'][chunk_to_split_index] = chunk_1

            # create a new line for chunk 2 (the right-hand piece)
            new_line = {'line_ascent': chunk_2['ascent'],
                        'chunks': [chunk_2]}

            remaining_chunks = lines_of_chunks[line_index]['chunks'][chunk_to_split_index + 1:]
            for remaining_chunk in remaining_chunks:
                new_line['chunks'].append(remaining_chunk)

                if remaining_chunk['ascent'] > new_line['line_ascent']:
                    new_line['line_ascent'] = remaining_chunk['ascent']

                lines_of_chunks[line_index]['chunks'].pop()

            # reset the line ascent to zero and recalculate it
            lines_of_chunks[line_index]['line_ascent'] = 0
            for pre_split_chunk in lines_of_chunks[line_index]['chunks']:
                if pre_split_chunk['ascent'] > lines_of_chunks[line_index]['line_ascent']:
                    lines_of_chunks[line_index]['line_ascent'] = pre_split_chunk['ascent']

            lines_of_chunks.insert(line_index + 1, new_line)

        else:
            warnings.warn('Unable to split word into'
                          ' chunks because text box is too narrow')

    def _draw_chunks_to_surface(self,
                                lines_of_chunks: List[Dict[str, Union[List[Dict[str, Any]], int]]]):
        """
        Takes a list of lines of chunks and draws it to a surface using the styles and positions
        attached to the chunks.

        :param lines_of_chunks:
        :return:
        """
        self.block_sprite = None
        if self.height != -1 and self.width != -1:
            self.block_sprite = pygame.Surface((self.width, self.height),
                                               pygame.SRCALPHA, depth=32)
            self.block_sprite.fill(pygame.Color('#00000000'))
        position = [0, 0]
        line_height_acc = 0
        max_line_length = 0
        for line in lines_of_chunks:
            line_chunks = []
            max_line_char_height = 0
            for chunk in line['chunks']:
                new_chunk = StyledChunk(chunk['style'].font_size,
                                        chunk['style'].font_name,
                                        chunk['text'],
                                        chunk['style'].style,
                                        chunk['style'].colour,
                                        chunk['style'].bg_colour,
                                        chunk['style'].is_link,
                                        chunk['style'].link_href,
                                        self.link_style,
                                        (position[0], position[1]),
                                        self.font_dict)
                position[0] += new_chunk.advance
                if new_chunk.height > max_line_char_height:
                    max_line_char_height = new_chunk.height
                line_chunks.append(new_chunk)

                if self.block_sprite is not None:
                    # need to adjust y start pos based on ascents
                    new_chunk.rect.y += (line['line_ascent'] - new_chunk.ascent)
                    self.block_sprite.blit(new_chunk.rendered_chunk, new_chunk.rect,
                                           special_flags=pygame.BLEND_PREMULTIPLIED)

            text_line = TextBlock.TextLine()
            text_line.chunks = line_chunks
            text_line.max_line_ascent = line['line_ascent']
            self.lines.append(text_line)

            if position[0] > max_line_length:
                max_line_length = position[0]
            position[0] = 0
            position[1] += max_line_char_height
            line_height_acc += max_line_char_height
        if self.block_sprite is None:
            self.width = max_line_length if self.width == -1 else self.width
            self.height = line_height_acc if self.height == -1 else self.height
            self.block_sprite = pygame.Surface((self.width, self.height),
                                               pygame.SRCALPHA, depth=32)
            self.block_sprite.fill(pygame.Color('#00000000'))

            for line in self.lines:
                for chunk in line.chunks:
                    # need to adjust y start pos based on ascents
                    chunk.rect.y += line.max_line_ascent - chunk.ascent
                    self.block_sprite.blit(chunk.rendered_chunk, chunk.rect,
                                           special_flags=pygame.BLEND_PREMULTIPLIED)

        self.final_dimensions = (self.width, self.height)

    def redraw_from_chunks(self, text_effect: Union[TextBoxEffect, None]):
        """
        Redraw only the last part of text block starting from the already complete styled and word
        wrapped StyledChunks.

        :param text_effect: The text effect to use when redrawing.
        """
        final_alpha = text_effect.get_final_alpha() if text_effect else 255
        self.block_sprite = pygame.Surface((self.width, self.height),
                                           flags=pygame.SRCALPHA, depth=32)
        self.block_sprite.fill(pygame.Color('#00000000'))

        if isinstance(self.bg_colour, ColourGradient):
            self.block_sprite.fill(pygame.Color("#FFFFFFFF"))
            self.bg_colour.apply_gradient_to_surface(self.block_sprite)
        else:
            self.block_sprite.fill(self.bg_colour)

        for text_line in self.lines:
            for chunk in text_line.chunks:
                if self.block_sprite is not None:
                    self.block_sprite.blit(chunk.rendered_chunk, chunk.rect,
                                           special_flags=pygame.BLEND_PREMULTIPLIED)
        self.block_sprite.set_alpha(final_alpha)

    def add_chunks_to_hover_group(self, hover_group: List[StyledChunk]):
        """
        Grab the StyledChunks that are hyperlinks and add them to a passed in 'hover group' so they
        can be checked by the UITextBox for mouse over and mouse click events.

        :param hover_group: The group to add our hyperlink StyledChunks to.
        """
        for line in self.lines:
            for chunk in line.chunks:
                if chunk.is_link:
                    hover_group.append(chunk)
