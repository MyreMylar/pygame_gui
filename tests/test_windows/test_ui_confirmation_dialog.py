import os
import pygame
import pytest
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows import UIConfirmationDialog


class TestUIConfirmationDialog:

    def test_creation(self, _init_pygame, default_ui_manager):
        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                             manager=default_ui_manager,
                             confirming_action_long_desc="Confirm a <b>bold</b> test of the confirmation dialog.",
                             window_title="Confirm",
                             confirming_action_short_name="Confirm")

    def test_press_close_window_button(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        is_alive_pre_process_event = confirm_dialog.alive()

        close_button_x = confirm_dialog.close_window_button.rect.centerx
        close_button_y = confirm_dialog.close_window_button.rect.centery

        # initiate a button press by clicking the left mouse down and up on the close button
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': pygame.BUTTON_LEFT,
                                                                                      'pos': (close_button_x,
                                                                                              close_button_y)}))

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': pygame.BUTTON_LEFT,
                                                                                    'pos': (close_button_x,
                                                                                            close_button_y)}))
        # let the window process the 'close window' event
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        is_dead_post_process_event = not confirm_dialog.alive()

        assert is_alive_pre_process_event is True and is_dead_post_process_event is True

    def test_press_cancel_button(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

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

    def test_press_confirm_button(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

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

    def test_update_menu_bar_grab(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': confirm_dialog.title_bar.rect.center}))
        confirm_dialog.update(0.01)

        assert confirm_dialog.grabbed_window is True

    def test_rebuild(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        confirm_dialog.rebuild()

        assert confirm_dialog.image is not None

    def test_rebuild_rounded_rectangle(self, _init_pygame, default_ui_manager):
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=default_ui_manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        confirm_dialog.shape_corner_radius = 15
        confirm_dialog.shape_type = 'rounded_rectangle'
        confirm_dialog.rebuild()

        assert confirm_dialog.image is not None

    def test_non_default_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_confirmation_dialog_non_default.json"))
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        assert confirm_dialog.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    def test_bad_values_theme_build(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_confirmation_dialog_bad_values.json"))
        confirm_dialog = UIConfirmationDialog(rect=pygame.Rect(100, 100, 400, 300),
                                              manager=manager,
                                              confirming_action_long_desc="Confirm a "
                                                                          "test of the confirmation dialog.",
                                              window_title="Confirm",
                                              confirming_action_short_name="Confirm")

        assert confirm_dialog.image is not None
