import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core._string_data import FiraCode_Regular, FiraCode_Bold
from pygame_gui.core._string_data import FiraMono_BoldItalic, FiraMono_RegularItalic

from pygame_gui.core.ui_font_dictionary import UIFontDictionary

pygame_gui.core.ui_font_dictionary.FiraCode_Regular = FiraCode_Regular
pygame_gui.core.ui_font_dictionary.FiraCode_Bold = FiraCode_Bold
pygame_gui.core.ui_font_dictionary.FiraMono_BoldItalic = FiraMono_BoldItalic
pygame_gui.core.ui_font_dictionary.FiraMono_RegularItalic = FiraMono_RegularItalic


class TestUIFontDictionary:
    def test_creation(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        assert font_dictionary.loaded_fonts is not None

    def test_load_default_font_from_strings(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        font_dictionary.load_default_font('fake_font.ttf', 'fake_path')

        assert font_dictionary.loaded_fonts is not None

    def test_find_font_unloaded_size(self, _init_pygame):
        font_dictionary = UIFontDictionary()

        with pytest.warns(UserWarning, match="Finding font with id"):
            font_dictionary.find_font(font_size=20, font_name='fira_code')

    def test_find_font_unloaded_style_bold(self, _init_pygame):
        font_dictionary = UIFontDictionary()

        with pytest.warns(UserWarning, match="Finding font with id"):
            font_dictionary.find_font(font_size=20, font_name='fira_code', bold=True)

    def test_find_font_unloaded_style_italic(self, _init_pygame):
        font_dictionary = UIFontDictionary()

        with pytest.warns(UserWarning, match="Finding font with id"):
            font_dictionary.find_font(font_size=20, font_name='fira_code', italic=True)

    def test_find_font_unloaded_style_bold_italic(self, _init_pygame):
        font_dictionary = UIFontDictionary()

        with pytest.warns(UserWarning, match="Finding font with id"):
            font_dictionary.find_font(font_size=20, font_name='fira_code', bold=True, italic=True)

    def test_find_font_unloaded(self, _init_pygame):
        font_dictionary = UIFontDictionary()

        font_dictionary.find_font(font_size=20, font_name='arial')

    def test_convert_html_size_to_point_size_invalid(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        assert font_dictionary.convert_html_size_to_point_size(9000) == font_dictionary.default_font_size

    def test_preload_already_loaded(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        with pytest.warns(UserWarning, match="Trying to pre-load font id"):
            font_dictionary.preload_font(font_name='fira_code', font_size=14)

    def test_preload_no_paths(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        with pytest.warns(UserWarning, match="Trying to pre-load font id"):
            font_dictionary.preload_font(font_name='arial', font_size=14)

    def test_preload_bad_paths(self, _init_pygame):
        font_dictionary = UIFontDictionary()
        font_dictionary.add_font_path('arial',
                                      font_path='doop/doop/doop.ttf',
                                      bold_path='doop/doop/doop.ttf',
                                      italic_path='doop/doop/doop.ttf',
                                      bold_italic_path='doop/doop/doop.ttf'
                                      )
        with pytest.warns(UserWarning, match="Failed to load font at path"):
            font_dictionary.preload_font(font_name='arial', font_size=14)

        with pytest.warns(UserWarning, match="Failed to load font at path"):
            font_dictionary.preload_font(font_name='arial', font_size=14, bold=True)

        with pytest.warns(UserWarning, match="Failed to load font at path"):
            font_dictionary.preload_font(font_name='arial', font_size=14, italic=True)

        with pytest.warns(UserWarning, match="Failed to load font at path"):
            font_dictionary.preload_font(font_name='arial', font_size=14, bold=True, italic=True)