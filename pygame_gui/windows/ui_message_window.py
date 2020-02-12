import pygame
from typing import Union

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core.ui_window import UIWindow
from pygame_gui import ui_manager
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


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
        super().__init__(message_window_rect, manager, new_element_ids, new_object_ids, resizable=True)

        self.grabbed_window = False
        self.starting_grab_difference = (0, 0)
        self.set_minimum_dimensions((250, 250))

        # Themed parameters
        self.shadow_width = None  # type: Union[None, int]
        self.border_width = None  # type: Union[None, int]
        self.background_colour = None
        self.border_colour = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        # UI elements
        self.menu_bar = None
        self.close_window_button = None
        self.dismiss_button = None
        self.text_block = None

        self.rebuild_from_changed_theme_data()

        menu_bar_height = 20
        close_button_width = 20
        self.menu_bar = UIButton(relative_rect=pygame.Rect((0, 0),
                                                           ((self.relative_rect.width -
                                                            (self.shadow_width * 2)) - close_button_width,
                                                            menu_bar_height)),
                                 text=message_title,
                                 manager=manager,
                                 container=self.get_container(),
                                 parent_element=self,
                                 object_id='#message_window_title_bar',
                                 anchors={'top': 'top', 'bottom': 'top',
                                          'left': 'left', 'right': 'right'}
                                 )
        self.menu_bar.set_hold_range((100, 100))

        self.close_window_button = UIButton(relative_rect=pygame.Rect((-close_button_width, 0),
                                                                      (close_button_width, menu_bar_height)),
                                            text='╳',
                                            manager=manager,
                                            container=self.get_container(),
                                            parent_element=self,
                                            object_id='#close_button',
                                            anchors={'top': 'top', 'bottom': 'top',
                                                     'left': 'right', 'right': 'right'}
                                            )

        button_size = (70, 20)
        bottom_right_margin = (20, 20)
        button_vertical_space = bottom_right_margin[1] + button_size[1]
        self.dismiss_button = UIButton(relative_rect=pygame.Rect((-bottom_right_margin[0] - button_size[0],
                                                                  -bottom_right_margin[1] - button_size[1]),
                                                                 button_size),
                                       text="Dismiss",
                                       manager=manager,
                                       container=self.get_container(),
                                       tool_tip_text="<font face=fira_code color=normal_text size=2>"
                                                     "Click to get rid of this message.</font>",
                                       parent_element=self,
                                       object_id='#dismiss_button',
                                       anchors={"left": "right",
                                                "top": "bottom",
                                                "right": "right",
                                                "bottom": "bottom"}
                                       )

        border_rect_width = self.relative_rect.width - (self.shadow_width * 2)
        border_rect_height = self.relative_rect.height - (self.shadow_width * 2)

        text_block_rect = pygame.Rect((self.border_width, menu_bar_height),
                                      (border_rect_width - self.border_width,
                                       (border_rect_height - menu_bar_height -
                                        button_vertical_space)))
        self.text_block = UITextBox(html_message, text_block_rect, manager=manager,
                                    container=self.get_container(),
                                    parent_element=self,
                                    anchors={"left": "left",
                                             "top": "top",
                                             "right": "right",
                                             "bottom": "bottom"}
                                    )

    def rebuild(self):
        """
        Rebuilds the message window when the theme has changed.

        """
        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.image = self.drawable_shape.get_surface('normal')

        self.container_margins['left'] = self.shadow_width
        self.container_margins['right'] = self.shadow_width
        self.container_margins['top'] = self.shadow_width
        self.container_margins['bottom'] = self.shadow_width

        self.set_dimensions(self.relative_rect.size)

    def update(self, time_delta: float):
        """
        Called every update loop of our UI manager. Handles moving and closing the window.

        :param time_delta: The time in seconds between calls to this function.
        """
        super().update(time_delta)

        if self.alive():

            if self.dismiss_button.check_pressed():
                self.kill()

            if self.menu_bar.held:
                mouse_x, mouse_y = self.ui_manager.get_mouse_position()
                if not self.grabbed_window:
                    self.window_stack.move_window_to_front(self)
                    self.grabbed_window = True
                    self.starting_grab_difference = (mouse_x - self.rect.x,
                                                     mouse_y - self.rect.y)

                current_grab_difference = (mouse_x - self.rect.x,
                                           mouse_y - self.rect.y)

                adjustment_required = (current_grab_difference[0] - self.starting_grab_difference[0],
                                       current_grab_difference[1] - self.starting_grab_difference[1])

                self.set_relative_position((self.relative_rect.x + adjustment_required[0],
                                            self.relative_rect.y + adjustment_required[1]))
            else:
                self.grabbed_window = False

            if self.close_window_button.check_pressed():
                self.kill()

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for this element when
        the theme data has changed.
        """
        has_any_changed = False

        shape_type = 'rectangle'
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if shape_type_string is not None and shape_type_string in ['rectangle', 'rounded_rectangle']:
            shape_type = shape_type_string
        if shape_type != self.shape_type:
            self.shape_type = shape_type
            has_any_changed = True

        corner_radius = 2
        shape_corner_radius_string = self.ui_theme.get_misc_data(self.object_ids,
                                                                 self.element_ids, 'shape_corner_radius')
        if shape_corner_radius_string is not None:
            try:
                corner_radius = int(shape_corner_radius_string)
            except ValueError:
                corner_radius = 2
        if corner_radius != self.shape_corner_radius:
            self.shape_corner_radius = corner_radius
            has_any_changed = True

        border_width = 1
        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            try:
                border_width = int(border_width_string)
            except ValueError:
                border_width = 1

        if border_width != self.border_width:
            self.border_width = border_width
            has_any_changed = True

        shadow_width = 2
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            try:
                shadow_width = int(shadow_width_string)
            except ValueError:
                shadow_width = 2
        if shadow_width != self.shadow_width:
            self.shadow_width = shadow_width
            has_any_changed = True

        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
