import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_tool_tip import UITooltip


class TestUIToolTip:

    def test_creation(self, _init_pygame, default_ui_manager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)
        assert tool_tip.text_block.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)
        tool_tip.rebuild()
        assert tool_tip.text_block.image is not None

    def test_kill(self, _init_pygame, default_ui_manager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)
        tool_tip.kill()
        assert tool_tip.alive() is False and tool_tip.text_block.alive() is False

    def test_find_valid_position(self, _init_pygame, default_ui_manager: UIManager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(400.0, 300.0))

        assert found_position is True

    @pytest.mark.filterwarnings("ignore:initial position for tool tip is off screen")
    def test_find_invalid_position(self, _init_pygame, default_ui_manager: UIManager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(0.0, -600.0))

        assert found_position is False

    def test_find_valid_position_off_bottom(self, _init_pygame, default_ui_manager: UIManager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(300.0, 590.0))

        root_window_rect = default_ui_manager.get_window_stack().get_root_window().get_container().rect

        assert found_position is True and bool(root_window_rect.contains(tool_tip.rect)) is True

    def test_find_valid_position_off_right(self, _init_pygame, default_ui_manager: UIManager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(799.0, 300.0))

        root_window_rect = default_ui_manager.get_window_stack().get_root_window().get_container().rect

        assert found_position is True and bool(root_window_rect.contains(tool_tip.rect)) is True

    def test_find_valid_position_off_left(self, _init_pygame, default_ui_manager: UIManager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(1.0, 300.0))

        root_window_rect = default_ui_manager.get_window_stack().get_root_window().get_container().rect

        assert found_position is True and bool(root_window_rect.contains(tool_tip.rect)) is True

    @pytest.mark.filterwarnings("ignore:Unable to fit tool tip on screen")
    def test_find_valid_position_screen_too_small(self, _init_pygame):
        manager = UIManager((50, 50))
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=manager)

        found_position = tool_tip.find_valid_position(pygame.Vector2(25.0, 25.0))

        root_window_rect = manager.get_window_stack().get_root_window().get_container().rect

        assert found_position is False and bool(root_window_rect.contains(tool_tip.rect)) is False

    def test_non_default_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_tool_tip_non_default.json"))
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=manager)

        assert tool_tip.text_block.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    def test_bad_values_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_tool_tip_bad_values.json"))
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=manager)

        assert tool_tip.text_block.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        tool_tip.set_position((150.0, 30.0))

        assert tool_tip.rect.topleft == (150, 30) and tool_tip.text_block.rect.topleft == (150, 30)

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        tool_tip = UITooltip(html_text="A tip about tools.",
                             hover_distance=(0, 10),
                             manager=default_ui_manager)

        tool_tip.set_relative_position((150.0, 30.0))

        assert tool_tip.rect.topleft == (150, 30) and tool_tip.text_block.rect.topleft == (150, 30)
