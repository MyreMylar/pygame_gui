import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.core.ui_container import UIContainer


class TestUILabel:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        assert label.image is not None

    def test_set_text(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        label.set_text("new text")
        assert label.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager,
                     _display_surface_return_none):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)
        label.rebuild()
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_1(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_label_non_default_1.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_2(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_label_non_default_2.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    def test_rebuild_from_theme_data_non_default_3(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_label_non_default_3.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Label Rect is too small for text")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_label_bad_values.json"))
        label = UILabel(relative_rect=pygame.Rect(100, 100, 10, 30),
                        text="Test Label",
                        manager=manager)
        assert label.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        container=test_container,
                        manager=default_ui_manager)

        label.set_position(pygame.math.Vector2(150.0, 30.0))

        assert label.relative_rect.topleft == (50, -70)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        container=test_container,
                        manager=default_ui_manager)

        label.set_relative_position((50, 50))

        assert label.rect.topleft == (150, 150)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        container=test_container,
                        manager=default_ui_manager)

        label.set_dimensions((200, 50))

        assert label.rect.size == (200, 50)

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)

        label.disable()

        assert label.is_enabled is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        label = UILabel(relative_rect=pygame.Rect(100, 100, 150, 30),
                        text="Test Label",
                        manager=default_ui_manager)

        label.disable()
        label.enable()

        assert label.is_enabled is True
