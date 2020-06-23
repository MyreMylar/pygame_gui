import os
import pygame
import pytest
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, _display_surface_return_none
from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows import UIConfirmationDialog

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIConfirmationDialog:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                             manager=default_ui_manager,
                             action_long_desc="Confirm a <b>bold</b> test of the confirmation "
                                              "dialog.",
                             window_title="Confirm",
                             action_short_name="Confirm")

    def test_create_too_small(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])

        with pytest.warns(UserWarning, match="Initial size"):
            UIConfirmationDialog(rect=pygame.Rect(100, 100, 50, 50),
                                 manager=default_ui_manager,
                                 action_long_desc="Confirm a <b>bold</b> test of the confirmation "
                                                  "dialog.",
                                 window_title="Confirm",
                                 action_short_name="Confirm")

    def test_press_close_window_button(self, _init_pygame, default_ui_manager,
                                       _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the confirmation "
                                                               "dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        is_alive_pre_process_event = confirm_dialog.alive()

        close_button_x = confirm_dialog.close_window_button.rect.centerx
        close_button_y = confirm_dialog.close_window_button.rect.centery

        # initiate a button press by clicking the left mouse down and up on the close button
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (close_button_x,
                                                                      close_button_y)}))

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (close_button_x,
                                                                      close_button_y)}))
        # let the window process the 'close window' event
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        is_dead_post_process_event = not confirm_dialog.alive()

        assert is_alive_pre_process_event is True and is_dead_post_process_event is True

    def test_press_cancel_button(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the confirmation "
                                                               "dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        is_alive_pre_events = confirm_dialog.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.cancel_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.cancel_button.rect.center}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)
        is_dead_post_events = not confirm_dialog.alive()

        assert is_alive_pre_events is True and is_dead_post_events is True

    def test_press_confirm_button(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        is_alive_pre_events = confirm_dialog.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.confirm_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.confirm_button.rect.center}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        confirm_event_fired = False
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

            if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED and
                    event.ui_element == confirm_dialog):
                confirm_event_fired = True
        is_dead_post_events = not confirm_dialog.alive()

        assert is_alive_pre_events
        assert is_dead_post_events
        assert confirm_event_fired

    def test_update_menu_bar_grab(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a "
                                                               "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.title_bar.rect.center}))
        confirm_dialog.update(0.01)

        assert confirm_dialog.grabbed_window is True

    def test_rebuild(self, _init_pygame, default_ui_manager,
                     _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        confirm_dialog.rebuild()

        assert confirm_dialog.image is not None

    def test_rebuild_rounded_rectangle(self, _init_pygame, default_ui_manager,
                                       _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the confirmation "
                                                               "dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        confirm_dialog.shape_corner_radius = 15
        confirm_dialog.shape = 'rounded_rectangle'
        confirm_dialog.rebuild()

        assert confirm_dialog.image is not None

    def test_non_default_theme_build(self, _init_pygame,
                                     _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_confirmation_dialog_non_default.json"))
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        assert confirm_dialog.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    def test_bad_values_theme_build(self, _init_pygame,
                                    _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_confirmation_dialog_bad_values.json"))
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm")

        assert confirm_dialog.image is not None

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm",
                                              visible=0)

        assert confirm_dialog.visible == 0

        assert confirm_dialog.confirm_button.visible == 0
        assert confirm_dialog.cancel_button.visible == 0

        confirm_dialog.show()

        assert confirm_dialog.visible == 1

        assert confirm_dialog.confirm_button.visible == 1
        assert confirm_dialog.cancel_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm",
                                              visible=1)

        assert confirm_dialog.visible == 1

        assert confirm_dialog.confirm_button.visible == 1
        assert confirm_dialog.cancel_button.visible == 1

        confirm_dialog.hide()

        assert confirm_dialog.visible == 0

        assert confirm_dialog.confirm_button.visible == 0
        assert confirm_dialog.cancel_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, _display_surface_return_none):
        resolution = (500, 500)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=manager,
                                              action_long_desc="Confirm a test of the "
                                                               "confirmation dialog.",
                                              window_title="Confirm",
                                              action_short_name="Confirm",
                                              visible=0)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        confirm_dialog.show()
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        confirm_dialog.hide()
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)
