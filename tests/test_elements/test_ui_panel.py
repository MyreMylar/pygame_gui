import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.ui_manager import UIManager

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIPanel:

    def test_creation(self, _init_pygame, default_ui_manager):
        UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                starting_layer_height=5,
                manager=default_ui_manager)

    def test_creation_with_margins(self, _init_pygame, default_ui_manager):
        UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                starting_layer_height=5,
                manager=default_ui_manager,
                margins={'left': 10,
                         'right': 10,
                         'top': 5,
                         'bottom': 5})

    def test_update(self, _init_pygame, default_ui_manager):
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        assert panel.layer_thickness == 1
        assert panel.get_container().layer_thickness == 0
        panel.get_container().layer_thickness = 4
        assert panel.layer_thickness == 1
        panel.update(0.05)
        assert panel.layer_thickness == 4

    def test_add_button(self, _init_pygame, default_ui_manager):
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        assert panel.layer_thickness == 1

        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=panel)

        assert button.layer_thickness == 1
        # happens 'cause elements added to container hover 1 layer up
        assert panel.get_container().layer_thickness == 2
        panel.update(0.05)
        assert panel.layer_thickness == 2

    def test_process_event(self, _init_pygame, default_ui_manager):
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        consumed_event_left = panel.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': pygame.BUTTON_LEFT, 'pos': panel.rect.center}))

        consumed_event_right = panel.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': pygame.BUTTON_RIGHT, 'pos': panel.rect.center}))

        consumed_event_middle = panel.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': pygame.BUTTON_MIDDLE, 'pos': panel.rect.center}))

        assert consumed_event_left and consumed_event_right and consumed_event_middle

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface):
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          container=panel)

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 4
        assert (default_ui_manager.get_sprite_group().sprites() ==
                [default_ui_manager.get_root_container(),
                 panel,
                 panel.get_container(),
                 button])
        panel.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert (default_ui_manager.get_sprite_group().sprites() ==
                [default_ui_manager.get_root_container()])

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300),
                                     manager=default_ui_manager)
        element_1 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'top',
                                     'bottom': 'top'})

        element_1.set_relative_position((20, 20))
        assert element_1.rect.topleft == (120, 120)
        assert element_1.rect.size == (50, 50)
        assert element_1.rect.bottomright == (170, 170)

        element_2 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'top'})

        element_2.set_relative_position((-20, 20))
        assert element_2.rect.topleft == (380, 120)
        assert element_2.rect.size == (50, 50)
        assert element_2.rect.bottomright == (430, 170)

        element_3 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

        element_3.set_relative_position((-70, -70))
        assert element_3.rect.topleft == (330, 330)
        assert element_3.rect.size == (50, 50)
        assert element_3.rect.bottomright == (380, 380)

        element_4 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

        element_4.set_relative_position((30, -70))
        assert element_4.rect.topleft == (130, 330)
        assert element_4.rect.size == (50, 50)
        assert element_4.rect.bottomright == (180, 380)

        element_5 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'bottom'})

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_relative_position((20, 20))
        assert element_5.rect.topleft == (120, 120)
        assert element_5.rect.size == (50, 50)
        assert element_5.rect.bottomright == (170, 170)
        assert element_5.relative_right_margin == 230
        assert element_5.relative_bottom_margin == 230

    def test_set_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)
        element = UIPanel(relative_rect=pygame.Rect(100, 100, 50, 50),
                          manager=default_ui_manager,
                          container=test_container,
                          starting_layer_height=5)

        element.set_position((150, 30))

        assert element.relative_rect.topleft == (140, 20)

        element_1 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'top',
                                     'bottom': 'top'})

        element_1.set_position((20, 20))
        assert element_1.relative_rect.topleft == (10, 10)
        assert element_1.relative_rect.size == (50, 50)
        assert element_1.relative_rect.bottomright == (60, 60)

        element_2 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'top'})

        element_2.set_position((280, 120))
        assert element_2.relative_rect.topleft == (-30, 110)
        assert element_2.relative_rect.size == (50, 50)
        assert element_2.relative_rect.bottomright == (20, 160)

        element_3 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

        element_3.set_position((230, 230))
        assert element_3.relative_rect.topleft == (-80, -80)
        assert element_3.relative_rect.size == (50, 50)
        assert element_3.relative_rect.bottomright == (-30, -30)

        element_4 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

        element_4.set_position((130, 230))
        assert element_4.relative_rect.topleft == (120, -80)
        assert element_4.relative_rect.size == (50, 50)
        assert element_4.relative_rect.bottomright == (170, -30)

        element_5 = UIPanel(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'bottom'})

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_position((20, 20))
        assert element_5.relative_rect.topleft == (10, 10)
        assert element_5.relative_rect.size == (50, 50)
        assert element_5.relative_rect.bottomright == (60, 60)
        assert element_5.relative_right_margin == 240
        assert element_5.relative_bottom_margin == 240

    def test_set_dimensions(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)

        element_1 = UIPanel(relative_rect=pygame.Rect(30, 30, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'top',
                                     'bottom': 'top'})
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

        element_2 = UIPanel(relative_rect=pygame.Rect(-60, 10, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'top'})

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

        element_3 = UIPanel(relative_rect=pygame.Rect(-70, -70, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'right',
                                     'right': 'right',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

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

        element_4 = UIPanel(relative_rect=pygame.Rect(50, -50, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'bottom',
                                     'bottom': 'bottom'})

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

        element_5 = UIPanel(relative_rect=pygame.Rect(10, 10, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_layer_height=5,
                            anchors={'left': 'left',
                                     'right': 'right',
                                     'top': 'top',
                                     'bottom': 'bottom'})

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

    def test_rebuild_from_changed_theme_data_non_default(self, _init_pygame,
                                                         _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_panel_non_default.json"))
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        assert panel.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame,
                                                        _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_panel_bad_values.json"))
        panel = UIPanel(relative_rect=pygame.Rect(50, 50, 150, 400),
                        starting_layer_height=5,
                        manager=manager,
                        margins={'left': 10,
                                 'right': 10,
                                 'top': 5,
                                 'bottom': 5})

        assert panel.image is not None

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        panel = UIPanel(relative_rect=pygame.Rect(0, 0, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=panel)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=panel)

        panel.disable()

        assert panel.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button_1.update(0.01)

        assert button_1.check_pressed() is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        panel = UIPanel(relative_rect=pygame.Rect(0, 0, 150, 400),
                        starting_layer_height=5,
                        manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=panel)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=panel)

        panel.disable()
        panel.enable()

        assert panel.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button_1.update(0.01)

        assert button_1.check_pressed() is True
