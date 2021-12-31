import pygame
import pygame.freetype
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import TextLineChunkFTFont
from pygame_gui.core.text import HTMLParser


class TestHTMLParser:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):

        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        assert len(parser.layout_rect_queue) == 0

    def test_handle_start_tag(self, _init_pygame, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        assert parser.current_style['italic'] is False
        assert parser.current_style['bold'] is False

        parser.handle_starttag(tag='b', attrs=dict([]))

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

        parser.handle_starttag(tag='i', attrs=dict([]))

        assert len(parser.style_stack) == 3
        assert parser.style_stack[2][0] == 'i'
        assert parser.current_style['italic'] is True

    def test_handle_end_tag(self, _init_pygame, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        assert parser.current_style['italic'] is False
        assert parser.current_style['bold'] is False

        parser.handle_starttag(tag='b', attrs=dict([]))

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

        parser.handle_endtag(tag='b')

        assert len(parser.style_stack) == 1
        assert parser.current_style['bold'] is False

    def test_handle_data(self, _init_pygame, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        assert len(parser.layout_rect_queue) == 0

        parser.handle_data('blep')

        assert len(parser.layout_rect_queue) == 1
        assert isinstance(parser.layout_rect_queue[0], TextLineChunkFTFont)
        assert parser.layout_rect_queue[0].text == 'blep'
        assert parser.layout_rect_queue[0].underlined is False

        parser.handle_starttag(tag='u', attrs=dict([]))
        parser.handle_data('underlined text')
        parser.handle_endtag(tag='u')

        assert len(parser.layout_rect_queue) == 2
        assert isinstance(parser.layout_rect_queue[1], TextLineChunkFTFont)
        assert parser.layout_rect_queue[1].text == 'underlined text'
        assert parser.layout_rect_queue[1].underlined is True

    def test_push_style(self, _init_pygame, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        style = {'bold': True}

        parser.push_style('b', style)

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

    def test_pop_style(self, _init_pygame, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        style = {'bold': True}

        parser.push_style('b', style)

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

        parser.pop_style('b')

        assert len(parser.style_stack) == 1
        assert parser.current_style['bold'] is False


if __name__ == '__main__':
    pytest.console_main()
