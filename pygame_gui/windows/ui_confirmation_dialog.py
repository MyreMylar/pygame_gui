import warnings
from typing import Union

import pygame

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_CONFIRMATION_DIALOG_CONFIRMED, UI_BUTTON_PRESSED, OldType
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIWindow, UIButton, UITextBox


class UIConfirmationDialog(UIWindow):
    """
    A confirmation dialog that lets a user choose between continuing on a path they've chosen or
    cancelling. It's good practice to give a very brief description of the action they are
    confirming on the button they click to confirm it i.e. 'Delete' for a file deletion operation
    or, 'Rename' for a file rename operation.

    :param rect: The size and position of the window, includes the menu bar across the top.
    :param manager: The UIManager that manages this UIElement.
    :param action_long_desc: Long-ish description of action. Can make use of HTML to
                             style the text.
    :param window_title: The title of the  window.
    :param action_short_name: Short, one or two word description of action for button.
    :param blocking: Whether this window should block all other mouse interactions with the GUI
                     until it is closed.
    :param object_id: A custom defined ID for fine tuning of theming. Defaults to
                      '#confirmation_dialog'.
    :param visible: Whether the element is visible by default.
    """

    def __init__(self, rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 action_long_desc: str,
                 *,
                 window_title: str = 'pygame-gui.Confirm',
                 action_short_name: str = 'pygame-gui.OK',
                 blocking: bool = True,
                 object_id: Union[ObjectID, str] = ObjectID('#confirmation_dialog', None),
                 visible: int = 1):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        minimum_dimensions = (260, 200)
        if rect.width < minimum_dimensions[0] or rect.height < minimum_dimensions[1]:
            warn_string = ("Initial size: " + str(rect.size) +
                           " is less than minimum dimensions: " + str(minimum_dimensions))
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                      text='pygame-gui.Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        # confirm_button_spacing = self.cancel_button.get_relative_rect().left - 10

        self.confirm_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                       text=action_short_name,
                                       manager=self.ui_manager,
                                       container=self,
                                       object_id='#confirm_button',
                                       anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'bottom',
                                                'bottom': 'bottom',
                                                'left_target': self.cancel_button,
                                                'right_target': self.cancel_button})

        text_width = self.get_container().get_size()[0] - 10
        text_height = self.get_container().get_size()[1] - 50
        self.confirmation_text = UITextBox(html_text=action_long_desc,
                                           relative_rect=pygame.Rect(5, 5,
                                                                     text_width,
                                                                     text_height),
                                           manager=self.ui_manager,
                                           container=self,
                                           anchors={'left': 'left',
                                                    'right': 'right',
                                                    'top': 'top',
                                                    'bottom': 'bottom'})

        self.set_blocking(blocking)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process any events relevant to the confirmation dialog.

        We close the window when the cancel button is pressed, and post a confirmation event
        (UI_CONFIRMATION_DIALOG_CONFIRMED) when the OK button is pressed, and also close the window.

        :param event: a pygame.Event.

        :return: Return True if we 'consumed' this event and don't want to pass it on to the rest
                 of the UI.

        """
        consumed_event = super().process_event(event)

        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.cancel_button:
            self.kill()

        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.confirm_button:
            # old event - to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_CONFIRMATION_DIALOG_CONFIRMED),
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            # new event
            event_data = {'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_CONFIRMATION_DIALOG_CONFIRMED, event_data))
            self.kill()

        return consumed_event
