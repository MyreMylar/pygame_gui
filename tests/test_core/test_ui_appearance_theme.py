import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core._string_data import default_theme
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme

pygame_gui.core.ui_appearance_theme.default_theme = default_theme


class TestUIAppearanceTheme:
    def test_creation(self, _init_pygame):
        UIAppearanceTheme()

    def test_load_default_theme_from_strings(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme._load_default_theme_file("load_from_file_instead")

    def test_get_colour_from_gradient(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_text_box_non_default.json"))
        colour = theme.get_colour(object_ids=[''], element_ids=['text_box'], colour_id='dark_bg')
        assert colour == pygame.Color('#25f92e')

    def test_load_theme_invalid_colour_gradients(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match="Invalid gradient"):
            theme.load_theme(os.path.join("tests", "data", "themes", "appearance_theme_test.json"))

    def test_get_colour_from_gradient_objects(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match="Invalid gradient"):
            theme.load_theme(os.path.join("tests", "data", "themes", "appearance_theme_test.json"))
        colour = theme.get_colour(object_ids=['#test_parent', '#test_child'], element_ids=['good_window','text_box'],
                                  colour_id='dark_bg')
        assert colour == pygame.Color('#25f92e')

    def test_load_theme_bad_font_data(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match="Unable to create subsurface rectangle from string"):
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "appearance_theme_bad_font_data_test.json"))

    def test_load_theme_twice(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match="Unable to create subsurface rectangle from string"):
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "appearance_theme_bad_font_data_test.json"))
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "ui_button_non_default.json"))

    def test_load_theme_with_non_preloaded_font(self, _init_pygame,
                                                _display_surface_return_none: None):
        theme = UIAppearanceTheme()
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_button_non_default.json"))

    def test_check_need_to_reload_bad_path(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme._theme_file_path = "not_a_theme.json"
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_is_false(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.check_need_to_reload()
        assert theme.check_need_to_reload() is False

    def test_update_shape_cache(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.update_shape_cache()

    def test_load_images_bad_path(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.ui_element_image_paths['button'] = {'regular_path': {'changed': True, 'path': 'not_an_image.png'}}
        with pytest.warns(UserWarning, match="Unable to load image at path"):
            theme._load_images()

    def test_build_all_combined_ids(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.raises(ValueError, match="Object ID hierarchy is not equal in length to Element ID hierarchy"):
            theme.build_all_combined_ids(object_ids=['whut', 'the', 'heck'], element_ids=['button'])

    def test_load_theme_bad_path(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match='Failed to open theme file at path'):
            theme.load_theme("blah.json")

    def test_load_theme_bad_json_syntax(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.warns(UserWarning, match='Failed to load current theme file, check syntax'):
            theme.load_theme(os.path.join("tests", "data", "themes", "bad_syntax_theme.json"))
