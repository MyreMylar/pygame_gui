import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_horizontal_slider import UIHorizontalSlider


class TestUIVerticalScrollBar:

    def test_creation(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)
        assert scroll_bar.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)
        scroll_bar.rebuild()
        assert scroll_bar.image is not None

    def test_check_has_moved_recently(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # move the scroll bar a bit
        scroll_bar.left_button.held = True
        scroll_bar.update(0.2)
        assert scroll_bar.has_moved_recently is True

    def test_check_update_buttons(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        scroll_bar.get_current_value() # Clear has moved this turn
        scroll_bar.left_button.held = True
        scroll_bar.update(0.3)
        scroll_bar.left_button.held = False
        scroll_bar.right_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.has_moved_recently is True

    def test_check_update_sliding_bar(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        pygame.mouse.set_pos((100, 15))
        scroll_bar.sliding_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is True

        scroll_bar.sliding_button.held = False
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is False

    def test_kill(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # should kill everything
        scroll_bar.kill()

        assert scroll_bar.alive() is False and scroll_bar.sliding_button.alive() is False

    def test_get_current_value(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        assert scroll_bar.get_current_value() == 50

    def test_set_current_value_in_range(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        scroll_bar.set_current_value(75)
        assert scroll_bar.get_current_value() == 75

    def test_set_current_value_out_of_range(self, _init_pygame, default_ui_manager):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        with pytest.warns(UserWarning, match='value not in range'):
            scroll_bar.set_current_value(200)

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_horizontal_slider_non_default.json"))

        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=manager)
        assert scroll_bar.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_horizontal_slider_bad_values.json"))

        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=51,
                                        value_range=(0, 100),
                                        manager=manager)
        assert scroll_bar.image is not None
