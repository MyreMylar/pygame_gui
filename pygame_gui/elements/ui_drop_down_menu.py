import pygame
from typing import Union, List, Tuple, Dict

import pygame_gui
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.container_interface import IContainerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList
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
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect

        self.expand_direction = expand_direction
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids

        # sizing variables
        self.options_list_height = 0
        self.option_list_y_pos = 0
        self.close_button_width = close_button_width

        # UI elements
        self.selected_option_button = None
        self.close_button = None
        self.options_selection_list = None

        # state transitioning
        self.should_transition = False
        self.target_state = 'closed'

    def rebuild(self):

        theming_parameters = {'normal_bg': self.drop_down_menu_ui.background_colour,
                              'normal_border': self.drop_down_menu_ui.border_colour,
                              'border_width': self.drop_down_menu_ui.border_width,
                              'shadow_width': self.drop_down_menu_ui.shadow_width,
                              'shape_corner_radius': self.drop_down_menu_ui.shape_corner_radius}

        if self.drop_down_menu_ui.shape_type == 'rectangle':
            self.drop_down_menu_ui.drawable_shape = RectDrawableShape(self.drop_down_menu_ui.relative_rect,
                                                                      theming_parameters,
                                                                      ['normal'], self.ui_manager)

        elif self.drop_down_menu_ui.shape_type == 'rounded_rectangle':
            self.drop_down_menu_ui.drawable_shape = RoundedRectangleShape(self.drop_down_menu_ui.relative_rect,
                                                                          theming_parameters,
                                                                          ['normal'], self.ui_manager)

        self.on_fresh_drawable_shape_ready()

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

        options_list_object_id = '#drop_down_options_list'
        options_list_object_ids = self.drop_down_menu_ui.object_ids[:]
        options_list_object_ids.append(options_list_object_id)
        options_list_element_ids = self.drop_down_menu_ui.element_ids[:]
        options_list_element_ids.append('selection_list')
        options_list_shadow_width_str = self.ui_manager.get_theme().get_misc_data(options_list_object_ids,
                                                                                  options_list_element_ids,
                                                                                  'shadow_width')
        options_list_border_width_str = self.ui_manager.get_theme().get_misc_data(options_list_object_ids,
                                                                                  options_list_element_ids,
                                                                                  'border_width')
        if options_list_shadow_width_str is not None:
            try:
                options_list_shadow_width = int(options_list_shadow_width_str)
            except ValueError:
                options_list_shadow_width = 2
        else:
            options_list_shadow_width = 2

        if options_list_border_width_str is not None:
            try:
                options_list_border_width = int(options_list_border_width_str)
            except ValueError:
                options_list_border_width = 1
        else:
            options_list_border_width = 1

        options_list_border_and_shadow = options_list_shadow_width + options_list_border_width
        self.options_list_height = (20 * len(self.options_list)) + (2 * options_list_border_and_shadow)
        self.option_list_y_pos = 0
        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                expand_button_symbol = '▲'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    self.drop_down_menu_ui.expansion_height_limit = self.base_position_rect.top

                self.options_list_height = min(self.options_list_height, self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.top - self.options_list_height

            elif self.expand_direction == 'down':
                expand_button_symbol = '▼'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    self.drop_down_menu_ui.expansion_height_limit = (self.drop_down_menu_ui.ui_container.relative_rect.height -
                                                                     self.base_position_rect.bottom)

                self.options_list_height = min(self.options_list_height, self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.bottom

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width

        self.close_button = UIButton(pygame.Rect((close_button_x, self.base_position_rect.y),
                                                 (self.close_button_width, self.base_position_rect.height)),
                                     expand_button_symbol,
                                     self.ui_manager,
                                     self.ui_container,
                                     starting_height=2,
                                     parent_element=self.drop_down_menu_ui,
                                     object_id='#expand_button')

        self.options_selection_list = UISelectionList(pygame.Rect(self.drop_down_menu_ui.relative_rect.left,
                                                                  self.option_list_y_pos,
                                                                  (self.drop_down_menu_ui.relative_rect.width -
                                                                   self.close_button_width),
                                                                  self.options_list_height),
                                                      item_list=self.options_list,
                                                      allow_doubleclicks=False,
                                                      manager=self.ui_manager,
                                                      parent_element=self.drop_down_menu_ui,
                                                      container=self.ui_container,
                                                      object_id='#drop_down_options_list')

        self.rebuild()

    def finish(self):
        """
        cleans everything up upon exiting the expanded menu state.
        """
        self.options_selection_list.kill()
        self.selected_option_button.kill()
        self.close_button.kill()

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element in [self.close_button, self.selected_option_button]):

            self.should_transition = True

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and
                event.ui_element == self.options_selection_list):
            self.drop_down_menu_ui.selected_option = self.options_selection_list.get_single_selection()
            self.should_transition = True

            event_data = {'user_type': pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
                          'text': self.drop_down_menu_ui.selected_option,
                          'ui_element': self.drop_down_menu_ui,
                          'ui_object_id': self.drop_down_menu_ui.most_specific_combined_id}
            drop_down_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(drop_down_changed_event)

        return consumed_event

    def update_position(self):
        """
        Update the position of all the button elements in the open drop down state.

        Used when the position of the  drop down has been altered directly, rather than when it has been moved as a
        consequence of it's container being moved.
        """

        # update the base position rect
        border_and_shadow = self.drop_down_menu_ui.shadow_width + self.drop_down_menu_ui.border_width
        self.base_position_rect.x = self.drop_down_menu_ui.relative_rect.x + border_and_shadow
        self.base_position_rect.y = self.drop_down_menu_ui.relative_rect.y + border_and_shadow

        # update all the ui elements that depend on the base position
        self.selected_option_button.set_relative_position(self.base_position_rect.topleft)
        self.options_selection_list.set_relative_position((self.drop_down_menu_ui.relative_rect.left,
                                                           self.option_list_y_pos))

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width
        self.close_button.set_relative_position([close_button_x, self.base_position_rect.y])

    def update_dimensions(self):
        """
        Update the dimensions of all the button elements in the closed drop down state.

        Used when the dimensions of the drop down have been altered.
        """

        # update the base position rect
        border_and_shadow = self.drop_down_menu_ui.shadow_width + self.drop_down_menu_ui.border_width
        self.base_position_rect.width = self.drop_down_menu_ui.relative_rect.width - (2 * border_and_shadow)
        self.base_position_rect.height = self.drop_down_menu_ui.relative_rect.height - (2 * border_and_shadow)

        # update all the ui elements that depend on the base position rect
        self.selected_option_button.set_dimensions((self.base_position_rect.width - self.close_button_width,
                                                    self.base_position_rect.height))

        self.options_selection_list.set_dimensions(((self.drop_down_menu_ui.relative_rect.width -
                                                     self.close_button_width),
                                                    self.options_list_height))
        self.options_selection_list.set_relative_position((self.drop_down_menu_ui.relative_rect.left,
                                                           self.option_list_y_pos))

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width
        self.close_button.set_dimensions((self.close_button_width, self.base_position_rect.height))
        self.close_button.set_relative_position((close_button_x, self.base_position_rect.y))

        self.rebuild()

    def on_fresh_drawable_shape_ready(self):
        self.drop_down_menu_ui.set_image(self.drop_down_menu_ui.drawable_shape.get_surface('normal'))


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
            self.drop_down_menu_ui.drawable_shape = RectDrawableShape(self.drop_down_menu_ui.rect, theming_parameters,
                                                                      ['normal'], self.ui_manager)
        elif self.drop_down_menu_ui.shape_type == 'rounded_rectangle':
            self.drop_down_menu_ui.drawable_shape = RoundedRectangleShape(self.drop_down_menu_ui.rect,
                                                                          theming_parameters,
                                                                          ['normal'], self.ui_manager)

        self.drop_down_menu_ui.image = self.drop_down_menu_ui.drawable_shape.get_surface('normal')

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

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False

        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element in [self.open_button, self.selected_option_button]):

            self.should_transition = True

        return consumed_event

    def update_position(self):
        """
        Update the position of all the button elements in the closed drop down state.

        Used when the position of the  drop down has been altered directly, rather than when it has been moved as a
        consequence of it's container being moved.
        """

        # update the base position rect
        border_and_shadow = self.drop_down_menu_ui.shadow_width + self.drop_down_menu_ui.border_width
        self.base_position_rect.x = self.drop_down_menu_ui.relative_rect.x + border_and_shadow
        self.base_position_rect.y = self.drop_down_menu_ui.relative_rect.y + border_and_shadow

        # update all the ui elements that depend on the base position
        self.selected_option_button.set_relative_position(self.base_position_rect.topleft)

        open_button_x = self.base_position_rect.x + self.base_position_rect.width - self.open_button_width
        self.open_button.set_relative_position((open_button_x, self.base_position_rect.y))

    def update_dimensions(self):
        """
        Update the dimensions of all the button elements in the closed drop down state.

        Used when the dimensions of the drop down have been altered.
        """

        # update the base position rect
        border_and_shadow = self.drop_down_menu_ui.shadow_width + self.drop_down_menu_ui.border_width
        self.base_position_rect.width = self.drop_down_menu_ui.relative_rect.width - (2 * border_and_shadow)
        self.base_position_rect.height = self.drop_down_menu_ui.relative_rect.height - (2 * border_and_shadow)

        # update all the ui elements that depend on the base position rect
        self.selected_option_button.set_dimensions((self.base_position_rect.width - self.open_button_width,
                                                    self.base_position_rect.height))
        open_button_x = self.base_position_rect.x + self.base_position_rect.width - self.open_button_width
        self.open_button.set_dimensions((self.open_button_width, self.base_position_rect.height))
        self.open_button.set_relative_position((open_button_x, self.base_position_rect.y))

    def on_fresh_drawable_shape_ready(self):
        self.drop_down_menu_ui.set_image(self.drop_down_menu_ui.drawable_shape.get_fresh_surface())


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
                 manager: UIManager,
                 container: Union[IContainerInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 expansion_height_limit: Union[int, None] = None,
                 anchors: Dict[str, str] = None
                 ):

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='drop_down_menu')
        super().__init__(relative_rect, manager, container,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids,
                         layer_thickness=3, starting_height=1,
                         anchors=anchors)
        self.options_list = options_list
        self.selected_option = starting_option
        self.open_button_width = 20

        self.expansion_height_limit = expansion_height_limit

        self.border_width = None
        self.shadow_width = None
        self.background_colour = None
        self.border_colour = None
        self.shape_type = "rectangle"
        self.shape_corner_radius = 2

        self.current_state = None
        self.background_rect = None
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
        super().update(time_delta)
        if self.alive() and self.current_state.should_transition:
            self.current_state.finish()
            self.current_state = self.menu_states[self.current_state.target_state]
            self.current_state.selected_option = self.selected_option
            self.current_state.start()

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False
        if self.is_enabled:
            consumed_event = self.current_state.process_event(event)

        return consumed_event

    def rebuild_from_changed_theme_data(self):
        has_any_changed = False

        expand_direction_string = self.ui_manager.get_theme().get_misc_data(self.object_ids,
                                                                            self.element_ids, 'expand_direction')
        expand_direction = 'down'
        if expand_direction_string is not None and expand_direction_string in ['up', 'down']:
            expand_direction = expand_direction_string

        if expand_direction != self.expand_direction:
            self.expand_direction = expand_direction
            has_any_changed = True

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
            border_and_shadow = self.border_width + self.shadow_width
            self.background_rect = pygame.Rect(self.relative_rect.x + border_and_shadow,
                                               self.relative_rect.y + border_and_shadow,
                                               self.relative_rect.width - (2 * border_and_shadow),
                                               self.relative_rect.height - (2 * border_and_shadow))

            for state in self.menu_states:
                self.menu_states[state].expand_direction = self.expand_direction

            self.rebuild()

    def rebuild(self):
        """
        A complete rebuild of the drawable parts of this element.

        """
        if self.current_state is not None:
            self.current_state.rebuild()

    def set_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Sets the absolute screen position of this drop down, updating all subordinate button elements at the same time.

        :param position: The absolute screen position to set.
        """
        super().set_position(position)
        self.current_state.update_position()

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Sets the relative screen position of this drop down, updating all subordinate button elements at the same time.

        :param position: The relative screen position to set.
        """
        super().set_relative_position(position)
        self.current_state.update_position()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Sets the dimensions of this drop down, updating all subordinate button elements at the same time.

        :param dimensions: The new dimensions to set.
        """
        super().set_dimensions(dimensions)
        self.current_state.update_dimensions()

    def on_fresh_drawable_shape_ready(self):
        self.current_state.on_fresh_drawable_shape_ready()

    def hover_point(self, x: float, y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a straightforward matter of
        seeing if a point is inside the rectangle. Occasionally it will also check if we are in a wider zone around
        a UI element once it is already active, this makes it easier to move scroll bars and the like.

        :param x: The x (horizontal) position of the point.
        :param y: The y (vertical) position of the point.
        :return bool: Returns True if we are hovering this element.
        """
        return bool(self.rect.collidepoint(x, y)) and bool(self.ui_container.rect.collidepoint(x, y))
