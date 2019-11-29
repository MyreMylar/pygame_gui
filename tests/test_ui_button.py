import os
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.ui_container import UIContainer


class TestUIButton:

    def test_creation(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)
        assert button.image is not None

    def test_set_any_images_from_theme(self, _init_pygame, default_display_surface):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_button_with_images.json"))
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=manager)
        assert button.normal_image is not None and button.image is not None

    def test_kill(self, _init_pygame, default_ui_manager):
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

    def test_hover_point_outside(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test outside button
        is_inside = button.hover_point(50, 50)
        assert is_inside is False

    def test_hover_point_inside(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button
        is_inside = button.hover_point(150, 115)
        assert is_inside is True

    def test_hover_point_held(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button when held
        button.set_hold_range((100, 100))
        button.held = True
        is_inside = button.hover_point(50, 50)
        assert is_inside is True

    def test_hover_point_not_held(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        # test inside button when held
        button.set_hold_range((100, 100))
        button.held = False
        is_inside = button.hover_point(50, 50)
        assert is_inside is False

    def test_can_hover(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        button.is_enabled = True
        button.held = False

        assert button.can_hover() is True

    def test_cannot_hover(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)

        button.is_enabled = True
        button.held = True

        assert button.can_hover() is False

    def test_on_hovered(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          manager=default_ui_manager)
        button.on_hovered()
        have_hovered_image = button.image == button.drawable_shape.get_surface("hovered")

        assert have_hovered_image is True and button.hover_time == 0.0

    def test_while_hovering(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create the tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        assert button.tool_tip is not None

    def test_while_not_hovering(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # fail to create the tool tip
        button.hover_time = 0.0
        button.while_hovering(0.01, pygame.math.Vector2(250.0, 250.0))

        assert button.tool_tip is None

    def test_on_unhovered(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # create the tool tip
        button.hover_time = 9999.0
        button.while_hovering(0.01, pygame.math.Vector2(150.0, 115.0))

        # unhover and kill the tool tip
        button.on_unhovered()
        assert button.tool_tip is None and button.image == button.drawable_shape.get_surface("normal")

    def test_update(self, _init_pygame, default_ui_manager):
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          manager=default_ui_manager)

        # test the 'one frame' button press flag
        button.pressed_event = True

        redraw_queue_length_pre_update = len(button.drawable_shape.states_to_redraw_queue)
        button.update(0.01)
        redraw_queue_length_post_update = len(button.drawable_shape.states_to_redraw_queue)

        assert button.pressed is True and redraw_queue_length_post_update == (redraw_queue_length_pre_update - 1)

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        button.set_relative_position(pygame.math.Vector2(150.0, 30.0))

        assert button.rect.topleft == (250, 130) and button.drawable_shape.containing_rect.topleft == (250, 130)

    def test_set_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 150, 30),
                          text="Test Button",
                          tool_tip_text="This is a test of the button's tool tip functionality.",
                          container=test_container,
                          manager=default_ui_manager)

        button.set_position(pygame.math.Vector2(150.0, 30.0))

        assert button.relative_rect.topleft == (50, -70) and button.drawable_shape.containing_rect.topleft == (150, 30)

    # def set_dimensions(self, _init_pygame, default_ui_manager):


    # Remaining functions to test
    # ---------------------------
    #
    # def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
    #
    # def update_containing_rect_position(self):
    #
    # def process_event(self, event: pygame.event.Event) -> bool:
    #
    # def check_pressed(self):
    #
    # def disable(self):
    #
    # def enable(self):
    #
    # def set_active(self):
    #
    # def set_inactive(self):
    #
    # def select(self):
    #
    # def unselect(self):
    #
    # def set_text(self, text: str):
    #
    # def set_hold_range(self, xy_range: Tuple[int, int]):
    #
    # def in_hold_range(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]) -> bool:
    #
    # def rebuild_from_changed_theme_data(self):
    #
    # def rebuild_shape(self):
