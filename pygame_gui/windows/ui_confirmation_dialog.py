import pygame
import pygame_gui
from pygame_gui import ui_manager
from pygame_gui._constants import UI_CONFIRMATION_DIALOG_CONFIRMED
from pygame_gui.elements import UIWindow, UIButton, UITextBox


class UIConfirmationDialog(UIWindow):
    def __init__(self, rect: pygame.Rect,
                 manager: 'ui_manager.UIManager',
                 confirming_action_long_desc: str,
                 window_title: str = 'Confirm',
                 confirming_action_short_name: str = 'OK',
                 blocking: bool = True):
        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id='#confirmation_dialog')

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text=confirming_action_short_name,
                                  manager=self.ui_manager,
                                  container=self.get_container(),
                                  parent_element=self,
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='Cancel',
                                      manager=self.ui_manager,
                                      container=self.get_container(),
                                      parent_element=self,
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        self.confirmation_text = UITextBox(html_text=confirming_action_long_desc,
                                           relative_rect=pygame.Rect(5, 5,
                                                                     self.get_container().relative_rect.width - 10,
                                                                     self.get_container().relative_rect.height - 50),
                                           manager=self.ui_manager,
                                           container=self.get_container(),
                                           parent_element=self,
                                           anchors={'left': 'left',
                                                    'right': 'right',
                                                    'top': 'top',
                                                    'bottom': 'bottom'})

        self.set_blocking(blocking)

    def process_event(self, event: pygame.event.Event) -> bool:
        handled = super().process_event(event)

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.cancel_button):
            self.kill()

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.ok_button):
            event_data = {'user_type': UI_CONFIRMATION_DIALOG_CONFIRMED,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            confirmation_dialog_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(confirmation_dialog_event)
            self.kill()

        return handled
