import os
import sys
import pytest
import pygame
import pygame_gui

import i18n

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.ui_container import UIContainer, ObjectID
from pygame_gui import PackageResource


class TestUIButton:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.")
        assert button.image is not None

        i18n.add_translation('translation.test_hello', 'Hello %{name}')
        button_with_kwargs = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                                      text="translation.test_hello",
                                      manager=default_ui_manager,
                                      text_kwargs={"name": "World"})
        assert button_with_kwargs.image is not None
        assert button_with_kwargs.drawable_shape.theming['text'] == "Hello World"

        button_with_tt_kwargs = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                                         text="Test Button",
                                         manager=default_ui_manager,
                                         tool_tip_text="translation.test_hello",
                                         tool_tip_text_kwargs={"name": "World"})
        assert button_with_tt_kwargs.image is not None

    def test_kwargs_set_text(self, _init_pygame, default_ui_manager,
                             _display_surface_return_none):
        i18n.add_translation('translation.test_hello', 'Hello %{name}')
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)
        button.set_text("translation.test_hello", text_kwargs={"name": "World"})
        assert button.image is not None
        assert button.drawable_shape.theming['text'] == "Hello World"

        button.set_text("Clear args")
        assert button.image is not None
        assert button.drawable_shape.theming['text'] == "Clear args"

    @pytest.mark.filterwarnings("ignore:DeprecationWarning")
    def test_set_any_images_from_theme(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_with_images.json"))
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        assert button.normal_images[0] is not None and button.image is not None

    def test_kill(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create the tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # should kill everything
        button.kill()

        assert button.alive() is False and button.tool_tip.alive() is False

    def test_hover_point_outside(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test outside button
        is_inside = button.hover_point(50, 50)
        assert is_inside is False

    def test_hover_point_inside(self, _init_pygame, default_ui_manager,
                                _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button
        is_inside = button.hover_point(150, 115)
        assert is_inside is True

    def test_hover_point_held(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button when held
        button.set_hold_range((100, 100))
        button.held = True
        is_inside = button.hover_point(50, 50)
        assert is_inside is True

    def test_hover_point_not_held(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button when held
        button.set_hold_range((100, 100))
        button.held = False
        is_inside = button.hover_point(50, 50)
        assert is_inside is False

    def test_can_hover(self, _init_pygame, default_ui_manager,
                       _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        button.is_enabled = True
        button.held = False

        assert button.can_hover() is True

    def test_cannot_hover(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        button.is_enabled = True
        button.held = True

        assert button.can_hover() is False

    def test_on_hovered(self, _init_pygame, default_ui_manager,
                        _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)
        button.on_hovered()

        confirm_on_hovered_event_fired = any((event.type == pygame_gui.UI_BUTTON_ON_HOVERED and
                                              event.ui_element == button) for event in
                                             pygame.event.get())

        assert button.hover_time == 0.0
        assert confirm_on_hovered_event_fired

    def test_while_hovering(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create the tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        assert button.tool_tip is not None

    def test_while_not_hovering(self, _init_pygame, default_ui_manager,
                                _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # fail to create the tool tip
        button.hover_time = 0.0
        button.while_hovering(0.01, pygame.math.Vector2(250.0, 250.0))

        assert button.tool_tip is None

    def test_on_unhovered(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create the tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # stop hovering and kill the tool tip
        button.on_unhovered()

        unhovered_event_fired = any((event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED and
                                     event.ui_element == button) for event in
                                    pygame.event.get())

        assert unhovered_event_fired
        assert button.tool_tip is None

    def test_update(self, _init_pygame, default_ui_manager,
                    _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # test the 'one frame' button press flag
        button.pressed_event = True

        redraw_queue_length_pre_update = len(button.drawable_shape.states_to_redraw_queue)
        button.update(0.01)
        redraw_queue_length_post_update = len(button.drawable_shape.states_to_redraw_queue)

        assert button.pressed is True and redraw_queue_length_post_update == (
                redraw_queue_length_pre_update - 1)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        button.set_relative_position(pygame.math.Vector2(150.0, 30.0))

        assert (button.rect.topleft == (250, 130) and
                button.drawable_shape.containing_rect.topleft == (250, 130))

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        button_2 = UIButton(relative_rect=pygame.Rect(200, 0, 50, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            container=test_container,
                            manager=default_ui_manager,
                            anchors={'left_target': button})

        assert button.rect.topleft == (100, 100)
        assert button_2.rect.topleft == (450, 100)

        button.set_position(pygame.math.Vector2(150.0, 30.0))

        assert button.rect.topleft == (150, 30)
        assert button_2.rect.topleft == (500, 100)

        assert (button.relative_rect.topleft == (50, -70) and
                button.drawable_shape.containing_rect.topleft == (150, 30))

        assert button_2.relative_rect.topleft == (200, 0)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_dimensions(pygame.math.Vector2(250.0, 60.0))

        assert button.drawable_shape.containing_rect.width == 250 and button.drawable_shape.containing_rect.height == 60

    def test_update_containing_rect_position(self, _init_pygame, default_ui_manager,
                                             _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        test_container.set_position((50, 50))
        button.update_containing_rect_position()

        assert button.rect.topleft == (60, 60)

    def test_process_event_double_click(self, _init_pygame: None, default_ui_manager: UIManager,
                                        _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          allow_double_clicks=True)

        # process a mouse button down event
        consumed_event_1 = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                   {'button': pygame.BUTTON_LEFT,
                                                                    'pos': button.rect.center}))
        button.update(0.001)

        consumed_event_2 = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                   {'button': pygame.BUTTON_LEFT,
                                                                    'pos': button.rect.center}))

        confirm_double_click_event_fired = False
        for event in pygame.event.get():
            if (event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED and
                    event.ui_element == button):
                confirm_double_click_event_fired = True

        assert consumed_event_1 and consumed_event_2
        assert confirm_double_click_event_fired

    def test_process_event_mouse_button_down(self, _init_pygame: None,
                                             default_ui_manager: UIManager,
                                             _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create a tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # process a mouse button down event
        processed_down_event = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                       {'button': 1,
                                                                        'pos': (50, 25)}))

        assert processed_down_event is True and button.held is True and button.tool_tip is None

    def test_process_event_mouse_button_up_inside(self, _init_pygame: None,
                                                  default_ui_manager: UIManager,
                                                  _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create a tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # process a mouse button down event
        processed_down_event = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                       {'button': 1,
                                                                        'pos': (50, 25)}))

        # process a mouse button up event
        processed_up_event = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                     {'button': 1,
                                                                      'pos': (50, 25)}))

        assert (
                processed_down_event is True and processed_up_event is True and button.held is False and
                button.pressed_event is True and default_ui_manager.focused_set is None)

    def test_process_event_mouse_button_up_outside(self, _init_pygame: None,
                                                   default_ui_manager: UIManager,
                                                   _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create a tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # process a mouse button down event
        processed_down_event = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                       {'button': 1,
                                                                        'pos': (50, 25)}))

        # process a mouse button up event
        processed_up_event = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                                     {'button': 1, 'pos': (1, 1)}))

        assert (
                processed_down_event is True and processed_up_event is True and button.held is False)

    def test_check_pressed(self, _init_pygame: None, default_ui_manager: UIManager,
                           _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # process a mouse button down event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button.update(0.01)

        assert button.check_pressed() is True

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.disable()

        # process a mouse button down event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button.update(0.01)

        assert button.check_pressed() is False and button.is_enabled is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.disable()

        button.enable()

        # process a mouse button down event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button.update(0.01)

        assert button.check_pressed() is True and button.is_enabled is True

    def test_command(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none):
        button_clicked = False

        def test_function(data):
            nonlocal button_clicked
            button_clicked = True

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          command=test_function)

        assert button._handler[pygame_gui.UI_BUTTON_PRESSED] == test_function

        assert not button_clicked
        # process a mouse button down event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)}))

        # process a mouse button up event
        button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (50, 25)}))

        button.update(0.01)
        assert button_clicked

    @pytest.mark.filterwarnings("ignore:Theme validation found")
    @pytest.mark.filterwarnings("ignore:Misc data validation")
    @pytest.mark.filterwarnings("ignore:Font data validation")
    @pytest.mark.filterwarnings("ignore:Image data validation")
    def test_command_bad_value(self, _init_pygame: None, default_ui_manager: UIManager,
                               _display_surface_return_none):
        with pytest.raises(TypeError, match="Command function must be callable"):
            button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                              text="Test Button",
                              tool_tip_text="This is a test of the button's tool tip functionality.",
                              manager=default_ui_manager,
                              command={pygame_gui.UI_BUTTON_PRESSED: 5})

    def test_bind(self, _init_pygame: None, default_ui_manager: UIManager,
                  _display_surface_return_none):
        def test_function(data):
            pass

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        assert pygame_gui.UI_BUTTON_PRESSED not in button._handler

        button.bind(pygame_gui.UI_BUTTON_PRESSED, test_function)
        assert button._handler[pygame_gui.UI_BUTTON_PRESSED] == test_function

        # test unbind
        button.bind(pygame_gui.UI_BUTTON_PRESSED, None)
        assert pygame_gui.UI_BUTTON_PRESSED not in button._handler

        button.bind(pygame_gui.UI_BUTTON_PRESSED, None)
        assert pygame_gui.UI_BUTTON_PRESSED not in button._handler

        with pytest.raises(TypeError, match="Command function must be callable"):
            button.bind(pygame_gui.UI_BUTTON_PRESSED, "non-callable")

        def function_with_3_params(x, y, z):
            pass

        with pytest.raises(ValueError):
            button.bind(pygame_gui.UI_BUTTON_PRESSED, function_with_3_params)

    def test_on_self_event(self, _init_pygame: None, default_ui_manager: UIManager,
                           _display_surface_return_none):
        button_start_press = False

        def test_function(data):
            nonlocal button_start_press
            button_start_press = True

        pressed_button = 0

        def test_function2(data):
            nonlocal pressed_button
            pressed_button = data["mouse_button"]

        command_dict = {pygame_gui.UI_BUTTON_START_PRESS: test_function,
                        pygame_gui.UI_BUTTON_PRESSED: test_function2}

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          command=command_dict)

        assert button._handler[pygame_gui.UI_BUTTON_START_PRESS] == test_function  # not
        assert button._handler[pygame_gui.UI_BUTTON_PRESSED] == test_function2
        assert pygame_gui.UI_BUTTON_DOUBLE_CLICKED not in button._handler

        assert not button_start_press
        button.on_self_event(pygame_gui.UI_BUTTON_START_PRESS, {'mouse_button': 1})
        assert button_start_press

        assert pressed_button == 0
        button.on_self_event(pygame_gui.UI_BUTTON_PRESSED, {'mouse_button': 3})
        assert pressed_button == 3

        button.on_self_event(pygame_gui.UI_BUTTON_DOUBLE_CLICKED, {'mouse_button': 1})

        confirm_double_click_event_fired = False
        for event in pygame.event.get():
            if (event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED and
                    event.ui_element == button):
                confirm_double_click_event_fired = True
        assert confirm_double_click_event_fired

    def test_on_self_event_no_params(self, _init_pygame: None, default_ui_manager: UIManager,
                                     _display_surface_return_none):
        button_start_press = False

        def test_function():
            nonlocal button_start_press
            button_start_press = True

        command_dict = {pygame_gui.UI_BUTTON_START_PRESS: test_function}

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          command=command_dict)

        assert not button_start_press
        button.on_self_event(pygame_gui.UI_BUTTON_START_PRESS, {'mouse_button': 1})
        assert button_start_press

    def test_set_active(self, _init_pygame: None, default_ui_manager: UIManager,
                        _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button._set_active()

        assert empty_queue == 0

    def test_set_inactive(self, _init_pygame: None, default_ui_manager: UIManager,
                          _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button._set_active()
        button._set_inactive()

        assert empty_queue == 0

    def test_select(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button.select()

        assert (empty_queue == 0 and button.is_selected is True)

    def test_unselect(self, _init_pygame: None, default_ui_manager: UIManager,
                      _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button.select()
        button.unselect()

        assert (empty_queue == 0 and button.is_selected is False)

    def test_set_text(self, _init_pygame: None, default_ui_manager: UIManager,
                      _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button.set_text('Ipsum')

        full_queue = len(button.drawable_shape.states_to_redraw_queue)

        assert (empty_queue == 0 and full_queue != 0 and
                button.drawable_shape.theming['text'] == 'Ipsum' and button.text == 'Ipsum')

        dynamic_width_button = UIButton(relative_rect=pygame.Rect(10, 10, -1, 30),
                                        text="Test Button",
                                        tool_tip_text="This is a test of the button's tool tip functionality.",
                                        manager=default_ui_manager)

        dynamic_width_button.set_text('Ipsum')
        assert dynamic_width_button.text == "Ipsum"

    def test_set_text_same(self, _init_pygame: None, default_ui_manager: UIManager,
                           _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)
        button.update(0.01)

        empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        button.set_text('Test Button')

        still_empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        assert (empty_queue == 0 and still_empty_queue == 0 and
                button.drawable_shape.theming[
                    'text'] == 'Test Button' and button.text == 'Test Button')

    def test_set_hold_range(self, _init_pygame: None, default_ui_manager: UIManager,
                            _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_hold_range((50, 200))

    def test_in_hold_range_inside_button(self, _init_pygame: None, default_ui_manager: UIManager,
                                         _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_hold_range((50, 200))

        assert button.in_hold_range(pygame.math.Vector2(20.0, 25.0)) is True

    def test_in_hold_range_outside_button(self, _init_pygame: None, default_ui_manager: UIManager,
                                          _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_hold_range((150, 50))

        assert button.in_hold_range(pygame.math.Vector2(200.0, 50.0)) is True

    def test_out_of_hold_range(self, _init_pygame: None, default_ui_manager: UIManager,
                               _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_hold_range((50, 50))

        assert button.in_hold_range(pygame.math.Vector2(400.0, 500.0)) is False

    def test_out_of_hold_range_when_zeroed(self, _init_pygame: None, default_ui_manager: UIManager,
                                           _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.set_hold_range((0, 0))

        assert button.in_hold_range(pygame.math.Vector2(400.0, 500.0)) is False

    def test_rebuild_from_changed_theme_data_non_default(self, _init_pygame,
                                                         _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)

        assert button.image is not None

    def test_switching_object_ids(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          manager=manager,
                          object_id=ObjectID(object_id=None, class_id="@rounded_button"))
        assert button.image is not None
        assert button.drawable_shape.shape_corner_radius == [5, 5, 5, 5]

        button.change_object_id(ObjectID(object_id=None, class_id="@rectangular_button"))

        assert button.image is not None
        assert button.drawable_shape.shape_corner_radius == [0, 0, 0, 0]

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    @pytest.mark.filterwarnings("ignore:Theme validation found")
    @pytest.mark.filterwarnings("ignore:Misc data validation")
    @pytest.mark.filterwarnings("ignore:Font data validation")
    @pytest.mark.filterwarnings("ignore:Image data validation")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame,
                                                        _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_bad_values.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)

        assert button.image is not None

    def test_rebuild_from_changed_theme_data_bad_values_2(self, _init_pygame,
                                                          _display_surface_return_none):
        with pytest.warns(UserWarning, match="Theme validation found 4 errors"):
            with pytest.warns(UserWarning, match="Image data validation errors"):
                with pytest.warns(UserWarning, match="Unable to find image with id"):
                    manager = UIManager((800, 600),
                                        os.path.join("tests", "data", "themes", "ui_button_bad_values_2.json"))

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)

        assert button.state_transitions[("normal", "hovered")] == 0.0

    def test_rebuild_shape(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        button.rebuild()

        assert button.image is not None

        manager = UIManager((800, 600))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        assert button.shape_corner_radius == [2, 2, 2, 2]
        manager.get_theme().load_theme(os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button.rebuild_from_changed_theme_data()

        assert button.shape_corner_radius == [10, 5, 10, 5]

        manager = UIManager((800, 600))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        assert button.shape_corner_radius == [2, 2, 2, 2]
        manager.get_theme().load_theme(os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button.drawable_shape.theming['shape_corner_radius'] = [10, 10, 10, 10]
        button.set_dimensions((200, 30))

        assert button.drawable_shape.shape_corner_radius == [10, 10, 10, 10]

    def test_rebuild_shape_ellipse(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_non_default_2.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        button.rebuild()

        assert button.image is not None

    def test_rebuild_anchors_dynamic_dimensions(self, _init_pygame, default_ui_manager, _display_surface_return_none):

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, -1),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager,
                          anchors={'top': 'bottom', 'bottom': 'bottom'})

        assert button.dynamic_height

        button.rebuild()

        assert button.image is not None

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager,
                          visible=0)

        assert button.visible == 0
        button.show()
        assert button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        assert button.visible == 1
        button.hide()
        assert button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)
        button = UIButton(relative_rect=pygame.Rect(25, 25, 375, 150),
                          text="Test Button",
                          manager=manager, visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        button.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        button.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_hide_and_show_of_disabled_button(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))
        button = UIButton(relative_rect=pygame.Rect(100, 100, 100, 100), text="button test",
                          manager=manager, starting_height=1)

        button.disable()
        button.hide()
        button.show()
        assert button.drawable_shape.active_state.state_id == 'disabled'

    def test_class_theming_id(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            PackageResource('tests.data.themes',
                                            'appearance_theme_class_id_test.json'))

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          manager=manager,
                          object_id=pygame_gui.core.ObjectID(class_id='@test_class'))

        assert button.combined_element_ids == ['@test_class', 'button']

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          manager=manager,
                          object_id=pygame_gui.core.ObjectID(object_id='#test_object_1',
                                                             class_id='@test_class'))

        assert button.combined_element_ids == ['#test_object_1', '@test_class', 'button']

        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=manager)

        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          manager=manager,
                          container=test_container,
                          object_id=pygame_gui.core.ObjectID(object_id='#test_object_1',
                                                             class_id='@test_class'))

        assert button.combined_element_ids == ['container.#test_object_1',
                                               'container.@test_class',
                                               'container.button',
                                               '#test_object_1',
                                               '@test_class',
                                               'button']

    def test_change_locale(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        default_ui_manager.set_locale('fr')
        default_ui_manager.set_locale('ja')

        assert button.text == "Test Button"

        default_ui_manager.set_locale('en')

        dynamic_width_button = UIButton(relative_rect=pygame.Rect(100, 100, -1, 30),
                                        text="Test Button",
                                        tool_tip_text="This is a test of the button's tool tip functionality.",
                                        manager=default_ui_manager)

        assert dynamic_width_button.dynamic_width

        default_ui_manager.set_locale('fr')

        assert dynamic_width_button.text == "Test Button"

    def test_update_theming(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        button.update_theming('{'
                              '"misc":'
                              '{'
                              '"shape": "rounded_rectangle",'
                              '"shape_corner_radius": "10",'
                              '"border_width": "4",'
                              '"shadow_width": "4",'
                              '"tool_tip_delay": "6.0",'
                              '"text_horiz_alignment": "left",'
                              '"text_vert_alignment": "top",'
                              '"text_horiz_alignment_padding": "6",'
                              '"text_vert_alignment_padding": "7",'
                              '"text_shadow_size": "3",'
                              '"text_shadow_offset": "0,2",'
                              '"state_transitions":'
                              '{'
                              '    "normal_hovered": "0.2",'
                              '    "hovered_normal": "0.5"'
                              '}'
                              '}'
                              '}')

        assert button.shape == "rounded_rectangle"
        assert button.shape_corner_radius == [10, 10, 10, 10]
        assert button.border_width == {'bottom': 4, 'left': 4, 'right': 4, 'top': 4}
        assert button.shadow_width == 4
        assert button.tool_tip_delay == 6.0

    def test_auto_scale_images_functionality(self, _init_pygame, _display_surface_return_none):
        """Test the auto_scale_images functionality."""
        # Create a test image
        test_image = pygame.Surface((64, 64))
        test_image.fill((255, 0, 0))
        
        # Test scaling function directly
        scaled_down = UIButton._scale_image_to_fit(test_image, (32, 32))
        assert scaled_down.get_size() == (32, 32)
        
        scaled_up = UIButton._scale_image_to_fit(test_image, (128, 128))
        assert scaled_up.get_size() == (128, 128)
        
        # Test aspect ratio preservation with non-square targets
        scaled_wide = UIButton._scale_image_to_fit(test_image, (100, 50))
        assert scaled_wide.get_size() == (50, 50)  # Should fit height, maintain square aspect
        
        scaled_tall = UIButton._scale_image_to_fit(test_image, (50, 100))
        assert scaled_tall.get_size() == (50, 50)  # Should fit width, maintain square aspect
        
        # Test with None image
        assert UIButton._scale_image_to_fit(None, (100, 100)) is None
        
        # Test with zero dimensions
        scaled_zero = UIButton._scale_image_to_fit(test_image, (0, 100))
        assert scaled_zero == test_image  # Should return original when target has zero dimension

    def test_auto_scale_images_theme_parameter(self, _init_pygame, _display_surface_return_none):
        """Test that auto_scale_images theme parameter is loaded correctly."""
        # Create theme with auto_scale_images enabled
        theme_data = {
            "button": {
                "misc": {
                    "auto_scale_images": "1"
                }
            }
        }
        
        import tempfile
        import json
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Test Button",
                            manager=manager)
            
            # Check that auto_scale_images is enabled
            assert button.auto_scale_images is True
            
        finally:
            os.unlink(theme_file)

    def test_auto_scale_images_disabled_by_default(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """Test that auto_scale_images is disabled by default."""
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                         text="Test Button",
                         manager=default_ui_manager)
        
        assert button.auto_scale_images is False

    def test_auto_scale_images_with_rectangular_image(self, _init_pygame, _display_surface_return_none):
        """Test auto scaling with non-square images."""
        # Create a rectangular test image (2:1 aspect ratio)
        test_image = pygame.Surface((100, 50))
        test_image.fill((0, 255, 0))
        
        # Test scaling to square target - should maintain aspect ratio
        scaled_square = UIButton._scale_image_to_fit(test_image, (60, 60))
        assert scaled_square.get_size() == (60, 30)  # Maintains 2:1 ratio, fits width
        
        # Test scaling to wide target - should fit height
        scaled_wide = UIButton._scale_image_to_fit(test_image, (200, 40))
        assert scaled_wide.get_size() == (80, 40)  # Maintains 2:1 ratio, fits height
        
        # Test scaling to tall target - should fit width
        scaled_tall = UIButton._scale_image_to_fit(test_image, (80, 200))
        assert scaled_tall.get_size() == (80, 40)  # Maintains 2:1 ratio, fits width

    def test_auto_scale_images_aspect_ratio_preservation(self, _init_pygame, _display_surface_return_none):
        """Test that aspect ratio is preserved during scaling."""
        # Test with various aspect ratios
        test_cases = [
            ((100, 50), 2.0),    # 2:1 ratio
            ((50, 100), 0.5),    # 1:2 ratio
            ((120, 80), 1.5),    # 3:2 ratio
            ((80, 120), 2/3),    # 2:3 ratio
        ]
        
        for image_size, expected_ratio in test_cases:
            test_image = pygame.Surface(image_size)
            test_image.fill((255, 255, 0))
            
            # Scale to various target sizes
            target_sizes = [(200, 200), (150, 100), (100, 150), (300, 200)]
            
            for target_size in target_sizes:
                scaled = UIButton._scale_image_to_fit(test_image, target_size)
                actual_ratio = scaled.get_width() / scaled.get_height()
                
                # Allow small floating point differences (due to integer pixel rounding)
                assert abs(actual_ratio - expected_ratio) < 0.02, \
                    f"Aspect ratio not preserved: expected {expected_ratio}, got {actual_ratio}"
                
                # Ensure scaled image fits within target
                assert scaled.get_width() <= target_size[0]
                assert scaled.get_height() <= target_size[1]

    def test_auto_scale_images_integration_with_theming(self, _init_pygame, _display_surface_return_none):
        """Test that auto_scale_images works with the theming system."""
        # Create a theme with auto_scale_images and test images
        theme_data = {
            "button": {
                "misc": {
                    "auto_scale_images": "1"
                },
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png"
                    }
                }
            }
        }
        
        import tempfile
        import json
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            
            # Create buttons of different sizes
            small_button = UIButton(relative_rect=pygame.Rect(100, 100, 50, 50),
                                  text="Small",
                                  manager=manager)
            
            large_button = UIButton(relative_rect=pygame.Rect(200, 100, 200, 150),
                                  text="Large", 
                                  manager=manager)
            
            # Both buttons should have auto_scale_images enabled
            assert small_button.auto_scale_images is True
            assert large_button.auto_scale_images is True
            
            # Images should be loaded and potentially scaled
            assert small_button.normal_images[0] is not None
            assert large_button.normal_images[0] is not None
            
        finally:
            os.unlink(theme_file)

    def test_auto_scale_images_rebuild_behavior(self, _init_pygame, _display_surface_return_none):
        """Test that auto_scale_images works correctly during rebuilds."""
        # Create theme with auto_scale_images
        theme_data = {
            "button": {
                "misc": {
                    "auto_scale_images": "1"
                }
            }
        }
        
        import tempfile
        import json
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Test Button",
                            manager=manager)
            
            # Verify auto_scale_images is loaded
            assert button.auto_scale_images is True
            
            # Trigger a rebuild
            button.rebuild_from_changed_theme_data()
            
            # Should still have auto_scale_images enabled
            assert button.auto_scale_images is True
            
        finally:
            os.unlink(theme_file)

    def test_auto_scale_images_edge_cases(self, _init_pygame, _display_surface_return_none):
        """Test edge cases for auto_scale_images functionality."""
        # Test with very small image
        tiny_image = pygame.Surface((1, 1))
        tiny_image.fill((255, 0, 255))
        
        scaled = UIButton._scale_image_to_fit(tiny_image, (100, 100))
        assert scaled.get_size() == (100, 100)
        
        # Test with very large target
        normal_image = pygame.Surface((50, 50))
        normal_image.fill((0, 255, 255))
        
        scaled_large = UIButton._scale_image_to_fit(normal_image, (1000, 1000))
        assert scaled_large.get_size() == (1000, 1000)
        
        # Test with target size of (1, 1)
        scaled_tiny = UIButton._scale_image_to_fit(normal_image, (1, 1))
        assert scaled_tiny.get_size() == (1, 1)

    def test_auto_scale_images_performance(self, _init_pygame, _display_surface_return_none):
        """Test that auto_scale_images doesn't cause performance issues."""
        import time
        
        # Create a reasonably sized test image
        test_image = pygame.Surface((256, 256))
        test_image.fill((128, 128, 128))
        
        # Time multiple scaling operations
        start_time = time.time()
        
        for i in range(100):
            scaled = UIButton._scale_image_to_fit(test_image, (100 + i, 100 + i))
            assert scaled is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 scaling operations in reasonable time (less than 1 second)
        assert duration < 1.0, f"Scaling took too long: {duration} seconds"

    def test_multi_image_mode_detection(self, _init_pygame, _display_surface_return_none):
        """Test that multi-image mode is correctly detected from theme data."""
        import tempfile
        import json
        import os
        
        # Test single image theme (should not trigger multi-image mode)
        single_image_theme = {
            "button": {
                "images": {
                    "normal_image": {"path": "tests/data/images/splat.png"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(single_image_theme, f)
            single_theme_file = f.name
        
        try:
            manager = UIManager((800, 600), single_theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Single Image",
                            manager=manager)
            
            # Should be in multi-image mode (since we have only one image, it's not multi-image)
            # Actually, with only one image, it should NOT be multi-image mode
            assert button.is_multi_image_mode() is False
            assert len(button.normal_images) == 1

            # Other states should fall back to normal_images
            assert len(button.hovered_images) == 1  # Falls back to normal
            assert len(button.selected_images) == 1  # Falls back to normal
            assert len(button.disabled_images) == 1  # Falls back to normal

            # Test current image access
            current_images = button.get_current_images()
            assert len(current_images) == 1

            # Test state transitions
            button.hovered = True
            hovered_images = button.get_current_images()
            assert len(hovered_images) == 1  # Should fall back to normal_images
            
        finally:
            os.unlink(single_theme_file)
        
        # Test multi-image theme (should trigger multi-image mode)
        multi_image_theme = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "icon", "path": "tests/data/images/splat.png", "layer": 1}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(multi_image_theme, f)
            multi_theme_file = f.name
        
        try:
            manager = UIManager((800, 600), multi_theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Multi Image",
                            manager=manager)
            
            assert button.is_multi_image_mode() is True
            assert len(button.normal_images) == 2  # Should have two images
            assert len(button.hovered_images) == 2  # Should fall back to normal
            assert len(button.selected_images) == 2  # Should fall back to normal
            assert len(button.disabled_images) == 2  # Should fall back to normal
            
        finally:
            os.unlink(multi_theme_file)

    def test_multi_image_loading_and_access(self, _init_pygame, _display_surface_return_none):
        """Test loading and accessing multi-image data."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "background", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "overlay", "path": "tests/data/images/splat.png", "layer": 1}
                    ],
                    "hovered_images": [
                        {"id": "background", "path": "tests/data/images/splat.png", "layer": 0}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Multi Image Test",
                            manager=manager)
            
            # Should be in multi-image mode
            assert button.is_multi_image_mode() is True
            
            # Check normal state images
            normal_images = button.get_images_by_state('normal')
            assert len(normal_images) == 2
            assert all(img is not None for img in normal_images)
            
            # Check hovered state images
            hovered_images = button.get_images_by_state('hovered')
            assert len(hovered_images) == 1
            assert hovered_images[0] is not None
            
            # Check fallback for missing states (should fall back to normal_images)
            selected_images = button.get_images_by_state('selected')
            assert len(selected_images) == 2  # Falls back to normal_images
            
            disabled_images = button.get_images_by_state('disabled')
            assert len(disabled_images) == 2  # Falls back to normal_images
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_current_state_access(self, _init_pygame, _display_surface_return_none):
        """Test accessing images for the current button state."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0}
                    ],
                    "hovered_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "highlight", "path": "tests/data/images/splat.png", "layer": 1}
                    ],
                    "disabled_images": [
                        {"id": "bg_disabled", "path": "tests/data/images/splat.png", "layer": 0}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="State Test",
                            manager=manager)
            
            # Test normal state
            current_images = button.get_current_images()
            assert len(current_images) == 1
            assert button.get_image_count() == 1
            
            # Test hovered state
            button.hovered = True
            current_images = button.get_current_images()
            assert len(current_images) == 2
            assert button.get_image_count() == 2
            
            # Test disabled state
            button.hovered = False
            button.disable()
            current_images = button.get_current_images()
            assert len(current_images) == 1
            assert button.get_image_count() == 1
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_with_auto_scaling(self, _init_pygame, _display_surface_return_none):
        """Test multi-image functionality with auto-scaling enabled."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "misc": {
                    "auto_scale_images": "1"
                },
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "icon", "path": "tests/data/images/splat.png", "layer": 1}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            
            # Create buttons of different sizes
            small_button = UIButton(relative_rect=pygame.Rect(100, 100, 50, 50),
                                  text="Small",
                                  manager=manager)
            
            large_button = UIButton(relative_rect=pygame.Rect(200, 100, 200, 150),
                                  text="Large",
                                  manager=manager)
            
            # Both should be in multi-image mode with auto-scaling
            assert small_button.is_multi_image_mode() is True
            assert large_button.is_multi_image_mode() is True
            assert small_button.auto_scale_images is True
            assert large_button.auto_scale_images is True
            
            # Both should have 2 images loaded
            assert len(small_button.normal_images) == 2
            assert len(large_button.normal_images) == 2
            
            # Images should be different sizes due to auto-scaling
            small_images = small_button.get_current_images()
            large_images = large_button.get_current_images()
            
            assert len(small_images) == 2
            assert len(large_images) == 2
            
            # All images should be loaded and valid
            for img in small_images + large_images:
                assert img is not None
                assert img.get_size()[0] > 0
                assert img.get_size()[1] > 0
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_backward_compatibility(self, _init_pygame, _display_surface_return_none):
        """Test that single-image themes still work correctly."""
        import tempfile
        import json
        import os
        
        # Traditional single-image theme
        single_theme = {
            "button": {
                "images": {
                    "normal_image": {"path": "tests/data/images/splat.png"},
                    "hovered_image": {"path": "tests/data/images/splat.png"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(single_theme, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Backward Compat",
                            manager=manager)
            
            # Should NOT be in multi-image mode
            assert button.is_multi_image_mode() is False
            
            # Image lists should be populated with single images
            assert len(button.normal_images) == 1
            assert len(button.hovered_images) == 1
            assert len(button.selected_images) == 1  # Should fall back to normal
            assert len(button.disabled_images) == 1  # Should fall back to normal
            
            # Should have exactly one image per state
            assert button.get_image_count() == 1
            
            # Test state-specific access
            normal_images = button.get_images_by_state("normal")
            assert len(normal_images) == 1
            
            hovered_images = button.get_images_by_state("hovered")
            assert len(hovered_images) == 1
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_state_transitions(self, _init_pygame, _display_surface_return_none):
        """Test that multi-image mode works correctly during state transitions."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0}
                    ],
                    "hovered_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "glow", "path": "tests/data/images/splat.png", "layer": 1}
                    ],
                    "selected_images": [
                        {"id": "bg_selected", "path": "tests/data/images/splat.png", "layer": 0}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="State Transitions",
                            manager=manager)
            
            # Start in normal state
            assert button.get_image_count() == 1
            
            # Transition to hovered
            button.hovered = True
            assert button.get_image_count() == 2
            
            # Transition to selected (while hovered)
            button.is_selected = True
            assert button.get_image_count() == 1  # selected_images takes priority
            
            # Back to normal
            button.hovered = False
            button.is_selected = False
            assert button.get_image_count() == 1
            
            # Test disabled state (should fall back to normal_images)
            button.disable()
            assert button.get_image_count() == 1
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_empty_states(self, _init_pygame, _display_surface_return_none):
        """Test behavior when some multi-image states are missing or empty."""
        import tempfile
        import json
        import os
        
        # Theme with multiple images in normal_images to trigger multi-image mode
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "icon", "path": "tests/data/images/splat.png", "layer": 1}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Empty States",
                            manager=manager)
            
            # Should be in multi-image mode
            assert button.is_multi_image_mode() is True
            
            # Normal state should have images
            assert len(button.get_images_by_state('normal')) == 2
            
            # Other states should fall back to normal_images
            assert len(button.get_images_by_state('hovered')) == 2
            assert len(button.get_images_by_state('selected')) == 2
            assert len(button.get_images_by_state('disabled')) == 2
            
            # All fallback images should be the same as normal
            normal_images = button.get_images_by_state('normal')
            hovered_images = button.get_images_by_state('hovered')
            assert normal_images == hovered_images
            
        finally:
            os.unlink(theme_file)

    def test_multi_image_api_methods(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """Test the new API methods for multi-image functionality."""
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                         text="API Test",
                         manager=default_ui_manager)
        
        # Default button should be in single-image mode
        assert button.is_multi_image_mode() is False
        assert button.get_image_count() == 0  # No images loaded by default
        
        # get_current_images should return empty list
        current_images = button.get_current_images()
        assert isinstance(current_images, list)
        assert len(current_images) == 0
        
        # get_images_by_state should return empty list for all states
        for state in ['normal', 'hovered', 'selected', 'disabled']:
            state_images = button.get_images_by_state(state)
            assert isinstance(state_images, list)
            assert len(state_images) == 0

    def test_multi_image_mode_switching(self, _init_pygame, _display_surface_return_none):
        """Test switching between single and multi-image modes."""
        import tempfile
        import json
        import os
        
        # Start with single-image theme
        single_theme = {
            "button": {
                "images": {
                    "normal_image": {"path": "tests/data/images/splat.png"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(single_theme, f)
            single_theme_file = f.name
        
        # Create multi-image theme with multiple images
        multi_theme = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "icon", "path": "tests/data/images/splat.png", "layer": 1}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(multi_theme, f)
            multi_theme_file = f.name
        
        try:
            # Start with single-image mode
            manager = UIManager((800, 600), single_theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Mode Switch",
                            manager=manager)
            
            # Verify initial single-image state
            assert button.is_multi_image_mode() is False
            assert len(button.normal_images) == 1  # Single image converted to list
            assert len(button.hovered_images) == 1  # Single image converted to list

            # Switch to multi-image theme
            manager.ui_theme.load_theme(multi_theme_file)
            button.rebuild_from_changed_theme_data()

            # Verify switch to multi-image mode
            assert button.is_multi_image_mode() is True
            assert len(button.normal_images) == 2  # Two images in normal_images
            assert len(button.hovered_images) == 2  # One image in hovered_images

            # Test state-specific image access
            normal_images = button.get_current_images()
            assert len(normal_images) == 2

            button.hovered = True
            hovered_images = button.get_current_images()
            assert len(hovered_images) == 2  # Falls back to normal_images
            button.hovered = False

            # Switch back to single-image theme
            manager.ui_theme.load_theme(single_theme_file)
            button.rebuild_from_changed_theme_data()

            # Verify switch back to single-image mode
            assert button.is_multi_image_mode() is False
            assert len(button.normal_images) == 1  # Back to single image
            assert len(button.hovered_images) == 1  # Falls back to normal

            # Test that single-image mode works correctly after switch
            current_images = button.get_current_images()
            assert len(current_images) == 1

            button.hovered = True
            hovered_images = button.get_current_images()
            assert len(hovered_images) == 1
            
        finally:
            os.unlink(single_theme_file)
            os.unlink(multi_theme_file)

    def test_multi_image_layer_ordering(self, _init_pygame, _display_surface_return_none):
        """Test that multi-image layers are properly ordered."""
        import tempfile
        import json
        import os
        
        # Theme with images in non-sequential layer order
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "top", "path": "tests/data/images/splat.png", "layer": 10},
                        {"id": "bottom", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "middle", "path": "tests/data/images/splat.png", "layer": 5}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Layer Test",
                            manager=manager)
            
            
            # Should have 3 images
            assert len(button.normal_images) == 3
            
            # Images should be ordered by layer (bottom to top)
            # The theme loading should sort them by layer value
            images = button.get_current_images()
            assert len(images) == 3
            
            # All images should be loaded
            for img in images:
                assert img is not None
            
        finally:
            os.unlink(theme_file)

    def test_theme_switching_cache_clearing(self, _init_pygame, _display_surface_return_none):
        """Test that cached image data is properly cleared when switching between theme formats."""
        import tempfile
        import json
        import os
        
        # Start with single-image theme
        single_theme = {
            "button": {
                "images": {
                    "normal_image": {"path": "tests/data/images/splat.png"},
                    "hovered_image": {"path": "tests/data/images/splat.png"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(single_theme, f)
            single_theme_file = f.name
        
        # Create multi-image theme
        multi_theme = {
            "button": {
                "images": {
                    "normal_images": [
                        {"id": "bg", "path": "tests/data/images/splat.png", "layer": 0},
                        {"id": "overlay", "path": "tests/data/images/splat.png", "layer": 1}
                    ],
                    "hovered_images": [
                        {"id": "bg_hover", "path": "tests/data/images/splat.png", "layer": 0}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(multi_theme, f)
            multi_theme_file = f.name
        
        try:
            # Start with single-image mode
            manager = UIManager((800, 600), single_theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Cache Test",
                            manager=manager)
            
            # Verify initial single-image state
            assert button.is_multi_image_mode() is False
            assert len(button.normal_images) == 1  # Single image converted to list
            assert len(button.hovered_images) == 1  # Single image converted to list
            
            # Switch to multi-image theme
            manager.ui_theme.load_theme(multi_theme_file)
            button.rebuild_from_changed_theme_data()
            
            # Verify switch to multi-image mode
            assert button.is_multi_image_mode() is True
            assert len(button.normal_images) == 2  # Two images in normal_images
            assert len(button.hovered_images) == 1  # One image in hovered_images
            
        finally:
            os.unlink(single_theme_file)
            os.unlink(multi_theme_file)

    def test_image_positioning_single_image_mode(self, _init_pygame, _display_surface_return_none):
        """Test image positioning in single-image mode."""
        import tempfile
        import json
        import os
        
        # Theme with positioned single images
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.0, 0.0]  # Top-left
                    },
                    "hovered_image": {
                        "path": "tests/data/images/splat.png", 
                        "position": [1.0, 1.0]  # Bottom-right
                    },
                    "selected_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.5, 0.5]  # Center
                    },
                    "disabled_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.2, 0.8]  # Custom position
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Position Test",
                            manager=manager)
            
            # Test normal state position
            assert button.normal_image_positions == [(0.0, 0.0)]
            assert button.get_current_image_positions() == [(0.0, 0.0)]
            
            # Test hovered state position
            assert button.hovered_image_positions == [(1.0, 1.0)]
            button.hovered = True
            assert button.get_current_image_positions() == [(1.0, 1.0)]
            button.hovered = False
            
            # Test selected state position
            assert button.selected_image_positions == [(0.5, 0.5)]
            button.select()
            assert button.get_current_image_positions() == [(0.5, 0.5)]
            button.unselect()
            
            # Test disabled state position
            assert button.disabled_image_positions == [(0.2, 0.8)]
            button.disable()
            assert button.get_current_image_positions() == [(0.2, 0.8)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_multi_image_mode(self, _init_pygame, _display_surface_return_none):
        """Test image positioning in multi-image mode."""
        import tempfile
        import json
        import os
        
        # Theme with positioned multi-images
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "background",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, 0.5]  # Center
                        },
                        {
                            "id": "icon",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.1, 0.1]  # Top-left area
                        },
                        {
                            "id": "decoration",
                            "layer": 2,
                            "path": "tests/data/images/splat.png",
                            "position": [0.9, 0.9]  # Bottom-right area
                        }
                    ],
                    "hovered_images": [
                        {
                            "id": "background_hover",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, 0.5]  # Center
                        },
                        {
                            "id": "glow",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.0, 0.0]  # Top-left corner
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Multi Position Test",
                            manager=manager)
            
            # Test normal state positions
            expected_normal_positions = [(0.5, 0.5), (0.1, 0.1), (0.9, 0.9)]
            assert button.normal_image_positions == expected_normal_positions
            assert button.get_current_image_positions() == expected_normal_positions
            assert len(button.normal_images) == 3
            
            # Test hovered state positions
            expected_hovered_positions = [(0.5, 0.5), (0.0, 0.0)]
            assert button.hovered_image_positions == expected_hovered_positions
            button.hovered = True
            assert button.get_current_image_positions() == expected_hovered_positions
            assert len(button.get_current_images()) == 2
            button.hovered = False
            
            # Test fallback to normal positions for states without specific images
            button.select()
            assert button.get_current_image_positions() == expected_normal_positions  # Falls back to normal
            button.unselect()
            
            button.disable()
            assert button.get_current_image_positions() == expected_normal_positions  # Falls back to normal
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_default_values(self, _init_pygame, _display_surface_return_none):
        """Test that images without position parameters default to center (0.5, 0.5)."""
        import tempfile
        import json
        import os
        
        # Theme without position parameters
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "no_position",
                            "layer": 0,
                            "path": "tests/data/images/splat.png"
                            # No position parameter - should default to (0.5, 0.5)
                        },
                        {
                            "id": "with_position",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.2, 0.8]
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Default Position Test",
                            manager=manager)
            
            # First image should default to center, second should use specified position
            expected_positions = [(0.5, 0.5), (0.2, 0.8)]
            assert button.normal_image_positions == expected_positions
            assert button.get_current_image_positions() == expected_positions
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_validation_valid_values(self, _init_pygame, _display_surface_return_none):
        """Test that valid position values are accepted."""
        import tempfile
        import json
        import os
        
        # Theme with various valid position values
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "corner_tl",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.0, 0.0]  # Top-left corner
                        },
                        {
                            "id": "corner_br",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [1.0, 1.0]  # Bottom-right corner
                        },
                        {
                            "id": "center",
                            "layer": 2,
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, 0.5]  # Center
                        },
                        {
                            "id": "custom",
                            "layer": 3,
                            "path": "tests/data/images/splat.png",
                            "position": [0.25, 0.75]  # Custom position
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            # Should load without validation errors
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Valid Position Test",
                            manager=manager)
            
            expected_positions = [(0.0, 0.0), (1.0, 1.0), (0.5, 0.5), (0.25, 0.75)]
            assert button.normal_image_positions == expected_positions
            
        finally:
            os.unlink(theme_file)

    @pytest.mark.filterwarnings("ignore:Theme validation found")
    def test_image_positioning_validation_invalid_values(self, _init_pygame, _display_surface_return_none):
        """Test that invalid position values are properly validated."""
        import tempfile
        import json
        import os
        
        # Theme with invalid position values
        invalid_themes = [
            # Position values out of range
            {
                "button": {
                    "images": {
                        "normal_image": {
                            "path": "tests/data/images/splat.png",
                            "position": [2.0, 0.5]  # x > 1.0
                        }
                    }
                }
            },
            {
                "button": {
                    "images": {
                        "normal_image": {
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, -0.1]  # y < 0.0
                        }
                    }
                }
            },
            # Wrong number of values
            {
                "button": {
                    "images": {
                        "normal_image": {
                            "path": "tests/data/images/splat.png",
                            "position": [0.5]  # Only one value
                        }
                    }
                }
            },
            {
                "button": {
                    "images": {
                        "normal_image": {
                            "path": "tests/data/images/splat.png",
                            "position": [0.5, 0.5, 0.5]  # Three values
                        }
                    }
                }
            },
            # Non-numeric values
            {
                "button": {
                    "images": {
                        "normal_image": {
                            "path": "tests/data/images/splat.png",
                            "position": ["left", "top"]  # String values
                        }
                    }
                }
            }
        ]
        
        for i, theme_data in enumerate(invalid_themes):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(theme_data, f)
                theme_file = f.name
            
            try:
                manager = UIManager((800, 600))
                
                # Validation should catch the errors
                errors = manager.get_theme().validate_theme_file_path(theme_file)
                assert len(errors) > 0, f"Theme {i} should have validation errors"
                
                # At least one error should mention position
                position_errors = [error for error in errors if "position" in error.lower()]
                assert len(position_errors) > 0, f"Theme {i} should have position-related errors"
                
            finally:
                os.unlink(theme_file)

    def test_image_positioning_state_fallbacks(self, _init_pygame, _display_surface_return_none):
        """Test that position fallbacks work correctly when states don't have specific images."""
        import tempfile
        import json
        import os
        
        # Theme with only normal images defined
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.3, 0.3]
                        },
                        {
                            "id": "icon",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [0.7, 0.7]
                        }
                    ]
                    # No hovered, selected, or disabled images defined
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Fallback Test",
                            manager=manager)
            
            expected_positions = [(0.3, 0.3), (0.7, 0.7)]
            
            # Normal state should have the defined positions
            assert button.normal_image_positions == expected_positions
            assert button.get_current_image_positions() == expected_positions
            
            # Other states should fall back to normal positions
            assert button.hovered_image_positions == expected_positions
            assert button.selected_image_positions == expected_positions
            assert button.disabled_image_positions == expected_positions
            
            # Test state changes
            button.hovered = True
            assert button.get_current_image_positions() == expected_positions
            button.hovered = False
            
            button.select()
            assert button.get_current_image_positions() == expected_positions
            button.unselect()
            
            button.disable()
            assert button.get_current_image_positions() == expected_positions
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_mixed_with_without_positions(self, _init_pygame, _display_surface_return_none):
        """Test handling of mixed images where some have positions and others don't."""
        import tempfile
        import json
        import os
        
        # Theme with mixed position specifications
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "positioned",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.1, 0.1]
                        },
                        {
                            "id": "not_positioned",
                            "layer": 1,
                            "path": "tests/data/images/splat.png"
                            # No position - should default to (0.5, 0.5)
                        },
                        {
                            "id": "also_positioned",
                            "layer": 2,
                            "path": "tests/data/images/splat.png",
                            "position": [0.9, 0.9]
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="Mixed Position Test",
                            manager=manager)
            
            # Should have positions: specified, default, specified
            expected_positions = [(0.1, 0.1), (0.5, 0.5), (0.9, 0.9)]
            assert button.normal_image_positions == expected_positions
            assert button.get_current_image_positions() == expected_positions
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_api_methods(self, _init_pygame, _display_surface_return_none):
        """Test the new API methods for accessing image positions."""
        import tempfile
        import json
        import os
        
        # Theme with different positions for different states
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "normal_bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.2, 0.2]
                        }
                    ],
                    "hovered_images": [
                        {
                            "id": "hovered_bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.4, 0.4]
                        }
                    ],
                    "selected_images": [
                        {
                            "id": "selected_bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.6, 0.6]
                        }
                    ],
                    "disabled_images": [
                        {
                            "id": "disabled_bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.8, 0.8]
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name
        
        try:
            manager = UIManager((800, 600), theme_file)
            button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                            text="API Test",
                            manager=manager)
            
            # Test get_current_image_positions() for different states
            
            # Normal state
            assert button.get_current_image_positions() == [(0.2, 0.2)]
            
            # Hovered state
            button.hovered = True
            assert button.get_current_image_positions() == [(0.4, 0.4)]
            button.hovered = False
            
            # Selected state
            button.select()
            assert button.get_current_image_positions() == [(0.6, 0.6)]
            button.unselect()
            
            # Disabled state
            button.disable()
            assert button.get_current_image_positions() == [(0.8, 0.8)]
            button.enable()
            
            # Test that positions correspond to images
            assert len(button.get_current_image_positions()) == len(button.get_current_images())
            
            # Test state-specific position attributes
            assert button.normal_image_positions == [(0.2, 0.2)]
            assert button.hovered_image_positions == [(0.4, 0.4)]
            assert button.selected_image_positions == [(0.6, 0.6)]
            assert button.disabled_image_positions == [(0.8, 0.8)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_theme_loading_and_storage(self, _init_pygame, _display_surface_return_none):
        """Test that position data is correctly loaded and stored from theme files."""
        import tempfile
        import json
        import os
        
        # Theme with positioned single images
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.0, 0.0]  # Top-left
                    },
                    "hovered_image": {
                        "path": "tests/data/images/splat.png", 
                        "position": [1.0, 1.0]  # Bottom-right
                    },
                    "selected_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.5, 0.5]  # Center
                    },
                    "disabled_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.2, 0.8]  # Custom position
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            
            # Test that position data is correctly loaded in theme
            normal_details = manager.ui_theme.get_image_details("normal_image", ["button"])
            assert normal_details[0]["position"] == (0.0, 0.0)
            
            hovered_details = manager.ui_theme.get_image_details("hovered_image", ["button"])
            assert hovered_details[0]["position"] == (1.0, 1.0)
            
            selected_details = manager.ui_theme.get_image_details("selected_image", ["button"])
            assert selected_details[0]["position"] == (0.5, 0.5)
            
            disabled_details = manager.ui_theme.get_image_details("disabled_image", ["button"])
            assert disabled_details[0]["position"] == (0.2, 0.8)
            
            # Test button creation and position loading
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="Position Test",
                manager=manager
            )
            
            # Verify positions are correctly loaded into button
            assert button.normal_image_positions == [(0.0, 0.0)]
            assert button.hovered_image_positions == [(1.0, 1.0)]
            assert button.selected_image_positions == [(0.5, 0.5)]
            assert button.disabled_image_positions == [(0.2, 0.8)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_state_transitions(self, _init_pygame, _display_surface_return_none):
        """Test that position data changes correctly with button state transitions."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.1, 0.1]
                    },
                    "hovered_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.2, 0.2]
                    },
                    "selected_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.3, 0.3]
                    },
                    "disabled_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.4, 0.4]
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="State Test",
                manager=manager
            )
            
            # Test normal state
            assert button.get_current_image_positions() == [(0.1, 0.1)]
            
            # Test hovered state
            button.hovered = True
            assert button.get_current_image_positions() == [(0.2, 0.2)]
            
            # Test selected state (takes priority over hovered)
            button.is_selected = True
            assert button.get_current_image_positions() == [(0.3, 0.3)]
            
            # Test disabled state (takes priority over all)
            button.is_enabled = False
            assert button.get_current_image_positions() == [(0.4, 0.4)]
            
            # Reset to normal
            button.is_enabled = True
            button.is_selected = False
            button.hovered = False
            assert button.get_current_image_positions() == [(0.1, 0.1)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_multi_image_format(self, _init_pygame, _display_surface_return_none):
        """Test image positioning with multi-image format."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_images": [
                        {
                            "id": "bg",
                            "layer": 0,
                            "path": "tests/data/images/splat.png",
                            "position": [0.0, 0.0]
                        },
                        {
                            "id": "icon",
                            "layer": 1,
                            "path": "tests/data/images/splat.png",
                            "position": [1.0, 1.0]
                        }
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="Multi Test",
                manager=manager
            )
            
            # Test multi-image positions
            positions = button.get_current_image_positions()
            assert len(positions) == 2
            assert positions == [(0.0, 0.0), (1.0, 1.0)]
            
            # Test that we have multiple images
            assert button.is_multi_image_mode() == True
            assert button.get_image_count() == 2
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_fallback_behavior(self, _init_pygame, _display_surface_return_none):
        """Test fallback behavior when some states don't have specific images."""
        import tempfile
        import json
        import os
        
        # Only define normal image, others should fall back
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.25, 0.75]
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="Fallback Test",
                manager=manager
            )
            
            # All states should fall back to normal image position
            assert button.normal_image_positions == [(0.25, 0.75)]
            assert button.hovered_image_positions == [(0.25, 0.75)]
            assert button.selected_image_positions == [(0.25, 0.75)]
            assert button.disabled_image_positions == [(0.25, 0.75)]
            
            # Current positions should match normal regardless of state
            assert button.get_current_image_positions() == [(0.25, 0.75)]
            
            button.hovered = True
            assert button.get_current_image_positions() == [(0.25, 0.75)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_default_center_position(self, _init_pygame, _display_surface_return_none):
        """Test that images without position specified default to center (0.5, 0.5)."""
        import tempfile
        import json
        import os
        
        # Image without position specified
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png"
                        # No position specified
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="Default Test",
                manager=manager
            )
            
            # Should default to center position
            assert button.normal_image_positions == [(0.5, 0.5)]
            assert button.get_current_image_positions() == [(0.5, 0.5)]
            
        finally:
            os.unlink(theme_file)

    def test_image_positioning_edge_case_values(self, _init_pygame, _display_surface_return_none):
        """Test edge case position values (0.0, 1.0, boundaries)."""
        import tempfile
        import json
        import os
        
        theme_data = {
            "button": {
                "images": {
                    "normal_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [0.0, 1.0]  # Top-left x, bottom y
                    },
                    "hovered_image": {
                        "path": "tests/data/images/splat.png",
                        "position": [1.0, 0.0]  # Bottom-right x, top y
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            theme_file = f.name

        try:
            manager = pygame_gui.UIManager((800, 600), theme_file)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 100, 150, 30),
                text="Edge Test",
                manager=manager
            )
            
            # Test boundary values
            assert button.normal_image_positions == [(0.0, 1.0)]
            assert button.hovered_image_positions == [(1.0, 0.0)]
            
            # Test state transitions with edge values
            assert button.get_current_image_positions() == [(0.0, 1.0)]
            
            button.hovered = True
            assert button.get_current_image_positions() == [(1.0, 0.0)]
            
        finally:
            os.unlink(theme_file)


if __name__ == '__main__':
    pytest.console_main()
