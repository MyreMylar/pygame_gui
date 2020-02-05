import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.core.ui_container import UIContainer


class TestUIDropDownMenu:

    def test_creation(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        assert menu.image is not None

    def test_kill(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.kill()

        assert menu.alive() is False

    def test_update_closed(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.update(0.01)
        assert menu.image is not None

    def test_update_state_transition(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.menu_buttons[0].pressed = True
        menu.update(0.01)
        assert menu.image is not None

    def test_update_closed_state_close_button(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.close_button.pressed = True
        menu.update(0.01)
        assert menu.image is not None

    def test_update_open_state_finish(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.open_button.pressed = True
        menu.update(0.01)
        assert menu.image is not None

    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_drop_down_menu_non_default.json"))

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.should_transition = True
        menu.update(0.01)
        manager.ui_theme.ui_element_misc_data['drop_down_menu']['expand_direction'] = 'down'
        menu.rebuild_from_changed_theme_data()
        assert menu.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_drop_down_menu_bad_values.json"))

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=manager)
        assert menu.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.set_position((200, 200))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (250, 215)}))
        # if we successfully clicked on the moved menu then this button should be True
        assert menu.current_state.selected_option_button.held is True

    def test_set_relative_position(self, _init_pygame, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60), manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              container=test_container,
                              manager=default_ui_manager)

        menu.set_relative_position((150.0, 30.0))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (260, 145)}))

        assert menu.rect.topleft == (250, 130) and menu.current_state.selected_option_button.held is True
