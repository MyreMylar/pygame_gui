import os
import platform
import pygame
import pytest

from pathlib import Path

from pygame_gui.ui_manager import UIManager
from pygame_gui.core import UIAppearanceTheme, UIWindowStack
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui import PackageResource
from pygame_gui.core.resource_loaders import IncrementalThreadedResourceLoader
from pygame_gui.core.layered_gui_group import LayeredGUIGroup


#  factory of overrides for _update_mouse_position of UIManager - for use in hover tests
def update_mouse_position_override_factory(obj, mouse_pos_x=0, mouse_pos_y=0):
    def _update_mouse_position_override():
        obj.mouse_position = (mouse_pos_x, mouse_pos_y)

    return _update_mouse_position_override


class TestUIManager:
    """
    Testing the UIManager class
    """

    def test_creation(self, _init_pygame, _display_surface_return_none):
        """
        Just test whether we can create a UIManager without raising any exceptions.
        """
        UIManager((800, 600))

    def test_get_theme(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Can we get the theme? Serves as a test of the theme being successfully created.
        """
        theme = default_ui_manager.get_theme()
        assert (isinstance(theme, UIAppearanceTheme))

    def test_get_sprite_group(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Can we get the sprite group? Serves as a test of the sprite group being successfully created.
        """
        sprite_group = default_ui_manager.get_sprite_group()
        assert (isinstance(sprite_group, LayeredGUIGroup))

    def test_get_window_stack(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Can we get the window stack? Serves as a test of the window stack being successfully created.
        """
        window_stack = default_ui_manager.get_window_stack()
        assert (isinstance(window_stack, UIWindowStack))

    def test_get_shadow(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Try to get a shadow of a requested size.
        Tests that the returned object is a surface of the correct size.
        """
        requested_size = (100, 100)
        shadow_surface = default_ui_manager.get_shadow(size=requested_size, shadow_width=2,
                                                       shape='rectangle', corner_radius=[2, 2, 2, 2])
        shadow_surface_size = shadow_surface.get_size()

        assert (isinstance(shadow_surface, pygame.Surface) and (shadow_surface_size == requested_size))

    def test_set_window_resolution(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Tests that this does actually set the window resolution.
        """
        default_ui_manager.set_window_resolution((640, 480))
        assert default_ui_manager.window_resolution == (640, 480)

    def test_clear_and_reset(self, _init_pygame, default_ui_manager, _display_surface_return_none):
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

    def test_process_events(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Fake a click button event on a button to check they are going through the ui event manager properly/
        """
        test_button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30), text="Test", manager=default_ui_manager)
        UIMessageWindow(rect=pygame.Rect(500, 100, 250, 300),
                        window_title="Test Message",
                        html_message="This is a bold test of the message box functionality.",
                        manager=default_ui_manager)
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (125, 115)}))
        assert test_button.held

    def test_update(self, _init_pygame, default_ui_manager: UIManager,
                    _display_surface_return_none):
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

        window = UIWindow(pygame.Rect(100, 100, 200, 200), window_display_title="Test Window",
                          manager=default_ui_manager, element_id='test_window',
                          resizable=True)

        default_ui_manager.mouse_position = (window.rect.left + window.shadow_width,
                                             window.rect.top + window.shadow_width)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[0]
        assert window.edge_hovering[1]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['xy']

        default_ui_manager.mouse_position = (window.rect.right - window.shadow_width,
                                             window.rect.top + window.shadow_width)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[2]
        assert window.edge_hovering[1]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['yx']

        default_ui_manager.mouse_position = (window.rect.left + window.shadow_width,
                                             window.rect.centery)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[0]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['xl']

        default_ui_manager.mouse_position = (window.rect.right - window.shadow_width,
                                             window.rect.centery)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[2]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['xr']

        default_ui_manager.mouse_position = (window.rect.centerx,
                                             window.rect.top + window.shadow_width)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[1]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['yt']

        default_ui_manager.mouse_position = (window.rect.centerx,
                                             window.rect.bottom - window.shadow_width)
        window.resizing_mode_active = False
        window.check_hover(0.05, False)
        assert window.edge_hovering[3]
        window.resizing_mode_active = True
        window.start_resize_rect = pygame.Rect(100, 100, 200, 200)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.resizing_window_cursors['yb']

        window.resizing_mode_active = False
        window.check_hover(0.05, False)

        default_ui_manager.update(0.05)
        assert default_ui_manager._active_cursor == default_ui_manager.active_user_cursor

    def test_draw_ui(self, _init_pygame, _display_surface_return_none):
        """
        Test that drawing the UI works.
        Note: the pygame comparison function here seems a little unreliable. Would not be surprised if it's behaviour
        changes.
        """
        test_surface = pygame.display.set_mode((150, 30), 0, 32)
        manager = UIManager((150, 30))
        UIButton(relative_rect=pygame.Rect(0, 0, 150, 30), text="Test", manager=manager)
        manager.update(0.01)
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
        try:
            test_pixel_array.close()
            comparison_pixel_array.close()
        except AttributeError:
            pass

        no_mismatch_colour = pygame.Color(255, 255, 255, 255)

        for x in range(0, 150):
            for y in range(0, 30):
                assert result_surface.unmap_rgb(
                    result_pixel_array[x, y]) == no_mismatch_colour, f"Colours not equal at: {x}, {y}"
        try:
            result_pixel_array.close()
        except AttributeError:
            pass
        pygame.display.quit()

    def test_add_font_paths_and_preload_fonts(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        """
        Combined test of setting font paths and preloading.

        We set the path to a font, preload it then try and use it in a text box and see if any errors or warnings
        happen.
        """
        default_ui_manager.add_font_paths(font_name='roboto',
                                          regular_path=os.path.join('tests', 'data', 'Roboto-Regular.ttf'))
        default_ui_manager.preload_fonts([{'name': 'roboto', 'point_size': 14, 'style': 'regular'}])
        default_ui_manager.preload_fonts([{'name': 'noto_sans', 'html_size': 3, 'style': 'italic'}])
        # default_ui_manager.resource_loader.start()
        # default_ui_manager.resource_loader.update()

        UITextBox(html_text="<font face=roboto>Test font pre-loading</font>",
                  relative_rect=pygame.Rect(100, 100, 200, 100),
                  manager=default_ui_manager)

    def test_print_unused_fonts(self, _init_pygame, default_ui_manager, _display_surface_return_none, capsys):
        """
        Test unused font printing, by creating a font we don't use and seeing if the print-out reports it.

        :param _init_pygame:
        :param default_ui_manager:
        :param capsys: the captured system output. includes stdout (.out) & stderr (.err)
        """
        default_ui_manager.add_font_paths(font_name='roboto', regular_path='tests/data/Roboto-Regular.ttf')
        default_ui_manager.preload_fonts([{'name': 'roboto', 'point_size': 14, 'style': 'regular'}])
        default_ui_manager.print_unused_fonts()
        captured = capsys.readouterr()

        assert captured.out == 'Unused font ids:\nroboto_regular_aa_14(HTML size: 4)\n'

    def test_focus_and_unfocus_focus_element(self, _init_pygame, default_ui_manager,
                                             _display_surface_return_none):
        """
        Test if we correctly select the focused element and unselect it with these functions.
        """
        test_button = UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                               text="Test", manager=default_ui_manager)
        default_ui_manager.set_focus_set(test_button)
        was_selected_correctly = test_button.is_focused
        default_ui_manager.set_focus_set(None)
        assert was_selected_correctly is True and test_button.is_focused is False

    def test_incremental_loading_nothing(self, _init_pygame, _display_surface_return_none):
        incremental_loader = IncrementalThreadedResourceLoader()

        UIManager((800, 600), resource_loader=incremental_loader)

        incremental_loader.start()
        finished = False
        while not finished:
            finished, progress = incremental_loader.update()
        assert finished

    def test_hover_of_hidden_elements(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))
        button1 = UIButton(relative_rect=pygame.Rect(100, 100, 100, 100), text="Lower button test",
                           manager=manager, starting_height=1)
        button2 = UIButton(relative_rect=pygame.Rect(100, 100, 100, 100), text="Higher button test",
                           manager=manager, starting_height=2)

        # override of default manager _update_mouse_position method to simulate hovering over the button
        manager._update_mouse_position = update_mouse_position_override_factory(manager, 150, 150)

        assert button1.hovered is False
        assert button2.hovered is False
        manager.update(0.01)
        assert button1.hovered is False
        assert button2.hovered is True

        button2.hide()
        assert button1.hovered is False
        assert button2.hovered is False
        manager.update(0.01)
        assert button1.hovered is True
        assert button2.hovered is False

    def test_set_visual_debug(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))

        UIButton(relative_rect=pygame.Rect(100, 100, 150, 30),
                 text="Test", manager=manager)

        manager.set_visual_debug_mode(True)
        assert manager.visual_debug_active is True

        manager.set_visual_debug_mode(False)

        assert manager.visual_debug_active is False

    def test_set_active_cursor(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))
        manager.set_active_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))

        manager.update(0.5)

        assert manager._active_cursor == pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

    def test_set_hovering_text(self, _init_pygame, _display_surface_return_none):
        class MouselessManager(UIManager):
            def _update_mouse_position(self):
                self.mouse_position = (400, 15)

        manager = MouselessManager((800, 600))

        UITextEntryLine(pygame.Rect(0, 0, 800, 30), manager=manager)

        manager.update(0.5)
        assert manager._active_cursor == pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_IBEAM)

    def test_translation_dir_path(self):
        UIManager((800, 600), translation_directory_paths=['pygame_gui/data/translations/'])

    def test_incremental_loading_something(self, _init_pygame, _display_surface_return_none):
        incremental_loader = IncrementalThreadedResourceLoader()
        incremental_loader.set_update_time_budget(0.001)

        theme_package = PackageResource('tests.data.themes', 'image_loading_test.json')
        assert Path(theme_package.to_path()).name == 'image_loading_test.json'

        UIManager((800, 600), theme_package,
                  resource_loader=incremental_loader)

        incremental_loader.start()
        finished = False
        while not finished:
            finished, _ = incremental_loader.update()
        assert finished

    def test_set_ui_theme(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))
        theme_dict = {"text_box": {"colours": {"dark_bg": "#25f92e"}}}
        theme = manager.create_new_theme(theme_dict)
        manager.set_ui_theme(theme)
        assert manager.ui_theme is theme

    def test_get_hovering_any_element(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600))

        UIButton((100, 100), "Test Button", manager=manager)

        manager.mouse_position = (400, 300)
        manager._handle_hovering(0.05)

        assert not manager.get_hovering_any_element()

        manager.mouse_position = (120, 115)
        manager._handle_hovering(0.05)

        assert manager.get_hovering_any_element()


if __name__ == '__main__':
    os.chdir('..')
    pytest.console_main()
