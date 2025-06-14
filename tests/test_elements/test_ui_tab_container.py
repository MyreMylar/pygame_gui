import pytest
import pygame


from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements.ui_tab_container import UITabContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.ui_container import UIContainer
from pygame_gui import UIManager
from pygame_gui import UI_BUTTON_PRESSED


class TestUITabContainer:
    def test_creation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )

    def test_creation_with_tab(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )

        tab_container.add_tab("Tab 1", "tab_1")

    def test_add_button(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )

        tab_1_container = tab_container.get_tab_container(
            tab_container.add_tab("Tab 1", "tab_1")
        )

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        assert button.image is not None

    def test_process_event(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        tab_2_id = tab_container.add_tab("Tab 2", "tab_2")
        tab_2_container = tab_container.get_tab_container(tab_2_id)
        tab_2_title_button = tab_container.get_title_button(tab_2_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        assert button.visible

        consumed_event = tab_container.process_event(
            pygame.event.Event(UI_BUTTON_PRESSED, {"ui_element": tab_2_title_button})
        )

        assert consumed_event and not button.visible

    def test_kill(
        self,
        _init_pygame,
        _display_surface_return_none,
        default_ui_manager: IUIManagerInterface,
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 7
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container(),
            tab_container,
            tab_container._root_container,
            tab_1_title_button,
            tab_1_container.get_container(),
            tab_1_container,
            button,
        ]
        tab_container.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container()
        ]

    def test_set_dimensions(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(10, 10, 700, 500), manager=default_ui_manager
        )

        tab_container_1 = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 350),
            manager=default_ui_manager,
            container=test_container,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
        tab_1_id = tab_container_1.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container_1.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container_1.get_title_button(tab_1_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        assert tab_container_1.relative_right_margin is None
        assert tab_container_1.relative_bottom_margin is None

        tab_container_1.set_dimensions((200, 200))
        assert tab_container_1.relative_rect.topleft == (50, 50)
        assert tab_container_1.relative_rect.size == (200, 200)
        assert tab_container_1.relative_rect.bottomright == (250, 250)
        assert tab_container_1.rect.topleft == (60, 60)
        assert tab_container_1.rect.size == (200, 200)
        assert tab_container_1.rect.bottomright == (260, 260)
        assert tab_container_1.relative_right_margin is None
        assert tab_container_1.relative_bottom_margin is None

    def test_enable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        tab_container.disable()
        tab_container.enable()

        assert tab_container.is_enabled is True
        assert button.is_enabled is True
        assert tab_1_title_button.is_enabled is True

    def test_panel_children_inheriting_hidden_status(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            manager=default_ui_manager,
            visible=False,
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )
        assert not tab_container.visible
        assert not button.visible
        assert not tab_1_title_button.visible

    def test_hidden_panel_children_behaviour_on_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            manager=default_ui_manager,
            visible=False,
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=tab_1_container,
        )

        assert not tab_container.visible
        assert not button.visible
        assert not tab_1_title_button.visible
        tab_container.show()
        assert tab_container.visible
        assert button.visible
        assert tab_1_title_button.visible
        tab_container.hide()
        assert not tab_container.visible
        assert not button.visible
        assert not tab_1_title_button.visible

    def test_get_title_text(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        tab_container = UITabContainer(
            relative_rect=pygame.Rect(50, 50, 150, 400), manager=default_ui_manager
        )
        tab_1_id = tab_container.add_tab("Tab 1", "tab_1")
        tab_1_container = tab_container.get_tab_container(tab_1_id)
        tab_1_title_button = tab_container.get_title_button(tab_1_id)

        assert tab_container.get_title_text(tab_1_id) == "Tab 1"

    def test_set_anchors(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UITabContainer(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
        panel.set_anchors(
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"}
        )
        assert panel.get_anchors()["left"] == "right"
        assert panel.get_anchors()["right"] == "right"


if __name__ == "__main__":
    pytest.console_main()
