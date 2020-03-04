import pygame
import pygame_gui

from pygame_gui import ui_manager
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_window import UIWindow


class UIMessageWindow(UIWindow):
    """
    A simple popup window for delivering text-only messages to users.

    :param rect: The size and position of the window, includes the menu bar across the top.
    :param html_message: The message itself. Can make use of HTML (a subset of) to style the text.
    :param manager: The UIManager that manages this UIElement.
    :param window_title: The title of the  window.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, rect: pygame.Rect,
                 html_message: str,
                 manager: ui_manager.UIManager,
                 *,
                 window_title: str = 'Message',
                 object_id: str = '#message_window'):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id)

        self.set_minimum_dimensions((250, 250))

        self.dismiss_button = None
        self.text_block = None

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

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process any events relevant to the message window. In this case we just close the window when the dismiss
        button is pressed.

        :param event: a pygame.Event.
        :return: Return True if we 'consumed' this event and don't want to pass it on to the rest of the UI.
        """
        consumed_event = super().process_event(event)

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.dismiss_button):
            self.kill()

        return consumed_event
