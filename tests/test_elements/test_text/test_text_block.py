import os

import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.html_parser import CharStyle
from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.text_block import TextBlock
from pygame_gui.core.ui_font_dictionary import UIFontDictionary


class TestTextBlock:
    def test_creation(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        styled_chunk = StyledChunk(font_size=14, font_name='fira_code',
                                   chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                                   bg_colour=pygame.Color('#000000'),
                                   is_link=False, link_href='test', link_style=CharStyle(),
                                   position=(0, 0), font_dictionary=dictionary)

        TextBlock(text='test', rect=pygame.Rect(0, 0, 100, 100),
                  indexed_styles={0: styled_chunk}, font_dict=dictionary, link_style=style,
                  bg_colour=pygame.Color('#FF0000'), wrap_to_height=True)

    def test_creation_scale_to_text(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        styled_chunk = StyledChunk(font_size=14, font_name='fira_code',
                                   chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                                   bg_colour=pygame.Color('#000000'),
                                   is_link=False, link_href='test', link_style=CharStyle(),
                                   position=(0, 0), font_dictionary=dictionary)

        TextBlock(text='test', rect=pygame.Rect(0, 0, -1, -1),
                  indexed_styles={0: styled_chunk}, font_dict=dictionary, link_style=style,
                  bg_colour=pygame.Color('#FF0000'), wrap_to_height=True)

    def test_creation_scale_vert_to_text(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        styled_chunk = StyledChunk(font_size=14, font_name='fira_code',
                                   chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                                   bg_colour=pygame.Color('#000000'),
                                   is_link=False, link_href='test', link_style=CharStyle(),
                                   position=(0, 0), font_dictionary=dictionary)

        TextBlock(text='test', rect=pygame.Rect(0, 0, -1, 100),
                  indexed_styles={0: styled_chunk}, font_dict=dictionary, link_style=style,
                  bg_colour=pygame.Color('#FF0000'), wrap_to_height=True)

    def test_word_split(self, _init_pygame):
        dictionary = UIFontDictionary()
        dictionary.preload_font(font_size=25, font_name='fira_code')
        style = CharStyle()
        styled_chunk_1 = StyledChunk(font_size=14, font_name='fira_code',
                                     chunk='text_text_text_text ', style=style,
                                     colour=pygame.Color('#FFFF00'),
                                     bg_colour=pygame.Color('#000000'),
                                     is_link=False, link_href='test', link_style=CharStyle(),
                                     position=(0, 0), font_dictionary=dictionary)

        styled_chunk_2 = StyledChunk(font_size=25, font_name='fira_code',
                                     chunk='DAN', style=style, colour=pygame.Color('#FFFF00'),
                                     bg_colour=pygame.Color('#000000'),
                                     is_link=False, link_href='test', link_style=CharStyle(),
                                     position=(0, 0), font_dictionary=dictionary)

        TextBlock(text='text_text_text_text DAN', rect=pygame.Rect(0, 0, 100, 100),
                  indexed_styles={0: styled_chunk_1, 21: styled_chunk_2},
                  font_dict=dictionary, link_style=style,
                  bg_colour=pygame.Color('#FF0000'), wrap_to_height=True)
