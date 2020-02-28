import os
import platform
import pygame
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core import UIAppearanceTheme, UIWindowStack
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar
from pygame_gui.windows.ui_message_window import UIMessageWindow

from tests.shared_fixtures import _init_pygame, default_ui_manager


class TestUIManager:
    """
    Testing the UIManager class
    """
    def test_creation(self, _init_pygame):
        """
        Just test whether we can create a UIManager without raising any exceptions.
        """
        UIManager((800, 600))

    def test_get_theme(self, _init_pygame, default_ui_manager):
        """
        Can we get the theme? Serves as a test of the theme being successfully created.
        """
        theme = default_ui_manager.get_theme()
        assert(type(theme) == UIAppearanceTheme)

    def test_get_sprite_group(self, _init_pygame, default_ui_manager):
        """
        Can we get the sprite group? Serves as a test of the sprite group being successfully created.
        """
        sprite_group = default_ui_manager.get_sprite_group()
        assert(type(sprite_group) == pygame.sprite.LayeredUpdates)

    def test_get_window_stack(self, _init_pygame, default_ui_manager):
        """
        Can we get the window stack? Serves as a test of the window stack being successfully created.
        """
        window_stack = default_ui_manager.get_window_stack()
        assert(type(window_stack) == UIWindowStack)

    def test_get_shadow(self, _init_pygame, default_ui_manager):
        """
        Try to get a shadow of a requested size.
        Tests that the returned object is a surface of the correct size.
        """
        requested_size = (100, 100)
        shadow_surface = default_ui_manager.get_shadow(size=requested_size, shadow_width=2,
                                                       shape='rectangle', corner_radius=2)
        shadow_surface_size = shadow_surface.get_size()

        assert ((type(shadow_surface) == pygame.Surface) and (shadow_surface_size == requested_size))

    def test_set_window_resolution(self, _init_pygame, default_ui_manager):
        """
        Tests that this does actually set the window resolution.
        """
        default_ui_manager.set_window_resolution((640, 480))
        assert default_ui_manager.window_resolution == (640, 480)

    def test_clear_and_reset(self, _init_pygame, default_ui_manager):
        """
        Check clear and reset is restoring manager to initial state with no extra, lingering, elements.
        """
        # start with just the root window container
        should_be_one_sprite = len(default_ui_manager.get_sprite_group().sprites())

        UIButton(relative_rect=pygame.Rect(100, 100, 150, 30), text="Test", manager=default_ui_manager)
        should_be_two_sprites = len(default_ui_manager.get_sprite_group().sprites())

        default_ui_manager.clear_and_reset()
        should_be_one_sprite_again = len(default_ui_manager.get_sprite_group().sprites())

        assert should_be_one_sprite == 1 and should_be_two_sprites == 2 and should_be_one_sprite_again == 1

    def test_process_events(self, _init_pygame, default_ui_manager):
        """
        Fake a click button event on a button to check they are going through the ui event manager properly/
        """
        test_button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30), text="Test", manager=default_ui_manager)
        UIMessageWindow(message_window_rect=pygame.Rect(500, 400, 200, 300),
                        message_title="Test Message",
                        html_message="This is a bold test of the message box functionality.",
                        manager=default_ui_manager)
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (125, 115)}))
        assert test_button.held

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        """
        Test update does store button shapes in the long term cache
        """
        button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30), text="Test", manager=default_ui_manager)
        default_ui_manager.theme_update_acc = 5.0
        default_ui_manager.get_theme()._theme_file_last_modified = None
        starting_long_term_cache_size = len(default_ui_manager.ui_theme.shape_cache.cache_long_term_lookup)
        default_ui_manager.update(0.01)
        long_term_cache_size_after_update = len(default_ui_manager.ui_theme.shape_cache.cache_long_term_lookup)

        button.hovered = True
        button.select()
        default_ui_manager.update(0.01)

        assert long_term_cache_size_after_update > starting_long_term_cache_size

    def test_draw_ui(self, _init_pygame):
        """
        Test that drawing the UI works.
        Note: the pygame comparison function here seems a little unreliable. Would not be surprised if it's behaviour
        changes.
        """
        test_surface = pygame.display.set_mode((150, 30), depth=32)
        manager = UIManager((150, 30))
        UIButton(relative_rect=pygame.Rect(0, 0, 150, 30), text="Test", manager=manager)
        # manager.update(0.01)
        manager.draw_ui(test_surface)
        plat = platform.system().upper()
        if plat == 'WINDOWS':
            comparison_surface = pygame.image.load(
                os.path.join('tests', 'comparison_images', 'test_ui_manager_draw_ui.png')).convert_alpha()
        else:
            comparison_surface = pygame.image.load(
                os.path.join('tests', 'comparison_images', 'test_ui_manager_draw_ui_linux.png')).convert_alpha()
        test_pixel_array = pygame.PixelArray(test_surface)
        comparison_pixel_array = pygame.PixelArray(comparison_surface)

        # just add a distance value to disable this test for now.
        result_pixel_array = test_pixel_array.compare(comparison_pixel_array, distance=0.05)
        result_surface = result_pixel_array.make_surface()
        test_pixel_array.close()
        comparison_pixel_array.close()

        no_mismatch_colour = pygame.Color(255, 255, 255, 255)

        for x in range(0, 150):
            for y in range(0, 30):
                assert result_surface.unmap_rgb(result_pixel_array[x, y]) == no_mismatch_colour

        result_pixel_array.close()
        pygame.display.quit()

    def test_add_font_paths_and_preload_fonts(self, _init_pygame, default_ui_manager):
        """
        Combined test of setting font paths and pre-loading.

        We sets the path to a font, preload it then try and use it in a text box and see if any errors or warnings
        happen.
        """
        default_ui_manager.add_font_paths(font_name='roboto', regular_path='tests/data/Roboto-Regular.ttf')
        default_ui_manager.preload_fonts([{'name': 'roboto', 'point_size': 14, 'style': 'regular'}])
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'html_size': 3, 'style': 'italic'}])

        UITextBox(html_text="<font face=roboto>Test font pre-loading</font>",
                  relative_rect=pygame.Rect(100, 100, 200, 100),
                  manager=default_ui_manager)

    def test_print_unused_fonts(self, _init_pygame, default_ui_manager, capsys):
        """
        Test unused font printing, by creating a font we don't use and seeing if the print out reports it.

        :param _init_pygame:
        :param default_ui_manager:
        :param capsys: the captured system output. includes stdout (.out) & stderr (.err)
        """
        default_ui_manager.add_font_paths(font_name='roboto', regular_path='tests/data/Roboto-Regular.ttf')
        default_ui_manager.preload_fonts([{'name': 'roboto', 'point_size': 14, 'style': 'regular'}])
        default_ui_manager.print_unused_fonts()
        captured = capsys.readouterr()

        assert captured.out == 'Unused font ids:\nroboto_regular_14(HTML size: 4)\n'

    def test_focus_and_unfocus_focus_element(self, _init_pygame, default_ui_manager):
        """
        Test if we correctly select the focused element and unselect it with these functions.
        """
        test_button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30), text="Test", manager=default_ui_manager)
        default_ui_manager.set_focus_element(test_button)
        was_selected_correctly = test_button.is_focused
        default_ui_manager.unset_focus_element()
        assert was_selected_correctly is True and test_button.is_selected is False

    def test_last_focus_vert_scrollbar(self, _init_pygame, default_ui_manager):
        test_scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                              visible_percentage=0.5,
                                              manager=default_ui_manager)

        default_ui_manager.set_focus_element(test_scroll_bar)
        found_bar = test_scroll_bar is default_ui_manager.get_last_focused_vert_scrollbar()
        default_ui_manager.clear_last_focused_from_vert_scrollbar(test_scroll_bar)
        no_last_focused_scroll_bar = default_ui_manager.get_last_focused_vert_scrollbar() is None

        assert found_bar is True and no_last_focused_scroll_bar is True
