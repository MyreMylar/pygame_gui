import pygame
from typing import Union

from ..elements.ui_button import UIButton
from ..elements.ui_text_box import UITextBox
from ..core.ui_window import UIWindow
from .. import ui_manager


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

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=None,
                                                                object_id=object_id,
                                                                element_id='message_window')
        super().__init__(message_window_rect, manager, new_element_ids, new_object_ids)

        self.bg_colour = self.ui_manager.get_theme().get_colour(self.object_ids, self.element_ids, 'dark_bg')
        self.border_colour = self.ui_manager.get_theme().get_colour(self.object_ids, self.element_ids, 'normal_border')

        self.border_width = 1
        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            self.border_width = int(border_width_string)

        self.shadow_width = 1
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            self.shadow_width = int(shadow_width_string)

        border_rect_width = self.rect.width - (self.shadow_width * 2)
        border_rect_height = self.rect.height - (self.shadow_width * 2)
        self.border_rect = pygame.Rect((self.shadow_width,
                                        self.shadow_width),
                                       (border_rect_width, border_rect_height))

        background_rect_width = border_rect_width - (self.border_width * 2)
        background_rect_height = border_rect_height - (self.border_width * 2)
        self.background_rect = pygame.Rect((self.shadow_width + self.border_width,
                                            self.shadow_width + self.border_width),
                                           (background_rect_width, background_rect_height))

        if self.shadow_width > 0:
            self.image = self.ui_manager.get_shadow(self.rect.size, self.shadow_width)
        else:
            self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        self.image.fill(self.border_colour, self.border_rect)
        self.image.fill(self.bg_colour, self.background_rect)

        self.get_container().relative_rect.width = self.rect.width - self.shadow_width * 2
        self.get_container().relative_rect.height = self.rect.height - self.shadow_width * 2
        self.get_container().relative_rect.x = self.get_container().relative_rect.x + self.shadow_width
        self.get_container().relative_rect.y = self.get_container().relative_rect.y + self.shadow_width
        self.get_container().update_containing_rect_position()

        menu_bar_height = 20
        close_button_width = 20
        self.menu_bar = UIButton(relative_rect=pygame.Rect((0, 0),
                                                           ((self.rect.width -
                                                             (self.shadow_width * 2)) - close_button_width,
                                                            menu_bar_height)),
                                 text=message_title,
                                 manager=manager,
                                 container=self.get_container(),
                                 parent_element=self,
                                 object_id='#message_window_title_bar'
                                 )
        self.menu_bar.set_hold_range((100, 100))

        self.grabbed_window = False
        self.starting_grab_difference = (0, 0)

        self.close_window_button = UIButton(relative_rect=pygame.Rect(((self.rect.width - self.shadow_width * 2) -
                                                                       close_button_width,
                                                                       0),
                                                                      (close_button_width, menu_bar_height)),
                                            text='╳',
                                            manager=manager,
                                            container=self.get_container(),
                                            parent_element=self,
                                            object_id='#close_button'
                                            )
        done_button_vertical_start = 30
        done_button_vertical_space = 40
        self.dismiss_button = UIButton(relative_rect=pygame.Rect(((self.rect.width / 2) + 45,
                                                                  (border_rect_height -
                                                                  done_button_vertical_start)),
                                                                 (70, 20)),
                                       text="Dismiss",
                                       manager=manager,
                                       container=self.get_container(),
                                       tool_tip_text="<font face=fira_code color=normal_text size=2>"
                                                     "Click to get rid of this message.</font>",
                                       parent_element=self,
                                       object_id='#dismiss_button'
                                       )

        text_block_rect = pygame.Rect((self.border_width, menu_bar_height),
                                      (self.border_rect.width - self.border_width,
                                       (border_rect_height - menu_bar_height -
                                        done_button_vertical_space)))
        self.text_block = UITextBox(html_message, text_block_rect, manager=manager,
                                    container=self.get_container(),
                                    parent_element=self)

    def update(self, time_delta: float):
        """
        Called every update loop of our UI manager. Handles moving and closing the window.

        :param time_delta: The time in seconds between calls to this function.
        """
        if self.alive():

            if self.dismiss_button.check_pressed():
                self.kill()

            if self.menu_bar.held:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if not self.grabbed_window:
                    self.window_stack.move_window_to_front(self)
                    self.grabbed_window = True
                    self.starting_grab_difference = (mouse_x - self.rect.x,
                                                     mouse_y - self.rect.y)

                current_grab_difference = (mouse_x - self.rect.x,
                                           mouse_y - self.rect.y)

                adjustment_required = (current_grab_difference[0] - self.starting_grab_difference[0],
                                       current_grab_difference[1] - self.starting_grab_difference[1])

                self.rect.x += adjustment_required[0]
                self.rect.y += adjustment_required[1]
                self.get_container().relative_rect.x += adjustment_required[0]
                self.get_container().relative_rect.y += adjustment_required[1]
                self.get_container().update_containing_rect_position()

            else:
                self.grabbed_window = False

            if self.close_window_button.check_pressed():
                self.kill()

        super().update(time_delta)
