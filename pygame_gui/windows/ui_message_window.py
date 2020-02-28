import pygame
from typing import Union

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui import ui_manager


class UIMessageWindow(UIWindow):
    """
    A simple popup window for delivering text-only messages to users.

    :param message_window_rect: The size and position of the window, includes the menu bar across the top.
    :param message_title: The title of the message window.
    :param html_message: The message itself. Can make use of HTML (a subset of) to style the text.
    :param manager: The UIManager that manages this UIElement.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, message_window_rect: pygame.Rect,
                 message_title: str,
                 html_message: str,
                 manager: ui_manager.UIManager,
                 object_id: Union[str, None] = None):

        super().__init__(message_window_rect, manager,
                         window_display_title=message_title,
                         element_id='message_window',
                         object_id=object_id,
                         resizable=True)

        self.set_minimum_dimensions((250, 250))

        self.dismiss_button = None
        self.text_block = None

        # self.rebuild_from_changed_theme_data()

        button_size = (70, 20)
        bottom_right_margin = (20, 20)
        button_vertical_space = bottom_right_margin[1] + button_size[1]
        self.dismiss_button = UIButton(relative_rect=pygame.Rect((-bottom_right_margin[0] - button_size[0],
                                                                  -bottom_right_margin[1] - button_size[1]),
                                                                 button_size),
                                       text="Dismiss",
                                       manager=manager,
                                       container=self,
                                       tool_tip_text="<font face=fira_code color=normal_text size=2>"
                                                     "Click to get rid of this message.</font>",
                                       object_id='#dismiss_button',
                                       anchors={"left": "right",
                                                "top": "bottom",
                                                "right": "right",
                                                "bottom": "bottom"}
                                       )

        text_block_rect = pygame.Rect(0, 0,
                                      self.get_container().rect.width,
                                      self.get_container().rect.height - button_vertical_space)
        self.text_block = UITextBox(html_message, text_block_rect, manager=manager,
                                    container=self,
                                    anchors={"left": "left",
                                             "top": "top",
                                             "right": "right",
                                             "bottom": "bottom"}
                                    )

    def update(self, time_delta: float):
        """
        Called every update loop of our UI manager. Handles moving and closing the window.

        :param time_delta: The time in seconds between calls to this function.
        """
        super().update(time_delta)

        if self.alive() and self.dismiss_button.check_pressed():
            self.kill()
