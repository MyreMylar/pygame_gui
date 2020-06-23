from pathlib import Path

import pygame
import pytest
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager, _display_surface_return_none
from tests.shared_comparators import compare_surfaces

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

        assert ('splat.png', '#file_list_item') not in file_dialog.current_file_list

        file_dialog.current_directory_path = str(Path('tests/data/images').resolve())
        file_dialog.update_current_file_list()

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

        file_dialog.current_directory_path = 'nonsense/path/that/does/not/exist'
        file_dialog.update_current_file_list()

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

    def test_press_cancel_button(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        is_alive_pre_events = file_dialog.alive()
        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.cancel_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        is_dead_post_events = not file_dialog.alive()

        assert is_alive_pre_events is True and is_dead_post_events is True

    def test_press_ok_button(self, _init_pygame, default_ui_manager,
                             _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        file_dialog.current_file_path = Path('tests/data/images/splat.png').absolute()
        file_dialog.ok_button.enable()

        is_alive_pre_events = file_dialog.alive()
        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.ok_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        confirm_event_fired = False
        event_path = None
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and
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

        file_dialog.current_file_path = Path('tests/data/images/splat.png').resolve()
        file_dialog.delete_button.enable()

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.delete_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.delete_confirmation_dialog is not None

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': file_dialog.delete_confirmation_dialog.cancel_button}
        cancel_event = pygame.event.Event(pygame.USEREVENT, event_data)

        default_ui_manager.process_events(cancel_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

    def test_press_delete_button_and_ok(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        with open(str(Path('tests/data/for_delete.txt')), 'w') as file_to_delete:
            file_to_delete.write('Some text')

        file_dialog.current_file_path = Path('tests/data/for_delete.txt').absolute()
        file_dialog.delete_button.enable()

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.delete_button.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.delete_confirmation_dialog is not None

        ok_event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                         'ui_element': file_dialog.delete_confirmation_dialog.confirm_button}
        ok_event = pygame.event.Event(pygame.USEREVENT, ok_event_data)

        default_ui_manager.process_events(ok_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert not Path('tests/data/for_delete.txt').exists()

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

        assert file_dialog.current_file_path is not None
        assert file_dialog.current_file_path.name == 'splat.png'
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

        event_data = {'user_type': pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                      'ui_element': file_dialog.file_selection_list,
                      'text': 'images'}
        directory_event = pygame.event.Event(pygame.USEREVENT, event_data)

        default_ui_manager.process_events(directory_event)

        assert file_dialog.current_directory_path == str(Path('tests/data/images').resolve())
        assert not file_dialog.ok_button.is_enabled
        assert not file_dialog.delete_button.is_enabled
        assert file_dialog.file_path_text_line.text == str(Path('tests/data/images').resolve())

    def test_file_path_entry_finished(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        file_dialog.file_path_text_line.set_text('tests/data/images')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.file_path_text_line.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.current_file_path is None
        assert str(Path(file_dialog.current_directory_path).parts[-1]) == 'images'

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   visible=0)
        file_dialog.file_path_text_line.set_text('tests/data/images')

        assert file_dialog.visible == 0
        assert file_dialog.dirty == 1

        assert file_dialog.cancel_button.visible == 0
        assert file_dialog.ok_button.visible == 0
        assert file_dialog.delete_button.visible == 0
        assert file_dialog.home_button.visible == 0
        assert file_dialog.parent_directory_button.visible == 0
        assert file_dialog.refresh_button.visible == 0
        assert file_dialog.close_window_button.visible == 0

        file_dialog.show()

        assert file_dialog.visible == 1
        assert file_dialog.dirty == 2

        assert file_dialog.cancel_button.visible == 1
        assert file_dialog.ok_button.visible == 1
        assert file_dialog.delete_button.visible == 1
        assert file_dialog.home_button.visible == 1
        assert file_dialog.parent_directory_button.visible == 1
        assert file_dialog.refresh_button.visible == 1
        assert file_dialog.close_window_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)
        file_dialog.file_path_text_line.set_text('tests/data/images')

        assert file_dialog.visible == 1
        assert file_dialog.dirty == 2

        assert file_dialog.cancel_button.visible == 1
        assert file_dialog.ok_button.visible == 1
        assert file_dialog.delete_button.visible == 1
        assert file_dialog.home_button.visible == 1
        assert file_dialog.parent_directory_button.visible == 1
        assert file_dialog.refresh_button.visible == 1
        assert file_dialog.close_window_button.visible == 1

        file_dialog.hide()

        assert file_dialog.visible == 0
        assert file_dialog.dirty == 1

        assert file_dialog.cancel_button.visible == 0
        assert file_dialog.ok_button.visible == 0
        assert file_dialog.delete_button.visible == 0
        assert file_dialog.home_button.visible == 0
        assert file_dialog.parent_directory_button.visible == 0
        assert file_dialog.refresh_button.visible == 0
        assert file_dialog.close_window_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (600, 600)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=manager,
                                   visible=0)
        file_dialog.file_path_text_line.set_text('tests/data/images')

        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        file_dialog.show()
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        file_dialog.hide()
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)
