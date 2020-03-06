from typing import Union, List
from os import listdir
from os.path import isfile, join, abspath, exists
from pathlib import Path

import pygame
import pygame_gui

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UISelectionList
from pygame_gui.windows import UIConfirmationDialog


class UIFileDialog(UIWindow):
    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'File Dialog',
                 initial_file_path: Union[str, None] = None,
                 ):
        super().__init__(rect, manager, window_display_title=window_title, object_id='#file_dialog')

        self.delete_confirmation_dialog = None  # type: Union[None, UIConfirmationDialog]

        if initial_file_path is not None:
            if exists(initial_file_path):
                self.current_directory_path = abspath(initial_file_path)
        else:
            self.current_directory_path = abspath('.')

        self.selected_file_path = None

        self.current_file_list = None  # type: Union[None, List[str]]
        self.update_current_file_list()

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text='OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})
        self.ok_button.disable()

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        self.home_button = UIButton(relative_rect=pygame.Rect(10, 10, 20, 20),
                                    text='⌂',
                                    tool_tip_text='Home Directory',
                                    manager=self.ui_manager,
                                    container=self,
                                    object_id='#home_icon_button',
                                    anchors={'left': 'left',
                                             'right': 'left',
                                             'top': 'top',
                                             'bottom': 'top'})

        self.delete_button = UIButton(relative_rect=pygame.Rect(32, 10, 20, 20),
                                      text='⌧',
                                      tool_tip_text='Delete',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#delete_icon_button',
                                      anchors={'left': 'left',
                                               'right': 'left',
                                               'top': 'top',
                                               'bottom': 'top'})
        self.delete_button.disable()

        self.parent_directory_button = UIButton(relative_rect=pygame.Rect(54, 10, 20, 20),
                                                text='↑',
                                                tool_tip_text='Parent Directory',
                                                manager=self.ui_manager,
                                                container=self,
                                                object_id='#parent_icon_button',
                                                anchors={'left': 'left',
                                                         'right': 'left',
                                                         'top': 'top',
                                                         'bottom': 'top'})

        self.refresh_button = UIButton(relative_rect=pygame.Rect(76, 10, 20, 20),
                                       text='⇪',
                                       tool_tip_text='Refresh Directory',
                                       manager=self.ui_manager,
                                       container=self,
                                       object_id='#refresh_icon_button',
                                       anchors={'left': 'left',
                                                'right': 'left',
                                                'top': 'top',
                                                'bottom': 'top'})

        text_line_rect = pygame.Rect(10, 40, self.get_container().relative_rect.width - 20, 25)
        self.file_path_text_line = UITextEntryLine(relative_rect=text_line_rect,
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   object_id='#file_path_text_line',
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'}
                                                   )
        self.file_path_text_line.set_text(self.current_directory_path)

        file_selection_rect = pygame.Rect(10, 80, self.get_container().relative_rect.width - 20,
                                          self.get_container().relative_rect.height - 130)
        self.file_selection_list = UISelectionList(relative_rect=file_selection_rect,
                                                   item_list=self.current_file_list,
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   object_id='#file_display_list',
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'bottom'})

    def update_current_file_list(self):
        try:
            directories_on_path = [f for f in listdir(self.current_directory_path)
                                   if not isfile(join(self.current_directory_path, f))]
            directories_on_path = sorted(directories_on_path, key=str.casefold)
            directories_on_path_tuples = [(f, '#directory_list_item') for f in directories_on_path]

            files_on_path = [f for f in listdir(self.current_directory_path)
                             if isfile(join(self.current_directory_path, f))]
            files_on_path = sorted(files_on_path, key=str.casefold)
            files_on_path_tuples = [(f, '#file_list_item') for f in files_on_path]

            self.current_file_list = directories_on_path_tuples + files_on_path_tuples
        except PermissionError:
            self.current_directory_path = str(Path(self.current_directory_path).parent)
            self.update_current_file_list()

    def process_event(self, event: pygame.event.Event) -> bool:
        handled = super().process_event(event)

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.cancel_button):
            self.kill()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
            and event.ui_element == self.ok_button and self.selected_file_path is not None and exists(
                self.selected_file_path) and isfile(self.selected_file_path)):
            event_data = {'user_type': pygame_gui.UI_FILE_DIALOG_PATH_PICKED,
                          'text': self.selected_file_path,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            new_file_chosen_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(new_file_chosen_event)
            self.kill()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.delete_button):
            confirmation_rect = pygame.Rect(0, 0, 300, 200)
            confirmation_rect.center = self.rect.center

            selected_file_name = Path(self.selected_file_path).name
            long_desc = "Delete " + str(selected_file_name) + "?"
            self.delete_confirmation_dialog = UIConfirmationDialog(rect=confirmation_rect,
                                                                   manager=self.ui_manager,
                                                                   confirming_action_long_desc=long_desc,
                                                                   confirming_action_short_name='Delete',
                                                                   window_title='Delete')

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED
                and event.ui_element == self.delete_confirmation_dialog):
            try:
                Path(self.selected_file_path).unlink()
                self.delete_button.disable()

                self.update_current_file_list()
                self.file_path_text_line.set_text(self.current_directory_path)
                self.file_selection_list.set_item_list(self.current_file_list)
            except FileNotFoundError:
                pass

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.parent_directory_button):
            self.current_directory_path = str(Path(self.current_directory_path).parent)

            self.update_current_file_list()
            self.file_path_text_line.set_text(self.current_directory_path)
            self.file_selection_list.set_item_list(self.current_file_list)

            self.delete_button.disable()
            self.ok_button.disable()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.refresh_button):

            self.update_current_file_list()
            self.file_path_text_line.set_text(self.current_directory_path)
            self.file_selection_list.set_item_list(self.current_file_list)

            self.delete_button.disable()
            self.ok_button.disable()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.home_button):
            self.current_directory_path = str(Path.home())

            self.update_current_file_list()
            self.file_path_text_line.set_text(self.current_directory_path)
            self.file_selection_list.set_item_list(self.current_file_list)

            self.delete_button.disable()
            self.ok_button.disable()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED
                and event.ui_element == self.file_path_text_line):
            entered_file_path = self.file_path_text_line.get_text()
            if exists(entered_file_path):
                self.current_directory_path = abspath(entered_file_path)

                self.update_current_file_list()
                self.file_path_text_line.set_text(self.current_directory_path)
                self.file_selection_list.set_item_list(self.current_file_list)

                self.delete_button.disable()
                self.ok_button.disable()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION
                and event.ui_element == self.file_selection_list):
            new_selection_file_path = join(self.current_directory_path, event.text)
            if exists(new_selection_file_path) and isfile(new_selection_file_path):
                self.selected_file_path = new_selection_file_path
                self.ok_button.enable()
                self.delete_button.enable()
            else:
                self.ok_button.disable()
                self.delete_button.disable()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
                and event.ui_element == self.file_selection_list):
            new_directory_file_path = join(self.current_directory_path, event.text)
            if exists(new_directory_file_path) and not isfile(new_directory_file_path):
                self.current_directory_path = abspath(new_directory_file_path)

                self.update_current_file_list()
                self.file_path_text_line.set_text(self.current_directory_path)
                self.file_selection_list.set_item_list(self.current_file_list)

                self.delete_button.disable()
                self.ok_button.disable()

        return handled
