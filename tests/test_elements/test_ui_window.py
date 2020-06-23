import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui import UIManager

from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIWindow:
    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                 manager=default_ui_manager, element_id='window')

    def test_set_blocking(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                          _display_surface_return_none):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='window')

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

    def test_set_minimum_dimensions(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                    _display_surface_return_none):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

        window.set_minimum_dimensions((200, 200))
        window.set_dimensions((100, 100))

        assert window.rect.size == (200, 200)

        window.set_minimum_dimensions((250, 250))

        assert window.rect.size == (250, 250)

    def test_set_dimensions(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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
        assert button.rect.topright == (374, 253)

        window.set_dimensions((300, 400))

        assert button.rect.topright == (window.get_container().rect.right - 10,
                                        window.get_container().rect.top + 10)
        assert button.rect.topright == (474, 253)

    def test_set_relative_position(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                   _display_surface_return_none):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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

        assert button.rect.topright == (374, 253)
        window.set_relative_position((100, 100))
        assert button.rect.topright == (274, 153)

    def test_set_position(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                          _display_surface_return_none):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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

        assert button.rect.topright == (374, 253)
        window.set_position((100, 100))
        assert button.rect.topright == (274, 153)

    def test_process_event(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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
            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                    event.ui_element == button):
                confirm_event_fired = True
                event_object_id = event.ui_object_id
        assert confirm_event_fired
        assert event_object_id == 'window.#specific_id_test'

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

    def test_check_clicked_inside(self, _init_pygame,
                                  default_ui_manager,
                                  _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)
        clicked_inside = window.check_clicked_inside_or_blocking(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                                    {'button': 1,
                                                                                     'pos': (100, 100)}))

        assert clicked_inside is True

    def test_update(self, _init_pygame, default_ui_manager,
                    _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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

    def test_check_hover(self, _init_pygame, default_ui_manager: UIManager,
                         _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager,
                          resizable=True)

        default_ui_manager.mouse_position = (window.rect.left + window.shadow_width,
                                             window.rect.centery)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[0]

        default_ui_manager.mouse_position = (window.rect.right - window.shadow_width,
                                             window.rect.centery)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[2]

        default_ui_manager.mouse_position = (window.rect.centerx,
                                             window.rect.top + window.shadow_width)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[1]

        default_ui_manager.mouse_position = (window.rect.centerx,
                                             window.rect.bottom - window.shadow_width)
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

    def test_get_top_layer(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        window = UIWindow(pygame.Rect(0, 0, 400, 300), window_display_title="Test Window",
                          manager=default_ui_manager)

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

    def test_change_layer(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

        assert window.get_top_layer() == 4

        window.change_layer(10)

        assert window.get_top_layer() == 12

        window.update(0.05)

        assert window.get_top_layer() == 12

    def test_kill(self, _init_pygame,
                  default_ui_manager: IUIManagerInterface,
                  _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)

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
        assert event_object_id == 'window'
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container()]

    def test_rebuild_from_changed_theme_data_non_default(self, _init_pygame,
                                                         _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_window_non_default.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager)

        assert window.image is not None

    def test_using_theme_prototype(self, _init_pygame,
                                   _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_window_prototype.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager)

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(relative_rect=button_rect,
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager,
                          container=window,
                          anchors={'left': 'right',
                                   'right': 'right',
                                   'top': 'top',
                                   'bottom': 'top'})

        assert window.image is not None
        assert window.shadow_width == 1
        assert window.border_width == 2
        assert window.shape_corner_radius == 10
        assert button.shadow_width == 1
        assert button.border_width == 2
        assert button.shape_corner_radius == 4

    def test_rebuild_from_changed_theme_data_no_title_bar(self, _init_pygame,
                                                          _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_window_no_title_bar.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200), window_display_title="Test Window",
                          manager=manager)

        assert window.title_bar is None
        assert window.close_window_button is None
        assert window.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame,
                                                        _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_window_bad_values.json"))
        window = UIWindow(pygame.Rect(0, 0, 200, 200),
                          window_display_title="Test Window",
                          manager=manager)

        assert window.image is not None

    def test_stub_methods(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        window = UIWindow(pygame.Rect(100, 100, 200, 200),
                          window_display_title="Test Window",
                          manager=default_ui_manager)

        window.focus()
        window.unfocus()

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=window)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=window)

        window.disable()

        assert window.is_enabled is False
        assert window.title_bar.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        window = UIWindow(pygame.Rect(200, 200, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=window)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=window)

        window.disable()
        window.enable()

        assert window.is_enabled is True
        assert window.title_bar.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is True

    def test_show(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        window = UIWindow(pygame.Rect(100, 100, 200, 200),
                          window_display_title="Test Window",
                          manager=default_ui_manager,
                          visible=0)

        assert window.visible == 0

        assert window._window_root_container.visible == 0
        assert window.title_bar.visible == 0
        assert window.window_element_container.visible == 0
        assert window.close_window_button.visible == 0

        window.show()

        assert window.visible == 1

        assert window._window_root_container.visible == 1
        assert window.title_bar.visible == 1
        assert window.window_element_container.visible == 1
        assert window.close_window_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        window = UIWindow(pygame.Rect(100, 100, 200, 200),
                          window_display_title="Test Window",
                          manager=default_ui_manager)

        assert window.visible == 1

        assert window._window_root_container.visible == 1
        assert window.title_bar.visible == 1
        assert window.window_element_container.visible == 1
        assert window.close_window_button.visible == 1

        window.hide()

        assert window.visible == 0

        assert window._window_root_container.visible == 0
        assert window.title_bar.visible == 0
        assert window.window_element_container.visible == 0
        assert window.close_window_button.visible == 0
