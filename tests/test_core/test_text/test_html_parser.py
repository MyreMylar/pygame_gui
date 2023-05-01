import pygame
import pygame.freetype
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import TextLineChunkFTFont
from pygame_gui.core.text import HTMLParser, LineBreakLayoutRect, ImageLayoutRect


class TestHTMLParser:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):

        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

    def test_handle_start_tag(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

        parser.handle_starttag(tag='b', attrs=[])

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

        parser.handle_starttag(tag='i', attrs=[])

        assert len(parser.style_stack) == 3
        assert parser.style_stack[2][0] == 'i'
        assert parser.current_style['italic'] is True

        parser.current_style['italic'] = False
        parser.current_style['bold'] = False

        with pytest.warns(UserWarning, match="Unsupported HTML Tag"):
            parser.handle_starttag(tag='bad_tag', attrs=[])

        parser.handle_starttag(tag='shadow', attrs=[('color', "link_text")])

        assert (parser.current_style['shadow_data'][3] ==
                default_ui_manager.get_theme().get_colour_or_gradient("link_text", combined_ids))

        parser.handle_starttag(tag='font', attrs=[('pixel_size', "8")])

        assert parser.current_style['font_size'] == 8

        parser.handle_starttag(tag='font', attrs=[('pixel_size', "")])

        assert parser.current_style['font_size'] is 14

        parser.handle_starttag(tag='font', attrs=[('size', "")])

        assert parser.current_style['font_size'] is 14

        with pytest.warns(UserWarning, match="not a supported html style size"):
            parser.handle_starttag(tag='font', attrs=[('size', "8")])

        parser.handle_starttag(tag='body', attrs=[('bgcolor', "link_text")])

        assert (parser.current_style['bg_colour'] ==
                default_ui_manager.get_theme().get_colour_or_gradient("link_text", combined_ids))

        parser.handle_starttag(tag='body', attrs=[('bgcolor', "")])

        assert parser.current_style['bg_colour'] == pygame.Color('#00000000')

        parser.handle_starttag(tag='p', attrs=[])
        parser.handle_starttag(tag='p', attrs=[])

        assert isinstance(parser.layout_rect_queue[-2], LineBreakLayoutRect)

        parser.handle_starttag(tag='img', attrs=[('src', 'tests/data/images/splat.png'),
                                                 ('float', 'none'),
                                                 ('padding', '0 0 0')])

        assert isinstance(parser.layout_rect_queue[-1], ImageLayoutRect)
        assert parser.layout_rect_queue[-1].padding.top == 0
        assert parser.layout_rect_queue[-1].padding.bottom == 0
        assert parser.layout_rect_queue[-1].padding.right == 0
        assert parser.layout_rect_queue[-1].padding.left == 0

    def test_handle_end_tag(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

        parser.handle_starttag(tag='b', attrs=[])

        assert len(parser.style_stack) == 2
        assert parser.style_stack[1][0] == 'b'
        assert parser.current_style['bold'] is True

        parser.handle_endtag(tag='b')

        assert len(parser.style_stack) == 1
        assert parser.current_style['bold'] is False

    def test_handle_data(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

        parser.handle_starttag(tag='u', attrs=[])
        parser.handle_data('underlined text')
        parser.handle_endtag(tag='u')

        assert len(parser.layout_rect_queue) == 2
        assert isinstance(parser.layout_rect_queue[1], TextLineChunkFTFont)
        assert parser.layout_rect_queue[1].text == 'underlined text'
        assert parser.layout_rect_queue[1].underlined is True

    def test_push_style(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

    def test_pop_style(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

        parser.pop_style('bad_tag')

    def test_error(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids([None],
                                                                             ['text_box'],
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

        with pytest.warns(UserWarning, match="test error"):
            parser.error("test error")


if __name__ == '__main__':
    pytest.console_main()
