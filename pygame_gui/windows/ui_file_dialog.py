import warnings

from typing import Union, List
from pathlib import Path

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED
from pygame_gui._constants import UI_CONFIRMATION_DIALOG_CONFIRMED, UI_FILE_DIALOG_PATH_PICKED

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UISelectionList
from pygame_gui.windows.ui_confirmation_dialog import UIConfirmationDialog


class UIFileDialog(UIWindow):
    """
    A dialog window for handling file selection operations. The dialog will let you pick a file
    from a file system but won't do anything with it once you have, the path will just be returned
    leaving it up to the rest of the application to decide what to do with it.

    :param rect: The size and position of the file dialog window. Includes the size of shadow,
                 border and title bar.
    :param manager: The manager for the whole of the UI.
    :param window_title: The title for the window, defaults to 'File Dialog'
    :param initial_file_path: The initial path to open the file dialog at.
    :param object_id: The object ID for the window, used for theming - defaults to '#file_dialog'

    """

    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'File Dialog',
                 initial_file_path: Union[str, None] = None,
                 object_id: str = '#file_dialog',
                 allow_existing_files_only: bool = False,
                 allow_picking_directories: bool = False
                 ):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True)

        minimum_dimensions = (260, 300)
        if rect.width < minimum_dimensions[0] or rect.height < minimum_dimensions[1]:
            warn_string = ("Initial size: " + str(rect.size) +
                           " is less than minimum dimensions: " + str(minimum_dimensions))
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.allow_existing_files_only = allow_existing_files_only
        self.allow_picking_directories = allow_picking_directories

        self.delete_confirmation_dialog = None  # type: Union[UIConfirmationDialog, None]
        self.current_file_path = None  # type: Union[Path, None]

        if initial_file_path is not None:
            pathed_initial_file_path = Path(initial_file_path)
            if pathed_initial_file_path.exists() and not pathed_initial_file_path.is_file():
                self.current_directory_path = str(pathed_initial_file_path.resolve())
                if self.allow_picking_directories:
                    self.current_file_path = self.current_directory_path
            elif pathed_initial_file_path.exists() and pathed_initial_file_path.is_file():
                self.current_file_path = pathed_initial_file_path.resolve()
                self.current_directory_path = str(pathed_initial_file_path.parent.resolve())
            elif pathed_initial_file_path.parent.exists():
                self.current_directory_path = str(pathed_initial_file_path.parent.resolve())
                self.current_file_path = (Path(initial_file_path).parent.resolve() /
                                          Path(initial_file_path).name)
        else:
            self.current_directory_path = str(Path('.').resolve())

        self.last_valid_directory_path = self.current_directory_path

        self.current_file_list = None  # type: Union[List[str], None]
        self.update_current_file_list()

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text='OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id='#ok_button',
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})
        if not self._validate_file_path(self.current_file_path):
            self.ok_button.disable()

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
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
        if not self._validate_path_exists_and_of_allowed_type(self.current_file_path,
                                                              allow_directories=False):
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

        text_line_rect = pygame.Rect(10, 40, self.get_container().get_size()[0] - 20, 25)
        self.file_path_text_line = UITextEntryLine(relative_rect=text_line_rect,
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   object_id='#file_path_text_line',
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'}
                                                   )
        if self.current_file_path is not None:
            self.file_path_text_line.set_text(str(self.current_file_path))
            self._highlight_file_name_for_editing()
        else:
            self.file_path_text_line.set_text(str(self.current_directory_path))

        file_selection_rect = pygame.Rect(10, 80, self.get_container().get_size()[0] - 20,
                                          self.get_container().get_size()[1] - 130)
        self.file_selection_list = UISelectionList(relative_rect=file_selection_rect,
                                                   item_list=self.current_file_list,
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   object_id='#file_display_list',
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'bottom'})

    def _highlight_file_name_for_editing(self):
        # try highlighting the file name
        if self.current_file_path is not None and not self.allow_existing_files_only:
            highlight_start = self.file_path_text_line.get_text().find(self.current_file_path.stem)
            highlight_end = highlight_start + len(self.current_file_path.stem)
            self.file_path_text_line.select_range[0] = highlight_start
            self.file_path_text_line.select_range[1] = highlight_end
            self.file_path_text_line.cursor_has_moved_recently = True
            self.file_path_text_line.edit_position = highlight_end

            text_clip_width = (self.file_path_text_line.rect.width -
                               (self.file_path_text_line.horiz_line_padding * 2) -
                               (self.file_path_text_line.shape_corner_radius * 2) -
                               (self.file_path_text_line.border_width * 2) -
                               (self.file_path_text_line.shadow_width * 2))

            text_width = self.file_path_text_line.font.size(self.file_path_text_line.get_text())[0]
            self.file_path_text_line.start_text_offset = max(0, text_width - text_clip_width)
            self.file_path_text_line.focus()

    def update_current_file_list(self):
        """
        Updates the currently displayed list of files and directories. Usually called when the
        directory path has changed.
        """
        try:
            directories_on_path = [f.name for f in Path(self.current_directory_path).iterdir()
                                   if not f.is_file()]
            directories_on_path = sorted(directories_on_path, key=str.casefold)
            directories_on_path_tuples = [(f, '#directory_list_item') for f in directories_on_path]

            files_on_path = [f.name for f in Path(self.current_directory_path).iterdir()
                             if f.is_file()]
            files_on_path = sorted(files_on_path, key=str.casefold)
            files_on_path_tuples = [(f, '#file_list_item') for f in files_on_path]

            self.current_file_list = directories_on_path_tuples + files_on_path_tuples
        except (PermissionError, FileNotFoundError):
            self.current_directory_path = self.last_valid_directory_path
            self.update_current_file_list()
        else:
            self.last_valid_directory_path = self.current_directory_path

    def _validate_file_path(self, path_to_validate: Path) -> bool:
        if self.allow_existing_files_only:
            return self._validate_path_exists_and_of_allowed_type(path_to_validate,
                                                                  self.allow_picking_directories)
        else:
            return self._validate_path_in_existing_directory(path_to_validate)

    @staticmethod
    def _validate_path_in_existing_directory(path_to_validate: Path) -> bool:
        """
        Checks the selected path is valid.

        :return: True if valid.

        """
        if path_to_validate is None:
            return False
        return len(path_to_validate.name) > 0 and path_to_validate.parent.exists()

    @staticmethod
    def _validate_path_exists_and_of_allowed_type(path_to_validate: Path,
                                                  allow_directories: bool) -> bool:
        """
        Checks the selected path is valid.

        :return: True if valid.

        """
        if path_to_validate is None:
            return False
        if allow_directories:
            valid_type = (path_to_validate.is_file() or path_to_validate.is_dir())
        else:
            valid_type = path_to_validate.is_file()
        return path_to_validate.exists() and valid_type

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. There are a lot of buttons in the
        file dialog.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        handled = super().process_event(event)

        self._process_ok_cancel_events(event)
        self._process_confirmation_dialog_events(event)
        self._process_mini_file_operation_button_events(event)
        self._process_file_path_entry_events(event)
        self._process_file_list_events(event)

        return handled

    def _process_file_path_entry_events(self, event):
        """
        Handle events coming from text entry element which displays the current file path.

        :param event: event to check.

        """
        if (event.type != pygame.USEREVENT
                or event.user_type not in [UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED]
                or event.ui_element != self.file_path_text_line):
            return
        entered_file_path = Path(self.file_path_text_line.get_text()).absolute()
        if self._validate_file_path(entered_file_path):
            if len(entered_file_path.name) > 0 and (entered_file_path.is_file() or
                                                    not entered_file_path.exists()):
                self.current_file_path = entered_file_path

                if self._validate_path_exists_and_of_allowed_type(self.current_file_path,
                                                                  allow_directories=False):
                    self.delete_button.enable()
                else:
                    self.delete_button.disable()
                self.ok_button.enable()
            else:
                self.current_directory_path = str(entered_file_path)
                self.current_file_path = None
                self.delete_button.disable()
                self.ok_button.disable()

            if event.user_type == UI_TEXT_ENTRY_FINISHED:
                if len(entered_file_path.name) > 0 and entered_file_path.is_dir():
                    self.current_directory_path = str(entered_file_path)
                elif len(entered_file_path.name) > 0 and (entered_file_path.is_file() or
                                                          not entered_file_path.exists()):
                    self.current_directory_path = str(entered_file_path.parent.absolute())
                else:
                    self.current_directory_path = str(entered_file_path)

                self.update_current_file_list()
                self.file_selection_list.set_item_list(self.current_file_list)

                if self.current_file_path is not None:
                    self.file_path_text_line.set_text(str(self.current_file_path))
                else:
                    self.file_path_text_line.set_text(self.current_directory_path)
        else:
            self.current_directory_path = self.last_valid_directory_path
            self.current_file_path = None
            self.delete_button.disable()
            self.ok_button.disable()

    def _process_file_list_events(self, event):
        """
        Handle events coming from the file/folder list.

        :param event: event to check.

        """
        if (event.type == pygame.USEREVENT and
                event.user_type == UI_SELECTION_LIST_NEW_SELECTION and
                event.ui_element == self.file_selection_list):
            new_selection_file_path = Path(self.current_directory_path) / event.text
            if self._validate_path_exists_and_of_allowed_type(new_selection_file_path,
                                                              self.allow_picking_directories):
                self.current_file_path = new_selection_file_path
                self.file_path_text_line.set_text(str(self.current_file_path))
                self._highlight_file_name_for_editing()
                self.ok_button.enable()
                if self._validate_path_exists_and_of_allowed_type(self.current_file_path,
                                                                  allow_directories=False):
                    self.delete_button.enable()
                else:
                    self.delete_button.disable()
            else:
                self.ok_button.disable()
                self.delete_button.disable()
        if (event.type == pygame.USEREVENT and
                event.user_type == UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
                and event.ui_element == self.file_selection_list):
            new_directory_file_path = Path(self.current_directory_path) / event.text
            self._change_directory_path(new_directory_file_path)

    def _change_directory_path(self, new_directory_path: Path):
        """
        Change the current directory path and update everything that needs to update when that
        happens.

        :param new_directory_path: The new path to change to.
        """
        if not new_directory_path.exists() or new_directory_path.is_file():
            return
        self.current_directory_path = str(new_directory_path.resolve())
        self.update_current_file_list()
        self.file_selection_list.set_item_list(self.current_file_list)

        if self.current_file_path is not None and not self.allow_existing_files_only:
            self.current_file_path = (new_directory_path / self.current_file_path.name).resolve()
            self.file_path_text_line.set_text(str(self.current_file_path))
            self._highlight_file_name_for_editing()
            self.ok_button.enable()
            if self._validate_path_exists_and_of_allowed_type(self.current_file_path,
                                                              allow_directories=False):
                self.delete_button.enable()
            else:
                self.delete_button.disable()
        else:
            self.current_file_path = None
            self.file_path_text_line.set_text(self.current_directory_path)
            self.delete_button.disable()
            self.ok_button.disable()

    def _process_confirmation_dialog_events(self, event):
        """
        Handle any events coming from the confirmation dialog if that's up.

        :param event: event to check.

        """
        if (event.type != pygame.USEREVENT
                or event.user_type != UI_CONFIRMATION_DIALOG_CONFIRMED
                or event.ui_element != self.delete_confirmation_dialog):
            return
        try:
            self.current_file_path.unlink()
            self.current_file_path = None
            self.delete_button.disable()
            self.ok_button.disable()

            self.update_current_file_list()
            self.file_path_text_line.set_text(self.current_directory_path)
            self.file_selection_list.set_item_list(self.current_file_list)

        except (PermissionError, FileNotFoundError):
            pass

    def _process_mini_file_operation_button_events(self, event):
        """
        Handle what happens when you press one of the tiny file/folder operation buttons.

        :param event: event to check.

        """
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.delete_button):
            confirmation_rect = pygame.Rect(0, 0, 300, 200)
            confirmation_rect.center = self.rect.center

            selected_file_name = self.current_file_path.name
            long_desc = "Delete " + str(selected_file_name) + "?"
            self.delete_confirmation_dialog = UIConfirmationDialog(rect=confirmation_rect,
                                                                   manager=self.ui_manager,
                                                                   action_long_desc=long_desc,
                                                                   action_short_name='Delete',
                                                                   window_title='Delete')
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.parent_directory_button):
            self._change_directory_path(Path(self.current_directory_path).parent)
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.refresh_button):
            self._change_directory_path(Path(self.current_directory_path))
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.home_button):
            self._change_directory_path(Path.home())

    def _process_ok_cancel_events(self, event):
        """
        Handle what happens when you press OK and Cancel.

        :param event: event to check.

        """
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.cancel_button):
            self.kill()
        if (event.type == pygame.USEREVENT and event.user_type == UI_BUTTON_PRESSED
                and event.ui_element == self.ok_button
                and self._validate_file_path(self.current_file_path)):
            event_data = {'user_type': UI_FILE_DIALOG_PATH_PICKED,
                          'text': str(self.current_file_path),
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            new_file_chosen_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(new_file_chosen_event)
            self.kill()
