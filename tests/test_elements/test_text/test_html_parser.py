import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.html_parser import CharStyle, TextHTMLParser, TextLineContext, TextStyleData


class TestCharStyle:
    def test_creation(self, _init_pygame):
        CharStyle()

    def test_comparison(self, _init_pygame):
        assert CharStyle() == CharStyle()


class TestTextLineContext:
    def test_creation(self, _init_pygame):
        TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                        color=pygame.Color('#FFFFFF'), bg_color=pygame.Color('#000000'),
                        is_link=True, link_href='None')

    def test_comparison(self, _init_pygame):
        text_line_1 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      color=pygame.Color('#FFFFFF'), bg_color=pygame.Color('#000000'),
                                      is_link=True, link_href='None')

        text_line_2 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      color=pygame.Color('#FFFFFF'), bg_color=pygame.Color('#000000'),
                                      is_link=True, link_href='None')

        assert text_line_1 == text_line_2
