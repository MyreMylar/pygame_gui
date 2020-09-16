import pytest
import pytest_benchmark

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

import pygame
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.text.html_parser import CharStyle
from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.text_block import TextBlock
from pygame_gui.core.ui_font_dictionary import UIFontDictionary
from pygame_gui.core import BlockingThreadedResourceLoader

from pygame_gui.elements.ui_old_text_box import UIOldTextBox
from pygame_gui.elements.ui_text_box import UITextBox


def test_old_char_style_performance(benchmark, _init_pygame, _display_surface_return_none):

    # this first part likely won't change with the new text module
    loader = BlockingThreadedResourceLoader()
    dictionary = UIFontDictionary(loader)
    dictionary.preload_font(font_size=25, font_name='fira_code')
    loader.start()
    loader.update()

    benchmark(CharStyle)


def test_old_styled_chunk_performance(benchmark, _init_pygame, _display_surface_return_none):

    # this first part likely won't change with the new text module
    loader = BlockingThreadedResourceLoader()
    dictionary = UIFontDictionary(loader)
    dictionary.preload_font(font_size=25, font_name='fira_code')
    loader.start()
    loader.update()

    style = CharStyle()
    benchmark(StyledChunk,
              font_size=14, font_name='fira_code',
              chunk='text_text_text_text ', style=style,
              colour=pygame.Color('#FFFF00'),
              bg_colour=pygame.Color('#000000'),
              is_link=False, link_href='test', link_style=CharStyle(),
              position=(0, 0), font_dictionary=dictionary)


def create_text_block(dictionary):
    # this part will likely all be different
    style = CharStyle()
    styled_chunk_1 = StyledChunk(
                               font_size=14, font_name='fira_code',
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

    TextBlock(text='text_text_text_text DAN',
              rect=pygame.Rect(0, 0, 100, 100),
              indexed_styles={0: styled_chunk_1, 21: styled_chunk_2},
              font_dict=dictionary, link_style=style,
              bg_colour=pygame.Color('#FF0000'), wrap_to_height=True)


def test_old_text_block_performance(benchmark, _init_pygame, _display_surface_return_none):

    # this first part likely won't change with the new text module
    loader = BlockingThreadedResourceLoader()
    dictionary = UIFontDictionary(loader)
    dictionary.preload_font(font_size=25, font_name='fira_code')
    loader.start()
    loader.update()

    # this part will likely all be different
    benchmark(create_text_block, dictionary)


def create_old_text_box(default_ui_manager):
    text_box = UIOldTextBox(
        html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                  "<i>styles</i>.",
        relative_rect=pygame.Rect(100, 100, 200, 300),
        manager=default_ui_manager)


def test_old_style_text_box_performance(benchmark, _init_pygame,
                                        default_ui_manager: UIManager,
                                        _display_surface_return_none):

    default_ui_manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                                      {"name": "fira_code", "size:": 14, "style": "italic"}])

    benchmark(create_old_text_box, default_ui_manager)


def create_new_text_box(default_ui_manager):
    text_box = UITextBox(
        html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                  "<i>styles</i>.",
        relative_rect=pygame.Rect(100, 100, 200, 300),
        manager=default_ui_manager)


def test_new_style_text_box_performance(benchmark, _init_pygame,
                                        default_ui_manager: UIManager,
                                        _display_surface_return_none):

    default_ui_manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                                      {"name": "fira_code", "size:": 14, "style": "italic"}])

    benchmark(create_new_text_box, default_ui_manager)
