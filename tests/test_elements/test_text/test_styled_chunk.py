import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.html_parser import CharStyle
from pygame_gui.core.ui_font_dictionary import UIFontDictionary
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.resource_loaders import BlockingThreadedResourceLoader


class TestStyledChunk:
    def test_creation(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        StyledChunk(font_size=14, font_name='fira_code',
                    chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                    bg_colour=pygame.Color('#000000'),
                    is_link=False, link_href='test', link_style=CharStyle(),
                    position=(0, 0), font_dictionary=dictionary)

    def test_redraw_bg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                            bg_colour=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_fg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, colour=gradient,
                            bg_colour=pygame.Color('#FFFF00'),
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_bg_and_fg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, colour=gradient,
                            bg_colour=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_changed_metrics(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                            bg_colour=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.chunk = 'testy'
        chunk.redraw()

    def test_redraw_empty_chunk(self, _init_pygame):
        dictionary = UIFontDictionary(BlockingThreadedResourceLoader())
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, colour=pygame.Color('#FFFF00'),
                            bg_colour=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.chunk = ''
        chunk.redraw()
