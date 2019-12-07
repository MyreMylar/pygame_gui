import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme


class TestUIAppearanceTheme:
    def test_creation(self, _init_pygame):
        UIAppearanceTheme()

    def test_get_colour_from_gradient(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_text_box_non_default.json"))
        colour = theme.get_colour(object_ids=[''], element_ids=['text_box'], colour_id='dark_bg')
        assert colour == pygame.Color('#25f92e')

    def test_check_need_to_reload_bad_path(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.__theme_file_path = "not_a_theme.json"
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_is_false(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.check_need_to_reload()
        assert theme.check_need_to_reload() is False

    def test_load_images_bad_path(self, _init_pygame):
        theme = UIAppearanceTheme()
        theme.ui_element_image_paths['button'] = {'regular_path': {'changed': True, 'path': 'not_an_image.png'}}
        with pytest.warns(UserWarning, match="Unable to load image at path"):
            theme.load_images()

    def test_build_all_combined_ids(self, _init_pygame):
        theme = UIAppearanceTheme()
        with pytest.raises(ValueError, match="Object ID hierarchy is not equal in length to Element ID hierarchy"):
            theme.build_all_combined_ids(object_ids=['whut', 'the', 'heck'], element_ids=['button'])
