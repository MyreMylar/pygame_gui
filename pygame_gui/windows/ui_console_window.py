import html
from typing import Union

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIWindow, UITextBox, UITextEntryLine
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_CONSOLE_COMMAND_ENTERED


class UIConsoleWindow(UIWindow):

    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'Console',
                 object_id: Union[ObjectID, str] = ObjectID('#console_window', None),
                 visible: int = 1
                 ):
        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        self.default_log_prefix = '> '
        self.log_prefix = self.default_log_prefix

        self.should_commands_escape_html = True

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

    def set_log_prefix(self, prefix: str):
        self.log_prefix = prefix

    def restore_default_prefix(self):
        self.log_prefix = self.default_log_prefix

    def set_commands_escape_html(self, should_escape: bool):
        self.should_commands_escape_html = should_escape

    def add_output_line_to_log(self, output: str,
                               is_bold: bool = True,
                               remove_line_break: bool = False,
                               escape_html: bool = True):

        output_to_log = html.escape(output) if escape_html else output
        line_ending = '' if remove_line_break else '<br>'
        if is_bold:
            self.log.append_html_text('<b>' + output_to_log + '</b>' + line_ending)
        else:
            self.log.append_html_text(output_to_log + line_ending)

    def process_event(self, event: pygame.event.Event) -> bool:
        handled = super().process_event(event)

        if (event.type == pygame.USEREVENT and
                event.user_type == UI_TEXT_ENTRY_FINISHED and
                event.ui_element == self.command_entry):
            handled = True
            command = self.command_entry.get_text()
            command_for_log = command
            if self.should_commands_escape_html:
                command_for_log = html.escape(command_for_log)
            self.log.append_html_text(self.log_prefix + command_for_log + "<br>")
            self.command_entry.set_text("")
            self.command_entry.cursor_has_moved_recently = True

            event_data = {'user_type': UI_CONSOLE_COMMAND_ENTERED,
                          'command': command,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            command_entered_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(command_entered_event)

        return handled
