import os

import pygame
import pytest
import platform

import pygame_gui

from pygame_gui.core.utility import clipboard_paste, clipboard_copy
from pygame_gui.elements.ui_text_entry_box import UITextEntryBox
from pygame_gui.ui_manager import UIManager
from pygame_gui.core import UIContainer


class TestUITextEntryBox:

    def test_creation(self, _init_pygame: None,
                      default_ui_manager: UIManager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextEntryBox(
            initial_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                         "<i>styles</i>.",
            relative_rect=pygame.Rect(100, 100, 200, 300),
            manager=default_ui_manager)
        assert text_box.image is not None

    def test_set_text(self, _init_pygame: None,
                      default_ui_manager: UIManager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextEntryBox(
            initial_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                         "<i>styles</i>.",
            relative_rect=pygame.Rect(100, 100, 200, 300),
            manager=default_ui_manager)
        assert text_box.image is not None

        text_box.set_text("<b>Changed text</b>")
        assert text_box.image is not None

    def test_clear(self, _init_pygame: None,
                   default_ui_manager: UIManager,
                   _display_surface_return_none):
        default_ui_manager.preload_fonts([{"name": "noto_sans", "size:": 14, "style": "bold"},
                                          {"name": "noto_sans", "size:": 14, "style": "italic"}])
        text_box = UITextEntryBox(
            initial_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
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
        text_box = UITextEntryBox(
            initial_text="Some text in a  box not using colours and styles. Hey hey hey, what is this?"
                         "More text padding this out a little. Well OK.",
            relative_rect=pygame.Rect(100, 100, -1, 50),
            manager=default_ui_manager)
        assert text_box.image is not None and text_box.rect.width == 804

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
        text_box = UITextEntryBox(initial_text=''
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
        # narrow text boxes are fine with no dashes between split words

        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text=''
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='<a href=None>lalaLAlalala</a>',
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA',
                                  relative_rect=pygame.Rect(100, 100, 150, 100),
                                  manager=default_ui_manager)
        text_box.redraw_from_text_block()
        assert text_box.image is not None

    def test_redraw_from_chunks_with_scrollbar(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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

    def test_set_active_effect_fade_in(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        assert type(text_box.active_text_effect) == pygame_gui.core.text.FadeInEffect

    def test_set_active_effect_fade_out(self, _init_pygame: None, default_ui_manager: UIManager,
                                        _display_surface_return_none: None):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        assert type(text_box.active_text_effect) == pygame_gui.core.text.FadeOutEffect

    def test_set_active_effect_invalid(self, _init_pygame: None,
                                       default_ui_manager: UIManager,
                                       _display_surface_return_none):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        htm_text_block_2 = UITextEntryBox(initial_text='<font face=noto_sans size=2 color=#000000>'
                                          '<b>Hey, What the heck!</b>'
                                          '<br><br>'
                                          'This is some <a href="test">text</a> in a different box,'
                                          ' hooray for variety - '
                                          'if you want then you should put a ring upon it. '
                                          '<body bgcolor=#990000>What if we do a really long word?'
                                          '</body> '
                                          '<b><i>derp FALALALALALALALXALALALXALALALALAAPaaaaarp'
                                          ' gosh</b></i></font>',
                                          relative_rect=pygame.Rect((0, 0), (250, 200)),
                                          manager=manager,
                                          object_id="#text_box_2")
        htm_text_block_2.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        htm_text_block_2.active_text_effect.text_changed = True
        htm_text_block_2.update(5.0)
        htm_text_block_2.update(5.0)
        assert type(htm_text_block_2.active_text_effect) == pygame_gui.core.text.TypingAppearEffect

    def test_process_event_mouse_buttons_with_scrollbar(self, _init_pygame: None,
                                                        default_ui_manager: UIManager,
                                                        _display_surface_return_none: None):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='<a href=none>alalaadads<a/>',
                                  relative_rect=pygame.Rect(0, 0, 150, 100),
                                  manager=default_ui_manager)

        processed_down_event = text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1, 'pos': (20, 15)}))
        text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (20, 15)}))

        assert processed_down_event is True

    def test_rebuild(self, _init_pygame,
                     default_ui_manager: UIManager,
                     _display_surface_return_none):
        text_box = UITextEntryBox(initial_text='hello',
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
        text_box = UITextEntryBox(initial_text="<font color=#FF0000 face=noto_sans>Some "
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
        text_box = UITextEntryBox(
            initial_text="<font color=#FF0000 face=noto_sans>Some text in a <b>bold box</b> using "
                         "colours and <i>styles</i>.</font>",
            relative_rect=pygame.Rect(100, 100, 200, 300),
            manager=manager)
        assert text_box.image is not None

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.focus()
        text_entry.disable()

        assert text_entry.is_enabled is False
        # process a mouse button down event
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_d,
                                                                           'mod': 0,
                                                                           'unicode': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0,
                                                                     'unicode': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_n, 'mod': 0,
                                                                     'unicode': 'n'}))

        assert processed_key_event is False and text_entry.get_text() == ''

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.disable()

        text_entry.focus()
        text_entry.enable()

        assert text_entry.is_enabled is True
        text_entry.focus()
        # process a mouse button down event
        processed_text_input_event = text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'n'}))

        assert processed_text_input_event is True and text_entry.get_text() == 'dan'

    def test_on_locale_changed(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text='la la LA LA LAL LAL ALALA'
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
        text_box = UITextEntryBox(initial_text="Some text\n"
                                               "On different lines with backslash n\n"
                                               "Done.",
                                  relative_rect=pygame.Rect(100, 100, 500, 300),
                                  manager=default_ui_manager)
        assert text_box.image is not None
        assert len(text_box.text_box_layout.layout_rows) == 3

    def test_rebuild_select_area_1(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_2(self, _init_pygame,
                                            _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_set_text_rebuild_select_area_3(self, _init_pygame,
                                            _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text("GOLDEN GOD")
        text_entry.select_range = [4, 7]
        text_entry.rebuild()

        assert text_entry.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_set_text_rebuild_select_area_4(self, _init_pygame,
                                            _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text("GOLD")
        text_entry.select_range = [0, 2]
        text_entry.rebuild()

        assert text_entry.image is not None

    def test_focus(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.focus()

        assert text_entry.image is not None

    def test_unfocus(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.unfocus()

        assert text_entry.image is not None

    def test_process_event_text_entered_success(self, _init_pygame: None,
                                                default_ui_manager: UIManager,
                                                _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.focus()

        processed_text_input_event = text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'd'}))

        text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'a'}))
        text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'n'}))

        assert processed_text_input_event and text_entry.get_text() == 'dan'

    def test_process_event_text_entered_with_select_range(self, _init_pygame: None,
                                                          default_ui_manager: UIManager,
                                                          _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('Hours and hours of fun writing tests')
        text_entry.focus()
        text_entry.select_range = [1, 9]

        # process a text input event
        processed_text_input_event = text_entry.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': 'o'}))

        assert (processed_text_input_event is True and
                text_entry.get_text() == 'Ho hours of fun writing tests')

    def test_process_event_text_ctrl_c(self, _init_pygame: None,
                                       _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_c,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'c'}))
        text_entry.cursor_on = True

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_text_ctrl_v(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 0]
        text_entry.edit_position = 3
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'danan'

    def test_process_event_text_ctrl_v_nothing(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        clipboard_copy('')
        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 0]
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_ctrl_v_at_limit(self, _init_pygame: None, default_ui_manager: UIManager,
                                           _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.length_limit = 3
        text_entry.select_range = [0, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))

        text_entry.set_text('bob')
        text_entry.focus()
        text_entry.select_range = [0, 3]
        text_entry.edit_position = 0
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dan'

    def test_process_event_text_ctrl_v_select_range(self, _init_pygame: None,
                                                    default_ui_manager: UIManager,
                                                    _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))
        text_entry.select_range = [0, 3]
        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_v,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'v'}))

        assert processed_key_event

        if not platform.system().upper() == "LINUX":
            # copy and paste is unreliable on linux, this part of the test fails fairly regularly there
            assert text_entry.get_text() == 'an'

    def test_process_event_text_ctrl_a(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_c,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'c'}))

        text_entry.select_range = [0, 0]
        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and text_entry.get_text() == 'dandan'

    def test_process_event_text_ctrl_x(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_a,
                                                                           'mod': pygame.KMOD_CTRL,
                                                                           'unicode': 'a'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_x,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'x'}))

        text_entry.process_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_v,
                                                                     'mod': pygame.KMOD_CTRL,
                                                                     'unicode': 'v'}))

        assert processed_key_event and clipboard_paste() == 'dan'

    def test_process_event_mouse_buttons(self, _init_pygame: None, default_ui_manager: UIManager,
                                         _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (30, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                         {'button': 1,
                                                                          'pos': (80, 15)}))

        assert processed_down_event
        assert processed_up_event
        assert text_entry.select_range == [3, 10]

    def test_process_event_mouse_button_double_click(self, _init_pygame: None,
                                                     default_ui_manager: UIManager,
                                                     _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [7, 14])

        text_entry.set_text('')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 0])

    def test_process_event_mouse_button_double_click_in_empty_space(
            self, _init_pygame: None,
            default_ui_manager: UIManager,
            _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('                      dan')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (90, 15)}))
        processed_up_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                         {'button': 1,
                                                                          'pos': (90, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 0])

    def test_process_event_mouse_button_double_click_first_word(self, _init_pygame: None,
                                                                default_ui_manager: UIManager,
                                                                _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': pygame.BUTTON_LEFT,
                                                        'pos': (15, 15)}))
        processed_up_event = text_entry.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': pygame.BUTTON_LEFT,
                                                        'pos': (15, 15)}))

        assert (processed_down_event and processed_up_event and text_entry.select_range == [0, 3])

    def test_process_event_mouse_button_up_outside(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan is amazing')
        processed_down_event = text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                           {'button': 1,
                                                                            'pos': (30, 15)}))
        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                                           'pos': (80, 50)}))

        assert processed_down_event and text_entry.selection_in_progress is False

    def test_process_event_text_return(self, _init_pygame: None, default_ui_manager: UIManager,
                                       _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RETURN}))

        assert processed_key_event

    def test_process_event_text_right(self, _init_pygame: None, default_ui_manager: UIManager,
                                      _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': 0}))

        assert processed_key_event

    def test_process_event_text_right_actually_move(self, _init_pygame: None,
                                                    default_ui_manager: UIManager,
                                                    _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.edit_position = 2
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.edit_position == 3

        text_entry.edit_position = 1
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, 2]
        assert text_entry.edit_position == 2

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, 3]
        assert text_entry.edit_position == 3

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, 2]
        assert text_entry.edit_position == 2

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 2

        text_entry.edit_position = 0
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.edit_position == 3

        text_entry.edit_position = 0
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': pygame.KMOD_CTRL | pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [0, 3]
        assert text_entry.edit_position == 3

    def test_process_event_text_left(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        assert text_entry.edit_position == 3

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.edit_position == 2

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, 2]
        assert text_entry.edit_position == 1

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [0, 2]
        assert text_entry.edit_position == 0

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, 2]
        assert text_entry.edit_position == 1

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 1

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.edit_position == 0

        text_entry.edit_position = 3
        text_entry.focus()

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': pygame.KMOD_CTRL | pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [0, 3]
        assert text_entry.edit_position == 0

    def test_process_event_text_down(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('daniel\nmulti-line\ntext')
        text_entry.edit_position = 3
        text_entry.focus()
        text_entry.update(0.1)

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DOWN,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.edit_position == 10

        text_entry.edit_position = 3
        text_entry.focus()
        text_entry.update(0.1)

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DOWN,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [3, 10]
        assert text_entry.edit_position == 10

    def test_process_event_text_up(self, _init_pygame: None, default_ui_manager: UIManager,
                                   _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('daniel\nmulti-line\ntext')
        text_entry.edit_position = 10
        text_entry.focus()
        text_entry.update(0.1)

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_UP,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.edit_position == 3

        text_entry.edit_position = 10
        text_entry.focus()
        text_entry.update(0.1)

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_UP,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [3, 10]
        assert text_entry.edit_position == 3

    def test_process_event_home(self, _init_pygame: None, default_ui_manager: UIManager,
                                _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_HOME,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 0

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_HOME,
                                                                           'mod': pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 0

        text_entry.set_text('daniel\nmulti-line\ntext')
        text_entry.edit_position = 3
        text_entry.focus()
        text_entry.select_range = [1, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_HOME,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [0, 1]
        assert text_entry.edit_position == 0

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_HOME,
                                                                           'mod': pygame.KMOD_SHIFT | pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.select_range == [0, 1]
        assert text_entry.edit_position == 0

    def test_process_event_end(self, _init_pygame: None, default_ui_manager: UIManager,
                               _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_END,
                                                                           'mod': 0}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 3

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_END,
                                                                           'mod': pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.select_range == [0, 0]
        assert text_entry.edit_position == 3

        text_entry.set_text('daniel\nmulti-line\ntext')
        text_entry.edit_position = 3
        text_entry.focus()
        text_entry.select_range = [1, 3]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_END,
                                                                           'mod': pygame.KMOD_SHIFT}))

        assert processed_key_event
        assert text_entry.select_range == [1, len("daniel")]
        assert text_entry.edit_position == len("daniel")

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_END,
                                                                           'mod': pygame.KMOD_SHIFT | pygame.KMOD_CTRL}))

        assert processed_key_event
        assert text_entry.select_range == [1, len("daniel\nmulti-line\ntext")]
        assert text_entry.edit_position == len("daniel\nmulti-line\ntext")

    def test_process_event_text_right_select_range(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_RIGHT,
                                                                           'mod': 0}))

        assert processed_key_event

    def test_process_event_text_left_select_range(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_LEFT,
                                                                           'mod': 0}))

        assert processed_key_event

    def test_process_event_delete_select_range(self, _init_pygame: None,
                                               default_ui_manager: UIManager,
                                               _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [0, 2]

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DELETE}))

        assert processed_key_event

    def test_process_event_delete(self, _init_pygame: None, default_ui_manager: UIManager,
                                  _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.edit_position = 1

        processed_key_event = text_entry.process_event(pygame.event.Event(pygame.KEYDOWN,
                                                                          {'key': pygame.K_DELETE}))

        assert processed_key_event

    def test_process_event_backspace(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.edit_position = 2
        text_entry.start_text_offset = 1

        processed_key_event = text_entry.process_event(
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE}))

        assert processed_key_event

    def test_process_event_backspace_select_range(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=default_ui_manager)

        text_entry.set_text('dan')
        text_entry.focus()
        text_entry.select_range = [1, 3]

        processed_key_event = text_entry.process_event(
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE}))

        assert processed_key_event

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_redraw_selected_text(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text("Yellow su")
        text_entry.select_range = [3, 8]
        text_entry.start_text_offset = 500

    def test_redraw_selected_text_different_theme(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default_2.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.set_text("Yellow su")
        text_entry.select_range = [3, 9]

    def test_update(self,  _init_pygame, _display_surface_return_none):
        pygame.display.init()

        class MouselessManager(UIManager):
            fixed_mouse_pos = (0, 0)

            def _update_mouse_position(self):
                self.mouse_position = MouselessManager.fixed_mouse_pos

        manager = MouselessManager((800, 600), os.path.join("tests", "data",
                                                            "themes",
                                                            "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.update(0.01)

        assert text_entry.alive()
        assert not manager.text_input_hovered

        MouselessManager.fixed_mouse_pos = (200, 115)
        manager.update(0.01)
        assert manager.text_input_hovered

        text_entry.kill()

        text_entry.update(0.01)

        assert not text_entry.alive()

    def test_update_after_click(self,  _init_pygame, _display_surface_return_none: None, default_ui_manager):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=manager)

        text_entry.set_text('Wow testing is great so amazing')
        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                                             'pos': (30, 15)}))
        default_ui_manager.mouse_position = (70, 15)

        text_entry.update(0.01)

    def test_update_newline_after_click(self,  _init_pygame, _display_surface_return_none: None, default_ui_manager):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 200, 30),
                                    manager=manager)

        text_entry.set_text('Wow testing is great so amazing\n\n')
        text_entry.focus()

        text_entry.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                                             'pos': (30, 15)}))
        default_ui_manager.mouse_position = (70, 15)

        text_entry.update(0.01)

    def test_update_after_long_wait(self,  _init_pygame, _display_surface_return_none):
        pygame.display.init()
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.update(0.01)
        text_entry.update(5.0)

    def test_update_cursor_blink(self,  _init_pygame, _display_surface_return_none: None):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_non_default.json"))
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)

        text_entry.focus()
        text_entry.cursor_blink_delay_after_moving_acc = 10.0
        text_entry.update(0.01)
        text_entry.blink_cursor_time_acc = 10.0
        text_entry.update(0.01)
        text_entry.blink_cursor_time_acc = 10.0
        text_entry.update(0.01)

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_text_entry_line_bad_values.json"))

        text_entry = UITextEntryBox(relative_rect=pygame.Rect(100, 100, 200, 30),
                                    manager=manager)
        assert text_entry.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 150, 30),
                                    container=test_container,
                                    manager=default_ui_manager)

        text_entry.set_position((150.0, 30.0))

        assert (text_entry.relative_rect.topleft == (50, -70) and
                text_entry.drawable_shape.containing_rect.topleft == (150, 30))

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(50, 50, 300, 250),
                                     manager=default_ui_manager)
        text_entry = UITextEntryBox(relative_rect=pygame.Rect(0, 0, 150, 30),
                                    container=test_container,
                                    manager=default_ui_manager)

        text_entry.set_relative_position((50.0, 30.0))

        assert text_entry.rect.topleft == (100, 80)


if __name__ == '__main__':
    pytest.console_main()
