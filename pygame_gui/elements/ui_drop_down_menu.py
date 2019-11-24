import pygame
from typing import Union, List

from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIExpandedDropDownState:
    """
    The expanded state of the drop down  displays the currently chosen option, all the available options and a button
    to close the menu and return to the closed state.

    Picking an option will also close the menu.
    """

    def __init__(self, drop_down_menu_ui, options_list, selected_option, base_position_rect,
                 close_button_width, expand_direction, manager, container, element_ids, object_ids):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.should_transition = False
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.selected_option_rect = None
        self.expand_direction = expand_direction
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids
        self.rect_height_offset = 0

        self.close_button_width = close_button_width

        self.selected_option_button = None
        self.close_button = None
        self.drawable_shape = None
        self.menu_buttons = []

        self.should_transition = False
        self.target_state = 'closed'

    def rebuild(self):
        # shape for expanded drop down is a little trick because it is two rectangles, one on top of the other
        # forming an 'L' shape (or an inverted L if dropping down)

        if self.expand_direction == 'down':
            overall_background_rect = pygame.Rect(self.drop_down_menu_ui.rect.topleft,
                                                  (self.drop_down_menu_ui.rect.width + 50,
                                                   self.base_position_rect.height * (1 + len(self.options_list)) +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width))

            options_background_rect = pygame.Rect(self.drop_down_menu_ui.rect.topleft,
                                                  (self.base_position_rect.width - self.close_button_width +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width,
                                                   self.base_position_rect.height * (1 + len(self.options_list)) +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width))
            self.rect_height_offset = 0
            self.selected_option_rect = pygame.Rect((0, 0),
                                                    self.drop_down_menu_ui.rect.size)
        else:
            # need to adjust the position of the rect so it appears in the right position
            self.rect_height_offset = self.base_position_rect.height * len(self.options_list)
            self.drop_down_menu_ui.rect.y = self.drop_down_menu_ui.rect.y - self.rect_height_offset
            self.drop_down_menu_ui.relative_rect.y = self.drop_down_menu_ui.relative_rect.y - self.rect_height_offset

            self.selected_option_rect = pygame.Rect((0, self.rect_height_offset),
                                                    self.drop_down_menu_ui.rect.size)

            overall_background_rect = pygame.Rect(self.drop_down_menu_ui.rect.topleft,
                                                  (self.drop_down_menu_ui.rect.width + 50,
                                                   self.base_position_rect.height * (1 + len(self.options_list)) +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width))

            options_background_rect = pygame.Rect(self.drop_down_menu_ui.rect.topleft,
                                                  (self.base_position_rect.width - self.close_button_width +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width,
                                                   self.base_position_rect.height * (1 + len(self.options_list)) +
                                                   2 * self.drop_down_menu_ui.shadow_width +
                                                   2 * self.drop_down_menu_ui.border_width))

        self.drop_down_menu_ui.image = pygame.Surface(overall_background_rect.size, flags=pygame.SRCALPHA)
        self.drop_down_menu_ui.image.fill(pygame.Color('#00000000'))

        theming_parameters = {'normal_bg': self.drop_down_menu_ui.background_colour,
                              'normal_border': self.drop_down_menu_ui.border_colour,
                              'border_width': self.drop_down_menu_ui.border_width,
                              'shadow_width': self.drop_down_menu_ui.shadow_width,
                              'shape_corner_radius': self.drop_down_menu_ui.shape_corner_radius}

        if self.drop_down_menu_ui.shape_type == 'rectangle':
            drawable_shape = RectDrawableShape(self.selected_option_rect, theming_parameters,
                                               ['normal'], self.ui_manager)

            self.drop_down_menu_ui.image.blit(drawable_shape.get_surface('normal'), self.selected_option_rect.topleft)
            self.drop_down_menu_ui.image.fill(pygame.Color('#00000000'),
                                              pygame.Rect((0, 0),
                                                          (options_background_rect.width -
                                                           self.drop_down_menu_ui.shadow_width -
                                                           self.drop_down_menu_ui.border_width,
                                                           options_background_rect.height)))

            options_drawable_shape = RectDrawableShape(options_background_rect, theming_parameters,
                                                       ['normal'], self.ui_manager)
            self.drop_down_menu_ui.image.blit(options_drawable_shape.get_surface('normal'), (0, 0))
        elif self.drop_down_menu_ui.shape_type == 'rounded_rectangle':
            drawable_shape = RoundedRectangleShape(self.selected_option_rect, theming_parameters,
                                                   ['normal'], self.ui_manager)

            self.drop_down_menu_ui.image.blit(drawable_shape.get_surface('normal'), self.selected_option_rect.topleft)
            self.drop_down_menu_ui.image.fill(pygame.Color('#00000000'),
                                              pygame.Rect((0, 0),
                                                          (options_background_rect.width -
                                                           self.drop_down_menu_ui.shadow_width -
                                                           self.drop_down_menu_ui.border_width,
                                                           options_background_rect.height)))

            options_drawable_shape = RoundedRectangleShape(options_background_rect, theming_parameters,
                                                           ['normal'], self.ui_manager)
            self.drop_down_menu_ui.image.blit(options_drawable_shape.get_surface('normal'), (0, 0))

        # extra
        if self.close_button is not None:
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.close_button.set_text(expand_button_symbol)

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

        expand_button_symbol = '▼'
        select_button_dist_to_move = self.selected_option_button.rect.height
        option_button_dist_to_move = self.base_position_rect.height

        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                expand_button_symbol = '▲'
                select_button_dist_to_move = -self.selected_option_button.rect.height
                option_button_dist_to_move = -self.base_position_rect.height
            elif self.expand_direction == 'down':
                expand_button_symbol = '▼'
                select_button_dist_to_move = self.selected_option_button.rect.height
                option_button_dist_to_move = self.base_position_rect.height

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width

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

        self.rebuild()

    def finish(self):
        """
        cleans everything up upon exiting the expanded menu state.
        """
        for button in self.menu_buttons:
            button.kill()

        self.menu_buttons.clear()

        self.selected_option_button.kill()
        self.close_button.kill()

        self.drop_down_menu_ui.rect.y += self.rect_height_offset
        self.drop_down_menu_ui.relative_rect.y += self.rect_height_offset

    def update(self):
        if self.close_button is not None and self.close_button.check_pressed():
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
                 open_button_width, expand_direction, manager, container, element_ids, object_ids):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.selected_option_button = None
        self.open_button = None
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.expand_direction = expand_direction
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids

        self.shape_type = None
        self.drawable_shape = None

        self.open_button_width = open_button_width

        self.should_transition = False
        self.target_state = 'expanded'

    def rebuild(self):
        theming_parameters = {'normal_bg': self.drop_down_menu_ui.background_colour,
                              'normal_border': self.drop_down_menu_ui.border_colour,
                              'border_width': self.drop_down_menu_ui.border_width,
                              'shadow_width': self.drop_down_menu_ui.shadow_width,
                              'shape_corner_radius': self.drop_down_menu_ui.shape_corner_radius}

        if self.drop_down_menu_ui.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.drop_down_menu_ui.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.drop_down_menu_ui.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.drop_down_menu_ui.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.drop_down_menu_ui.image = self.drawable_shape.get_surface('normal')

        # extra
        if self.open_button is not None:
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.open_button.set_text(expand_button_symbol)

    def start(self):
        """
        Called each time we enter the closed state. It creates the necessary elements, the selected option and the
        open button.
        """
        self.rebuild()

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

        expand_button_symbol = '▼'
        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                expand_button_symbol = '▲'
            elif self.expand_direction == 'down':
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

        self.border_width = None
        self.shadow_width = None
        self.background_colour = None
        self.border_colour = None
        self.shape_type = "rectangle"
        self.shape_corner_radius = 2

        self.current_state = None
        self.border_rect = None
        self.background_rect = None
        self.relative_background_rect = None

        self.expand_direction = None

        self.menu_states = {}

        self.rebuild_from_changed_theme_data()

        self.menu_states = {'closed': UIClosedDropDownState(self,
                                                            self.selected_option,
                                                            self.background_rect,
                                                            self.open_button_width,
                                                            self.expand_direction,
                                                            self.ui_manager,
                                                            self.ui_container,
                                                            self.element_ids,
                                                            self.object_ids),
                            'expanded': UIExpandedDropDownState(self,
                                                                self.options_list,
                                                                self.selected_option,
                                                                self.background_rect,
                                                                self.open_button_width,
                                                                self.expand_direction,
                                                                self.ui_manager,
                                                                self.ui_container,
                                                                self.element_ids,
                                                                self.object_ids
                                                                )}
        self.current_state = self.menu_states['closed']
        self.current_state.start()

    def kill(self):
        """
        Overrides the standard sprite kill to also properly kill/finish the current state of the drop down.
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

    def rebuild_from_changed_theme_data(self):
        has_any_changed = False

        expand_direction_string = self.ui_manager.get_theme().get_misc_data(self.object_ids,
                                                                            self.element_ids, 'expand_direction')
        expand_direction = 'down'
        if expand_direction_string is not None:
            if expand_direction_string in ['up', 'down']:
                expand_direction = expand_direction_string

        if expand_direction != self.expand_direction:
            self.expand_direction = expand_direction
            has_any_changed = True

        shape_type = 'rectangle'
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if shape_type_string is not None:
            if shape_type_string in ['rectangle', 'rounded_rectangle']:
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
            self.border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                           (self.rect.width - (2 * self.shadow_width),
                                            self.rect.height - (2 * self.shadow_width)))

            self.relative_background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                         self.border_width + self.shadow_width),
                                                        (self.border_rect.width - (2 * self.border_width),
                                                         self.border_rect.height - (2 * self.border_width)))

            self.background_rect = pygame.Rect((self.relative_background_rect.x + self.relative_rect.x,
                                                self.relative_background_rect.y + self.relative_rect.y),
                                               self.relative_background_rect.size)

            for state in self.menu_states:
                self.menu_states[state].expand_direction = self.expand_direction

            if self.current_state is not None:

                self.current_state.rebuild()
