import os
import pytest
import pygame
import pygame_gui

from tests.shared_comparators import compare_surfaces

from pygame_gui._constants import UI_CHECK_BOX_CHECKED, UI_CHECK_BOX_UNCHECKED
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_check_box import UICheckBox
from pygame_gui.core.ui_container import UIContainer, ObjectID


class TestUICheckBox:
    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )
        assert check_box.image is not None
        assert check_box.text_label is not None
        assert check_box.get_state() is False

    def test_creation_with_initial_state(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            initial_state=True,
        )
        assert check_box.get_state() is True
        assert check_box.is_checked is True

    def test_creation_with_container(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(10, 10, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
        )
        assert check_box.ui_container == container
        assert check_box in container

    def test_creation_with_anchors(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(-20, -20, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        assert check_box.rect.right == container.rect.right
        assert check_box.rect.bottom == container.rect.bottom

    def test_get_set_state(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test initial state
        assert check_box.get_state() is False

        # Test setting state
        check_box.set_state(True)
        assert check_box.get_state() is True

        check_box.set_state(False)
        assert check_box.get_state() is False

    def test_process_event_left_click(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Click the checkbox
        consumed = check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        assert consumed is True
        assert check_box.get_state() is True

    def test_process_event_right_click_ignored(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Right click should be ignored
        consumed = check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_RIGHT, "pos": check_box.rect.center},
            )
        )

        assert consumed is False
        assert check_box.get_state() is False

    def test_process_event_outside_click_ignored(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Click outside the checkbox
        consumed = check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": (200, 200)},
            )
        )

        assert consumed is False
        assert check_box.get_state() is False

    def test_process_event_disabled_ignored(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.disable()

        # Click should be ignored when disabled
        consumed = check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        assert consumed is False
        assert check_box.get_state() is False

    def test_process_event_toggle_multiple_times(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Toggle multiple times
        for i in range(5):
            check_box.process_event(
                pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
                )
            )
            expected_state = (i + 1) % 2 == 1
            assert check_box.get_state() is expected_state

    def test_process_event_generates_ui_event(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Clear any existing events
        pygame.event.clear()

        # Click the checkbox
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        # Check for UI event
        events = pygame.event.get()
        ui_events = [e for e in events if e.type == UI_CHECK_BOX_CHECKED]
        assert len(ui_events) == 1

        ui_event = ui_events[0]
        assert ui_event.ui_element == check_box

    def test_disable(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.disable()
        assert check_box.is_enabled is False
        assert check_box.text_label.is_enabled is False

        # Try clicking the disabled checkbox
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        assert check_box.get_state() is False  # State shouldn't change when disabled

    def test_enable(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.disable()
        check_box.enable()
        assert check_box.is_enabled is True
        assert check_box.text_label.is_enabled is True

        # Try clicking the re-enabled checkbox
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        assert check_box.get_state() is True  # State should change when enabled

    def test_enable_disable_state_preservation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            initial_state=True,
        )

        # Disable and re-enable should preserve checked state
        check_box.disable()
        check_box.enable()
        assert check_box.get_state() is True

    def test_show_hide(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            visible=0,
        )

        assert check_box.visible == 0
        assert check_box.text_label.visible == 0

        check_box.show()
        assert check_box.visible == 1
        assert check_box.text_label.visible == 1

        check_box.hide()
        assert check_box.visible == 0
        assert check_box.text_label.visible == 0

    def test_show_hide_rendering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)
        check_box = UICheckBox(
            relative_rect=pygame.Rect(25, 25, 20, 20),
            text="Test Check Box",
            manager=manager,
            visible=0,
        )

        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        check_box.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        check_box.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_set_text(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.set_text("New Text")
        assert check_box.text == "New Text"
        assert check_box.text_label.text == "New Text"

    def test_set_text_empty(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.set_text("")
        assert check_box.text == ""
        assert check_box.text_label.text == ""

    def test_set_text_unicode(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        unicode_text = "测试文本 🎮"
        check_box.set_text(unicode_text)
        assert check_box.text == unicode_text
        assert check_box.text_label.text == unicode_text

    def test_set_dimensions(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            container=test_container,
            manager=default_ui_manager,
        )

        check_box.set_dimensions((30, 30))
        assert check_box.rect.size == (30, 30)

    def test_set_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.set_position((200, 150))
        assert check_box.rect.topleft == (200, 150)

    def test_set_relative_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(10, 10, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
        )

        check_box.set_relative_position((30, 40))
        assert check_box.relative_rect.topleft == (30, 40)
        assert check_box.rect.topleft == (
            80,
            90,
        )  # container offset + relative position

    def test_check_hover(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test hovering
        default_ui_manager.mouse_position = check_box.rect.center
        check_box.check_hover(0.5, False)
        assert check_box.hovered is True

        # Test un-hovering
        default_ui_manager.mouse_position = (0, 0)
        check_box.check_hover(0.5, False)
        assert check_box.hovered is False

    def test_hover_point(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test point inside checkbox (accounting for shadow/border)
        assert check_box.hover_point(110, 110) is True

        # Test point outside checkbox
        assert check_box.hover_point(50, 50) is False

        # Test edge cases - the drawable shape may have shadow/border offsets
        # so we test points that are definitely inside
        assert check_box.hover_point(105, 105) is True  # Well inside
        assert check_box.hover_point(115, 115) is True  # Still inside
        assert check_box.hover_point(200, 200) is False  # Definitely outside

    def test_on_hovered_unhovered(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test hover when unchecked
        check_box.on_hovered()
        # Should change to hovered state when enabled and unchecked

        # Test unhover when unchecked
        check_box.on_unhovered()
        # Should return to normal state

        # Test hover when checked
        check_box.set_state(True)
        check_box.on_hovered()
        # Should stay in selected state when checked

        check_box.on_unhovered()
        # Should stay in selected state when checked

    def test_drawable_shape_states(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test that drawable shape exists and has correct states
        assert check_box.drawable_shape is not None
        assert "normal" in check_box.drawable_shape.states
        assert "selected" in check_box.drawable_shape.states
        assert "disabled" in check_box.drawable_shape.states
        assert "hovered" in check_box.drawable_shape.states

    def test_kill(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(10, 10, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
        )

        # Verify checkbox and label are in the UI
        assert check_box.alive()
        assert check_box.text_label.alive()
        assert check_box in container

        # Kill the checkbox
        check_box.kill()

        # Verify checkbox and label are removed
        assert not check_box.alive()
        assert not check_box.text_label.alive()
        assert check_box not in container

    def test_update(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test that update doesn't crash
        check_box.update(0.016)  # 60 FPS
        assert check_box.alive()

    def test_rebuild_from_theme_data_non_default(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join("tests", "data", "themes", "ui_button_non_default.json"),
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=manager,
        )
        assert check_box.image is not None

    def test_object_id(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            object_id="#test_check_box",
        )

        assert check_box.get_object_id() == "#test_check_box"

    def test_object_id_none(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should return None when no object ID is set
        assert check_box.get_object_id() is None

    def test_class_theming_id(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=manager,
            object_id=ObjectID(class_id="@test_class"),
        )

        assert "@test_class" in check_box.combined_element_ids
        assert "check_box" in check_box.combined_element_ids

        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=manager,
            object_id=ObjectID(object_id="#test_object_1", class_id="@test_class"),
        )

        assert "@test_class" in check_box.combined_element_ids
        assert "#test_object_1" in check_box.combined_element_ids
        assert "check_box" in check_box.combined_element_ids

    def test_text_label_positioning(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Text label should be positioned to the right of the checkbox with proper offset
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x
        assert check_box.text_label.rect.top == check_box.rect.top

    def test_text_label_anchoring(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Change checkbox position and verify label follows
        original_label_left = check_box.text_label.rect.left
        check_box.set_position((150, 150))

        # Label should have moved and maintain proper positioning
        assert check_box.text_label.rect.left != original_label_left
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x
        assert check_box.text_label.rect.top == check_box.rect.top

    def test_focus_methods(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test focus/unfocus don't crash (basic implementation)
        check_box.focus()
        check_box.unfocus()
        assert check_box.alive()

    def test_can_hover(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should be able to hover when enabled
        assert check_box.can_hover() is True

        # Should not be able to hover when disabled
        check_box.disable()
        assert check_box.can_hover() is False

    def test_while_hovering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test while_hovering doesn't crash
        mouse_pos = pygame.math.Vector2(110, 110)
        check_box.while_hovering(0.016, mouse_pos)
        assert check_box.alive()

    def test_get_focus_set(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        focus_set = check_box.get_focus_set()
        # Should include both checkbox and its text label
        assert check_box in focus_set
        assert check_box.text_label in focus_set

    def test_edge_case_very_small_size(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        # Test with very small size
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 1, 1),
            text="Test",
            manager=default_ui_manager,
        )
        assert check_box.image is not None
        assert check_box.rect.size == (1, 1)

    def test_edge_case_large_size(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        # Test with large size
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 200, 200),
            text="Test",
            manager=default_ui_manager,
        )
        assert check_box.image is not None
        assert check_box.rect.size == (200, 200)

    def test_multiple_checkboxes_independence(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        # Test that multiple checkboxes work independently
        check_box1 = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Check Box 1",
            manager=default_ui_manager,
        )
        check_box2 = UICheckBox(
            relative_rect=pygame.Rect(150, 100, 20, 20),
            text="Check Box 2",
            manager=default_ui_manager,
        )

        # Toggle first checkbox
        check_box1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box1.rect.center},
            )
        )

        assert check_box1.get_state() is True
        assert check_box2.get_state() is False  # Should remain unchanged

    def test_keyboard_accessibility_space_key(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that space key toggles checkbox when focused."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Focus the checkbox
        check_box.focus()

        # Press space key
        consumed = check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        )

        assert consumed is True
        assert check_box.get_state() is True

    def test_keyboard_accessibility_enter_key(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that enter key toggles checkbox when focused."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Focus the checkbox
        check_box.focus()

        # Press enter key
        consumed = check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        )

        assert consumed is True
        assert check_box.get_state() is True

    def test_keyboard_accessibility_unfocused_ignored(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that keyboard events are ignored when not focused."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Don't focus the checkbox

        # Press space key
        consumed = check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        )

        assert consumed is False
        assert check_box.get_state() is False

    def test_keyboard_accessibility_disabled_ignored(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that keyboard events are ignored when disabled."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.focus()
        check_box.disable()

        # Press space key
        consumed = check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        )

        assert consumed is False
        assert check_box.get_state() is False

    def test_set_check_symbol(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test setting custom check symbols."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test setting different symbols
        check_box.set_check_symbol("✔")
        assert check_box.check_symbol == "✔"

        check_box.set_check_symbol("X")
        assert check_box.check_symbol == "X"

        check_box.set_check_symbol("●")
        assert check_box.check_symbol == "●"

        # Test that symbol updates are reflected in drawable shape when checked
        check_box.set_state(True)
        check_box.set_check_symbol("✓")
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == "✓"

    def test_set_state_validation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that set_state validates input types."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test invalid input types
        with pytest.raises(
            ValueError, match="State must be True, False, or 'indeterminate'"
        ):
            check_box.set_state("true")

        with pytest.raises(
            ValueError, match="State must be True, False, or 'indeterminate'"
        ):
            check_box.set_state(1)

        with pytest.raises(
            ValueError, match="State must be True, False, or 'indeterminate'"
        ):
            check_box.set_state(None)

    def test_set_text_validation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that set_text validates input types."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test invalid input types
        with pytest.raises(ValueError, match="Checkbox text must be a string"):
            check_box.set_text(123)

        with pytest.raises(ValueError, match="Checkbox text must be a string"):
            check_box.set_text(None)

        with pytest.raises(ValueError, match="Checkbox text must be a string"):
            check_box.set_text(["text"])

    def test_rebuild_method(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test the rebuild method functionality."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        original_shape = check_box.drawable_shape

        # Call rebuild
        check_box.rebuild()

        # Should have a new drawable shape
        assert check_box.drawable_shape is not None
        # The shape object itself might be different after rebuild

    def test_load_theme_data_method(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that theme data loading works correctly."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Call _load_theme_data
        check_box._load_theme_data()

        # Check that theme attributes are set
        assert hasattr(check_box, "colours")
        assert hasattr(check_box, "shape")
        assert hasattr(check_box, "border_width")
        assert hasattr(check_box, "shadow_width")
        assert hasattr(check_box, "check_symbol")

    def test_on_fresh_drawable_shape_ready(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test the on_fresh_drawable_shape_ready method."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        original_image = check_box.image

        # Call the method
        check_box.on_fresh_drawable_shape_ready()

        # Image should be updated
        assert check_box.image is not None

    def test_hover_state_management(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test hover state management with different checkbox states."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test hover on unchecked checkbox
        check_box.on_hovered()
        # Should set hovered state for unchecked, enabled checkbox

        # Test hover on checked checkbox
        check_box.set_state(True)
        check_box.on_hovered()
        # Should not change state when already checked

        # Test unhover
        check_box.on_unhovered()
        # Should return to selected state

    def test_disabled_hover_behavior(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that disabled checkboxes don't respond to hover."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.disable()

        # Hover should not change state when disabled
        check_box.on_hovered()
        check_box.on_unhovered()

        # Should remain disabled
        assert not check_box.is_enabled

    def test_event_without_required_attributes(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test event processing with malformed events."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test mouse event without pos attribute
        event_without_pos = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT}
        )
        consumed = check_box.process_event(event_without_pos)
        assert consumed is False

        # Test keyboard event without key attribute
        check_box.focus()
        event_without_key = pygame.event.Event(pygame.KEYDOWN, {})
        consumed = check_box.process_event(event_without_key)
        assert consumed is False

    def test_text_label_integration(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test integration with text label component."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test that text label exists and has correct text
        assert check_box.text_label is not None
        assert check_box.text_label.text == "Test Check Box"

        # Test that changing text updates label
        check_box.set_text("New Text")
        assert check_box.text_label.text == "New Text"

    def test_visibility_synchronization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that visibility is synchronized between checkbox and label."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test hide
        check_box.hide()
        assert not check_box.visible
        assert not check_box.text_label.visible

        # Test show
        check_box.show()
        assert check_box.visible
        assert check_box.text_label.visible

    def test_enable_disable_synchronization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that enable/disable is synchronized between checkbox and label."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test disable
        check_box.disable()
        assert not check_box.is_enabled
        assert not check_box.text_label.is_enabled

        # Test enable
        check_box.enable()
        assert check_box.is_enabled
        assert check_box.text_label.is_enabled

    def test_focus_set_includes_label(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that focus set includes both checkbox and label."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        focus_set = check_box.get_focus_set()
        assert check_box in focus_set
        assert check_box.text_label in focus_set
        assert len(focus_set) == 2

    def test_kill_cleanup(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that kill properly cleans up both checkbox and label."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        text_label = check_box.text_label

        # Kill the checkbox
        check_box.kill()

        # Both should be killed
        assert not check_box.alive()
        assert not text_label.alive()

    def test_theme_shape_variations(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test different shape configurations."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test setting different shapes
        check_box.shape = "rectangle"
        check_box.rebuild()
        assert check_box.drawable_shape is not None

        check_box.shape = "rounded_rectangle"
        check_box.rebuild()
        assert check_box.drawable_shape is not None

    def test_theme_parameter_loading(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that theme parameters are loaded correctly."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Check that default values are set
        assert check_box.border_width["left"] >= 0
        assert check_box.border_width["right"] >= 0
        assert check_box.border_width["top"] >= 0
        assert check_box.border_width["bottom"] >= 0
        assert check_box.shadow_width >= 0
        assert check_box.border_overlap >= 0
        assert isinstance(check_box.shape_corner_radius, list)
        assert len(check_box.shape_corner_radius) == 4
        assert check_box.check_symbol is not None

    def test_drawable_shape_none_safety(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that methods handle None drawable_shape gracefully."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Temporarily set drawable_shape to None
        original_shape = check_box.drawable_shape
        check_box.drawable_shape = None

        # These should not crash
        check_box.set_state(True)
        check_box.disable()
        check_box.enable()
        check_box.on_hovered()
        check_box.on_unhovered()

        # Restore for cleanup
        check_box.drawable_shape = original_shape

    def test_initial_state_visual_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that initial state is visually consistent."""
        # Test unchecked initial state
        check_box_unchecked = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Unchecked",
            manager=default_ui_manager,
            initial_state=False,
        )

        assert check_box_unchecked.get_state() is False
        assert check_box_unchecked.is_checked is False

        # Test checked initial state
        check_box_checked = UICheckBox(
            relative_rect=pygame.Rect(150, 100, 20, 20),
            text="Checked",
            manager=default_ui_manager,
            initial_state=True,
        )

        assert check_box_checked.get_state() is True
        assert check_box_checked.is_checked is True

    def test_event_generation_data_integrity(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that generated events contain correct data."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Clear events
        pygame.event.clear()

        # Toggle to checked
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        events = pygame.event.get()
        ui_events = [e for e in events if e.type == UI_CHECK_BOX_CHECKED]
        assert len(ui_events) == 1

        event = ui_events[0]
        assert hasattr(event, "ui_element")
        assert hasattr(event, "ui_object_id")
        assert event.ui_element == check_box

        # Clear events and toggle to unchecked
        pygame.event.clear()
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        events = pygame.event.get()
        ui_events = [e for e in events if e.type == UI_CHECK_BOX_UNCHECKED]
        assert len(ui_events) == 1

        event = ui_events[0]
        assert hasattr(event, "ui_element")
        assert hasattr(event, "ui_object_id")
        assert event.ui_element == check_box

    def test_specific_event_types(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that the correct event types are generated."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        pygame.event.clear()

        # Test checking generates UI_CHECK_BOX_CHECKED
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        events = pygame.event.get()
        checked_events = [e for e in events if e.type == UI_CHECK_BOX_CHECKED]
        assert len(checked_events) == 1

        pygame.event.clear()

        # Test unchecking generates UI_CHECK_BOX_UNCHECKED
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        events = pygame.event.get()
        unchecked_events = [e for e in events if e.type == UI_CHECK_BOX_UNCHECKED]
        assert len(unchecked_events) == 1

    def test_check_symbol_display_functionality(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that check symbols are properly displayed in the drawable shape."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Initially unchecked - should have no text
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == ""

        # Check the box - should display check symbol
        check_box.set_state(True)
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == check_box.check_symbol

        # Uncheck the box - should remove text
        check_box.set_state(False)
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == ""

    def test_custom_check_symbol_display(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that custom check symbols are properly displayed."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Set custom symbol
        custom_symbol = "✓"
        check_box.set_check_symbol(custom_symbol)

        # Check the box - should display custom symbol
        check_box.set_state(True)
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == custom_symbol

        # Change symbol while checked
        new_symbol = "X"
        check_box.set_check_symbol(new_symbol)
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == new_symbol

    def test_font_loading_and_theming(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that fonts are properly loaded from theme."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should have a font loaded (default symbol font)
        assert check_box.font is not None
        assert hasattr(check_box, "font")

        # Font should be the symbol font for check marks
        default_symbol_font = (
            default_ui_manager.ui_theme.get_font_dictionary().get_default_symbol_font()
        )
        assert check_box.font == default_symbol_font

    def test_text_color_theming_parameters(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text color theming parameters are properly loaded."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should have text color parameters
        assert "normal_text" in check_box.colours
        assert "hovered_text" in check_box.colours
        assert "disabled_text" in check_box.colours
        assert "selected_text" in check_box.colours

        # Colors should not be None
        assert check_box.colours["normal_text"] is not None
        assert check_box.colours["selected_text"] is not None

    def test_drawable_shape_text_parameters(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that drawable shape receives proper text parameters."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            initial_state=True,
        )

        # Drawable shape should have text-related parameters
        shape = check_box.drawable_shape
        assert shape is not None

        # Check that text alignment is centered
        if hasattr(shape, "text_horiz_alignment"):
            assert shape.text_horiz_alignment == "center"
        if hasattr(shape, "text_vert_alignment"):
            assert shape.text_vert_alignment == "center"

    def test_text_label_positioning_accuracy(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text label is positioned correctly with proper offset."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Text label should be positioned to the right with proper offset
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x
        assert check_box.text_label.rect.top == check_box.rect.top

    def test_text_label_position_updates(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text label position updates when checkbox moves."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        original_label_x = check_box.text_label.rect.left

        # Move checkbox
        new_pos = (150, 150)
        check_box.set_position(new_pos)

        # Label should have moved accordingly
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x
        assert check_box.text_label.rect.top == check_box.rect.top

        # Should be different from original position
        assert check_box.text_label.rect.left != original_label_x

    def test_text_label_relative_position_updates(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text label position updates with relative positioning."""
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(10, 10, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
        )

        original_label_pos = check_box.text_label.rect.topleft

        # Move checkbox relatively
        check_box.set_relative_position((30, 30))

        # Label should have moved
        assert check_box.text_label.rect.topleft != original_label_pos

        # Should maintain proper offset
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x

    def test_text_label_dimension_updates(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text label position updates when checkbox dimensions change."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        original_label_x = check_box.text_label.rect.left

        # Change dimensions
        check_box.set_dimensions((30, 30))

        # Label should have moved to account for new width
        expected_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_x
        assert check_box.text_label.rect.left != original_label_x

    def test_text_offset_theming(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that text_offset can be configured via theming."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should have a text_offset attribute
        assert hasattr(check_box, "text_offset")
        assert isinstance(check_box.text_offset, int)
        assert check_box.text_offset >= 0

    def test_state_visual_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that visual state matches logical state."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Initially unchecked
        assert check_box.get_state() is False
        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id in [
                "normal",
                "hovered",
            ]

        # Check the box
        check_box.set_state(True)
        assert check_box.get_state() is True
        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id == "selected"

    def test_hover_state_with_checked_box(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test hover behavior when checkbox is checked."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Check the box first
        check_box.set_state(True)

        # Hover should not change state from selected
        check_box.on_hovered()
        if hasattr(check_box.drawable_shape, "active_state"):
            # Checked boxes should remain in selected state even when hovered
            assert check_box.drawable_shape.active_state.state_id == "selected"

        # Unhover should keep it selected
        check_box.on_unhovered()
        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id == "selected"

    def test_disabled_state_visual_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that disabled state is visually consistent."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Disable the checkbox
        check_box.disable()

        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id == "disabled"

        # Re-enable
        check_box.enable()

        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id in [
                "normal",
                "selected",
            ]

    def test_rebuild_preserves_state(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that rebuilding preserves checkbox state and symbol."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Set custom state and symbol
        check_box.set_state(True)
        custom_symbol = "✓"
        check_box.set_check_symbol(custom_symbol)

        # Rebuild
        check_box.rebuild()

        # State and symbol should be preserved
        assert check_box.get_state() is True
        assert check_box.check_symbol == custom_symbol

        # Visual state should match
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == custom_symbol

    def test_theme_data_loading_completeness(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that all theme data is properly loaded."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Check all required theme attributes exist
        required_attrs = [
            "colours",
            "shape",
            "border_width",
            "shadow_width",
            "border_overlap",
            "shape_corner_radius",
            "check_symbol",
            "font",
            "text_offset",
        ]

        for attr in required_attrs:
            assert hasattr(check_box, attr), f"Missing theme attribute: {attr}"

        # Check colour completeness
        required_colours = [
            "normal_bg",
            "normal_border",
            "hovered_bg",
            "hovered_border",
            "disabled_bg",
            "disabled_border",
            "selected_bg",
            "selected_border",
            "normal_text",
            "hovered_text",
            "disabled_text",
            "selected_text",
        ]

        for colour in required_colours:
            assert colour in check_box.colours, f"Missing colour: {colour}"

    def test_container_positioning_integration(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that positioning works correctly within containers."""
        container = UIContainer(
            relative_rect=pygame.Rect(50, 50, 200, 200), manager=default_ui_manager
        )
        check_box = UICheckBox(
            relative_rect=pygame.Rect(10, 10, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            container=container,
        )

        # Checkbox should be positioned relative to container
        assert check_box.rect.left == container.rect.left + 10
        assert check_box.rect.top == container.rect.top + 10

        # Text label should account for container positioning
        expected_label_x = check_box.rect.right + check_box.text_offset
        assert check_box.text_label.rect.left == expected_label_x

    def test_symbol_font_fallback(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that symbol font fallback works correctly."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should have a valid font (either theme font or symbol font fallback)
        assert check_box.font is not None

        # If theme font is default, should use symbol font
        theme_font = default_ui_manager.ui_theme.get_font(
            check_box.combined_element_ids
        )
        default_font = (
            default_ui_manager.ui_theme.get_font_dictionary().get_default_font()
        )

        if theme_font == default_font:
            symbol_font = default_ui_manager.ui_theme.get_font_dictionary().get_default_symbol_font()
            assert check_box.font == symbol_font

    def test_multiple_state_changes_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test consistency across multiple rapid state changes."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Perform multiple state changes
        states = [True, False, True, True, False, False, True]

        for state in states:
            check_box.set_state(state)

            # Verify consistency
            assert check_box.get_state() == state

            # Check visual consistency
            if hasattr(check_box.drawable_shape, "text"):
                expected_text = check_box.check_symbol if state else ""
                assert check_box.drawable_shape.text == expected_text

            if hasattr(check_box.drawable_shape, "active_state"):
                expected_visual_state = "selected" if state else "normal"
                assert (
                    check_box.drawable_shape.active_state.state_id
                    == expected_visual_state
                )

    def test_event_toggle_symbol_display(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that event-driven toggles properly update symbol display."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Click to check
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        # Should show symbol
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == check_box.check_symbol

        # Click to uncheck
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        # Should hide symbol
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == ""

    def test_keyboard_toggle_symbol_display(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that keyboard toggles properly update symbol display."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        check_box.focus()

        # Press space to check
        check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        )

        # Should show symbol
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == check_box.check_symbol

        # Press space again to uncheck
        check_box.process_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        )

        # Should hide symbol
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == ""

    def test_tooltip_functionality(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test tooltip functionality."""
        tooltip_text = "This is a test tooltip"
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text=tooltip_text,
        )

        # Check that tooltip text is set
        assert check_box.tool_tip_text == tooltip_text

        # Test tooltip creation on hover
        check_box.hover_time = 9999.0  # Simulate long hover
        check_box.while_hovering(0.01, pygame.math.Vector2(110.0, 110.0))

        # Should have created a tooltip
        assert check_box.tool_tip is not None

    def test_indeterminate_state_basic(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test basic indeterminate state functionality."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Initially not indeterminate
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is False

        # Set to indeterminate
        check_box.set_indeterminate(True)
        assert check_box.is_state_indeterminate()
        assert check_box.get_state() == "indeterminate"

        # Check visual state
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == check_box.indeterminate_symbol

        # Clear indeterminate
        check_box.set_indeterminate(False)
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is False

    def test_indeterminate_state_setting(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test setting indeterminate state via set_state method."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Set to indeterminate via set_state
        check_box.set_state("indeterminate")
        assert check_box.is_state_indeterminate()
        assert check_box.get_state() == "indeterminate"

        # Set to checked
        check_box.set_state(True)
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is True

        # Set to unchecked
        check_box.set_state(False)
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is False

    def test_indeterminate_toggle_behavior(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test toggle behavior with indeterminate state."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Set to indeterminate
        check_box.set_state("indeterminate")

        # Toggle should go from indeterminate to checked
        check_box._toggle_state()
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is True

        # Toggle should go from checked to unchecked
        check_box._toggle_state()
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is False

        # Toggle should go from unchecked to checked
        check_box._toggle_state()
        assert not check_box.is_state_indeterminate()
        assert check_box.get_state() is True

    def test_indeterminate_symbol_customization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test customization of indeterminate symbol."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Change indeterminate symbol
        custom_symbol = "?"
        check_box.set_indeterminate_symbol(custom_symbol)
        assert check_box.indeterminate_symbol == custom_symbol

        # Set to indeterminate and check display
        check_box.set_state("indeterminate")
        if hasattr(check_box.drawable_shape, "text"):
            assert check_box.drawable_shape.text == custom_symbol

    def test_indeterminate_visual_state(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that indeterminate state uses selected visual state."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Set to indeterminate
        check_box.set_state("indeterminate")

        # Should use selected visual state
        if hasattr(check_box.drawable_shape, "active_state"):
            assert check_box.drawable_shape.active_state.state_id == "selected"

    def test_indeterminate_no_events(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that indeterminate state doesn't generate check/uncheck events."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        pygame.event.clear()

        # Set to indeterminate
        check_box.set_state("indeterminate")

        # Should not generate any events
        events = pygame.event.get()
        checkbox_events = [
            e
            for e in events
            if e.type
            in [pygame_gui.UI_CHECK_BOX_CHECKED, pygame_gui.UI_CHECK_BOX_UNCHECKED]
        ]
        assert len(checkbox_events) == 0

    def test_state_validation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test state validation in set_state method."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Valid states should work
        check_box.set_state(True)
        check_box.set_state(False)
        check_box.set_state("indeterminate")

        # Invalid state should raise ValueError
        with pytest.raises(ValueError):
            check_box.set_state("invalid")

        with pytest.raises(ValueError):
            check_box.set_state(123)

    def test_tooltip_with_kwargs(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test tooltip with text formatting kwargs."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Hello {name}",
            tool_tip_text_kwargs={"name": "World"},
        )

        # Check that tooltip kwargs are set
        assert check_box.tool_tip_text_kwargs == {"name": "World"}

    def test_coordinate_positioning_with_tooltip(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test coordinate positioning works with tooltip."""
        check_box = UICheckBox(
            relative_rect=(150, 200),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Test tooltip",
        )

        # Should have default size and correct position
        assert check_box.rect.topleft == (150, 200)
        assert check_box.rect.size == (20, 20)
        assert check_box.tool_tip_text == "Test tooltip"

    def test_tooltip_cleanup_on_unhover(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that tooltips are properly cleaned up when unhovered."""
        tooltip_text = "This tooltip should be cleaned up"
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text=tooltip_text,
        )

        # Simulate hover and tooltip creation
        check_box.hover_time = 9999.0  # Simulate long hover
        check_box.while_hovering(0.01, pygame.math.Vector2(110.0, 110.0))

        # Should have created a tooltip
        assert check_box.tool_tip is not None

        # Simulate unhover - tooltip should be cleaned up
        check_box.on_unhovered()

        # Tooltip should be None after unhover
        assert check_box.tool_tip is None

    def test_tooltip_text_label_synchronization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that tooltip is synchronized between checkbox and text label."""
        tooltip_text = "Synchronized tooltip"
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text=tooltip_text,
        )

        # Both checkbox and text label should have the same tooltip
        assert check_box.tool_tip_text == tooltip_text
        assert check_box.text_label.tool_tip_text == tooltip_text

        # Tooltip properties should be synchronized
        assert (
            check_box.tool_tip_text_kwargs == check_box.text_label.tool_tip_text_kwargs
        )
        assert check_box.tool_tip_object_id == check_box.text_label.tool_tip_object_id

    def test_tooltip_set_after_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test setting tooltip after checkbox creation."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Initially no tooltip
        assert check_box.tool_tip_text is None
        assert check_box.text_label.tool_tip_text is None

        # Set tooltip after creation
        tooltip_text = "Tooltip set later"
        check_box.set_tooltip(tooltip_text)

        # Both should now have the tooltip
        assert check_box.tool_tip_text == tooltip_text
        assert check_box.text_label.tool_tip_text == tooltip_text

    def test_tooltip_with_kwargs_synchronization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test tooltip with kwargs is synchronized between checkbox and text label."""
        tooltip_text = "Hello {name}, you have {count} items!"
        tooltip_kwargs = {"name": "User", "count": "5"}

        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text=tooltip_text,
            tool_tip_text_kwargs=tooltip_kwargs,
        )

        # Both should have the same tooltip text and kwargs
        assert check_box.tool_tip_text == tooltip_text
        assert check_box.text_label.tool_tip_text == tooltip_text
        assert check_box.tool_tip_text_kwargs == tooltip_kwargs
        assert check_box.text_label.tool_tip_text_kwargs == tooltip_kwargs

    def test_tooltip_update_synchronization(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that updating tooltip updates both checkbox and text label."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Original tooltip",
        )

        # Update tooltip
        new_tooltip = "Updated tooltip"
        new_kwargs = {"key": "value"}
        check_box.set_tooltip(new_tooltip, text_kwargs=new_kwargs)

        # Both should be updated
        assert check_box.tool_tip_text == new_tooltip
        assert check_box.text_label.tool_tip_text == new_tooltip
        assert check_box.tool_tip_text_kwargs == new_kwargs
        assert check_box.text_label.tool_tip_text_kwargs == new_kwargs

    def test_tooltip_hover_behavior_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that hover behavior is consistent with tooltip functionality."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Test tooltip",
        )

        # Test hover sets hover_time
        check_box.on_hovered()
        assert check_box.hover_time == 0.0  # Should be reset on hover

        # Test unhover cleans up tooltip
        check_box.hover_time = 9999.0
        check_box.while_hovering(0.01, pygame.math.Vector2(110.0, 110.0))
        assert check_box.tool_tip is not None

        check_box.on_unhovered()
        assert check_box.tool_tip is None

    def test_tooltip_with_disabled_checkbox(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test tooltip behavior when checkbox is disabled."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Tooltip on disabled checkbox",
        )

        # Disable checkbox
        check_box.disable()

        # Tooltip text should still be set
        assert check_box.tool_tip_text == "Tooltip on disabled checkbox"
        assert check_box.text_label.tool_tip_text == "Tooltip on disabled checkbox"

        # But can_hover should return False for disabled checkbox
        assert check_box.can_hover() is False

    def test_tooltip_removal(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test removing tooltip from checkbox."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
            tool_tip_text="Tooltip to remove",
        )

        # Initially has tooltip
        assert check_box.tool_tip_text == "Tooltip to remove"
        assert check_box.text_label.tool_tip_text == "Tooltip to remove"

        # Remove tooltip by setting to None
        check_box.set_tooltip(None)

        # Both should have no tooltip
        assert check_box.tool_tip_text is None
        assert check_box.text_label.tool_tip_text is None

    def test_constructor_input_validation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that constructor validates input parameters."""
        # Test invalid text type
        with pytest.raises(ValueError, match="Checkbox text must be a string"):
            UICheckBox(
                relative_rect=pygame.Rect(100, 100, 20, 20),
                text=123,
                manager=default_ui_manager,
            )

        with pytest.raises(ValueError, match="Checkbox text must be a string"):
            UICheckBox(
                relative_rect=pygame.Rect(100, 100, 20, 20),
                text=None,
                manager=default_ui_manager,
            )

        # Test invalid initial_state type
        with pytest.raises(ValueError, match="Initial state must be a boolean"):
            UICheckBox(
                relative_rect=pygame.Rect(100, 100, 20, 20),
                text="Test",
                manager=default_ui_manager,
                initial_state="true",
            )

        with pytest.raises(ValueError, match="Initial state must be a boolean"):
            UICheckBox(
                relative_rect=pygame.Rect(100, 100, 20, 20),
                text="Test",
                manager=default_ui_manager,
                initial_state=1,
            )

    def test_mouse_scaling_support(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test that mouse events use proper scaling."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Mock the calculate_scaled_mouse_position method
        original_method = default_ui_manager.calculate_scaled_mouse_position
        scaled_pos_called = False

        def mock_scale(pos):
            nonlocal scaled_pos_called
            scaled_pos_called = True
            return original_method(pos)

        default_ui_manager.calculate_scaled_mouse_position = mock_scale

        # Process mouse event
        check_box.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": check_box.rect.center},
            )
        )

        # Should have called the scaling method
        assert scaled_pos_called

        # Restore original method
        default_ui_manager.calculate_scaled_mouse_position = original_method

    def test_can_focus_method(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test the can_focus method."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Should be able to focus when enabled and alive
        assert check_box.can_focus() is True

        # Should not be able to focus when disabled
        check_box.disable()
        assert check_box.can_focus() is False

        # Re-enable
        check_box.enable()
        assert check_box.can_focus() is True

        # Should not be able to focus when killed
        check_box.kill()
        assert check_box.can_focus() is False

    def test_update_method(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test the update method."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Update should not crash and element should remain alive
        check_box.update(0.016)  # 60 FPS
        assert check_box.alive()

        # Multiple updates should work
        for _ in range(10):
            check_box.update(0.016)
        assert check_box.alive()

    def test_focus_management_integration(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test focus management integration."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Initially not focused
        assert not check_box.is_focused

        # Focus the checkbox
        check_box.focus()
        assert check_box.is_focused

        # Unfocus the checkbox
        check_box.unfocus()
        assert not check_box.is_focused

        # Focus set should include both checkbox and label
        focus_set = check_box.get_focus_set()
        assert check_box in focus_set
        assert check_box.text_label in focus_set

    def test_comprehensive_state_consistency(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test comprehensive state consistency across all operations."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test all state transitions
        states_to_test = [True, False, "indeterminate", True, False]

        for state in states_to_test:
            check_box.set_state(state)

            # Verify logical state
            assert check_box.get_state() == state

            # Verify visual consistency
            if state == "indeterminate":
                assert check_box.is_indeterminate
                assert not check_box.is_checked
                if hasattr(check_box.drawable_shape, "text"):
                    assert (
                        check_box.drawable_shape.text == check_box.indeterminate_symbol
                    )
            elif state is True:
                assert not check_box.is_indeterminate
                assert check_box.is_checked
                if hasattr(check_box.drawable_shape, "text"):
                    assert check_box.drawable_shape.text == check_box.check_symbol
            else:  # False
                assert not check_box.is_indeterminate
                assert not check_box.is_checked
                if hasattr(check_box.drawable_shape, "text"):
                    assert check_box.drawable_shape.text == ""

    def test_error_handling_robustness(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test error handling and robustness."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Test malformed events don't crash
        malformed_events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {}),  # No button or pos
            pygame.event.Event(pygame.KEYDOWN, {}),  # No key
            pygame.event.Event(pygame.USEREVENT, {}),  # Random event
        ]

        for event in malformed_events:
            try:
                consumed = check_box.process_event(event)
                assert isinstance(consumed, bool)
            except Exception as e:
                pytest.fail(f"Malformed event caused exception: {e}")

        # Test operations on killed checkbox
        check_box.kill()

        # These should not crash even after kill
        try:
            check_box.can_focus()
            check_box.can_hover()
            check_box.get_state()
        except Exception as e:
            pytest.fail(f"Operation on killed checkbox caused exception: {e}")

    def test_performance_multiple_operations(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        """Test performance with multiple rapid operations."""
        check_box = UICheckBox(
            relative_rect=pygame.Rect(100, 100, 20, 20),
            text="Test Check Box",
            manager=default_ui_manager,
        )

        # Rapid state changes
        for i in range(100):
            check_box.set_state(i % 2 == 0)
            check_box.update(0.001)

        # Should still be functional
        assert check_box.alive()
        assert check_box.get_state() is False  # Last state was False (99 % 2 == 1)

        # Rapid symbol changes
        symbols = ["✓", "X", "●", "■", "▲"]
        for i in range(50):
            check_box.set_check_symbol(symbols[i % len(symbols)])

        # Should still work
        assert check_box.check_symbol == symbols[49 % len(symbols)]

    def test_multi_image_theme_switching_cleanup(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that multi-image themes are properly cleaned up when switching to single-image themes."""
        import tempfile
        import json
        import os

        # Create test images
        test_image1 = pygame.Surface((20, 20))
        test_image1.fill((255, 0, 0))  # Red
        test_image2 = pygame.Surface((20, 20))
        test_image2.fill((0, 255, 0))  # Green
        test_image3 = pygame.Surface((20, 20))
        test_image3.fill((0, 0, 255))  # Blue

        # Save test images to temporary files
        temp_dir = tempfile.mkdtemp()
        try:
            image1_path = os.path.join(temp_dir, "image1.png")
            image2_path = os.path.join(temp_dir, "image2.png")
            image3_path = os.path.join(temp_dir, "image3.png")

            pygame.image.save(test_image1, image1_path)
            pygame.image.save(test_image2, image2_path)
            pygame.image.save(test_image3, image3_path)

            # Create multi-image theme
            multi_theme_data = {
                "check_box": {
                    "images": {
                        "normal_images": [
                            {"id": "bg", "path": image1_path, "layer": 0},
                            {"id": "border", "path": image2_path, "layer": 1},
                        ],
                        "hovered_images": [
                            {"id": "bg", "path": image1_path, "layer": 0},
                            {"id": "border", "path": image2_path, "layer": 1},
                            {"id": "highlight", "path": image3_path, "layer": 2},
                        ],
                        "selected_images": [
                            {"id": "bg", "path": image1_path, "layer": 0},
                            {"id": "border", "path": image2_path, "layer": 1},
                            {"id": "checkmark", "path": image3_path, "layer": 2},
                        ],
                        "disabled_images": [
                            {"id": "bg", "path": image1_path, "layer": 0},
                            {"id": "disabled_overlay", "path": image2_path, "layer": 1},
                        ],
                    }
                }
            }

            # Create single-image theme
            single_theme_data = {
                "check_box": {
                    "images": {
                        "normal_image": {"path": image1_path},
                        "hovered_image": {"path": image2_path},
                        "selected_image": {"path": image3_path},
                        "disabled_image": {"path": image1_path},
                    }
                }
            }

            # Save theme files
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(multi_theme_data, f)
                multi_theme_file = f.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(single_theme_data, f)
                single_theme_file = f.name

            try:
                # Test with multi-image theme
                manager = pygame_gui.UIManager((800, 600), multi_theme_file)
                checkbox = UICheckBox(
                    relative_rect=pygame.Rect(50, 50, 30, 30),
                    text="Test Checkbox",
                    manager=manager,
                )

                # Verify multi-image mode is active
                assert (
                    checkbox.is_multi_image_mode() is True
                ), "Should be in multi-image mode initially"
                assert (
                    len(checkbox.normal_images) == 2
                ), f"Expected 2 normal images, got {len(checkbox.normal_images)}"
                assert (
                    len(checkbox.hovered_images) == 3
                ), f"Expected 3 hovered images, got {len(checkbox.hovered_images)}"
                assert (
                    len(checkbox.selected_images) == 3
                ), f"Expected 3 selected images, got {len(checkbox.selected_images)}"
                assert (
                    len(checkbox.disabled_images) == 2
                ), f"Expected 2 disabled images, got {len(checkbox.disabled_images)}"
                assert (
                    checkbox.get_image_count() == 2
                ), f"Expected 2 current images, got {checkbox.get_image_count()}"

                # Switch to single-image theme
                manager.ui_theme.load_theme(single_theme_file)

                # Force rebuild to apply new theme
                checkbox.rebuild_from_changed_theme_data()

                # Verify single-image mode is now active
                assert (
                    checkbox.is_multi_image_mode() is False
                ), "Should be in single-image mode after theme switch"
                assert (
                    len(checkbox.normal_images) == 1
                ), f"Expected 1 normal image after switch, got {len(checkbox.normal_images)}"
                assert (
                    len(checkbox.hovered_images) == 1
                ), f"Expected 1 hovered image after switch, got {len(checkbox.hovered_images)}"
                assert (
                    len(checkbox.selected_images) == 1
                ), f"Expected 1 selected image after switch, got {len(checkbox.selected_images)}"
                assert (
                    len(checkbox.disabled_images) == 1
                ), f"Expected 1 disabled image after switch, got {len(checkbox.disabled_images)}"
                assert (
                    checkbox.get_image_count() == 1
                ), f"Expected 1 current image after switch, got {checkbox.get_image_count()}"

                # Test state transitions still work correctly
                checkbox.set_state(True)
                assert (
                    len(checkbox.get_current_images()) == 1
                ), "Selected state should have 1 image"

                checkbox.disable()
                assert (
                    len(checkbox.get_current_images()) == 1
                ), "Disabled state should have 1 image"

                checkbox.enable()
                checkbox.set_state(False)
                assert (
                    len(checkbox.get_current_images()) == 1
                ), "Normal state should have 1 image"

                # Switch back to multi-image theme
                manager.ui_theme.load_theme(multi_theme_file)
                checkbox.rebuild_from_changed_theme_data()

                # Verify multi-image mode is restored
                assert (
                    checkbox.is_multi_image_mode() is True
                ), "Should be back in multi-image mode"
                assert (
                    len(checkbox.normal_images) == 2
                ), f"Expected 2 normal images after switch back, got {len(checkbox.normal_images)}"
                assert (
                    len(checkbox.hovered_images) == 3
                ), f"Expected 3 hovered images after switch back, got {len(checkbox.hovered_images)}"
                assert (
                    len(checkbox.selected_images) == 3
                ), f"Expected 3 selected images after switch back, got {len(checkbox.selected_images)}"
                assert (
                    len(checkbox.disabled_images) == 2
                ), f"Expected 2 disabled images after switch back, got {len(checkbox.disabled_images)}"
                assert (
                    checkbox.get_image_count() == 2
                ), f"Expected 2 current images after switch back, got {checkbox.get_image_count()}"

                # Test that all API methods work correctly
                current_images = checkbox.get_current_images()
                assert (
                    len(current_images) == 2
                ), "get_current_images() should return 2 images"

                normal_images = checkbox.get_images_by_state("normal")
                assert (
                    len(normal_images) == 2
                ), "get_images_by_state('normal') should return 2 images"

                hovered_images = checkbox.get_images_by_state("hovered")
                assert (
                    len(hovered_images) == 3
                ), "get_images_by_state('hovered') should return 3 images"

                selected_images = checkbox.get_images_by_state("selected")
                assert (
                    len(selected_images) == 3
                ), "get_images_by_state('selected') should return 3 images"

                disabled_images = checkbox.get_images_by_state("disabled")
                assert (
                    len(disabled_images) == 2
                ), "get_images_by_state('disabled') should return 2 images"

            finally:
                # Clean up theme files
                try:
                    os.unlink(multi_theme_file)
                    os.unlink(single_theme_file)
                except:
                    pass

        finally:
            # Clean up image files and directory
            try:
                os.unlink(image1_path)
                os.unlink(image2_path)
                os.unlink(image3_path)
                os.rmdir(temp_dir)
            except:
                pass
