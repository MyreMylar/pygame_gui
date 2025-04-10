import os

import pygame
import pytest

import i18n

import pygame_gui
from pygame_gui.core.utility import clipboard_paste
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.ui_manager import UIManager
from tests.shared_comparators import compare_surfaces
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont

from pygame_gui import UITextEffectType


class TestUITextBox:

    def test_creation(self, _init_pygame: None,
                      default_ui_manager: UIManager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None
        i18n.add_translation('translation.test_hello', 'Hello %{name}')
        text_box_with_kwargs = UITextBox(relative_rect=pygame.Rect(100, 100, 150, 30),
                                         html_text="translation.test_hello",
                                         manager=default_ui_manager,
                                         text_kwargs={"name": "World"})
        assert text_box_with_kwargs.image is not None
        text_chunk = text_box_with_kwargs.text_box_layout.layout_rows[0].items[0]
        assert isinstance(text_chunk, TextLineChunkFTFont)
        assert text_chunk.text == "Hello World"

    def test_set_text(self, _init_pygame: None,
                      default_ui_manager: UIManager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None

        text_box.set_text("<b>Changed text</b>")
        assert text_box.image is not None

    def test_kwargs_set_text(self, _init_pygame, default_ui_manager,
                             _display_surface_return_none):
        i18n.add_translation('translation.test_hello', 'Hello %{name}')
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        text_box.set_text("translation.test_hello", text_kwargs={"name": "World"})
        assert text_box.image is not None
        text_chunk = text_box.text_box_layout.layout_rows[0].items[0]
        assert isinstance(text_chunk, TextLineChunkFTFont)
        assert text_chunk.text == "Hello World"

    def test_clear(self, _init_pygame: None,
                   default_ui_manager: UIManager,
                   _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None

        text_box.clear()
        assert text_box.image is not None

    def test_creation_grow_to_fit_width(self, _init_pygame: None,
                                        default_ui_manager: UIManager,
                                        _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>. Hey hey hey, what is this? More text padding this "
                                       "out a little."
                                       "Well OK.",
                             relative_rect=pygame.Rect(100, 100, -1, 50),
                             manager=default_ui_manager)
        assert text_box.image is not None and text_box.rect.width == 808

    def test_creation_and_rebuild_with_scrollbar(self, _init_pygame: None,
                                                 default_ui_manager: UIManager,
                                                 _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'noto_sans', 'html_size': 4.5, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 4.5, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'italic'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'bold_italic'},
                                          {'name': 'noto_sans', 'html_size': 4, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 4, 'style': 'italic'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'bold_italic'}])
        text_box = UITextBox(html_text=''
                                       '<font color=regular_text><font color=#E784A2 size=4.5><br><b><u>Lorem</u>'
                                       '<br><br><br>'
                                       'ipsum dolor sit amet</b></font>,'
                                       ' <b><a href="test">consectetur</a></b> adipiscing elit. in a flibb de '
                                       'dib do '
                                       '<p>rub a la clob slip the perry tin fo glorp yip dorp'
                                       'skorp si pork flum de dum be '
                                       '<shadow size=1 offset=0,0 color=#306090>dung</shadow>, '
                                       'slob be robble glurp destination flum'
                                       ' kin slum. </p>'
                                       'Ram slim gordo, fem tulip squirrel slippers save socks certainly.<br>'
                                       'Vestibulum in <i>commodo me</i> tellus in nisi finibus a sodales.<br>'
                                       'Vestibulum'
                                       '<font size=2>hendrerit mi <i>sed nulla</i> scelerisque</font>, posuere '
                                       'ullamcorper '
                                       'sem pulvinar.'
                                       'Nulla at pulvinar a odio, a dictum dolor.<br>Maecenas at <font size=6><b>'
                                       'tellus a'
                                       'tortor. a<br>'
                                       '<img src="tests/data/images/test_emoji.png" float=left '
                                       'padding="5px 10px 5px 5px">'
                                       '<img src="tests/data/images/test_emoji.png" float=right '
                                       'padding="5px 10px">'
                                       '<img src="tests/data/images/test_emoji.png" '
                                       'padding="5px">'
                                       'In <i>bibendum</i> orci et velit</b> gravida lacinia.<br><br>'
                                       'In hac a habitasse to platea dictumst.<br>'
                                       '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec porttitor.'
                                       '<br>Morbi '
                                       'accumsan, lectus at '
                                       'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                                       'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                                       'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet on '
                                       'pharetra a ante '
                                       'sollicitudin.</font></font>'
                                       '<br><br>'
                                       '<b>consectetur</b> adipiscing elit. in a<br>'
                                       'Vestibulum in <i>commodo me</i> tellus in nisi finibus a sodales.<br>'
                                       'Vestibulum <font size=2>hendrerit mi <i>sed nulla</i> scelerisque</font>, '
                                       'posuere ullamcorper sem pulvinar. '
                                       'Nulla at pulvinar a odio, a dictum dolor.<br>'
                                       'Maecenas at <font size=6><b>tellus a tortor. a<br>'
                                       'In <i>bibendum</i> orci et velit</b> gravida lacinia.<br><br>'
                                       'In hac a habitasse to platea dictumst.<br>'
                                       '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec '
                                       'porttitor.<br>Morbi '
                                       'accumsan, lectus at'
                                       'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                                       'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                                       'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet on '
                                       'pharetra a ante '
                                       'sollicitudin.</font></font>',
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)

        text_box.rebuild()

        assert text_box.image is not None

    def test_create_too_narrow_textbox_for_font(self, _init_pygame: None,
                                                default_ui_manager: UIManager,
                                                _display_surface_return_none):
        with pytest.warns(UserWarning, match="Unable to split word into chunks because text box is too narrow"):
            with pytest.raises(RuntimeError, match="Row longer than layout"):
                text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                               'LLALAALALA ALALA ALAL ALA'
                                               'LAALA ALALA ALALA AAaal aa'
                                               'ALALAa laalal alalal alala'
                                               '<a>alalalala</a> alalalalalal alal'
                                               'alalalala alala alalala ala'
                                               'alalalalal lalal alalalal al',
                                     relative_rect=pygame.Rect(100, 100, 5, 50),
                                     manager=default_ui_manager)

                assert text_box.image is not None

    def test_kill(self, _init_pygame: None, default_ui_manager: UIManager,
                  _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'noto_sans', 'html_size': 4.5, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 4.5, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'italic'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'regular'},
                                          {'name': 'noto_sans', 'html_size': 6, 'style': 'bold_italic'},
                                          {'name': 'noto_sans', 'html_size': 4, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 4, 'style': 'italic'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'bold'},
                                          {'name': 'noto_sans', 'html_size': 2, 'style': 'bold_italic'}])
        text_box = UITextBox(html_text=''
                                       '<font color=regular_text><font color=#E784A2 size=4.5><br><b><u>Lorem</u>'
                                       '<br><br><br>'
                                       'ipsum dolor sit amet</b></font>,'
                                       ' <b><a href="test">consectetur</a></b> adipiscing elit. in a flibb de '
                                       'dib do '
                                       'rub a la clob slip the perry tin fo glorp yip dorp'
                                       'skorp si pork flum de dum be dung, slob be robble glurp destination flum '
                                       'kin slum. '
                                       'Ram slim gordo, fem tulip squirrel slippers save socks certainly.<br>'
                                       'Vestibulum in <i>commodo me</i> tellus in nisi finibus a sodales.<br>'
                                       'Vestibulum'
                                       '<font size=2>hendrerit mi <i>sed nulla</i> scelerisque</font>, posuere '
                                       'ullamcorper '
                                       'sem pulvinar.'
                                       'Nulla at pulvinar a odio, a dictum dolor.<br>Maecenas at <font size=6><b>'
                                       'tellus a'
                                       'tortor. a<br>'
                                       'In <i>bibendum</i> orci et velit</b> gravida lacinia.<br><br>'
                                       'In hac a habitasse to platea dictumst.<br>'
                                       '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec porttitor.'
                                       '<br>Morbi '
                                       'accumsan, lectus at '
                                       'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                                       'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                                       'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet on '
                                       'pharetra a ante '
                                       'sollicitudin.</font></font>'
                                       '<br><br>'
                                       '<b>consectetur</b> adipiscing elit. in a<br>'
                                       'Vestibulum in <i>commodo me</i> tellus in nisi finibus a sodales.<br>'
                                       'Vestibulum <font size=2>hendrerit mi <i>sed nulla</i> scelerisque</font>, '
                                       'posuere ullamcorper sem pulvinar. '
                                       'Nulla at pulvinar a odio, a dictum dolor.<br>'
                                       'Maecenas at <font size=6><b>tellus a tortor. a<br>'
                                       'In <i>bibendum</i> orci et velit</b> gravida lacinia.<br><br>'
                                       'In hac a habitasse to platea dictumst.<br>'
                                       '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec '
                                       'porttitor.<br>Morbi '
                                       'accumsan, lectus at'
                                       'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                                       'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                                       'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet '
                                       'on pharetra a ante '
                                       'sollicitudin.</font></font>',
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)

        assert len(default_ui_manager.get_root_container().elements) == 3
        assert len(default_ui_manager.get_sprite_group().sprites()) == 7
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container(),
                                                                   text_box,
                                                                   text_box.scroll_bar,
                                                                   text_box.scroll_bar.button_container,
                                                                   text_box.scroll_bar.top_button,
                                                                   text_box.scroll_bar.bottom_button,
                                                                   text_box.scroll_bar.sliding_button]
        text_box.kill()
        text_box.update(0.01)
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container()]

    def test_on_fresh_drawable_shape_ready(self, _init_pygame: None,
                                           default_ui_manager: UIManager,
                                           _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala alala alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 100, 100),
                             manager=default_ui_manager)
        text_box.on_fresh_drawable_shape_ready()

        assert text_box.background_surf is not None

    def test_set_position_with_scrollbar(self, _init_pygame: None,
                                         default_ui_manager: UIManager,
                                         _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala alala alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 100, 100),
                             manager=default_ui_manager)
        text_box.set_position(pygame.math.Vector2(0.0, 0.0))
        assert text_box.rect.topleft == (0, 0)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (92, 8)}))
        # if we successfully clicked on the moved text box scroll bar then this button should be True
        assert text_box.scroll_bar.top_button.held is True

    def test_set_relative_position_with_scrollbar(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala alala alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.set_relative_position(pygame.math.Vector2(0.0, 0.0))
        assert text_box.rect.topleft == (0, 0)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (142, 8)}))
        # if we successfully clicked on the moved text box
        # scroll bar then this button should be True
        assert text_box.scroll_bar.top_button.held is True

    def test_update_with_scrollbar(self, _init_pygame: None,
                                   default_ui_manager: UIManager,
                                   _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.scroll_bar.has_moved_recently = True
        text_box.update(5.0)
        assert text_box.image is not None

        text_box.set_dimensions((0, 0))
        text_box.update(0.02)

        text_box.set_dimensions((150, 200))
        text_box.update(0.02)
        text_box.update(0.02)
        text_box.update(0.2)

        # trigger rebuild from update
        text_box.should_trigger_full_rebuild = True
        text_box.full_rebuild_countdown = 0.0
        text_box.update(0.01)
        assert text_box.image is not None

    def test_update_without_scrollbar(self, _init_pygame: None,
                                      default_ui_manager: UIManager,
                                      _display_surface_return_none: None):
        text_box = UITextBox(html_text='<a href=None>lalaLAlalala</a>',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)
        default_ui_manager.mouse_position = (20, 15)
        text_box.update(5.0)
        default_ui_manager.mouse_position = (200, 200)
        text_box.update(5.0)

        assert text_box.image is not None

    def test_redraw_from_text_block_with_scrollbar(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.redraw_from_text_block()

        assert text_box.image is not None

        text_box.rect.width = 0
        text_box.redraw_from_text_block()  # should return

        assert text_box.image is not None

    def test_redraw_from_text_block_no_scrollbar(self, _init_pygame: None,
                                                 default_ui_manager: UIManager,
                                                 _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.redraw_from_text_block()
        assert text_box.image is not None

    def test_redraw_from_chunks_with_scrollbar(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.redraw_from_chunks()
        assert text_box.image is not None

    def test_full_redraw_with_scrollbar(self, _init_pygame: None,
                                        default_ui_manager: UIManager,
                                        _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.full_redraw()
        assert text_box.image is not None

    def test_select_with_scrollbar(self, _init_pygame: None,
                                   default_ui_manager: UIManager,
                                   _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        default_ui_manager.set_focus_set(text_box.get_focus_set())
        assert text_box.scroll_bar.is_focused is True

    def test_set_active_effect_typing(self, _init_pygame: None, default_ui_manager: UIManager,
                                      _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal <effect id=test>alalalal</effect> al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        text_box.active_text_effect.text_changed = True
        text_box.update(5.0)
        assert isinstance(text_box.active_text_effect, pygame_gui.core.text.TypingAppearEffect)

        # try setting a nonsense effect on a chunk
        with pytest.warns(UserWarning, match="Unsupported effect name: blork for text chunk"):
            text_box.set_active_effect(effect_type=UITextEffectType('blork'), effect_tag='test')

    def test_set_active_effect_fade_in(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_IN)
        text_box.update(5.0)
        assert isinstance(text_box.active_text_effect, pygame_gui.core.text.FadeInEffect)

    def test_set_active_effect_fade_out(self, _init_pygame: None, default_ui_manager: UIManager,
                                        _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_OUT)
        text_box.update(5.0)
        assert isinstance(text_box.active_text_effect, pygame_gui.core.text.FadeOutEffect)

    def test_set_active_effect_invalid(self, _init_pygame: None,
                                       default_ui_manager: UIManager,
                                       _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        with pytest.warns(UserWarning, match="Unsupported effect name"):
            text_box.set_active_effect("ghost_text")

    def test_set_active_effect_none(self, _init_pygame: None,
                                    default_ui_manager: UIManager,
                                    _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)

        text_box.set_active_effect(None)
        assert text_box.active_text_effect is None

    def test_set_active_effect_with_word_split(self, _init_pygame: None,
                                               _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_non_default.json"))
        manager.preload_fonts([{"name": "noto_sans", "point_size": 10, "style": "regular"},
                               {'name': 'noto_sans', 'point_size': 10, 'style': 'bold'},
                               {"name": "noto_sans", "point_size": 10, "style": "italic"},
                               {"name": "noto_sans", "point_size": 10, "style": "bold_italic"}])
        htm_text_block_2 = UITextBox('<font face=noto_sans size=2 color=#000000>'
                                     '<b>Hey, What the heck!</b>'
                                     '<br><br>'
                                     'This is some <a href="test">text</a> in a different box,'
                                     ' hooray for variety - '
                                     'if you want then you should put a ring upon it. '
                                     '<body bgcolor=#990000>What if we do a really long word?'
                                     '</body> '
                                     '<b><i>derp FALALALALALALALXALALALXALALALALAAPaaaaarp'
                                     ' gosh</b></i></font>',
                                     pygame.Rect((0, 0), (250, 200)),
                                     manager=manager,
                                     object_id="#text_box_2")
        htm_text_block_2.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        htm_text_block_2.active_text_effect.text_changed = True
        htm_text_block_2.update(5.0)
        htm_text_block_2.update(5.0)
        assert isinstance(htm_text_block_2.active_text_effect, pygame_gui.core.text.TypingAppearEffect)

    def test_process_event_mouse_buttons_with_scrollbar(self, _init_pygame: None,
                                                        default_ui_manager: UIManager,
                                                        _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        processed_down_event = text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1, 'pos': (30, 15)}))
        text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (80, 15)}))

        assert processed_down_event is True

    def test_process_event_mouse_buttons_no_scrollbar(self, _init_pygame: None,
                                                      default_ui_manager: UIManager,
                                                      _display_surface_return_none: None):
        text_box = UITextBox(html_text='<a href=none>alalaadads<a/>',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        processed_down_event = text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1, 'pos': (20, 15)}))
        text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (20, 15)}))

        assert processed_down_event is True

    def test_rebuild(self, _init_pygame,
                     default_ui_manager: UIManager,
                     _display_surface_return_none):
        text_box = UITextBox(html_text='hello',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        text_box.rebuild()

        assert text_box.image is not None

        # try with 0 height rect, should return
        text_box.rect.height = 0
        text_box.rebuild()

        assert text_box.image is not None

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_non_default.json"))

        manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                               {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=noto_sans>Some "
                                       "<font color=regular_text>text</font> "
                                       "in a <b>bold box</b> <a>using</a> "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        text_box.redraw_from_chunks()
        text_box.full_redraw()
        assert text_box.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_bad_values.json"))

        manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                               {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=noto_sans>Some text in a <b>bold box</b> using "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        assert text_box.image is not None

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al'
                                       'al alalalal lfed alal alal alal al'
                                       'ala lalalal lasda lal a lalalal slapl'
                                       'alalala lal la blop lal alal aferlal al',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        text_box.set_dimensions((200, 80))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (195, 75)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert text_box.scroll_bar.bottom_button.held is True

    def test_create_very_short_text_box(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):
        x = 640
        y = 360
        width = 320
        height = 10  # height will auto increase
        text = "this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=True,
                             starting_height=100,
                             object_id="screen_message")

        assert text_box.rect.height != 10

        x = 640
        y = 360
        width = 320
        height = 0  # height will auto increase
        text = "this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=True,
                             starting_height=100,
                             object_id="screen_message")

        assert text_box.rect.height != 0

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        text_box.disable()

        assert text_box.is_enabled is False
        assert text_box.scroll_bar.is_enabled is False

        # process a mouse button down event
        text_box.scroll_bar.bottom_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': 1, 'pos': text_box.scroll_bar.bottom_button.rect.center}))

        text_box.scroll_bar.update(0.1)

        # process a mouse button up event
        text_box.scroll_bar.bottom_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP,
                               {'button': 1, 'pos': text_box.scroll_bar.bottom_button.rect.center}))

        assert text_box.scroll_bar.scroll_position == 0.0

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        text_box.disable()
        text_box.enable()

        assert text_box.is_enabled is True
        assert text_box.scroll_bar.is_enabled is True

        # process a mouse button down event
        text_box.scroll_bar.bottom_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': 1, 'pos': text_box.scroll_bar.bottom_button.rect.center}))

        text_box.scroll_bar.update(0.1)

        # process a mouse button up event
        text_box.scroll_bar.bottom_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP,
                               {'button': 1, 'pos': text_box.scroll_bar.bottom_button.rect.center}))

        assert text_box.scroll_bar.scroll_position != 0.0

    def test_show_without_scrollbar(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        x = 640
        y = 360
        width = 320
        height = 100
        text = "this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=False,
                             starting_height=100,
                             object_id="screen_message",
                             visible=0)

        assert text_box.visible == 0

        assert text_box.scroll_bar is None

        text_box.show()

        assert text_box.visible == 1

        assert text_box.scroll_bar is None

    def test_show_with_scrollbar(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        x = 640
        y = 360
        width = 100
        height = 32
        text = "this is a test, this is a test, this is a test, this is a test, this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=False,
                             starting_height=100,
                             object_id="screen_message",
                             visible=0)

        assert text_box.visible == 0

        assert text_box.scroll_bar.visible == 0
        assert text_box.scroll_bar.button_container.visible == 0
        assert text_box.scroll_bar.sliding_button.visible == 0
        assert text_box.scroll_bar.top_button.visible == 0
        assert text_box.scroll_bar.bottom_button.visible == 0

        text_box.show()

        assert text_box.visible == 1

        assert text_box.scroll_bar.visible == 1
        assert text_box.scroll_bar.button_container.visible == 1
        assert text_box.scroll_bar.sliding_button.visible == 1
        assert text_box.scroll_bar.top_button.visible == 1
        assert text_box.scroll_bar.bottom_button.visible == 1

    def test_hide_without_scrollbar(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        x = 640
        y = 360
        width = 320
        height = 100
        text = "this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=False,
                             starting_height=100,
                             object_id="screen_message")

        assert text_box.visible == 1

        assert text_box.scroll_bar is None

        text_box.hide()

        assert text_box.visible == 0

        assert text_box.scroll_bar is None

    def test_hide_with_scrollbar(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        x = 640
        y = 360
        width = 100
        height = 32
        text = "this is a test, this is a test, this is a test, this is a test, this is a test, this is a test"

        rect = pygame.Rect((x, y), (width, height))

        text_box = UITextBox(html_text=text,
                             relative_rect=rect,
                             manager=default_ui_manager,
                             wrap_to_height=False,
                             starting_height=100,
                             object_id="screen_message")

        assert text_box.visible == 1

        assert text_box.scroll_bar.visible == 1
        assert text_box.scroll_bar.button_container.visible == 1
        assert text_box.scroll_bar.sliding_button.visible == 1
        assert text_box.scroll_bar.top_button.visible == 1
        assert text_box.scroll_bar.bottom_button.visible == 1

        text_box.hide()

        assert text_box.visible == 0

        assert text_box.scroll_bar.visible == 0
        assert text_box.scroll_bar.button_container.visible == 0
        assert text_box.scroll_bar.sliding_button.visible == 0
        assert text_box.scroll_bar.top_button.visible == 0
        assert text_box.scroll_bar.bottom_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)
        text_box = UITextBox(html_text="some test text",
                             relative_rect=pygame.Rect(100, 100, 400, 400),
                             manager=manager,
                             wrap_to_height=False,
                             starting_height=100,
                             object_id="screen_message",
                             visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        text_box.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        text_box.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_on_locale_changed(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       'alalalalal lalal alalalal al'
                                       'al alalalal lfed alal alal alal al'
                                       'ala lalalal lasda lal a lalalal slapl'
                                       'alalala lal la blop lal alal aferlal al',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        default_ui_manager.set_locale('fr')

        default_ui_manager.set_locale('ja')

        assert text_box.image is not None

    def test_text_owner_interface(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala <a href=none>alala<a/> '
                                       'alalala ala'
                                       '<a href=none>alalalalal lalal alalalal al'
                                       'al alalalal lfed alal alal alal al'
                                       'ala lalalal lasda lal a lalalal slapl'
                                       'alalala lal la blop lal alal aferlal al</a>',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)

        # these do nothing right now for full block effects
        text_box.set_text_offset_pos((0, 0))
        text_box.set_text_rotation(0)
        text_box.set_text_scale(0)

        assert text_box.image is not None

    def test_pre_parsing(self, _init_pygame: None,
                         default_ui_manager: UIManager,
                         _display_surface_return_none):
        text_box = UITextBox(html_text="Some text\n"
                                       "On different lines with backslash n\n"
                                       "Done.",
                             relative_rect=pygame.Rect(100, 100, 500, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None
        assert len(text_box.text_box_layout.layout_rows) == 3

    def test_process_event_text_ctrl_c(self, _init_pygame: None,
                                       _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextBox(html_text="dan",
                               relative_rect=pygame.Rect(100, 100, 200, 30),
                               manager=manager)

        text_entry.focus()
        text_entry.select_range = [0, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_c,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'c'}))
        text_entry.cursor_on = True

        assert processed_key_event and clipboard_paste() == 'dan'


if __name__ == '__main__':
    pytest.console_main()
