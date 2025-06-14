import os
import pytest
import pygame
import tempfile
import json

from tests.shared_comparators import compare_surfaces

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.ui_manager import UIManager


class TestUIPanel:
    def test_creation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
        )

    def test_creation_with_margins(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

    def test_update(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        assert panel.layer_thickness == 1
        assert panel.get_container().layer_thickness == 0
        panel.get_container().layer_thickness = 4
        assert panel.layer_thickness == 1
        panel.update(0.05)
        assert panel.layer_thickness == 4

    def test_add_button(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        assert panel.layer_thickness == 1

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=panel,
        )

        assert button.layer_thickness == 1
        # happens 'cause elements added to container hover 1 layer up
        assert panel.get_container().layer_thickness == 2
        panel.update(0.05)
        assert panel.layer_thickness == 2

    def test_process_event(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        consumed_event_left = panel.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": panel.rect.center},
            )
        )

        consumed_event_right = panel.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_RIGHT, "pos": panel.rect.center},
            )
        )

        consumed_event_middle = panel.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_MIDDLE, "pos": panel.rect.center},
            )
        )

        assert consumed_event_left and consumed_event_right and consumed_event_middle

    def test_kill(
        self,
        _init_pygame,
        _display_surface_return_none,
        default_ui_manager: IUIManagerInterface,
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=panel,
        )

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 4
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container(),
            panel.get_container(),
            panel,
            button,
        ]
        panel.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [
            default_ui_manager.get_root_container()
        ]

    def test_set_relative_position(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(100, 100, 300, 300), manager=default_ui_manager
        )
        element_1 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )

        element_1.set_relative_position((20, 20))
        assert element_1.rect.topleft == (120, 120)
        assert element_1.rect.size == (50, 50)
        assert element_1.rect.bottomright == (170, 170)

        element_2 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        element_2.set_relative_position((-20, 20))
        assert element_2.rect.topleft == (380, 120)
        assert element_2.rect.size == (50, 50)
        assert element_2.rect.bottomright == (430, 170)

        element_3 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        element_3.set_relative_position((-70, -70))
        assert element_3.rect.topleft == (330, 330)
        assert element_3.rect.size == (50, 50)
        assert element_3.rect.bottomright == (380, 380)

        element_4 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        element_4.set_relative_position((30, -70))
        assert element_4.rect.topleft == (130, 330)
        assert element_4.rect.size == (50, 50)
        assert element_4.rect.bottomright == (180, 380)

        element_5 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_relative_position((20, 20))
        assert element_5.rect.topleft == (120, 120)
        assert element_5.rect.size == (50, 50)
        assert element_5.rect.bottomright == (170, 170)
        assert element_5.relative_right_margin == 230
        assert element_5.relative_bottom_margin == 230

        # test with margins
        element_6 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert element_6.rect.topleft == (100, 100)
        assert element_6.rect.size == (50, 50)
        assert element_6.rect.bottomright == (150, 150)
        assert element_6.relative_right_margin == 250
        assert element_6.relative_bottom_margin == 250

        assert element_6.get_container().rect.topleft == (110, 105)
        assert element_6.get_container().rect.size == (30, 40)
        assert element_6.get_container().rect.bottomright == (140, 145)

        element_6.set_relative_position((20, 20))

        assert element_6.rect.topleft == (120, 120)
        assert element_6.rect.size == (50, 50)
        assert element_6.rect.bottomright == (170, 170)
        assert element_6.relative_right_margin == 230
        assert element_6.relative_bottom_margin == 230

        assert element_6.get_container().rect.topleft == (130, 125)
        assert element_6.get_container().rect.size == (30, 40)
        assert element_6.get_container().rect.bottomright == (160, 165)

    def test_set_position(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager
        )
        element = UIPanel(
            relative_rect=pygame.Rect(100, 100, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
        )

        element.set_position((150, 30))

        assert element.relative_rect.topleft == (140, 20)

        element_1 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )

        element_1.set_position((20, 20))
        assert element_1.relative_rect.topleft == (10, 10)
        assert element_1.relative_rect.size == (50, 50)
        assert element_1.relative_rect.bottomright == (60, 60)

        element_2 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        element_2.set_position((280, 120))
        assert element_2.relative_rect.topleft == (-30, 110)
        assert element_2.relative_rect.size == (50, 50)
        assert element_2.relative_rect.bottomright == (20, 160)

        element_3 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        element_3.set_position((230, 230))
        assert element_3.relative_rect.topleft == (-80, -80)
        assert element_3.relative_rect.size == (50, 50)
        assert element_3.relative_rect.bottomright == (-30, -30)

        element_4 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        element_4.set_position((130, 230))
        assert element_4.relative_rect.topleft == (120, -80)
        assert element_4.relative_rect.size == (50, 50)
        assert element_4.relative_rect.bottomright == (170, -30)

        element_5 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_position((20, 20))
        assert element_5.relative_rect.topleft == (10, 10)
        assert element_5.relative_rect.size == (50, 50)
        assert element_5.relative_rect.bottomright == (60, 60)
        assert element_5.relative_right_margin == 240
        assert element_5.relative_bottom_margin == 240

        # test with margins
        element_6 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert element_6.relative_rect.topleft == (0, 0)
        assert element_6.relative_rect.size == (50, 50)
        assert element_6.relative_rect.bottomright == (50, 50)
        assert element_6.relative_right_margin == 250
        assert element_6.relative_bottom_margin == 250

        assert element_6.get_container().get_relative_rect().topleft == (10, 5)
        assert element_6.get_container().get_relative_rect().size == (30, 40)
        assert element_6.get_container().get_relative_rect().bottomright == (40, 45)

        element_6.set_position((20, 20))

        assert element_6.relative_rect.topleft == (10, 10)
        assert element_6.relative_rect.size == (50, 50)
        assert element_6.relative_rect.bottomright == (60, 60)
        assert element_6.relative_right_margin == 240
        assert element_6.relative_bottom_margin == 240

        assert element_6.get_container().get_relative_rect().topleft == (20, 15)
        assert element_6.get_container().get_relative_rect().size == (30, 40)
        assert element_6.get_container().get_relative_rect().bottomright == (50, 55)

    def test_set_dimensions(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager
        )

        element_1 = UIPanel(
            relative_rect=pygame.Rect(30, 30, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
        assert element_1.relative_right_margin is None
        assert element_1.relative_bottom_margin is None

        element_1.set_dimensions((20, 20))
        assert element_1.relative_rect.topleft == (30, 30)
        assert element_1.relative_rect.size == (20, 20)
        assert element_1.relative_rect.bottomright == (50, 50)
        assert element_1.rect.topleft == (40, 40)
        assert element_1.rect.size == (20, 20)
        assert element_1.rect.bottomright == (60, 60)
        assert element_1.relative_right_margin is None
        assert element_1.relative_bottom_margin is None

        element_2 = UIPanel(
            relative_rect=pygame.Rect(-60, 10, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert element_2.relative_right_margin == 10
        assert element_2.relative_bottom_margin is None
        element_2.set_dimensions((60, 60))
        assert element_2.relative_rect.topleft == (-60, 10)
        assert element_2.relative_rect.size == (60, 60)
        assert element_2.relative_rect.bottomright == (0, 70)
        assert element_2.rect.topleft == (250, 20)
        assert element_2.rect.size == (60, 60)
        assert element_2.rect.bottomright == (310, 80)
        assert element_2.relative_right_margin == 0
        assert element_2.relative_bottom_margin is None

        element_3 = UIPanel(
            relative_rect=pygame.Rect(-70, -70, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        assert element_3.relative_right_margin == 20
        assert element_3.relative_bottom_margin == 20
        element_3.set_dimensions((30, 30))
        assert element_3.relative_rect.topleft == (-70, -70)
        assert element_3.relative_rect.size == (30, 30)
        assert element_3.relative_rect.bottomright == (-40, -40)
        assert element_3.rect.topleft == (240, 240)
        assert element_3.rect.size == (30, 30)
        assert element_3.rect.bottomright == (270, 270)
        assert element_3.relative_right_margin == 40
        assert element_3.relative_bottom_margin == 40

        element_4 = UIPanel(
            relative_rect=pygame.Rect(50, -50, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        assert element_4.relative_right_margin is None
        assert element_4.relative_bottom_margin == 0

        element_4.set_dimensions((100, 100))
        assert element_4.relative_rect.topleft == (50, -50)
        assert element_4.relative_rect.size == (100, 100)
        assert element_4.relative_rect.bottomright == (150, 50)
        assert element_4.rect.topleft == (60, 260)
        assert element_4.rect.size == (100, 100)
        assert element_4.rect.bottomright == (160, 360)
        assert element_4.relative_right_margin is None
        assert element_4.relative_bottom_margin == -50

        element_5 = UIPanel(
            relative_rect=pygame.Rect(10, 10, 50, 50),
            manager=default_ui_manager,
            container=test_container,
            starting_height=5,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        button = UIButton(
            relative_rect=pygame.Rect(0, 40, 10, 10),
            text="A",
            manager=default_ui_manager,
            container=element_5,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(40, 0, 10, 10),
            text="A",
            manager=default_ui_manager,
            container=element_5,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        assert element_5.relative_right_margin == 240
        assert element_5.relative_bottom_margin == 240

        element_5.set_dimensions((90, 90))
        assert element_5.relative_rect.topleft == (10, 10)
        assert element_5.relative_rect.size == (90, 90)
        assert element_5.relative_rect.bottomright == (100, 100)
        assert element_5.rect.topleft == (20, 20)
        assert element_5.rect.size == (90, 90)
        assert element_5.rect.bottomright == (110, 110)
        assert element_5.relative_right_margin == 200
        assert element_5.relative_bottom_margin == 200

    def test_rebuild_from_changed_theme_data_non_default(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_panel_non_default.json"),
        )
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        assert panel.image is not None

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
            os.path.join("tests", "data", "themes", "ui_panel_bad_values.json"),
        )
        panel = UIPanel(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            starting_height=5,
            manager=manager,
            margins={"left": 10, "right": 10, "top": 5, "bottom": 5},
        )

        assert panel.image is not None

    def test_disable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=panel,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=panel,
        )

        panel.disable()

        assert panel.is_enabled is False
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
        panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 150, 400),
            starting_height=5,
            manager=default_ui_manager,
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=panel,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=panel,
        )

        panel.disable()
        panel.enable()

        assert panel.is_enabled is True
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

    def test_panel_children_inheriting_hidden_status(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            visible=0,
            starting_height=5,
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=panel,
            visible=1,
        )
        assert panel.visible == 0
        assert button.visible == 0

    def test_hidden_panel_children_behaviour_on_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            visible=0,
            starting_height=5,
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=panel,
        )
        assert panel.visible == 0
        assert button.visible == 0
        panel.show()
        assert panel.visible == 1
        assert button.visible == 1

    def test_visible_panel_children_behaviour_on_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            visible=1,
            starting_height=5,
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=panel,
            visible=0,
        )
        assert panel.visible == 1
        assert button.visible == 0
        panel.show()
        assert panel.visible == 1
        assert button.visible == 0

    def test_visible_panel_children_behaviour_on_hide(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            visible=1,
            starting_height=5,
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=panel,
        )
        assert panel.visible == 1
        assert button.visible == 1
        panel.hide()
        assert panel.visible == 0
        assert button.visible == 0

    def test_hidden_panel_children_behaviour_on_hide(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            visible=0,
            starting_height=5,
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=panel,
        )
        button.show()
        assert panel.visible == 0
        assert button.visible == 1
        panel.hide()
        assert panel.visible == 0
        assert button.visible == 1

    def test_show_hide_rendering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        panel = UIPanel(
            pygame.Rect(25, 25, 375, 150), manager=manager, visible=0, starting_height=1
        )
        UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=manager,
            container=panel,
        )

        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        panel.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        panel.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_iteration(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=default_ui_manager,
            container=panel,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(150, 50, 50, 50),
            text="2",
            manager=default_ui_manager,
            container=panel,
        )

        assert button_1 in panel
        assert button_2 in panel
        count = 0
        for button in panel:
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
        container = UIPanel(pygame.Rect(100, 100, 200, 200), manager=manager)
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=manager,
            container=container,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(125, 50, 50, 50),
            text="2",
            manager=manager,
            container=container,
        )
        manager.mouse_position = (155, 155)
        button_1.check_hover(0.1, False)
        button_2.check_hover(0.1, False)

        assert container.are_contents_hovered()

    def test_are_nested_contents_hovered(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        panel = UIPanel(pygame.Rect(100, 100, 250, 300), manager=manager)

        container_2 = UIScrollingContainer(
            pygame.Rect(10, 10, 230, 280), manager=manager, container=panel
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

        assert panel.are_contents_hovered()

    def test_set_anchors(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            starting_height=5,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
        panel.set_anchors(
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"}
        )
        assert panel.get_anchors()["left"] == "right"
        assert panel.get_anchors()["right"] == "right"

    def test_multi_image_mode_detection(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test multi-image mode detection for UIPanel."""
        manager = UIManager((800, 600))

        # Test single image mode (default)
        panel = UIPanel(relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager)
        assert not panel.is_multi_image_mode()
        assert panel.get_image_count() == 0

        # Test with single image theme
        single_image_theme = {
            "panel": {
                "images": {"background_image": {"path": "tests/data/images/splat.png"}}
            }
        }
        manager.ui_theme.load_theme(single_image_theme)
        panel.rebuild_from_changed_theme_data()

        assert not panel.is_multi_image_mode()  # Single image = not multi-image mode
        assert panel.get_image_count() == 1

        # Test with multi-image theme
        multi_image_theme = {
            "panel": {
                "images": {
                    "background_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {
                            "id": "overlay",
                            "path": "tests/data/images/test_emoji.png",
                            "layer": 1,
                        },
                    ]
                }
            }
        }
        manager.ui_theme.load_theme(multi_image_theme)
        panel.rebuild_from_changed_theme_data()

        assert panel.is_multi_image_mode()
        assert panel.get_image_count() == 2

    def test_multi_image_loading_and_access(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test loading and accessing multi-image data for UIPanel."""
        manager = UIManager((800, 600))

        # Create theme with multiple background images
        multi_image_theme = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "background",
                            "path": "tests/data/images/splat.png",
                            "layer": 0,
                        },
                        {
                            "id": "border",
                            "path": "tests/data/images/space_1.jpg",
                            "layer": 1,
                        },
                        {
                            "id": "decoration",
                            "path": "tests/data/images/test_emoji.png",
                            "layer": 2,
                        },
                    ]
                }
            }
        }

        manager.ui_theme.load_theme(multi_image_theme)
        panel = UIPanel(relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager)

        # Test image access
        current_images = panel.get_current_images()
        assert len(current_images) == 3
        assert panel.get_image_count() == 3
        assert panel.is_multi_image_mode()

        # Verify all images are loaded
        for image in current_images:
            assert image is not None
            assert isinstance(image, pygame.Surface)

    def test_multi_image_backward_compatibility(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that single image themes still work with multi-image system."""
        manager = UIManager((800, 600))

        # Test legacy single image format
        single_image_theme = {
            "panel": {
                "images": {"background_image": {"path": "tests/data/images/splat.png"}}
            }
        }

        manager.ui_theme.load_theme(single_image_theme)
        panel = UIPanel(relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager)

        # Should work as single image in list format internally
        assert not panel.is_multi_image_mode()
        assert panel.get_image_count() == 1

        current_images = panel.get_current_images()
        assert len(current_images) == 1
        assert current_images[0] is not None

    def test_multi_image_api_methods(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test the multi-image API methods for UIPanel."""
        panel = UIPanel(
            relative_rect=pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        # Test with no images
        assert panel.get_current_images() == []
        assert not panel.is_multi_image_mode()
        assert panel.get_image_count() == 0

        # Test with theme that has images
        multi_image_theme = {
            "panel": {
                "images": {
                    "background_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {
                            "id": "overlay",
                            "path": "tests/data/images/test_emoji.png",
                            "layer": 1,
                        },
                    ]
                }
            }
        }

        default_ui_manager.ui_theme.load_theme(multi_image_theme)
        panel.rebuild_from_changed_theme_data()

        # Test API methods
        current_images = panel.get_current_images()
        assert len(current_images) == 2
        assert panel.is_multi_image_mode()
        assert panel.get_image_count() == 2

    def test_multi_image_theme_switching_cleanup(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that switching from multi-image to single-image themes properly cleans up."""
        # Start with multi-image theme
        multi_image_theme = {
            "panel": {
                "images": {
                    "background_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {
                            "id": "overlay",
                            "path": "tests/data/images/test_emoji.png",
                            "layer": 1,
                        },
                    ]
                }
            }
        }

        # Create single image theme
        single_image_theme = {
            "panel": {
                "images": {"background_image": {"path": "tests/data/images/splat.png"}}
            }
        }

        # Create no image theme
        no_image_theme = {"panel": {}}

        # Save theme files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(multi_image_theme, f)
            multi_theme_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(single_image_theme, f)
            single_theme_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(no_image_theme, f)
            no_image_theme_file = f.name

        try:
            # Start with multi-image theme
            manager = UIManager((800, 600), multi_theme_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # Verify multi-image mode
            assert panel.is_multi_image_mode()
            assert panel.get_image_count() == 2

            # Switch to single image theme
            manager.ui_theme.load_theme(single_theme_file)
            panel.rebuild_from_changed_theme_data()

            # Verify proper cleanup
            assert not panel.is_multi_image_mode()
            assert panel.get_image_count() == 1

            # Switch to no image theme
            manager.ui_theme.load_theme(no_image_theme_file)
            panel.rebuild_from_changed_theme_data()

            # Verify complete cleanup
            assert not panel.is_multi_image_mode()
            assert panel.get_image_count() == 0
            assert panel.get_current_images() == []

        finally:
            # Clean up theme files
            try:
                os.unlink(multi_theme_file)
                os.unlink(single_theme_file)
                os.unlink(no_image_theme_file)
            except:
                pass

    def test_image_positioning_single_image_mode(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test image positioning in single-image mode."""
        import tempfile
        import json
        import os

        # Theme with positioned single image
        theme_data = {
            "panel": {
                "images": {
                    "background_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.0, 0.0],  # Top-left corner
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = UIManager((800, 600), theme_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # Test position
            assert panel.background_image_positions == [(0.0, 0.0)]
            assert panel.get_current_image_positions() == [(0.0, 0.0)]

            # Test API methods
            assert not panel.is_multi_image_mode()
            assert panel.get_image_count() == 1

        finally:
            os.unlink(theme_file)

    def test_image_positioning_multi_image_mode(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test image positioning in multi-image mode."""
        import tempfile
        import json
        import os

        # Theme with positioned multi-images
        theme_data = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "background",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, 0.5],  # Center
                        },
                        {
                            "id": "top_left",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.0, 0.0],  # Top-left corner
                        },
                        {
                            "id": "bottom_right",
                            "layer": 2,
                            "path": "tests/data/images/splat.png",
                            "position": [1.0, 1.0],  # Bottom-right corner
                        },
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = UIManager((800, 600), theme_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # Test positions
            expected_positions = [(0.5, 0.5), (0.0, 0.0), (1.0, 1.0)]
            assert panel.background_image_positions == expected_positions
            assert panel.get_current_image_positions() == expected_positions

            # Test API methods
            assert panel.is_multi_image_mode()
            assert panel.get_image_count() == 3

            # Test image access
            current_images = panel.get_current_images()
            assert len(current_images) == 3
            for image in current_images:
                assert isinstance(image, pygame.Surface)

        finally:
            os.unlink(theme_file)

    def test_image_positioning_default_values(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that images without position parameters default to center (0.5, 0.5)."""
        import tempfile
        import json
        import os

        # Theme without position parameters
        theme_data = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "no_position",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            # No position parameter - should default to (0.5, 0.5)
                        },
                        {
                            "id": "with_position",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.2, 0.8],
                        },
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = UIManager((800, 600), theme_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # First image should default to center, second should use specified position
            expected_positions = [(0.5, 0.5), (0.2, 0.8)]
            assert panel.background_image_positions == expected_positions
            assert panel.get_current_image_positions() == expected_positions

        finally:
            os.unlink(theme_file)

    def test_image_positioning_api_methods(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test the API methods for image positioning."""
        manager = UIManager((800, 600))
        panel = UIPanel(relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager)

        # Create test images first
        panel.background_images = [pygame.Surface((10, 10)) for _ in range(2)]

        # Test setting positions
        test_positions = [(0.1, 0.1), (0.9, 0.9)]
        panel.set_image_positions(test_positions)
        assert panel.background_image_positions == test_positions

        # Test setting individual position
        panel.set_image_position(0, (0.3, 0.3))
        assert panel.background_image_positions[0] == (0.3, 0.3)

        # Test invalid index
        assert not panel.set_image_position(99, (0.5, 0.5))

        # Test auto-extension of positions list
        panel.background_images = [pygame.Surface((10, 10)) for _ in range(3)]
        panel.set_image_positions([(0.1, 0.1)])
        assert len(panel.background_image_positions) == 3
        assert panel.background_image_positions[0] == (0.1, 0.1)
        assert panel.background_image_positions[1] == (
            0.5,
            0.5,
        )  # Default center position
        assert panel.background_image_positions[2] == (
            0.5,
            0.5,
        )  # Default center position

    def test_image_positioning_mixed_with_without_positions(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test handling of mixed images where some have positions and others don't."""
        import tempfile
        import json
        import os

        theme_data = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "with_position",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.1, 0.1],
                        },
                        {
                            "id": "no_position",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            # No position - should default to center
                        },
                        {
                            "id": "with_position_2",
                            "layer": 2,
                            "path": "tests/data/images/splat.png",
                            "position": [0.9, 0.9],
                        },
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = UIManager((800, 600), theme_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # Should have positions: specified, default, specified
            expected_positions = [(0.1, 0.1), (0.5, 0.5), (0.9, 0.9)]
            assert panel.background_image_positions == expected_positions
            assert panel.get_current_image_positions() == expected_positions

        finally:
            os.unlink(theme_file)

    def test_image_positioning_theme_loading_and_storage(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that image positions are properly loaded and stored when switching themes."""
        import tempfile
        import json
        import os

        # First theme with positions
        theme_1 = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "bg1",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.1, 0.1],
                        },
                        {
                            "id": "bg2",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.9, 0.9],
                        },
                    ]
                }
            }
        }

        # Second theme with different positions
        theme_2 = {
            "panel": {
                "images": {
                    "background_images": [
                        {
                            "id": "bg1",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.2, 0.2],
                        },
                        {
                            "id": "bg2",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.8, 0.8],
                        },
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_1, f)
            theme_1_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_2, f)
            theme_2_file = f.name

        try:
            manager = UIManager((800, 600), theme_1_file)
            panel = UIPanel(
                relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager
            )

            # Check first theme positions
            assert panel.background_image_positions == [(0.1, 0.1), (0.9, 0.9)]

            # Switch to second theme
            manager.ui_theme.load_theme(theme_2_file)
            panel.rebuild_from_changed_theme_data()

            # Check second theme positions
            assert panel.background_image_positions == [(0.2, 0.2), (0.8, 0.8)]

        finally:
            os.unlink(theme_1_file)
            os.unlink(theme_2_file)

    def test_image_positioning_edge_case_values(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test image positioning with edge case values."""
        manager = UIManager((800, 600))
        panel = UIPanel(relative_rect=pygame.Rect(100, 100, 200, 200), manager=manager)

        # Test with empty positions list
        panel.set_image_positions([])
        assert panel.background_image_positions == []

        # Test with single image but multiple positions
        panel.background_images = [pygame.Surface((10, 10))]
        panel.set_image_positions([(0.1, 0.1), (0.2, 0.2)])
        assert panel.background_image_positions == [(0.1, 0.1)]

        # Test with multiple images but single position
        panel.background_images = [pygame.Surface((10, 10)) for _ in range(3)]
        panel.set_image_positions([(0.3, 0.3)])
        assert len(panel.background_image_positions) == 3
        assert panel.background_image_positions[0] == (0.3, 0.3)
        assert panel.background_image_positions[1] == (0.5, 0.5)  # Default center
        assert panel.background_image_positions[2] == (0.5, 0.5)  # Default center


if __name__ == "__main__":
    pytest.console_main()
