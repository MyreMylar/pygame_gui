import os
from os.path import isfile, join, abspath, exists
from pathlib import Path

import pygame
import pytest
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows import UIFileDialog

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIUIFileDialog:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager)

    def test_create_too_small(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        with pytest.warns(UserWarning, match="Initial size"):
            UIFileDialog(rect=pygame.Rect(100, 100, 50, 50),
                         manager=default_ui_manager)

    def test_update_current_file_list(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        assert file_dialog.current_file_list != [('splat.png', '#file_list_item')]

        file_dialog.current_directory_path = abspath('tests/data/images')
        file_dialog.update_current_file_list()

        assert file_dialog.current_file_list == [('splat.png', '#file_list_item')]

        file_dialog.current_directory_path = 'nonsense/path/that/does/not/exist'
        file_dialog.update_current_file_list()

        assert file_dialog.current_file_list == [('splat.png', '#file_list_item')]

    def test_press_cancel_button(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        is_alive_pre_events = file_dialog.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.cancel_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.cancel_button.rect.center}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        is_dead_post_events = not file_dialog.alive()

        assert is_alive_pre_events is True and is_dead_post_events is True

    def test_press_ok_button(self, _init_pygame, default_ui_manager,
                             _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        file_dialog.selected_file_path = abspath('tests/data/images/splat.png')
        file_dialog.ok_button.enable()

        is_alive_pre_events = file_dialog.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.ok_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.ok_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        confirm_event_fired = False
        event_path = None
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

            if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and
                    event.ui_element == file_dialog):
                confirm_event_fired = True
                event_path = event.text
        is_dead_post_events = not file_dialog.alive()

        assert is_alive_pre_events
        assert is_dead_post_events
        assert confirm_event_fired
        assert event_path is not None and Path(event_path).name == 'splat.png'

    def test_press_delete_button_and_cancel(self, _init_pygame, default_ui_manager,
                                            _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        file_dialog.selected_file_path = abspath('tests/data/images/splat.png')
        file_dialog.delete_button.enable()

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.delete_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.delete_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.delete_confirmation_dialog is not None

        cancel_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                           'ui_element': file_dialog.delete_confirmation_dialog.cancel_button})

        default_ui_manager.process_events(cancel_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

    def test_press_delete_button_and_ok(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        with open(abspath('tests/data/for_delete.txt'), 'w') as file_to_delete:
            file_to_delete.write('Some text')

        file_dialog.selected_file_path = abspath('tests/data/for_delete.txt')
        file_dialog.delete_button.enable()

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.delete_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.delete_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.delete_confirmation_dialog is not None

        ok_event = pygame.event.Event(pygame.USEREVENT,
                                      {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                       'ui_element': file_dialog.delete_confirmation_dialog.confirm_button})

        default_ui_manager.process_events(ok_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert (not exists(abspath('tests/data/for_delete.txt')))

    def test_press_parent_button(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        parent_event = pygame.event.Event(pygame.USEREVENT,
                                      {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                       'ui_element': file_dialog.parent_directory_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'data'

    def test_press_refresh_button(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        parent_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                           'ui_element': file_dialog.refresh_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'images'

    def test_press_home_button(self, _init_pygame, default_ui_manager,
                               _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        home_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                                           'ui_element': file_dialog.home_button})

        default_ui_manager.process_events(home_event)

        assert Path(file_dialog.current_directory_path).name == Path.home().name

    def test_new_file_selection(self, _init_pygame, default_ui_manager,
                                _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        select_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                           'ui_element': file_dialog.file_selection_list,
                                           'text': 'splat.png'})

        default_ui_manager.process_events(select_event)

        assert file_dialog.selected_file_path is not None and Path(file_dialog.selected_file_path).name == 'splat.png'
        assert file_dialog.ok_button.is_enabled

        select_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                           'ui_element': file_dialog.file_selection_list,
                                           'text': 'not_a_file.not'})

        default_ui_manager.process_events(select_event)

        assert not file_dialog.ok_button.is_enabled

    def test_directory_double_clicked(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/')

        directory_event = pygame.event.Event(pygame.USEREVENT,
                                          {'user_type': pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                                           'ui_element': file_dialog.file_selection_list,
                                           'text': 'images'})

        default_ui_manager.process_events(directory_event)

        assert file_dialog.current_directory_path == abspath('tests/data/images')
        assert not file_dialog.ok_button.is_enabled
        assert not file_dialog.delete_button.is_enabled
        assert file_dialog.file_path_text_line.text == abspath('tests/data/images')

    def test_file_path_entry_finished(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        file_dialog.file_path_text_line.set_text('tests/data/images')

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.file_path_text_line.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': file_dialog.file_path_text_line.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}
                                                             ))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.current_file_list == [('splat.png', '#file_list_item')]