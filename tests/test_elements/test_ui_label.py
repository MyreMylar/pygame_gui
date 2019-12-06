import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_label import UILabel


class TestUILabel:

    def test_creation(self, _init_pygame, default_ui_manager):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        assert label.image is not None

    def test_set_text(self, _init_pygame, default_ui_manager):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        label.set_text("new text")
        assert label.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        label.rebuild()
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_1(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_label_non_default_1.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_2(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_label_non_default_2.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_3(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_label_non_default_3.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Label Rect is too small for text")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes", "ui_label_bad_values.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 10, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None
