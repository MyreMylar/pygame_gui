import pygame
from typing import Union, List

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement
from ..elements.ui_button import UIButton


class UIExpandedDropDownState:
    """
    The expanded state of the drop down  displays the currently chosen option, all the available options and a button
    to close the menu and return to the closed state.

    Picking an option will also close the menu.
    """
    def __init__(self, drop_down_menu_ui, options_list, selected_option, base_position_rect,
                 close_button_width, manager, container, element_ids, object_ids):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.should_transition = False
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids

        self.close_button_width = close_button_width

        self.selected_option_button = None
        self.close_button = None
        self.menu_buttons = []

        self.should_transition = False
        self.target_state = 'closed'

    def start(self):
        """
        Called each time we enter the expanded state. It creates the necessary elements, the selected option, all the
        other available options and the close button.
        """
        self.should_transition = False
        option_y_pos = self.base_position_rect.y
        self.selected_option_button = UIButton(pygame.Rect(self.base_position_rect.topleft,
                                                           (self.base_position_rect.width - self.close_button_width,
                                                            self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               parent_element=self.drop_down_menu_ui,
                                               object_id='#selected_option')

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width

        expand_direction = self.ui_manager.get_theme().get_misc_data(self.object_ids,
                                                                     self.element_ids, 'expand_direction')
        expand_button_symbol = '▼'
        select_button_dist_to_move = self.selected_option_button.rect.height
        option_button_dist_to_move = self.base_position_rect.height

        if expand_direction is not None:
            if expand_direction == 'up':
                expand_button_symbol = '▲'
                select_button_dist_to_move = -self.selected_option_button.rect.height
                option_button_dist_to_move = -self.base_position_rect.height
            elif expand_direction == 'down':
                expand_button_symbol = '▼'
                select_button_dist_to_move = self.selected_option_button.rect.height
                option_button_dist_to_move = self.base_position_rect.height

        self.close_button = UIButton(pygame.Rect((close_button_x, self.base_position_rect.y),
                                                 (self.close_button_width, self.base_position_rect.height)),
                                     expand_button_symbol,
                                     self.ui_manager,
                                     self.ui_container,
                                     starting_height=2,
                                     parent_element=self.drop_down_menu_ui,
                                     object_id='#expand_button')

        option_y_pos += select_button_dist_to_move
        for option in self.options_list:
            new_button = UIButton(pygame.Rect((self.base_position_rect.x, option_y_pos),
                                              (self.base_position_rect.width - self.close_button_width,
                                  self.base_position_rect.height)),
                                  option,
                                  self.ui_manager,
                                  self.ui_container,
                                  starting_height=3,  # height allows options to overlap other UI elements
                                  parent_element=self.drop_down_menu_ui,
                                  object_id='#option')
            option_y_pos += option_button_dist_to_move
            self.menu_buttons.append(new_button)

    def finish(self):
        """
        cleans everything up upon exiting the expanded menu state.
        """
        for button in self.menu_buttons:
            button.kill()

        self.menu_buttons.clear()

        self.selected_option_button.kill()
        self.close_button.kill()

    def update(self):
        if self.close_button.check_pressed():
            self.should_transition = True

        for button in self.menu_buttons:
            if button.check_pressed():
                self.drop_down_menu_ui.selected_option = button.text
                self.should_transition = True

                drop_down_changed_event = pygame.event.Event(pygame.USEREVENT,
                                                             {'user_type': 'ui_drop_down_menu_changed',
                                                              'text': button.text,
                                                              'ui_element': self.drop_down_menu_ui,
                                                              'ui_object_id': self.object_ids[-1]})
                pygame.event.post(drop_down_changed_event)


class UIClosedDropDownState:
    """
    The closed state of the drop down just displays the currently chosen option and a button that will switch the menu
    to the expanded state.
    """
    def __init__(self, drop_down_menu_ui, selected_option, base_position_rect,
                 open_button_width, manager, container, element_ids, object_ids):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.selected_option_button = None
        self.open_button = None
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids

        self.open_button_width = open_button_width

        self.should_transition = False
        self.target_state = 'expanded'

    def start(self):
        """
        Called each time we enter the closed state. It creates the necessary elements, the selected option and the
        open button.
        """
        self.should_transition = False
        self.selected_option_button = UIButton(pygame.Rect((self.base_position_rect.x,
                                                            self.base_position_rect.y),
                                                           (self.base_position_rect.width - self.open_button_width,
                                               self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               parent_element=self.drop_down_menu_ui,
                                               object_id='#selected_option')
        open_button_x = self.base_position_rect.x + self.base_position_rect.width - self.open_button_width

        expand_direction = self.ui_manager.get_theme().get_misc_data(self.object_ids,
                                                                     self.element_ids, 'expand_direction')
        expand_button_symbol = '▼'
        if expand_direction is not None:
            if expand_direction == 'up':
                expand_button_symbol = '▲'
            elif expand_direction == 'down':
                expand_button_symbol = '▼'

        self.open_button = UIButton(pygame.Rect((open_button_x,
                                                 self.base_position_rect.y),
                                                (self.open_button_width, self.base_position_rect.height)),
                                    expand_button_symbol,
                                    self.ui_manager,
                                    self.ui_container,
                                    starting_height=2,
                                    parent_element=self.drop_down_menu_ui,
                                    object_id='#expand_button')

    def finish(self):
        """
        Called when we leave the closed state. Kills the open button and the selected option button.
        """
        self.selected_option_button.kill()
        self.open_button.kill()

    def update(self):
        if self.open_button.check_pressed():
            self.should_transition = True


class UIDropDownMenu(UIElement):
    """
    A drop down menu lets us choose one text option from a list. That list of options can be expanded and hidden
    at the press of a button. While the element is called a drop down, it can also be made to 'climb up' by changing
    the 'expand_direction' styling option to 'up' in the theme file.

    The drop down is implemented through two states, one representing the 'closed' menu state and one for when it has
    been 'expanded'.


    :param options_list: The list of of options to choose from. They must be strings.
    :param starting_option: The starting option, selected when the menu is first created.
    :param relative_rect: The size and position of the element when not expanded.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, options_list: List[str],
                 starting_option: str,
                 relative_rect: pygame.Rect,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None
                 ):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='drop_down_menu')
        super().__init__(relative_rect, manager, container,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids,
                         layer_thickness=1, starting_height=1)
        self.options_list = options_list
        self.selected_option = starting_option
        self.open_button_width = 20

        self.border_width = 0
        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            self.border_width = int(border_width_string)

        self.shadow_width = 0
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            self.shadow_width = int(shadow_width_string)

        self.background_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'dark_bg')
        self.border_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'border')

        if self.shadow_width > 0:
            self.image = self.ui_manager.get_shadow(self.rect.size)
        else:
            self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                  (self.rect.width - (2 * self.shadow_width),
                                   self.rect.height - (2 * self.shadow_width)))
        if self.border_width > 0:
            self.image.fill(self.border_colour,
                            border_rect)

        relative_background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                self.border_width + self.shadow_width),
                                               (border_rect.width - (2 * self.border_width),
                                                border_rect.height - (2 * self.border_width)))

        background_rect = pygame.Rect((relative_background_rect.x + relative_rect.x,
                                       relative_background_rect.y + relative_rect.y),
                                      relative_background_rect.size)
        self.image.fill(self.background_colour,
                        relative_background_rect)

        self.menu_states = {'closed': UIClosedDropDownState(self,
                                                            self.selected_option,
                                                            background_rect,
                                                            self.open_button_width,
                                                            self.ui_manager,
                                                            self.ui_container,
                                                            self.element_ids,
                                                            self.object_ids),
                            'expanded': UIExpandedDropDownState(self,
                                                                self.options_list,
                                                                self.selected_option,
                                                                background_rect,
                                                                self.open_button_width,
                                                                self.ui_manager,
                                                                self.ui_container,
                                                                self.element_ids,
                                                                self.object_ids
                                                                )}
        self.current_state = self.menu_states['closed']
        self.current_state.start()

    def kill(self):
        """
        Overrides the standard sprite kill to also properly kill/finish the current state of the dropdown.
        Depending on whether it is expanded or closed the drop down menu will have different elements to clean up.
        """
        self.current_state.finish()
        super().kill()

    def update(self, time_delta: float):
        """
        The update here deals with transitioning between the two states of the drop down menu and then passes the
        rest of the work onto whichever state is active.

        :param time_delta: The time in second between calls to update.
        """
        if self.alive():
            if self.current_state.should_transition:
                self.current_state.finish()
                self.current_state = self.menu_states[self.current_state.target_state]
                self.current_state.selected_option = self.selected_option
                self.current_state.start()

            self.current_state.update()
