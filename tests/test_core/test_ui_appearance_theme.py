import os
import pytest
import pygame
import warnings

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame_gui.core.ui_appearance_theme import (
    UIAppearanceTheme,
    UIThemeValidator,
    UIThemeValidationError,
)
from pygame_gui.core.resource_loaders import BlockingThreadedResourceLoader
from pygame_gui import PackageResource


class TestUIAppearanceTheme:
    def test_creation(self, _init_pygame, _display_surface_return_none):
        UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

    def test_load_non_default_theme_from_package(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.load_theme(
            PackageResource("tests.data.themes", "ui_text_box_non_default.json")
        )
        colour = theme.get_colour(
            colour_id="dark_bg", combined_element_ids=["text_box"]
        )
        assert colour == pygame.Color("#25f92e")

    def test_load_non_default_theme_from_dictionary(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme_dict = {"text_box": {"colours": {"dark_bg": "#25f92e"}}}
        theme.load_theme(theme_dict)
        colour = theme.get_colour(
            colour_id="dark_bg", combined_element_ids=["text_box"]
        )
        assert colour == pygame.Color("#25f92e")

    def test_load_images_from_package(
        self, _init_pygame, _display_surface_return_none: None
    ):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale="en")
        theme.load_theme(
            PackageResource("tests.data.themes", "appearance_theme_package_test.json")
        )
        loader.start()
        loader.update()
        image = theme.get_image(
            image_id="normal_image", combined_element_ids=["button"]
        )
        assert isinstance(image, pygame.Surface)

    def test_load_fonts_from_package(
        self, _init_pygame, _display_surface_return_none: None
    ):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale="en")
        theme.load_theme(
            PackageResource("tests.data.themes", "appearance_theme_package_test.json")
        )
        loader.start()
        loader.update()
        font = theme.get_font(combined_element_ids=["button"])
        assert isinstance(font, IGUIFontInterface)

    def test_get_colour_from_gradient(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.load_theme(
            os.path.join("tests", "data", "themes", "ui_text_box_non_default.json")
        )
        colour = theme.get_colour(
            colour_id="dark_bg", combined_element_ids=["text_box"]
        )
        assert colour == pygame.Color("#25f92e")

    def test_load_theme_invalid_colour_gradients(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Invalid gradient"):
                theme.load_theme(
                    os.path.join(
                        "tests", "data", "themes", "appearance_theme_test.json"
                    )
                )

    def test_get_colour_from_gradient_objects(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Invalid gradient"):
                theme.load_theme(
                    os.path.join(
                        "tests", "data", "themes", "appearance_theme_test.json"
                    )
                )
        colour = theme.get_colour(
            colour_id="dark_bg", combined_element_ids=["#test_parent"]
        )
        assert colour == pygame.Color("#25f92e")

    def test_load_theme_bad_font_data(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(UserWarning, match="Theme validation found 4 errors"):
            with pytest.warns(UserWarning, match="Font data validation errors"):
                with pytest.warns(UserWarning, match="Image data validation errors"):
                    with pytest.warns(
                        UserWarning, match="Unable to create subsurface rectangle"
                    ):
                        theme.load_theme(
                            os.path.join(
                                "tests",
                                "data",
                                "themes",
                                "appearance_theme_bad_font_data_test.json",
                            )
                        )

    def test_load_theme_twice(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(UserWarning, match="Theme validation found 4 errors"):
            with pytest.warns(UserWarning, match="Font data validation errors"):
                with pytest.warns(UserWarning, match="Image data validation errors"):
                    with pytest.warns(
                        UserWarning, match="Unable to create subsurface rectangle"
                    ):
                        theme.load_theme(
                            os.path.join(
                                "tests",
                                "data",
                                "themes",
                                "appearance_theme_bad_font_data_test.json",
                            )
                        )
                        theme.load_theme(
                            os.path.join(
                                "tests", "data", "themes", "ui_button_non_default.json"
                            )
                        )

    def test_load_theme_with_non_preloaded_font(
        self, _init_pygame, _display_surface_return_none: None
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.load_theme(
            os.path.join("tests", "data", "themes", "ui_button_non_default.json")
        )

    def test_check_need_to_reload_bad_path(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme._theme_file_path = "not_a_theme.json"
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_is_false(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.check_need_to_reload()
        assert theme.check_need_to_reload() is False

    def test_check_need_to_reload_no_theme(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme._theme_file_path = None
        assert theme.check_need_to_reload() is False

    def test_update_shape_cache(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.update_caching(0.1)
        theme.update_caching(10.0)

        theme.st_cache_clear_timer = 15.0
        theme.update_caching(0.1)
        assert theme.st_cache_clear_timer == 0.0

    def test_load_images_bad_path(self, _init_pygame, _display_surface_return_none):
        loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(loader, locale="en")
        theme.ui_element_image_locs["button"] = {
            "regular_path": {"changed": True, "path": "not_an_image.png"}
        }
        with pytest.warns(UserWarning, match="Unable to load resource"):
            theme._load_images()
            loader.start()
            loader.update()

    def test_build_all_combined_ids(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.raises(
            ValueError,
            match="Object & class ID hierarchy is not "
            "equal in length to Element ID hierarchy",
        ):
            theme.build_all_combined_ids(
                element_base_ids=[None],
                element_ids=["button"],
                class_ids=[None],
                object_ids=["whut", "the", "heck"],
            )

    def test_load_theme_bad_path(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(UserWarning, match="Failed to open theme file at path"):
            theme.load_theme("blah.json")

    def test_load_theme_bad_json_syntax(
        self, _init_pygame, _display_surface_return_none
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        with pytest.warns(
            UserWarning, match="Failed to load current theme file, check syntax"
        ):
            theme.load_theme(
                os.path.join("tests", "data", "themes", "bad_syntax_theme.json")
            )

    def test_use_class_id_simple(self, _init_pygame, _display_surface_return_none):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.load_theme(
            PackageResource("tests.data.themes", "appearance_theme_class_id_test.json")
        )
        border_width = theme.get_misc_data(
            misc_data_id="border_width",
            combined_element_ids=["#test_object_2", "@test_class", "button"],
        )
        assert border_width == {"bottom": 3, "left": 3, "right": 3, "top": 3}

    def test_use_class_id_generated(
        self, _init_pygame, _display_surface_return_none: None
    ):
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")
        theme.load_theme(
            PackageResource("tests.data.themes", "appearance_theme_class_id_test.json")
        )

        combined_ids = theme.build_all_combined_ids(
            element_base_ids=[None],
            element_ids=["button"],
            class_ids=["@test_class"],
            object_ids=["#test_object_2"],
        )

        assert combined_ids == ["#test_object_2", "@test_class", "button"]

        border_width = theme.get_misc_data(
            misc_data_id="border_width", combined_element_ids=combined_ids
        )
        shadow_width = theme.get_misc_data(
            misc_data_id="shadow_width", combined_element_ids=combined_ids
        )
        assert shadow_width == "0"
        assert border_width == {"bottom": 3, "left": 3, "right": 3, "top": 3}

        combined_ids = theme.build_all_combined_ids(
            element_base_ids=[None],
            element_ids=["button"],
            class_ids=["@test_class"],
            object_ids=["#test_object_1"],
        )

        assert combined_ids == ["#test_object_1", "@test_class", "button"]

        border_width = theme.get_misc_data(
            misc_data_id="border_width", combined_element_ids=combined_ids
        )

        shadow_width = theme.get_misc_data(
            misc_data_id="shadow_width", combined_element_ids=combined_ids
        )
        assert border_width == {"bottom": 1, "left": 1, "right": 1, "top": 1}
        assert shadow_width == "3"

        combined_ids = theme.build_all_combined_ids(
            element_base_ids=[None],
            element_ids=["button"],
            class_ids=[None],
            object_ids=["#test_object_2"],
        )

        assert combined_ids == ["#test_object_2", "button"]

        border_width = theme.get_misc_data(
            misc_data_id="border_width", combined_element_ids=combined_ids
        )

        shadow_width = theme.get_misc_data(
            misc_data_id="shadow_width", combined_element_ids=combined_ids
        )
        assert border_width == {"bottom": 2, "left": 2, "right": 2, "top": 2}
        assert shadow_width == "0"

    def test_get_font(self, _init_pygame, _display_surface_return_none: None):
        resource_loader = BlockingThreadedResourceLoader()
        theme = UIAppearanceTheme(resource_loader, locale="nonsense_locale")
        theme.load_theme(
            os.path.join("tests", "data", "themes", "ui_button_non_default.json")
        )
        resource_loader.start()
        resource_loader.update()
        assert (
            theme.get_font_info(["button"])
            == theme.ui_element_fonts_info["button"]["en"]
        )
        assert (
            theme.get_font(["button"]) == theme.ele_font_res["button"]["en"].loaded_font
        )

    # Theme Validation Tests
    def test_theme_validator_valid_theme(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that valid theme data passes validation."""
        valid_theme = {
            "button": {
                "colours": {
                    "normal_bg": "#45494e",
                    "hovered_bg": "#35393e",
                    "normal_text": "#c5cbd8",
                },
                "misc": {
                    "border_width": "2",
                    "shadow_width": "1",
                    "shape": "rounded_rectangle",
                },
                "font": {"name": "arial", "size": "14", "bold": "0"},
            }
        }

        errors = UIThemeValidator.validate_theme_file(valid_theme)
        assert len(errors) == 0

    def test_theme_validator_invalid_colors(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test validation of invalid color data."""
        invalid_theme = {
            "button": {
                "colours": {
                    "normal_bg": "not_a_color",  # Invalid color
                    "hovered_bg": [300, 400, 500],  # Invalid RGB values
                    "normal_text": 123,  # Wrong type
                }
            }
        }

        errors = UIThemeValidator.validate_theme_file(invalid_theme)
        assert len(errors) == 3
        assert any("Invalid color string 'not_a_color'" in error for error in errors)
        assert any(
            "Color values must be numbers between 0-255" in error for error in errors
        )
        assert any(
            "Color must be string or tuple, got int" in error for error in errors
        )

    def test_theme_validator_invalid_misc(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test validation of invalid misc data."""
        invalid_theme = {
            "button": {
                "misc": {
                    "border_width": "not_a_number",  # Invalid number
                    "shadow_width": "-5",  # Negative value
                    "shape": "invalid_shape",  # Invalid choice
                    "enable_arrow_buttons": "maybe",  # Invalid boolean
                }
            }
        }

        errors = UIThemeValidator.validate_theme_file(invalid_theme)
        assert len(errors) == 4
        assert any("Must be a number" in error for error in errors)
        assert any("Value -5.0 must be between 0 and 50" in error for error in errors)
        assert any(
            "Must be one of ['rectangle', 'rounded_rectangle', 'ellipse']" in error
            for error in errors
        )
        assert any(
            "Boolean field must be '0', '1', 'true', or 'false'" in error
            for error in errors
        )

    def test_theme_validator_invalid_font(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test validation of invalid font data."""
        invalid_theme = {
            "button": {
                "font": {
                    "name": 123,  # Wrong type
                    "size": "-10",  # Invalid size
                    "bold": "maybe",  # Invalid boolean
                }
            }
        }

        errors = UIThemeValidator.validate_theme_file(invalid_theme)
        assert len(errors) == 3
        assert any("Must be a string, got int" in error for error in errors)
        assert any("Must be positive, got -10" in error for error in errors)
        assert any(
            "Boolean field must be '0', '1', 'true', or 'false'" in error
            for error in errors
        )

    def test_theme_validator_invalid_images(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test validation of invalid image data."""
        invalid_theme = {
            "button": {
                "images": {
                    "background": {
                        # Missing path or package/resource
                        "sub_surface_rect": "1,2,3"  # Wrong number of values
                    }
                }
            }
        }

        errors = UIThemeValidator.validate_theme_file(invalid_theme)
        assert len(errors) == 2
        assert any(
            "Must have either 'path' or both 'package' and 'resource'" in error
            for error in errors
        )
        assert any(
            "Must have 4 comma-separated values, got 3" in error for error in errors
        )

    def test_theme_validator_invalid_element_type(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test validation of invalid element type."""
        invalid_theme = {
            "invalid_element": "not_a_dict"  # Wrong type for element
        }

        errors = UIThemeValidator.validate_theme_file(invalid_theme)
        assert len(errors) == 1
        assert "Element 'invalid_element' must be a dictionary, got str" in errors[0]

    def test_theme_validator_color_validation_methods(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific color validation methods."""
        # Test valid colors
        valid_colors = {
            "hex_color": "#FF0000",
            "tuple_color": [255, 0, 0],
            "named_color": "red",
        }
        errors = UIThemeValidator._validate_colors(valid_colors, "test_element")
        assert len(errors) == 0

        # Test invalid colors
        invalid_colors = {
            "bad_color": "not_a_color",
            "bad_tuple": [300, -50, 500],
            "wrong_type": 123,
        }
        errors = UIThemeValidator._validate_colors(invalid_colors, "test_element")
        assert len(errors) == 3

    def test_theme_validator_misc_validation_methods(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific misc validation methods."""
        # Test valid misc data
        valid_misc = {
            "border_width": "5",
            "shape": "rectangle",
            "enable_arrow_buttons": "1",
        }
        errors = UIThemeValidator._validate_misc(valid_misc, "test_element")
        assert len(errors) == 0

        # Test invalid misc data
        invalid_misc = {
            "border_width": "not_a_number",
            "shape": "triangle",
            "enable_arrow_buttons": "maybe",
        }
        errors = UIThemeValidator._validate_misc(invalid_misc, "test_element")
        assert len(errors) == 3

    def test_theme_validator_font_validation_methods(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific font validation methods."""
        # Test valid font data
        valid_font = {"name": "arial", "size": "14", "bold": "0", "italic": "0"}
        errors = UIThemeValidator._validate_font(valid_font, "test_element")
        assert len(errors) == 0

        # Test invalid font data
        invalid_font = {"name": 123, "size": "-10", "bold": "maybe"}
        errors = UIThemeValidator._validate_font(invalid_font, "test_element")
        assert len(errors) == 3

    def test_theme_validator_image_validation_methods(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific image validation methods."""
        # Test valid image data
        valid_images = {
            "background": {"path": "test.png"},
            "icon": {"package": "test.package", "resource": "test.png"},
        }
        errors = UIThemeValidator._validate_images(valid_images, "test_element")
        assert len(errors) == 0

        # Test invalid image data
        invalid_images = {
            "background": {
                # Missing path or package/resource
                "sub_surface_rect": "1,2,3"  # Wrong number of values
            }
        }
        errors = UIThemeValidator._validate_images(invalid_images, "test_element")
        assert len(errors) == 2

    def test_appearance_theme_validate_theme_data(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test UIAppearanceTheme.validate_theme_data method."""
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

        # Test valid theme
        valid_theme = {
            "button": {
                "colours": {"normal_bg": "#FF0000"},
                "misc": {"border_width": "2"},
            }
        }
        errors = theme.validate_theme_data(valid_theme)
        assert len(errors) == 0

        # Test invalid theme
        invalid_theme = {"button": {"colours": {"normal_bg": "invalid_color"}}}
        errors = theme.validate_theme_data(invalid_theme)
        assert len(errors) == 1

    def test_appearance_theme_validation_integration(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that validation is integrated into theme loading."""
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

        # Test loading invalid theme generates warnings
        invalid_theme = {
            "button": {
                "colours": {"normal_bg": "invalid_color"},
                "misc": {"border_width": "not_a_number"},
            }
        }

        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Invalid Theme Colour"):
                with pytest.warns(UserWarning, match="Misc data validation errors"):
                    with pytest.warns(UserWarning, match="Invalid border_width value"):
                        theme.update_theming(invalid_theme)

    def test_appearance_theme_validation_warnings_for_misc_data(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that misc data validation generates warnings during loading."""
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

        invalid_theme = {
            "button": {
                "misc": {"border_width": "not_a_number", "shape": "invalid_shape"}
            }
        }
        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Misc data validation errors"):
                with pytest.warns(UserWarning, match="Invalid border_width value"):
                    theme.update_theming(invalid_theme)

    def test_appearance_theme_validation_warnings_for_font_data(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that font data validation generates warnings during loading."""
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

        invalid_theme = {"button": {"font": {"name": 123, "size": "-10"}}}
        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Font data validation errors"):
                with pytest.warns(
                    UserWarning, match="Font size less than or equal to 0"
                ):
                    with pytest.warns(
                        UserWarning,
                        match="Trying to pre-load font id:_regular_aa_14 with no paths set & its not a system font",
                    ):
                        theme.update_theming(invalid_theme)

    def test_appearance_theme_validation_warnings_for_image_data(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test that image data validation generates warnings during loading."""
        theme = UIAppearanceTheme(BlockingThreadedResourceLoader(), locale="en")

        invalid_theme = {
            "button": {
                "images": {
                    "background": {
                        "sub_surface_rect": "1,2,3"  # Wrong number of values
                    }
                }
            }
        }
        with pytest.warns(UserWarning, match="Theme validation found 2 errors"):
            with pytest.warns(UserWarning, match="Image data validation errors"):
                with pytest.warns(
                    UserWarning, match="Unable to find image with id: background"
                ):
                    theme.update_theming(invalid_theme)

    def test_theme_validator_text_shadow_offset_validation(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific validation for text_shadow_offset tuple values."""

        # Test valid formats
        valid_themes = [
            {"button": {"misc": {"text_shadow_offset": "2,3"}}},  # String format
            {
                "button": {"misc": {"text_shadow_offset": " -1 , 5 "}}
            },  # String with spaces
            {"button": {"misc": {"text_shadow_offset": (1, 2)}}},  # Tuple format
            {"button": {"misc": {"text_shadow_offset": [0, -10]}}},  # List format
            {"button": {"misc": {"text_shadow_offset": (-50, 50)}}},  # Boundary values
        ]

        for theme_data in valid_themes:
            errors = UIThemeValidator.validate_theme_file(theme_data)
            assert len(errors) == 0, f"Valid theme should have no errors: {theme_data}"

        # Test invalid formats
        invalid_themes = [
            (
                {"button": {"misc": {"text_shadow_offset": "5"}}},
                "Must have 2 comma-separated values",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": "1,2,3"}}},
                "Must have 2 comma-separated values",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": "abc,def"}}},
                "expected 'x,y' with numeric values",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": (1, 2, 3)}}},
                "Must have 2 values",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": ("a", "b")}}},
                "Values must be numeric",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": 5}}},
                "Must be string 'x,y' or tuple/list",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": (100, 0)}}},
                "X value 100.0 must be between -50 and 50",
            ),
            (
                {"button": {"misc": {"text_shadow_offset": (0, -100)}}},
                "Y value -100.0 must be between -50 and 50",
            ),
        ]

        for theme_data, expected_message in invalid_themes:
            errors = UIThemeValidator.validate_theme_file(theme_data)
            assert len(errors) >= 1, f"Invalid theme should have errors: {theme_data}"
            assert expected_message in str(
                errors
            ), f"Expected message '{expected_message}' not found in errors: {errors}"

    def test_theme_validator_shape_corner_radius_validation(
        self, _init_pygame, _display_surface_return_none
    ):
        """Test specific validation for shape_corner_radius single and 4-corner values."""

        # Test valid formats
        valid_themes = [
            {"button": {"misc": {"shape_corner_radius": "5"}}},  # Single value string
            {"button": {"misc": {"shape_corner_radius": 10}}},  # Single value integer
            {"button": {"misc": {"shape_corner_radius": 7.5}}},  # Single value float
            {"button": {"misc": {"shape_corner_radius": "2,4,6,8"}}},  # 4-corner string
            {
                "button": {"misc": {"shape_corner_radius": " 1 , 2 , 3 , 4 "}}
            },  # 4-corner string with spaces
            {
                "button": {"misc": {"shape_corner_radius": (5, 10, 15, 20)}}
            },  # 4-corner tuple
            {
                "button": {"misc": {"shape_corner_radius": [0, 5, 10, 15]}}
            },  # 4-corner list
            {"button": {"misc": {"shape_corner_radius": [25]}}},  # Single value in list
            {
                "button": {"misc": {"shape_corner_radius": (0, 100, 0, 100)}}
            },  # Boundary values
        ]

        for theme_data in valid_themes:
            errors = UIThemeValidator.validate_theme_file(theme_data)
            assert len(errors) == 0, f"Valid theme should have no errors: {theme_data}"

        # Test invalid formats
        invalid_themes = [
            (
                {"button": {"misc": {"shape_corner_radius": "1,2"}}},
                "Must have 1 value (all corners) or 4 comma-separated values",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": "1,2,3"}}},
                "Must have 1 value (all corners) or 4 comma-separated values",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": "abc,def,ghi,jkl"}}},
                "corner value must be numeric",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": (1, 2, 3)}}},
                "Must have 1 value (all corners) or 4 values",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": ("a", "b", "c", "d")}}},
                "corner value must be numeric",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": {"radius": 5}}}},
                "Must be number, string, or list/tuple",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": 150}}},
                "Value 150 must be between 0 and 100",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": -5}}},
                "Value -5 must be between 0 and 100",
            ),
            (
                {"button": {"misc": {"shape_corner_radius": (5, 150, 10, 20)}}},
                "top-right corner value 150.0 must be between 0 and 100",
            ),
        ]

        for theme_data, expected_message in invalid_themes:
            errors = UIThemeValidator.validate_theme_file(theme_data)
            assert len(errors) >= 1, f"Invalid theme should have errors: {theme_data}"
            assert expected_message in str(
                errors
            ), f"Expected message '{expected_message}' not found in errors: {errors}"


if __name__ == "__main__":
    pytest.console_main()
