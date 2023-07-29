import html
from typing import Union, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIWindow, UITextBox, UITextEntryLine
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED
from pygame_gui._constants import UI_CONSOLE_COMMAND_ENTERED


class UIConsoleWindow(UIWindow):
    """
    Create a basic console window. By default it doesn't do anything except log
    commands entered into the console in the text box log. There is an event
    and a few methods however that allow you to hook this console window up
    to do whatever you would like with the entered text commands.

    See the pygame GUI examples repository for an example using it to run the
    Python Interactive Shell.

    :param rect: A rect determining the size and position of the console window.
    :param manager: The UI manager. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param window_title: The title displayed in the windows title bar.
    :param object_id: The object ID for the window, used for theming - defaults to
                      '#console_window'
    :param visible: Whether the element is visible by default.
    """
    def __init__(self,
                 rect: pygame.Rect,
                 manager: Optional[IUIManagerInterface] = None,
                 window_title: str = 'pygame-gui.console_title_bar',
                 object_id: Union[ObjectID, str] = ObjectID('#console_window', None),
                 visible: int = 1,
                 preload_bold_log_font: bool = True):
        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        self.default_log_prefix = '> '
        self.log_prefix = self.default_log_prefix

        self.should_logged_commands_escape_html = True

        self.logged_commands_above = []
        self.current_logged_command = None
        self.logged_commands_below = []

        self.command_entry = UITextEntryLine(
            relative_rect=pygame.rect.Rect((2, -32),
                                           (self.get_container().get_size()[0]-4, 30)),
            manager=self.ui_manager,
            container=self,
            object_id='#command_entry',
            anchors={'left': 'left',
                     'right': 'right',
                     'top': 'bottom',
                     'bottom': 'bottom'})

        self.log = UITextBox(
            html_text="",
            relative_rect=pygame.rect.Rect((2, 2), (self.get_container().get_size()[0]-4,
                                                    self.get_container().get_size()[1]-36)),
            manager=manager,
            container=self,
            object_id='#log',
            anchors={'left': 'left',
                     'right': 'right',
                     'top': 'top',
                     'bottom': 'bottom'})

        if preload_bold_log_font:
            # Would be better to load this font during UIManager setup, but this is probably
            # second best place. We can't know if someone will use the console window in advance
            # but if they do and use the default bold output setup for it, it would be a good idea
            # to load the bold font at th the same time th other UI stuff is loaded.

            log_font_info = self.ui_theme.get_font_info(self.log.combined_element_ids)
            font_dict = self.ui_manager.get_theme().get_font_dictionary()
            bold_font_id = font_dict.create_font_id(log_font_info['size'],
                                                    log_font_info['name'],
                                                    bold=True,
                                                    italic=False)
            if not font_dict.check_font_preloaded(bold_font_id):
                font_dict.preload_font(log_font_info['size'],
                                       log_font_info['name'],
                                       bold=True)

    def set_log_prefix(self, prefix: str) -> None:
        """
        Set the prefix to add before commands when they are displayed in the log.
        This defaults to '> '.

        :param prefix: A string that is prepended to commands before they are added to the
                       log text box.
        """
        self.log_prefix = prefix

    def restore_default_prefix(self) -> None:
        """
        Restore the console log prefix to it's default value (which is: '> ')
        """
        self.log_prefix = self.default_log_prefix

    def set_logged_commands_escape_html(self, should_escape: bool) -> None:
        """
        Sets whether commands should have any HTML characters escaped before being added
        to the log. This is because the log uses an HTML Text box and most of the time we don't
        want to assume that every entered > or < is part of an HTML tag.

        By default HTML is escaped for commands added to the log.

        :param should_escape: A bool to switch escaping HTML on commands on or off.
        """
        self.should_logged_commands_escape_html = should_escape

    def add_output_line_to_log(self, text_to_add: str,
                               is_bold: bool = True,
                               remove_line_break: bool = False,
                               escape_html: bool = True) -> None:
        """
        Adds a single line of text to the log text box. This is intended as a hook to add
        output/responses to commands entered into the console.

        :param text_to_add: The single line of text to add to the log.
        :param is_bold: Determines whether the output is shown in bold or not. Defaults to True.
        :param remove_line_break: Set this to True to remove the automatic line break at the end
                                  of the line of text. Sometimes you might want to add some output
                                  all on a single line (e.g. a console style 'progress bar')
        :param escape_html:  Determines whether to escape any HTML in this line of text. Defaults
                             to True, as most people won't be expecting every > or < to be
                             processed as HTML.
        """
        output_to_log = html.escape(text_to_add) if escape_html else text_to_add
        line_ending = '' if remove_line_break else '<br>'
        if is_bold:
            self.log.append_html_text('<b>' + output_to_log + '</b>' + line_ending)
        else:
            self.log.append_html_text(output_to_log + line_ending)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        See if we need to handle an event passed down by the UI manager.
        Returns True if the console window dealt with this event.

        :param event: The event to handle
        """
        handled = super().process_event(event)

        if (self.command_entry.is_focused and
                event.type == pygame.KEYDOWN):
            if event.key == pygame.K_DOWN:
                if len(self.logged_commands_below) > 0:
                    popped_command = self.logged_commands_below.pop()
                    if self.current_logged_command is not None:
                        self.logged_commands_above.append(self.current_logged_command)
                    self.current_logged_command = popped_command
                    self.command_entry.set_text(self.current_logged_command)
            elif event.key == pygame.K_UP:
                if len(self.logged_commands_above) > 0:
                    popped_command = self.logged_commands_above.pop()
                    if self.current_logged_command is not None:
                        self.logged_commands_below.append(self.current_logged_command)
                    self.current_logged_command = popped_command
                    self.command_entry.set_text(self.current_logged_command)

        if event.type == UI_TEXT_ENTRY_FINISHED and event.ui_element == self.command_entry:
            handled = True
            command = self.command_entry.get_text()
            command_for_log = command
            self._restore_command_log_to_end()
            self.logged_commands_above.append(command_for_log)
            if self.should_logged_commands_escape_html:
                command_for_log = html.escape(command_for_log)
            self.log.append_html_text(self.log_prefix + command_for_log + "<br>")
            self.command_entry.set_text("")

            event_data = {'command': command,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            command_entered_event = pygame.event.Event(UI_CONSOLE_COMMAND_ENTERED, event_data)
            pygame.event.post(command_entered_event)

        if event.type == UI_TEXT_ENTRY_CHANGED and event.ui_element == self.command_entry:
            self._restore_command_log_to_end()

        return handled

    def _restore_command_log_to_end(self):
        if self.current_logged_command is not None:
            self.logged_commands_above.append(self.current_logged_command)
        self.current_logged_command = None
        while len(self.logged_commands_below) > 0:
            self.logged_commands_above.append(self.logged_commands_below.pop())

    def clear_log(self):
        """
        Clear the console log, re-starting  with a fresh, empty console with no old commands.
        """
        self.logged_commands_above = []
        self.current_logged_command = None
        self.logged_commands_below = []

        self.log.set_text("")
