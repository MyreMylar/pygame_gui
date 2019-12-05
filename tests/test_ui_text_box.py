import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox


class TestUITextBox:

    def test_creation(self, _init_pygame: None, default_ui_manager: UIManager):
        default_ui_manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                                          {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000>Some text</font> in a <b>bold box</b> using colours and "
                                       "<i>styles</i>.",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)
        assert text_box.image is not None

    def test_creation_and_rebuild_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'html_size': 4.5, 'style': 'bold'},
                                          {'name': 'fira_code', 'html_size': 4.5, 'style': 'regular'},
                                          {'name': 'fira_code', 'html_size': 2, 'style': 'regular'},
                                          {'name': 'fira_code', 'html_size': 2, 'style': 'italic'},
                                          {'name': 'fira_code', 'html_size': 6, 'style': 'bold'},
                                          {'name': 'fira_code', 'html_size': 6, 'style': 'regular'},
                                          {'name': 'fira_code', 'html_size': 6, 'style': 'bold_italic'},
                                          {'name': 'fira_code', 'html_size': 4, 'style': 'bold'},
                                          {'name': 'fira_code', 'html_size': 4, 'style': 'italic'},
                                          {'name': 'fira_code', 'html_size': 2, 'style': 'bold'},
                                          {'name': 'fira_code', 'html_size': 2, 'style': 'bold_italic'}])
        text_box = UITextBox(html_text=''
                             '<font color=regular_text><font color=#E784A2 size=4.5><br><b><u>Lorem</u><br><br><br>'
                             'ipsum dolor sit amet</b></font>,'
                             ' <b><a href="test">consectetur</a></b> adipiscing elit. in a flibb de dib do '
                             'rub a la clob slip the perry tin fo glorp yip dorp'
                             'skorp si pork flum de dum be dung, slob be robble glurp destination flum kin slum. '
                             'Ram slim gordo, fem tulip squirrel slippers save socks certainly.<br>'
                             'Vestibulum in <i>commodo me</i> tellus in nisi finibus a sodales.<br>Vestibulum'
                             '<font size=2>hendrerit mi <i>sed nulla</i> scelerisque</font>, posuere ullamcorper '
                             'sem pulvinar.'
                             'Nulla at pulvinar a odio, a dictum dolor.<br>Maecenas at <font size=6><b>tellus a'
                             'tortor. a<br>'
                             'In <i>bibendum</i> orci et velit</b> gravida lacinia.<br><br>'
                             'In hac a habitasse to platea dictumst.<br>'
                             '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec porttitor.<br>Morbi '
                             'accumsan, lectus at '
                             'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                             'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                             'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet on pharetra a ante '
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
                             '<font color=#4CD656 size=4>Vivamus I interdum mollis lacus nec porttitor.<br>Morbi '
                             'accumsan, lectus at'
                             'tincidunt to dictum, neque <font color=#879AF6>erat tristique erat</font>, '
                             'sed a tempus for <b>nunc</b> dolor in nibh.<br>'
                             'Suspendisse in viverra dui <i>fringilla dolor laoreet</i>, sit amet on pharetra a ante '
                             'sollicitudin.</font></font>',
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=default_ui_manager)

        text_box.rebuild()

        assert text_box.image is not None

    def test_create_too_narrow_textbox_for_font(self, _init_pygame: None, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match="Unable to split word into chunks because text box is too narrow"):
            text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                           'LLALAALALA ALALA ALAL ALA'
                                           'LAALA ALALA ALALA AAaal aa'
                                           'ALALAa laalal alalal alala'
                                           'alalalala alalalalalal alal'
                                           'alalalala alala alalala ala'
                                           'alalalalal lalal alalalal al',
                                 relative_rect=pygame.Rect(100, 100, 50, 50),
                                 manager=default_ui_manager)

        assert text_box.image is not None

    def test_set_position_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala alala alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 100, 100),
                             manager=default_ui_manager)
        text_box.set_position(pygame.Vector2(0.0, 0.0))
        assert text_box.rect.topleft == (0, 0)

    def test_set_relative_position_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
        text_box = UITextBox(html_text='la la LA LA LAL LAL ALALA'
                                       'LLALAALALA ALALA ALAL ALA'
                                       'LAALA ALALA ALALA AAaal aa'
                                       'ALALAa laalal alalal alala'
                                       'alalalala alalalalalal alal'
                                       'alalalala alala alalala ala'
                                       'alalalalal lalal alalalal al',
                             relative_rect=pygame.Rect(100, 100, 150, 100),
                             manager=default_ui_manager)
        text_box.set_relative_position(pygame.Vector2(0.0, 0.0))
        assert text_box.rect.topleft == (0, 0)

    def test_update_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
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

    def test_update_without_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
        text_box = UITextBox(html_text='<a href=None>lalaLA</a>',
                             relative_rect=pygame.Rect(0, 0, 150, 100),
                             manager=default_ui_manager)
        pygame.mouse.set_pos(20, 15)
        text_box.update(5.0)
        pygame.mouse.set_pos(200, 200 )
        text_box.update(5.0)

        assert text_box.image is not None

    def test_redraw_from_text_block_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
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

    def test_redraw_from_chunks_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
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

    def test_full_redraw_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
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

    def test_select_with_scrollbar(self, _init_pygame: None, default_ui_manager: UIManager):
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
        text_box.select()
        assert text_box.scroll_bar.sliding_button.is_selected is True

    def test_set_active_effect_typing(self, _init_pygame: None, default_ui_manager: UIManager):
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
        text_box.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        text_box.update(5.0)
        assert type(text_box.active_text_effect) == pygame_gui.elements.text.TypingAppearEffect

    def test_set_active_effect_fade_in(self, _init_pygame: None, default_ui_manager: UIManager):
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
        assert type(text_box.active_text_effect) == pygame_gui.elements.text.FadeInEffect

    def test_set_active_effect_fade_out(self, _init_pygame: None, default_ui_manager: UIManager):
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
        assert type(text_box.active_text_effect) == pygame_gui.elements.text.FadeOutEffect

    def test_set_active_effect_invalid(self, _init_pygame: None, default_ui_manager: UIManager):
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
            text_box.set_active_effect(pygame_gui.UI_BUTTON_PRESSED)

    def test_set_active_effect_none(self, _init_pygame: None, default_ui_manager: UIManager):
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

    def test_process_event_mouse_buttons(self, _init_pygame: None, default_ui_manager: UIManager,
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
        processed_up_event = text_box.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                       {'button': 1, 'pos': (80, 15)}))

        assert processed_down_event is True

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_non_default.json"))

        manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                               {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=fira_code>Some text in a <b>bold box</b> using "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        assert text_box.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_text_box_bad_values.json"))

        manager.preload_fonts([{"name": "fira_code", "size:": 14, "style": "bold"},
                               {"name": "fira_code", "size:": 14, "style": "italic"}])
        text_box = UITextBox(html_text="<font color=#FF0000 face=fira_code>Some text in a <b>bold box</b> using "
                                       "colours and <i>styles</i>.</font>",
                             relative_rect=pygame.Rect(100, 100, 200, 300),
                             manager=manager)
        assert text_box.image is not None
