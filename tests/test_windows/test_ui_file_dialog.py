from pathlib import Path

import pygame
import pytest
import pygame_gui

from tests.shared_comparators import compare_surfaces

from pygame_gui.windows import UIFileDialog
from pygame_gui import UI_TEXT_ENTRY_CHANGED, UI_TEXT_ENTRY_FINISHED


class TestUIUIFileDialog:

    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager)

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager,
                     allow_picking_directories=True,
                     initial_file_path='tests/data/images')

    def test_create_too_small(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        with pytest.warns(UserWarning, match="Initial size"):
            UIFileDialog(rect=pygame.Rect(100, 100, 50, 50),
                         manager=default_ui_manager)

    def test_create_options(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, allow_existing_files_only=True)

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, allow_picking_directories=True)

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, initial_file_path='tests/data/images')

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, initial_file_path='tests/data/images/splat.png')

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, initial_file_path='tests/data/images/splot.png')

        UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                     manager=default_ui_manager, initial_file_path='nonsense/path/that/does/not/exist')

    def test_update_current_file_list(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        assert ('splat.png', '#file_list_item') not in file_dialog.current_file_list

        file_dialog.current_directory_path = str(Path('tests/data/images').resolve())
        file_dialog.update_current_file_list()

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

        file_dialog.current_directory_path = 'nonsense/path/that/does/not/exist'
        file_dialog.update_current_file_list()

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

    def test_press_cancel_button(self, _init_pygame, _display_surface_return_none, default_ui_manager):
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

    def test_press_ok_button(self, _init_pygame, _display_surface_return_none, default_ui_manager):
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

            if (event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and
                    event.ui_element == file_dialog):
                confirm_event_fired = True
                event_path = event.text
        is_dead_post_events = not file_dialog.alive()

        assert is_alive_pre_events
        assert is_dead_post_events
        assert confirm_event_fired
        assert event_path is not None and Path(event_path).name == 'splat.png'

    def test_press_delete_button_and_cancel(self, _init_pygame, _display_surface_return_none, default_ui_manager):

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

        # fail to delete
        file_dialog.current_file_path = Path('tests/data/images/not_a_file.png')
        confirm_delete_event = pygame.event.Event(pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
                                                  {'ui_element': file_dialog.delete_confirmation_dialog})

        default_ui_manager.process_events(confirm_delete_event)
        # cancel
        event_data = {'ui_element': file_dialog.delete_confirmation_dialog.cancel_button}
        cancel_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)

        default_ui_manager.process_events(cancel_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

    def test_press_delete_button_and_ok(self, _init_pygame, _display_surface_return_none, default_ui_manager):

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

        ok_event_data = {'ui_element': file_dialog.delete_confirmation_dialog.confirm_button}
        ok_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, ok_event_data)

        default_ui_manager.process_events(ok_event)

        assert (not file_dialog.delete_confirmation_dialog.alive())

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert not Path('tests/data/for_delete.txt').exists()

    def test_press_parent_button(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        parent_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                          {'ui_element': file_dialog.parent_directory_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'data'

    def test_press_refresh_button(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        parent_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                          {'ui_element': file_dialog.refresh_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'images'

        file_dialog.current_file_path = Path('tests/data/images/splat.png')

        parent_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                          {'ui_element': file_dialog.refresh_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'images'
        assert Path(file_dialog.current_file_path).name == 'splat.png'

        file_dialog.current_file_path = Path('tests/data/images/splot.png')

        parent_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                          {'ui_element': file_dialog.refresh_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'images'
        assert Path(file_dialog.current_file_path).name == 'splot.png'

        file_dialog.current_file_path = Path('tests/data/badpath/')

        parent_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                          {'ui_element': file_dialog.refresh_button})

        default_ui_manager.process_events(parent_event)

        assert Path(file_dialog.current_directory_path).name == 'images'

    def test_press_home_button(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        home_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED,
                                        {'ui_element': file_dialog.home_button})

        default_ui_manager.process_events(home_event)

        assert Path(file_dialog.current_directory_path).name == Path.home().name

    def test_new_file_selection(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images/')

        select_event = pygame.event.Event(pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                          {'ui_element': file_dialog.file_selection_list,
                                           'text': 'splat.png'})

        default_ui_manager.process_events(select_event)

        assert file_dialog.current_file_path is not None
        assert file_dialog.current_file_path.name == 'splat.png'
        assert file_dialog.ok_button.is_enabled

        file_dialog.kill()

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/',
                                   allow_picking_directories=True)

        select_event = pygame.event.Event(pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                          {'ui_element': file_dialog.file_selection_list,
                                           'text': 'images'})

        default_ui_manager.process_events(select_event)

        assert not file_dialog.delete_button.is_enabled

        select_event = pygame.event.Event(pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                          {'ui_element': file_dialog.file_selection_list,
                                           'text': 'not_a_file.not'})

        default_ui_manager.process_events(select_event)

        assert not file_dialog.ok_button.is_enabled

    def test_directory_double_clicked(self, _init_pygame, _display_surface_return_none, default_ui_manager):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/')

        event_data = {'ui_element': file_dialog.file_selection_list,
                      'text': 'images'}
        directory_event = pygame.event.Event(pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                                             event_data)

        default_ui_manager.process_events(directory_event)

        assert file_dialog.current_directory_path == str(Path('tests/data/images').resolve())
        assert not file_dialog.ok_button.is_enabled
        assert not file_dialog.delete_button.is_enabled
        assert file_dialog.file_path_text_line.text == str(Path('tests/data/images').resolve())

    def test_file_path_entry_finished(self, _init_pygame, _display_surface_return_none, default_ui_manager):
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

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert file_dialog.current_file_path is None
        assert str(Path(file_dialog.current_directory_path).parts[-1]) == 'images'

        assert ('splat.png', '#file_list_item') in file_dialog.current_file_list

        file_dialog.file_path_text_line.set_text('tests/data/images/splat.png')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': file_dialog.file_path_text_line.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert Path(file_dialog.current_directory_path).name == 'images'

    def test_process_event(self, default_ui_manager, _display_surface_return_none):

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)

        assert not file_dialog.delete_button.is_enabled

        file_dialog.file_path_text_line.set_text('tests/data/images/splat.png')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_CHANGED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert file_dialog.delete_button.is_enabled

        file_dialog.file_path_text_line.set_text('tests/data/images/splot.png')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_CHANGED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert not file_dialog.delete_button.is_enabled

        file_dialog.file_path_text_line.set_text('tests/data/images/splat.png')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_FINISHED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert file_dialog.delete_button.is_enabled

        file_dialog.file_path_text_line.set_text('tests/data/images/splot.png')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_FINISHED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert not file_dialog.delete_button.is_enabled

        file_dialog.file_path_text_line.set_text('tests/data/badpath/splot.png')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_FINISHED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert Path(file_dialog.current_directory_path).name == 'images'

        file_dialog.file_path_text_line.set_text('/')

        file_dialog.process_event(pygame.event.Event(UI_TEXT_ENTRY_FINISHED,
                                                     {'ui_element': file_dialog.file_path_text_line}))

        assert Path(file_dialog.current_directory_path).name == ''

    def test_show(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   visible=0)
        file_dialog.file_path_text_line.set_text('tests/data/images')

        assert file_dialog.visible == 0

        assert file_dialog.cancel_button.visible == 0
        assert file_dialog.ok_button.visible == 0
        assert file_dialog.delete_button.visible == 0
        assert file_dialog.home_button.visible == 0
        assert file_dialog.parent_directory_button.visible == 0
        assert file_dialog.refresh_button.visible == 0
        assert file_dialog.close_window_button.visible == 0

        file_dialog.show()

        assert file_dialog.visible == 1

        assert file_dialog.cancel_button.visible == 1
        assert file_dialog.ok_button.visible == 1
        assert file_dialog.delete_button.visible == 1
        assert file_dialog.home_button.visible == 1
        assert file_dialog.parent_directory_button.visible == 1
        assert file_dialog.refresh_button.visible == 1
        assert file_dialog.close_window_button.visible == 1

    def test_hide(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager)
        file_dialog.file_path_text_line.set_text('tests/data/images')

        assert file_dialog.visible == 1

        assert file_dialog.cancel_button.visible == 1
        assert file_dialog.ok_button.visible == 1
        assert file_dialog.delete_button.visible == 1
        assert file_dialog.home_button.visible == 1
        assert file_dialog.parent_directory_button.visible == 1
        assert file_dialog.refresh_button.visible == 1
        assert file_dialog.close_window_button.visible == 1

        file_dialog.hide()

        assert file_dialog.visible == 0

        assert file_dialog.cancel_button.visible == 0
        assert file_dialog.ok_button.visible == 0
        assert file_dialog.delete_button.visible == 0
        assert file_dialog.home_button.visible == 0
        assert file_dialog.parent_directory_button.visible == 0
        assert file_dialog.refresh_button.visible == 0
        assert file_dialog.close_window_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        resolution = (600, 600)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)

        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=manager,
                                   visible=0)
        file_dialog.file_path_text_line.set_text('tests/data/images')
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        file_dialog.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        file_dialog.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_change_directory_path(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='tests/data/images')

        file_dialog._change_directory_path(Path('blep/blep/'))

        assert Path(file_dialog.current_directory_path).name == "images"

    def test_highlight_file_name_for_editing(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        file_dialog = UIFileDialog(rect=pygame.Rect(100, 100, 440, 500),
                                   manager=default_ui_manager,
                                   initial_file_path='')

        file_dialog.current_file_path = None
        file_dialog._highlight_file_name_for_editing()


if __name__ == '__main__':
    pytest.console_main()
