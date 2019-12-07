import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.styled_chunk import StyledChunk
from pygame_gui.elements.text.html_parser import CharStyle
from pygame_gui.core.ui_font_dictionary import UIFontDictionary
from pygame_gui.core.colour_gradient import ColourGradient


class TestStyledChunk:
    def test_creation(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        StyledChunk(font_size=14, font_name='fira_code',
                    chunk='text', style=style, color=pygame.Color('#FFFF00'),
                    bg_color=pygame.Color('#000000'),
                    is_link=False, link_href='test', link_style=CharStyle(),
                    position=(0, 0), font_dictionary=dictionary)

    def test_redraw_bg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, color=pygame.Color('#FFFF00'),
                            bg_color=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_fg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, color=gradient,
                            bg_color=pygame.Color('#FFFF00'),
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_bg_and_fg_gradient(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, color=gradient,
                            bg_color=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.redraw()

    def test_redraw_changed_metrics(self, _init_pygame):
        dictionary = UIFontDictionary()
        style = CharStyle()
        gradient = ColourGradient(0, pygame.Color('#FFFF00'), pygame.Color('#FF0000'))
        chunk = StyledChunk(font_size=14, font_name='fira_code',
                            chunk='text', style=style, color=pygame.Color('#FFFF00'),
                            bg_color=gradient,
                            is_link=False, link_href='test', link_style=CharStyle(),
                            position=(0, 0), font_dictionary=dictionary)
        chunk.chunk = 'testy'
        chunk.redraw()
