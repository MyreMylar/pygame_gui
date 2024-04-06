import os
import pytest
import pygame

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme
from pygame_gui.core.resource_loaders import BlockingThreadedResourceLoader
from pygame_gui import PackageResource


class TestUIAppearanceTheme:
    def test_creation(self, _init_pygame, _display_surface_return_none):
        UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')

    def test_load_non_default_theme_from_package(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.load_theme(PackageResource('tests.data.themes', 'ui_text_box_non_default.json'))
        colour = theme.get_colour(colour_id='dark_bg', combined_element_ids=['text_box'])
        assert colour == pygame.Color('#25f92e')

    def test_load_non_default_theme_from_dictionary(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme_dict = {"text_box": {"colours": {"dark_bg": "#25f92e"}}}
        theme.load_theme(theme_dict)
        colour = theme.get_colour(colour_id='dark_bg', combined_element_ids=['text_box'])
        assert colour == pygame.Color('#25f92e')

    def test_load_images_from_package(self, _init_pygame, _display_surface_return_none: None):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale='en')
        theme.load_theme(PackageResource('tests.data.themes', 'appearance_theme_package_test.json'))
        loader.start()
        loader.update()
        image = theme.get_image(image_id='normal_image', combined_element_ids=['button'])
        assert isinstance(image, pygame.Surface)

    def test_load_fonts_from_package(self, _init_pygame, _display_surface_return_none: None):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale='en')
        theme.load_theme(PackageResource('tests.data.themes', 'appearance_theme_package_test.json'))
        loader.start()
        loader.update()
        font = theme.get_font(combined_element_ids=['button'])
        assert isinstance(font, IGUIFontInterface)

    def test_get_colour_from_gradient(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_text_box_non_default.json"))
        colour = theme.get_colour(colour_id='dark_bg', combined_element_ids=['text_box'])
        assert colour == pygame.Color('#25f92e')

    def test_load_theme_invalid_colour_gradients(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match="Invalid gradient"):
            theme.load_theme(os.path.join("tests", "data", "themes", "appearance_theme_test.json"))

    def test_get_colour_from_gradient_objects(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match="Invalid gradient"):
            theme.load_theme(os.path.join("tests", "data", "themes", "appearance_theme_test.json"))
        colour = theme.get_colour(colour_id='dark_bg', combined_element_ids=['#test_parent'])
        assert colour == pygame.Color('#25f92e')

    def test_load_theme_bad_font_data(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match="Unable to create subsurface rectangle from string"):
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "appearance_theme_bad_font_data_test.json"))

    def test_load_theme_twice(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match="Unable to create subsurface rectangle from string"):
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "appearance_theme_bad_font_data_test.json"))
            theme.load_theme(os.path.join("tests", "data", "themes",
                                          "ui_button_non_default.json"))

    def test_load_theme_with_non_preloaded_font(self, _init_pygame,
                                                _display_surface_return_none: None):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_button_non_default.json"))

    def test_check_need_to_reload_bad_path(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme._theme_file_path = "not_a_theme.json"
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_is_false(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.check_need_to_reload()
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_no_theme(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme._theme_file_path = None
        assert theme.check_need_to_reload() is False

    def test_update_shape_cache(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.update_caching(0.1)
        theme.update_caching(10.0)

        theme.st_cache_clear_timer = 15.0
        theme.update_caching(0.1)
        assert theme.st_cache_clear_timer == 0.0

    def test_load_images_bad_path(self, _init_pygame, _display_surface_return_none):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale='en')
        theme.ui_element_image_locs['button'] = {'regular_path': {'changed': True,
                                                                  'path': 'not_an_image.png'}}
        with pytest.warns(UserWarning, match="Unable to load resource"):
            theme._load_images()
            loader.start()
            loader.update()

    def test_build_all_combined_ids(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.raises(ValueError, match="Object & class ID hierarchy is not "
                                             "equal in length to Element ID hierarchy"):
            theme.build_all_combined_ids(element_base_ids=[None],
                                         element_ids=['button'],
                                         class_ids=[None],
                                         object_ids=['whut', 'the', 'heck'])

    def test_load_theme_bad_path(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match='Failed to open theme file at path'):
            theme.load_theme("blah.json")

    def test_load_theme_bad_json_syntax(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        with pytest.warns(UserWarning, match='Failed to load current theme file, check syntax'):
            theme.load_theme(os.path.join("tests", "data", "themes", "bad_syntax_theme.json"))

    def test_use_class_id_simple(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.load_theme(PackageResource('tests.data.themes',
                                         'appearance_theme_class_id_test.json'))
        border_width = theme.get_misc_data(misc_data_id='border_width',
                                           combined_element_ids=['#test_object_2',
                                                                 '@test_class',
                                                                 'button'])
        assert border_width == '3'

    def test_use_class_id_generated(self, _init_pygame, _display_surface_return_none: None):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='en')
        theme.load_theme(PackageResource('tests.data.themes',
                                         'appearance_theme_class_id_test.json'))

        combined_ids = theme.build_all_combined_ids(element_base_ids=[None],
                                                    element_ids=['button'],
                                                    class_ids=['@test_class'],
                                                    object_ids=['#test_object_2'])

        assert combined_ids == ['#test_object_2', '@test_class', 'button']

        border_width = theme.get_misc_data(misc_data_id='border_width',
                                           combined_element_ids=combined_ids)
        shadow_width = theme.get_misc_data(misc_data_id='shadow_width',
                                           combined_element_ids=combined_ids)
        assert shadow_width == '0'
        assert border_width == '3'

        combined_ids = theme.build_all_combined_ids(element_base_ids=[None],
                                                    element_ids=['button'],
                                                    class_ids=['@test_class'],
                                                    object_ids=['#test_object_1'])

        assert combined_ids == ['#test_object_1', '@test_class', 'button']

        border_width = theme.get_misc_data(misc_data_id='border_width',
                                           combined_element_ids=combined_ids)

        shadow_width = theme.get_misc_data(misc_data_id='shadow_width',
                                           combined_element_ids=combined_ids)
        assert border_width == '1'
        assert shadow_width == '3'

        combined_ids = theme.build_all_combined_ids(element_base_ids=[None],
                                                    element_ids=['button'], class_ids=[None],
                                                    object_ids=['#test_object_2'])

        assert combined_ids == ['#test_object_2', 'button']

        border_width = theme.get_misc_data(misc_data_id='border_width',
                                           combined_element_ids=combined_ids)

        shadow_width = theme.get_misc_data(misc_data_id='shadow_width',
                                           combined_element_ids=combined_ids)
        assert border_width == '2'
        assert shadow_width == '0'

    def test_get_font(self, _init_pygame, _display_surface_return_none: None):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale='nonsense_locale')
        theme.load_theme(os.path.join("tests", "data", "themes", "ui_button_non_default.json"))
        assert theme.get_font_info(['button']) == theme.ui_element_fonts_info['button']['en']
        assert theme.get_font(['button']) == theme.ele_font_res['button']['en'].loaded_font


if __name__ == '__main__':
    pytest.console_main()

