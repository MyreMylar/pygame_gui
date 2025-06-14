import os
import pytest
import pygame
import pygame_gui

from tests.shared_comparators import compare_surfaces

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui import UIManager

from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu


class TestUIWindow:
    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        UIWindow(
            pygame.Rect(100, 100, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            element_id="window",
        )

    def test_set_blocking(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            element_id="window",
        )

        button = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            allow_double_clicks=True,
        )

        default_ui_manager.process_events(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )
        assert button.held

        default_ui_manager.process_events(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )

        window.set_blocking(True)

        default_ui_manager.process_events(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )
        assert not button.held

        window.set_blocking(False)
        window.always_on_top = True
        window.set_blocking(True)

        default_ui_manager.process_events(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )
        assert not button.held

        window.set_blocking(False)
        window.always_on_top = False

        UIWindow(
            pygame.Rect(0, 0, 100, 100),
            window_display_title="Test On Top Window",
            manager=default_ui_manager,
            element_id="window",
            always_on_top=True,
        )

        window.set_blocking(True)
        default_ui_manager.process_events(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )
        assert not button.held

        window.set_blocking(False)

    def test_set_minimum_dimensions(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        window.set_minimum_dimensions((200, 200))
        window.set_dimensions((100, 100))

        assert window.rect.size == (200, 200)

        window.set_minimum_dimensions((250, 250))

        assert window.rect.size == (250, 250)

    def test_set_dimensions(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert button.rect.topright == (
            window.get_container().rect.right - 10,
            window.get_container().rect.top + 10,
        )
        assert button.rect.topright == (389, 238)

        window.set_dimensions((300, 400))

        assert button.rect.topright == (
            window.get_container().rect.right - 10,
            window.get_container().rect.top + 10,
        )
        assert button.rect.topright == (459, 238)

        confirm_event_fired = False
        event_object_id = None
        new_external_dimensions = (0, 0)
        new_internal_dimensions = (0, 0)
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_WINDOW_RESIZED
                and event.ui_element == window
            ):
                confirm_event_fired = True
                event_object_id = event.ui_object_id
                new_external_dimensions = event.external_size
                new_internal_dimensions = event.internal_size
        assert confirm_event_fired
        assert event_object_id == "window"
        assert new_external_dimensions == (300, 400)
        assert new_internal_dimensions == (268, 341)

    def test_set_relative_position(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert button.rect.topright == (389, 238)
        window.set_relative_position((100, 100))
        assert button.rect.topright == (304, 153)

    def test_set_position(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert button.rect.topright == (389, 238)
        window.set_position((100, 100))
        assert button.rect.topright == (304, 153)

    def test_process_event(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            object_id="#specific_id_test",
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )
        button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )

        confirm_event_fired = False
        event_object_id = None
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == button
            ):
                confirm_event_fired = True
                event_object_id = event.ui_object_id
        assert confirm_event_fired
        assert event_object_id == "window.#specific_id_test"

        consumed_event = window.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_RIGHT, "pos": window.rect.center},
            )
        )
        assert consumed_event is True

        window.edge_hovering[0] = True
        consumed_event = window.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": window.rect.topleft},
            )
        )
        assert consumed_event and window.resizing_mode_active

        consumed_event = window.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": (500, 500)}
            )
        )
        assert not (consumed_event or window.resizing_mode_active)

        consumed_event = window.process_event(
            pygame.event.Event(
                pygame_gui.UI_BUTTON_PRESSED, {"ui_element": window.close_window_button}
            )
        )
        assert not (consumed_event or window.alive())

    def test_check_clicked_inside(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )
        clicked_inside = window.check_clicked_inside_or_blocking(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (100, 100)})
        )

        assert clicked_inside is True

    def test_update(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

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

        window.start_resize_rect = pygame.Rect(0, 0, 190, 190)
        default_ui_manager.mouse_position = (25, 25)
        window.update(time_delta=0.05)

        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            draggable=True,
        )

        window.title_bar.held = True
        default_ui_manager.mouse_position = (100, 10)
        window.update(time_delta=0.05)
        default_ui_manager.mouse_position = (150, 10)
        window.update(time_delta=0.05)

        assert window.get_relative_rect().topleft == (35, -15)

        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            draggable=False,
        )

        window.title_bar.held = True
        default_ui_manager.mouse_position = (100, 10)
        window.update(time_delta=0.05)
        default_ui_manager.mouse_position = (150, 10)
        window.update(time_delta=0.05)

        assert window.get_relative_rect().topleft == (-15, -15)

    def test_check_hover(
        self,
        _init_pygame,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        window = UIWindow(
            pygame.Rect(100, 100, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            resizable=True,
        )

        default_ui_manager.mouse_position = (
            window.rect.left + window.shadow_width,
            window.rect.centery,
        )
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[0]

        default_ui_manager.mouse_position = (
            window.rect.right - window.shadow_width,
            window.rect.centery,
        )
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[2]

        default_ui_manager.mouse_position = (
            window.rect.centerx,
            window.rect.top + window.shadow_width,
        )
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[1]

        default_ui_manager.mouse_position = (
            window.rect.centerx,
            window.rect.bottom - window.shadow_width,
        )
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

    def test_get_top_layer(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 400, 300),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        UIDropDownMenu(
            options_list=["eggs", "flour", "sugar"],
            starting_option="eggs",
            relative_rect=pygame.Rect(10, 10, 150, 30),
            manager=default_ui_manager,
            container=window,
        )

        assert window.get_top_layer() == 5
        window.update(0.05)
        assert window.get_top_layer() == 7  # This used to be 6, maybe it should be

    def test_change_layer(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        assert window.get_top_layer() == 5

        window.change_layer(10)

        assert window.get_top_layer() == 12

        window.update(0.05)

        assert window.get_top_layer() == 12

    def test_kill(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none: None,
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 6
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container(),
            window,
            window._window_root_container,
            window.window_element_container,
            window.title_bar,
            window.close_window_button,
        ]
        window.kill()

        confirm_event_fired = False
        event_object_id = None
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == window:
                confirm_event_fired = True
                event_object_id = event.ui_object_id
        assert confirm_event_fired
        assert event_object_id == "window"
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container()
        ]

    def test_set_display_title(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            element_id="window",
        )

        window.set_display_title("New Title")

        assert window.title_bar.text == "New Title"

    def test_rebuild_options(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            element_id="window",
        )

        window.enable_close_button = False

        window.rebuild()

        assert window.close_window_button is None

        window.enable_close_button = True

        window.rebuild()

        assert window.close_window_button is not None
        assert window.title_bar is not None

        window.enable_title_bar = False

        window.rebuild()

        assert window.close_window_button is None
        assert window.title_bar is None

    def test_rebuild_from_changed_theme_data_non_default(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_window_non_default.json"),
        )
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=manager,
        )

        assert window.image is not None

    def test_using_theme_prototype(self, _init_pygame, _display_surface_return_none):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_window_prototype.json"),
        )
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=manager,
        )

        button_rect = pygame.Rect(0, 0, 150, 30)
        button_rect.topright = (-10, 10)
        button = UIButton(
            relative_rect=button_rect,
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=manager,
            container=window,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert window.image is not None
        assert window.shadow_width == 1
        assert window.border_width == {"bottom": 2, "left": 2, "right": 2, "top": 2}
        assert window.shape_corner_radius == [10, 10, 10, 10]
        assert button.shadow_width == 1
        assert button.border_width == {"bottom": 2, "left": 2, "right": 2, "top": 2}
        assert button.shape_corner_radius == [4, 4, 4, 4]

    def test_rebuild_from_changed_theme_data_no_title_bar(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_window_no_title_bar.json"),
        )
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=manager,
        )

        assert window.title_bar is None
        assert window.close_window_button is None
        assert window.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    @pytest.mark.filterwarnings("ignore:Theme validation found")
    @pytest.mark.filterwarnings("ignore:Misc data validation")
    @pytest.mark.filterwarnings("ignore:Font data validation")
    @pytest.mark.filterwarnings("ignore:Image data validation")
    def test_rebuild_from_changed_theme_data_bad_values(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_window_bad_values.json"),
        )
        window = UIWindow(
            pygame.Rect(0, 0, 200, 200),
            window_display_title="Test Window",
            manager=manager,
        )

        assert window.image is not None

    def test_stub_methods(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        window = UIWindow(
            pygame.Rect(100, 100, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

        window.focus()
        window.unfocus()

    def test_disable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=window,
        )

        window.disable()

        assert window.is_enabled is False
        assert window.title_bar.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": button_1.rect.center}
            )
        )

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": button_1.rect.center}
            )
        )

        button_1.update(0.01)

        assert button_1.check_pressed() is False

    def test_enable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        window = UIWindow(
            pygame.Rect(200, 200, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=window,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=window,
        )

        window.disable()
        window.enable()

        assert window.is_enabled is True
        assert window.title_bar.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": button_1.rect.center}
            )
        )

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": button_1.rect.center}
            )
        )

        button_1.update(0.01)

        assert button_1.check_pressed() is True

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        window = UIWindow(
            pygame.Rect(100, 100, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
            visible=0,
        )

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

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        window = UIWindow(
            pygame.Rect(100, 100, 200, 200),
            window_display_title="Test Window",
            manager=default_ui_manager,
        )

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

    def test_show_hide_rendering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        window = UIWindow(
            pygame.Rect(100, 100, 400, 400),
            window_display_title="Test Window",
            manager=manager,
            visible=0,
        )
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        window.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        window.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_get_relative_mouse_pos(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        window = UIWindow(
            pygame.Rect(100, 100, 400, 400),
            window_display_title="Test Window",
            manager=default_ui_manager,
            visible=0,
        )

        default_ui_manager.mouse_position = (0, 0)
        assert window.get_relative_mouse_pos() is None

        default_ui_manager.mouse_position = (200, 200)
        assert window.get_relative_mouse_pos() == (99, 72)

    def test_drag_resizing(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        window = UIWindow(
            pygame.Rect(0, 0, 101, 101),
            window_display_title="Test Window",
            manager=default_ui_manager,
            visible=0,
            ignore_shadow_for_initial_size_and_pos=False,
        )

        window.start_resize_point = (50, 101)
        window.start_resize_rect = window.rect.copy()
        window.edge_hovering[3] = True
        default_ui_manager.mouse_position = (50, 99)
        window._update_drag_resizing()
        window.edge_hovering[3] = False

        window.start_resize_point = (50, 0)
        window.start_resize_rect = window.rect.copy()
        window.edge_hovering[1] = True
        default_ui_manager.mouse_position = (50, 5)
        window._update_drag_resizing()
        window.edge_hovering[1] = False

        window.start_resize_point = (101, 50)
        window.start_resize_rect = window.rect.copy()
        window.edge_hovering[2] = True
        default_ui_manager.mouse_position = (99, 50)
        window._update_drag_resizing()
        window.edge_hovering[2] = False

        window.start_resize_point = (0, 50)
        window.start_resize_rect = window.rect.copy()
        window.edge_hovering[0] = True
        default_ui_manager.mouse_position = (5, 50)
        window._update_drag_resizing()
        window.edge_hovering[0] = False

        assert window.rect.width == 100 and window.rect.height == 100

    def test_iteration(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        window = UIWindow(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=default_ui_manager,
            container=window,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(150, 50, 50, 50),
            text="2",
            manager=default_ui_manager,
            container=window,
        )

        assert button_1 in window
        assert button_2 in window
        count = 0
        for button in window:
            button.get_relative_rect()
            count += 1
        assert count == 2

    def test_are_contents_hovered(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        window = UIWindow(pygame.Rect(100, 100, 200, 200), manager=manager)
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=manager,
            container=window,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(125, 50, 50, 50),
            text="2",
            manager=manager,
            container=window,
        )
        manager.mouse_position = button_1.rect.center
        button_1.check_hover(0.1, False)
        button_2.check_hover(0.1, False)

        assert window.are_contents_hovered()

    def test_are_nested_contents_hovered(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        window = UIWindow(pygame.Rect(100, 100, 250, 300), manager=manager)

        container_2 = UIScrollingContainer(
            pygame.Rect(10, 10, 230, 280), manager=manager, container=window
        )

        nested_text_box = UITextBox(
            html_text="Some text inside a scrolling text box, itself"
            " inside a container that scrolls inside "
            " another container. ",
            relative_rect=pygame.Rect(10, 10, 180, 200),
            container=container_2,
            manager=manager,
        )
        manager.mouse_position = nested_text_box.rect.center
        nested_text_box.check_hover(0.1, False)

        assert window.are_contents_hovered()


if __name__ == "__main__":
    pytest.console_main()
