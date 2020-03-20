import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, \
    _display_surface_return_none

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui import UIManager

from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu

class TestUIWindow:
    def test_creation(self, _init_pygame, default_ui_manager):
        UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                 manager=default_ui_manager, element_id='test_window')

    def test_set_blocking(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          allow_double_clicks=True)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': button.rect.center}))
        assert button.held

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': button.rect.center}))

        window.set_blocking(True)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': button.rect.center}))
        assert not button.held

    def test_set_minimum_dimensions(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        window.set_minimum_dimensions((200, 200))
        window.set_dimensions((100, 100))

        assert window.rect.size == (200, 200)

        window.set_minimum_dimensions((100, 100))

        assert window.rect.size == (100, 100)

    def test_set_dimensions(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        assert button.rect.topright == (window.get_container().rect.right - 10,
                                        window.get_container().rect.top + 10)
        assert button.rect.topright == (387, 240)

        window.set_dimensions((300, 400))

        assert button.rect.topright == (window.get_container().rect.right - 10,
                                        window.get_container().rect.top + 10)
        assert button.rect.topright == (487, 240)

    def test_set_relative_position(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        assert button.rect.topright == (387, 240)
        window.set_relative_position((100, 100))
        assert button.rect.topright == (287, 140)

    def test_set_position(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        assert button.rect.topright == (387, 240)
        window.set_position((100, 100))
        assert button.rect.topright == (287, 140)

    def test_process_event(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          object_id='#specific_id_test',
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                {'button': pygame.BUTTON_LEFT,
                                                 'pos': button.rect.center}))
        button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                {'button': pygame.BUTTON_LEFT,
                                                 'pos': button.rect.center}))

        confirm_event_fired = False
        event_object_id = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                    event.ui_element == button):
                confirm_event_fired = True
                event_object_id = event.ui_object_id
        assert confirm_event_fired
        assert event_object_id == 'test_window.#specific_id_test'

        consumed_event = window.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                 {'button': pygame.BUTTON_RIGHT,
                                                                  'pos': window.rect.center}))
        assert consumed_event is True

        window.edge_hovering[0] = True
        consumed_event = window.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                 {'button': pygame.BUTTON_LEFT,
                                                                  'pos': window.rect.topleft}))
        assert consumed_event and window.resizing_mode_active

        consumed_event = window.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                 {'button': pygame.BUTTON_LEFT,
                                                                  'pos': (500, 500)}))
        assert not (consumed_event or window.resizing_mode_active)

        consumed_event = window.process_event(pygame.event.Event(pygame.USEREVENT,
                                                                 {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                                                  'ui_element': window.close_window_button}))
        assert not (consumed_event or window.alive())

    def test_check_clicked_inside(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')
        clicked_inside = window.check_clicked_inside_or_blocking(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                                    {'button': 1, 'pos': (100, 100)}))

        assert clicked_inside is True

    def test_update(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        window.update(time_delta=0.05)

        window.title_bar.held = True
        window.update(time_delta=0.05)
        window.update(time_delta=0.05)
        window.title_bar.held = False
        window.update(time_delta=0.05)

        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(0, 0, 190, 190)
        window.edge_hovering[0] = True
        window.edge_hovering[1] = True
        window.update(time_delta=0.05)
        window.edge_hovering[0] = False
        window.edge_hovering[1] = False
        window.edge_hovering[2] = True
        window.edge_hovering[3] = True
        window.update(time_delta=0.05)

    def test_check_hover(self, _init_pygame, default_ui_manager: UIManager):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window',
                          resizable=True)

        default_ui_manager.mouse_position = window.rect.midleft
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[0]

        default_ui_manager.mouse_position = window.rect.midright
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[2]

        default_ui_manager.mouse_position = window.rect.midtop
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[1]

        default_ui_manager.mouse_position = window.rect.midbottom
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[3]

        default_ui_manager.mouse_position = (800, 800)
        window.resizing_mode_active = True
        assert window.check_hover(0.05, False)
        window.resizing_mode_active = False

        window.is_blocking = True
        assert window.check_hover(0.05, False)
        window.is_blocking = False

        assert not window.check_hover(0.05, False)

    def test_get_top_layer(self, _init_pygame, default_ui_manager):
        window = UIWindow(pygame.Rect(0, 0, 400, 300), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 150, 30),
                              manager=default_ui_manager,
                              container=window)

        assert window.get_top_layer() == 4
        window.update(0.05)
        assert window.get_top_layer() == 6

    def test_change_layer(self, _init_pygame, default_ui_manager):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        assert window.get_top_layer() == 4

        window.change_layer(10)

        assert window.get_top_layer() == 12

        window.update(0.05)

        assert window.get_top_layer() == 12

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface, _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 6
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container(),
                                                                   window,
                                                                   window._window_root_container,
                                                                   window.window_element_container,
                                                                   window.title_bar,
                                                                   window.close_window_button
                                                                   ]
        window.kill()

        confirm_event_fired = False
        event_object_id = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE and
                    event.ui_element == window):
                confirm_event_fired = True
                event_object_id = event.ui_object_id
        assert confirm_event_fired
        assert event_object_id == 'test_window'
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container()]

    def test_rebuild_from_changed_theme_data_non_default(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_window_non_default.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager, element_id='test_window')

        assert window.image is not None

    def test_rebuild_from_changed_theme_data_no_title_bar(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_window_no_title_bar.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager, element_id='test_window')

        assert window.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_window_bad_values.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager, element_id='test_window')

        assert window.image is not None

    def test_stub_methods(self, _init_pygame, default_ui_manager):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window')

        window.focus()
        window.unfocus()
