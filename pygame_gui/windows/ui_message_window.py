import warnings
from typing import Union, Optional, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_BUTTON_PRESSED
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIButton, UITextBox, UIWindow
from pygame_gui.core.gui_type_hints import RectLike


class UIMessageWindow(UIWindow):
    """
    A simple popup window for delivering text-only messages to users.

    :param rect: The size and position of the window, includes the menu bar across the top.
    :param html_message: The message itself. Can make use of HTML (a subset of) to style the text.
    :param manager: The UIManager that manages this UIElement. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param window_title: The title of the  window.
    :param object_id: A custom defined ID for fine-tuning of theming. Defaults to '#message_window'.
    :param visible: Whether the element is visible by default.
    """
    def __init__(self, rect: RectLike,
                 html_message: str,
                 manager: Optional[IUIManagerInterface] = None,
                 *,
                 window_title: str = 'pygame-gui.message_window_title_bar',
                 object_id: Union[ObjectID, str] = ObjectID('#message_window', None),
                 visible: int = 1,
                 html_message_text_kwargs: Optional[Dict[str, str]] = None):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         element_id=['message_window'],
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        minimum_dimensions = (250, 160)
        if self.relative_rect.width < minimum_dimensions[0] or self.relative_rect.height < minimum_dimensions[1]:
            warn_string = ("Initial size: " + str(self.relative_rect.size) +
                           " is less than minimum dimensions: " + str(minimum_dimensions))
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.dismiss_button = None
        self.text_block = None

        button_size = (-1, 24)
        button_spacing = 10
        button_vertical_space = (button_spacing * 2) + button_size[1]

        dismiss_button_rect = pygame.Rect((0, 0), button_size)
        dismiss_button_rect.bottomright = (-button_spacing, -button_spacing)
        self.dismiss_button = UIButton(relative_rect=dismiss_button_rect,
                                       text="pygame-gui.Dismiss",
                                       manager=manager,
                                       container=self,
                                       tool_tip_text="Click to get rid of this message.",
                                       object_id='#dismiss_button',
                                       anchors={"left": "right",
                                                "top": "bottom",
                                                "right": "right",
                                                "bottom": "bottom"}
                                       )

        text_block_rect = pygame.Rect(0, 0,
                                      self.get_container().get_size()[0],
                                      self.get_container().get_size()[1] - button_vertical_space)
        self.text_block = UITextBox(html_message, text_block_rect, manager=manager,
                                    container=self,
                                    anchors={"left": "left",
                                             "top": "top",
                                             "right": "right",
                                             "bottom": "bottom"},
                                    text_kwargs=html_message_text_kwargs)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process any events relevant to the message window. In this case we just close the window
        when the dismiss button is pressed.

        :param event: a pygame.Event.

        :return: Return True if we 'consumed' this event and don't want to pass it on to the rest
                 of the UI.

        """
        consumed_event = super().process_event(event)

        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.dismiss_button:
            self.kill()

        return consumed_event
