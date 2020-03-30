import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.ui_container import UIContainer

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIButton:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)
        assert button.image is not None

    @pytest.mark.filterwarnings("ignore:DeprecationWarning")
    def test_set_any_images_from_theme(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_with_images.json"))
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        assert button.normal_image is not None and button.image is not None

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

        confirm_on_hovered_event_fired = any((event.type == pygame.USEREVENT and
                                              event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED and
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

        unhovered_event_fired = any((event.type == pygame.USEREVENT and
                                     event.user_type == pygame_gui.UI_BUTTON_ON_UNHOVERED and
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

        assert button.rect.topleft == (
        250, 130) and button.drawable_shape.containing_rect.topleft == (250, 130)

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        button.set_position(pygame.math.Vector2(150.0, 30.0))

        assert button.relative_rect.topleft == (
        50, -70) and button.drawable_shape.containing_rect.topleft == (150, 30)

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

        test_container.rect.topleft = (50, 50)
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

        consumed_event_2 = button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                                   {'button': pygame.BUTTON_LEFT,
                                                                    'pos': button.rect.center}))

        confirm_double_click_event_fired = False
        for event in pygame.event.get():
            if (
                    event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED and
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
                    button.pressed_event is True and default_ui_manager.focused_element is None)

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

        button.set_active()

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

        button.set_active()
        button.set_inactive()

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

        old_text_rect = button.drawable_shape.aligned_text_rect.copy()

        button.set_text('Ipsum')

        full_queue = len(button.drawable_shape.states_to_redraw_queue)

        assert (empty_queue == 0 and full_queue != 0 and
                button.drawable_shape.aligned_text_rect != old_text_rect and
                button.drawable_shape.theming['text'] == 'Ipsum' and button.text == 'Ipsum')

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

        old_text_rect = button.drawable_shape.aligned_text_rect.copy()

        button.set_text('Test Button')

        still_empty_queue = len(button.drawable_shape.states_to_redraw_queue)

        assert (empty_queue == 0 and still_empty_queue == 0 and
                button.drawable_shape.aligned_text_rect == old_text_rect and
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

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame,
                                                        _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_bad_values.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)

        assert button.image is not None

    def test_rebuild_shape(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        button.rebuild()

        assert button.image is not None

    def test_rebuild_shape_ellipse(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            os.path.join("tests", "data", "themes", "ui_button_non_default_2.json"))
        button = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        button.rebuild()

        assert button.image is not None
