import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.html_parser import CharStyle, TextHTMLParser, TextLineContext, TextStyleData
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme
from pygame_gui.core.resource_loaders import BlockingThreadedResourceLoader


class TestCharStyle:
    def test_creation(self, _init_pygame):
        CharStyle()

    def test_comparison(self, _init_pygame):
        assert CharStyle() == CharStyle()


class TestTextLineContext:
    def test_creation(self, _init_pygame):
        TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                        colour=pygame.Color('#FFFFFF'),
                        bg_colour=pygame.Color('#000000'),
                        is_link=True, link_href='None')

    def test_comparison_equal(self, _init_pygame):
        text_line_1 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      colour=pygame.Color('#FFFFFF'),
                                      bg_colour=pygame.Color('#000000'),
                                      is_link=True, link_href='None')

        text_line_2 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      colour=pygame.Color('#FFFFFF'),
                                      bg_colour=pygame.Color('#000000'),
                                      is_link=True, link_href='None')

        assert text_line_1 == text_line_2

        text_line_2.font_size = 15

        assert (text_line_1 == text_line_2) is False

    def test_comparison_not_equal(self, _init_pygame):
        text_line_1 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      colour=pygame.Color('#FFFFFF'),
                                      bg_colour=pygame.Color('#000000'),
                                      is_link=True, link_href='None')

        text_line_2 = TextLineContext(font_size=14, font_name='fira_code', style=CharStyle(),
                                      colour=pygame.Color('#FF0000'),
                                      bg_colour=pygame.Color('#000000'),
                                      is_link=False, link_href='gui')

        assert text_line_1 != text_line_2


class TestHtmlParser:
    def test_creation(self, _init_pygame):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader())
        parser = TextHTMLParser(theme, [])
        parser.feed('<b>text</b>')

    def test_invalid_tag(self, _init_pygame):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader())
        parser = TextHTMLParser(theme, [])
        with pytest.warns(UserWarning, match='Unsupported HTML Tag'):
            parser.feed('</font><video>text</video>')

    def test_body_gradient(self, _init_pygame):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader())
        parser = TextHTMLParser(theme, [])
        parser.feed('<body bgcolor=#FF0000,#FFFF00,0>text</body></body>')

    def test_weird_html(self, _init_pygame):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader())
        parser = TextHTMLParser(theme, [])
        parser.feed('<body bgcolor="" > <font size="" face="" >text</font></body>')
