import os
import pytest
import pygame
import pygame_gui

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.core.ui_container import UIContainer
from pygame_gui import PackageResource


class TestUIDropDownMenu:

    def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        assert menu.image is not None

    def test_addition(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        menu.add_options(['spam', 'bad spam'])

        assert menu.options_list[-1] == 'bad spam'

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state == menu.menu_states['expanded']

        menu.add_options(['steak'])

        assert menu.options_list[-1] == 'steak'
        assert menu.current_state == menu.menu_states['closed']

    def test_kill(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.kill()

        assert menu.alive() is False

    def test_update_closed(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.update(0.01)
        assert menu.image is not None

    def test_update_state_transition(self, _init_pygame, default_ui_manager,
                                     _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.options_selection_list.item_list[0]['button_element'].pressed = True
        default_ui_manager.update(0.01)
        assert menu.image is not None

    def test_update_closed_state_close_button(self, _init_pygame, default_ui_manager,
                                              _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.current_state.close_button.pressed = True
        menu.update(0.01)
        assert menu.image is not None

    def test_update_open_state_finish(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
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

    def test_process_event(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        # process a mouse button down event
        menu.process_event(pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, {'ui_element': menu.menu_states['closed'].open_button}))

        assert menu.current_state.should_transition

        menu.update(0.01)

        assert not menu.current_state.should_transition

        menu.process_event(pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {'ui_element': menu.menu_states['expanded'].close_button}))

        assert menu.current_state.should_transition

        menu.update(0.01)

        assert not menu.current_state.should_transition

        menu.process_event(pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {'ui_element': menu.menu_states['closed'].selected_option_button}))

        assert menu.current_state.should_transition

        menu.update(0.01)

        assert not menu.current_state.should_transition

        menu.process_event(pygame.event.Event(
            pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
            {'ui_element': menu.menu_states['expanded'].options_selection_list}))

        confirm_drop_down_changed_event_fired = False
        for event in pygame.event.get():
            if (event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and
                    event.ui_element == menu):
                confirm_drop_down_changed_event_fired = True

        assert confirm_drop_down_changed_event_fired

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
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

        border_and_shadow_width = 3
        item_list_height = 15
        assert menu.menu_states['expanded'].options_list_height == (3 * item_list_height +
                                                                    2 * border_and_shadow_width)
        assert menu.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_drop_down_menu_bad_values.json"))

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=manager)
        assert menu.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        menu.set_position((0, 0))
        menu.current_state.should_transition = True
        menu.update(0.01)
        menu.set_position((200, 200))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (250, 215)}))
        # if we successfully clicked on the moved menu then this button should be True
        assert menu.current_state.selected_option_button.held is True

        drop_down_anchor_bottom_right = UIDropDownMenu(relative_rect=pygame.Rect(0, 0, 50, 50),
                                                       options_list=['eggs', 'flour', 'sugar'],
                                                       starting_option='eggs',
                                                       manager=default_ui_manager,
                                                       container=test_container,
                                                       anchors={'left': 'right',
                                                                'right': 'right',
                                                                'top': 'bottom',
                                                                'bottom': 'bottom'})

        drop_down_anchor_bottom_right.current_state.should_transition = True
        drop_down_anchor_bottom_right.update(0.01)

        drop_down_anchor_bottom_right.set_position((230, 230))
        assert drop_down_anchor_bottom_right.relative_rect.topleft == (-80, -80)
        assert drop_down_anchor_bottom_right.relative_rect.size == (50, 50)
        assert drop_down_anchor_bottom_right.relative_rect.bottomright == (-30, -30)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              container=test_container,
                              manager=default_ui_manager)

        menu.set_relative_position((150.0, 30.0))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (260, 145)}))

        assert menu.rect.topleft == (250, 130) and menu.current_state.selected_option_button.held is True

        menu.current_state.should_transition = True
        menu.update(0.01)

        menu.set_relative_position((50.0, 20.0))
        assert menu.rect.topleft == (150, 120)

    def test_set_dimensions(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)
        menu.set_dimensions((300, 50))

        assert (menu.current_state.open_button.relative_rect.right ==
                300 - (menu.border_width + menu.shadow_width))

        assert (menu.current_state.open_button.relative_rect.bottom ==
                50 - (menu.border_width + menu.shadow_width))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': (390, 125)}))
        # if we successfully clicked on the moved menu then this button should be True
        assert menu.current_state.open_button.held is True

        menu.current_state.should_transition = True
        menu.update(0.01)

        menu.set_dimensions((200, 30))

        # try to click on the menu
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (290, 115)}))
        # if we successfully clicked on the moved menu then this button should be True
        assert menu.current_state.close_button.held is True

    def test_on_fresh_drawable_shape_ready(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        assert not menu.on_fresh_drawable_shape_ready()

    def test_hover_point(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        assert not menu.hover_point(0, 0)
        assert menu.hover_point(150, 115)

    def test_cropping_size_of_drop_down(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state.options_selection_list.rect.height == 366  # uncropped

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(100, 100, 200, 30),
                              manager=default_ui_manager,
                              expansion_height_limit=200)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state.options_selection_list.scroll_bar is not None
        assert menu.current_state.options_selection_list.rect.height == 200  # cropped to fixed height

        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 100),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager,
                              container=test_container)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state.options_selection_list.rect.height == 63  # cropped to container size by default

        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_drop_down_menu_non_default.json"))

        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 100), manager=manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar',
                                            'eggs', 'flour', 'sugar', 'eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 50, 200, 30),
                              manager=manager,
                              container=test_container)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state.options_selection_list.rect.height == 53  # cropped to container size by default

    def test_select_option_from_drop_down(self, _init_pygame, default_ui_manager,
                                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(0, 0, 300, 300),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager,
                              container=test_container)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.selected_option == 'eggs'
        flour_button = menu.current_state.options_selection_list.item_list_container.elements[1]

        flour_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                      {'button': pygame.BUTTON_LEFT,
                                                       'pos': flour_button.rect.center}))

        flour_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                      {'button': pygame.BUTTON_LEFT,
                                                       'pos': flour_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert menu.selected_option == 'flour'

    def test_disable(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(0, 0, 300, 300),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager,
                              container=test_container)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state == menu.menu_states['expanded']
        assert menu.selected_option == 'eggs'

        menu.disable()
        assert menu.is_enabled is False
        assert menu.current_state == menu.menu_states['closed']

        expand_button = menu.current_state.open_button

        expand_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                       {'button': pygame.BUTTON_LEFT,
                                                        'pos': expand_button.rect.center}))

        expand_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                       {'button': pygame.BUTTON_LEFT,
                                                        'pos': expand_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert menu.current_state.should_transition is False

    def test_enable(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(0, 0, 300, 300),
                                     manager=default_ui_manager)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager,
                              container=test_container)

        menu.current_state.should_transition = True
        menu.update(0.01)

        assert menu.current_state == menu.menu_states['expanded']
        assert menu.selected_option == 'eggs'

        menu.disable()
        assert menu.is_enabled is False

        menu.enable()
        assert menu.is_enabled is True
        assert menu.current_state == menu.menu_states['closed']

        expand_button = menu.current_state.open_button

        expand_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                       {'button': pygame.BUTTON_LEFT,
                                                        'pos': expand_button.rect.center}))

        expand_button.process_event(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                       {'button': pygame.BUTTON_LEFT,
                                                        'pos': expand_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert menu.current_state.should_transition is True

        menu.update(0.01)

        assert menu.current_state == menu.menu_states['expanded']
        assert menu.selected_option == 'eggs'

    def test_show_of_dropdown(self, _init_pygame, default_ui_manager):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager,
                              visible=0)

        assert menu.visible == 0
        assert menu.current_state == menu.menu_states['closed']
        assert menu.menu_states["closed"].visible == 0
        assert menu.menu_states["closed"].selected_option_button.visible == 0
        assert menu.menu_states["closed"].open_button.visible == 0

        menu.show()

        assert menu.visible == 1
        assert menu.current_state == menu.menu_states['closed']
        assert menu.menu_states["closed"].visible == 1
        assert menu.menu_states["closed"].selected_option_button.visible == 1
        assert menu.menu_states["closed"].open_button.visible == 1

    def test_hide_of_closed_dropdown(self, _init_pygame, default_ui_manager,
                                     _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager)

        assert menu.visible == 1
        assert menu.current_state == menu.menu_states['closed']
        assert menu.menu_states["closed"].visible == 1
        assert menu.menu_states["closed"].selected_option_button.visible == 1
        assert menu.menu_states["closed"].open_button.visible == 1

        menu.hide()
        assert menu.visible == 0
        assert menu.current_state == menu.menu_states['closed']
        assert menu.menu_states["closed"].visible == 0
        assert menu.menu_states["closed"].selected_option_button.visible == 0
        assert menu.menu_states["closed"].open_button.visible == 0

    def test_hide_of_expanded_dropdown(self, _init_pygame, default_ui_manager,
                                       _display_surface_return_none):
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=default_ui_manager)

        menu.process_event(pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {'ui_element': menu.menu_states['closed'].open_button}))
        menu.update(0.01)

        assert menu.visible == 1
        assert menu.current_state == menu.menu_states['expanded']

        menu.hide()
        menu.update(0.01)

        assert menu.visible == 0
        assert menu.current_state == menu.menu_states['closed']
        assert menu.menu_states["closed"].visible == 0
        assert menu.menu_states["closed"].selected_option_button.visible == 0
        assert menu.menu_states["closed"].open_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame,
                                 default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)
        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(25, 25, 375, 150),
                              manager=manager,
                              visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        menu.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        menu.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_class_theming_id(self, _init_pygame, _display_surface_return_none):
        manager = UIManager((800, 600),
                            PackageResource('tests.data.themes',
                                            'appearance_theme_class_id_test.json'))

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=manager,
                              object_id=pygame_gui.core.ObjectID(object_id=None,
                                                                 class_id='@test_class')
                              )

        assert menu.combined_element_ids == ['@test_class', 'drop_down_menu']

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              manager=manager,
                              object_id=pygame_gui.core.ObjectID(object_id='#test_object_1',
                                                                 class_id='@test_class'))

        assert menu.combined_element_ids == ['#test_object_1', '@test_class', 'drop_down_menu']

        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=manager)

        menu = UIDropDownMenu(options_list=['eggs', 'flour', 'sugar'],
                              starting_option='eggs',
                              relative_rect=pygame.Rect(10, 10, 200, 30),
                              container=test_container,
                              manager=manager,
                              object_id=pygame_gui.core.ObjectID(object_id='#test_object_1',
                                                                 class_id='@test_class'))

        assert menu.combined_element_ids == ['container.#test_object_1',
                                             'container.@test_class',
                                             'container.drop_down_menu',
                                             '#test_object_1',
                                             '@test_class',
                                             'drop_down_menu']


if __name__ == '__main__':
    pytest.console_main()
