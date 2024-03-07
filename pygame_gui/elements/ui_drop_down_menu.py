from typing import Union, List, Tuple, Dict, Optional

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui._constants import UI_DROP_DOWN_MENU_CHANGED, OldType

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement, ObjectID
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.ui_container import UIContainer

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList


class UIExpandedDropDownState:
    """
    The expanded state of the drop down  displays the currently chosen option, all the available
    options and a button to close the menu and return to the closed state.

    Picking an option will also close the menu.

    :param drop_down_menu_ui: The UIDropDownElement this state belongs to.
    :param options_list: The list of options in this drop down.
    :param selected_option: The currently selected option.
    :param base_position_rect: Position and dimensions rectangle.
    :param close_button_width: Width of close button.
    :param expand_direction: Direction of expansion, 'up' or 'down'.
    :param manager: The UI Manager for the whole UI.
    :param container: The container the element is within.
    :param object_ids: The object IDs for the drop down UI element.
    :param element_ids: The element IDs for the drop down UI element.
    """

    def __init__(self,
                 drop_down_menu_ui: 'UIDropDownMenu',
                 options_list: List[str],
                 selected_option: str,
                 base_position_rect: Union[pygame.Rect, None],
                 close_button_width: int,
                 expand_direction: Union[str, None],
                 manager: IUIManagerInterface,
                 container: IContainerLikeInterface,
                 object_ids: Union[List[Union[str, None]], None],
                 element_ids: Union[List[str], None],
                 expand_on_option_click):

        self.drop_down_menu_ui = drop_down_menu_ui
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect

        self.expand_direction = expand_direction
        self.ui_manager = manager
        self.ui_container = container
        self.element_ids = element_ids
        self.object_ids = object_ids
        self.expand_on_option_click = expand_on_option_click

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

        self.active_buttons = []

    def rebuild(self):
        """
        Rebuild the state from theming parameters and dimensions.

        """
        theming_parameters = {'normal_bg': self.drop_down_menu_ui.background_colour,
                              'normal_border': self.drop_down_menu_ui.border_colour,
                              'border_width': self.drop_down_menu_ui.border_width,
                              'shadow_width': self.drop_down_menu_ui.shadow_width,
                              'shape_corner_radius': self.drop_down_menu_ui.shape_corner_radius}

        shape_rect = self.drop_down_menu_ui.relative_rect
        if self.drop_down_menu_ui.shape == 'rectangle':
            self.drop_down_menu_ui.drawable_shape = RectDrawableShape(shape_rect,
                                                                      theming_parameters,
                                                                      ['normal'],
                                                                      self.ui_manager)

        elif self.drop_down_menu_ui.shape == 'rounded_rectangle':
            self.drop_down_menu_ui.drawable_shape = RoundedRectangleShape(shape_rect,
                                                                          theming_parameters,
                                                                          ['normal'],
                                                                          self.ui_manager)

        self.drop_down_menu_ui.on_fresh_drawable_shape_ready()

        # extra
        if self.close_button is not None:
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.close_button.set_text(expand_button_symbol)

    def start(self, should_rebuild: bool = True):
        """
        Called each time we enter the expanded state. It creates the necessary elements, the
        selected option, all the other available options and the close button.

        """
        self.should_transition = False

        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.active_buttons = []
        self.selected_option_button = UIButton(pygame.Rect((border_and_shadow, border_and_shadow),
                                                           (self.base_position_rect.width -
                                                            self.close_button_width,
                                                            self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               parent_element=self.drop_down_menu_ui,
                                               object_id=ObjectID('#selected_option', None))
        self.drop_down_menu_ui.join_focus_sets(self.selected_option_button)
        self.active_buttons.append(self.selected_option_button)

        expand_button_symbol = '▼'

        list_object_id = '#drop_down_options_list'
        list_object_ids = self.drop_down_menu_ui.object_ids[:]
        list_object_ids.append(list_object_id)
        list_class_ids = self.drop_down_menu_ui.class_ids[:]
        list_class_ids.append(None)
        list_element_ids = self.drop_down_menu_ui.element_ids[:]
        list_element_ids.append('selection_list')
        list_base_element_ids = self.drop_down_menu_ui.element_base_ids[:]
        list_base_element_ids.append(None)

        final_ids = self.ui_manager.get_theme().build_all_combined_ids(list_base_element_ids,
                                                                       list_element_ids,
                                                                       list_class_ids,
                                                                       list_object_ids)

        self._calculate_options_list_sizes(final_ids)
        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                expand_button_symbol = '▲'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    self.drop_down_menu_ui.expansion_height_limit = self.base_position_rect.top

                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.top - self.options_list_height

            elif self.expand_direction == 'down':
                expand_button_symbol = '▼'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    height_limit = (self.drop_down_menu_ui.ui_container.relative_rect.height -
                                    self.base_position_rect.bottom)
                    self.drop_down_menu_ui.expansion_height_limit = height_limit

                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.bottom

        if self.close_button_width > 0:
            close_button_x = (border_and_shadow +
                              self.base_position_rect.width -
                              self.close_button_width)

            self.close_button = UIButton(pygame.Rect((close_button_x,
                                                      border_and_shadow),
                                                     (self.close_button_width,
                                                      self.base_position_rect.height)),
                                         expand_button_symbol,
                                         self.ui_manager,
                                         self.ui_container,
                                         starting_height=2,
                                         parent_element=self.drop_down_menu_ui,
                                         object_id='#expand_button')
            self.drop_down_menu_ui.join_focus_sets(self.close_button)
            self.active_buttons.append(self.close_button)
        list_rect = pygame.Rect(self.drop_down_menu_ui.relative_rect.left,
                                self.option_list_y_pos,
                                (self.drop_down_menu_ui.relative_rect.width -
                                 self.close_button_width),
                                self.options_list_height)
        self.options_selection_list = UISelectionList(list_rect,
                                                      starting_height=3,
                                                      item_list=self.options_list,
                                                      allow_double_clicks=False,
                                                      manager=self.ui_manager,
                                                      parent_element=self.drop_down_menu_ui,
                                                      container=self.drop_down_menu_ui.ui_container,
                                                      anchors=self.drop_down_menu_ui.anchors,
                                                      object_id='#drop_down_options_list',
                                                      default_selection=self.selected_option)
        self.drop_down_menu_ui.join_focus_sets(self.options_selection_list)
        if self.options_selection_list.scroll_bar is not None:
            # our options list is long enough to have a scroll bar.
            # we want to scroll it enough that the currently selected option is on screen.
            start_percentage = self.options_selection_list.get_single_selection_start_percentage()
            self.options_selection_list.scroll_bar.set_scroll_from_start_percentage(start_percentage)
            self.options_selection_list.update(0.0)

        if should_rebuild:
            self.rebuild()

    def _calculate_options_list_sizes(self, final_ids):
        try:
            list_shadow_width = int(
                self.ui_manager.get_theme().get_misc_data('shadow_width', final_ids))
        except (LookupError, ValueError):
            list_shadow_width = 2
        try:
            list_border_width = int(
                self.ui_manager.get_theme().get_misc_data('border_width', final_ids))
        except (LookupError, ValueError):
            list_border_width = 1
        try:
            list_item_height = int(
                self.ui_manager.get_theme().get_misc_data('list_item_height', final_ids))
        except (LookupError, ValueError):
            list_item_height = 20
        options_list_border_and_shadow = list_shadow_width + list_border_width
        self.options_list_height = ((list_item_height * len(self.options_list)) +
                                    (2 * options_list_border_and_shadow))
        self.option_list_y_pos = 0

    def finish(self):
        """
        cleans everything up upon exiting the expanded menu state.
        """
        self.options_selection_list.kill()
        self.selected_option_button.kill()
        if self.close_button is not None:
            self.close_button.kill()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Processes events for the closed state of the drop down.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        if event.type == UI_BUTTON_PRESSED:
            if ((self.expand_on_option_click and event.ui_element in self.active_buttons) or
                    (not self.expand_on_option_click and
                     self.close_button is not None and event.ui_element == self.close_button)):
                self.should_transition = True
                return True

        if (event.type == UI_SELECTION_LIST_NEW_SELECTION and
                event.ui_element == self.options_selection_list):
            selection = self.options_selection_list.get_single_selection()
            self.drop_down_menu_ui.selected_option = selection
            self.should_transition = True

            # old event - to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_DROP_DOWN_MENU_CHANGED),
                          'text': self.drop_down_menu_ui.selected_option,
                          'ui_element': self.drop_down_menu_ui,
                          'ui_object_id': self.drop_down_menu_ui.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

            # new event
            event_data = {'text': self.drop_down_menu_ui.selected_option,
                          'ui_element': self.drop_down_menu_ui,
                          'ui_object_id': self.drop_down_menu_ui.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_DROP_DOWN_MENU_CHANGED, event_data))

        return False  # don't consume any events

    def update_position(self):
        """
        Update the position of all the button elements in the open drop down state.

        Used when the position of the  drop down has been altered directly, rather than when it
        has been moved as a consequence of it's container being moved.
        """

        # update the base position rect
        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.base_position_rect.x = self.drop_down_menu_ui.relative_rect.x + border_and_shadow
        self.base_position_rect.y = self.drop_down_menu_ui.relative_rect.y + border_and_shadow

        # update all the ui elements that depend on the base position
        self.selected_option_button.set_relative_position((border_and_shadow, border_and_shadow))
        list_post = (self.drop_down_menu_ui.relative_rect.left, self.option_list_y_pos)
        self.options_selection_list.set_relative_position(list_post)

        if self.close_button is not None:
            close_button_x = (border_and_shadow +
                              self.base_position_rect.width -
                              self.close_button_width)
            self.close_button.set_relative_position([close_button_x, border_and_shadow])

    def update_dimensions(self):
        """
        Update the dimensions of all the button elements in the closed drop down state.

        Used when the dimensions of the drop down have been altered.
        """

        # update the base position rect
        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.base_position_rect.width = (self.drop_down_menu_ui.relative_rect.width -
                                         (2 * border_and_shadow))
        self.base_position_rect.height = (self.drop_down_menu_ui.relative_rect.height -
                                          (2 * border_and_shadow))

        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)
                self.option_list_y_pos = self.base_position_rect.top - self.options_list_height

            elif self.expand_direction == 'down':
                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)
                self.option_list_y_pos = self.base_position_rect.bottom

        # update all the ui elements that depend on the base position rect
        self.selected_option_button.set_dimensions((self.base_position_rect.width -
                                                    self.close_button_width,
                                                    self.base_position_rect.height))

        self.options_selection_list.set_dimensions(((self.drop_down_menu_ui.relative_rect.width -
                                                     self.close_button_width),
                                                    self.options_list_height))

        list_pos = (self.drop_down_menu_ui.relative_rect.left, self.option_list_y_pos)
        self.options_selection_list.set_relative_position(list_pos)
        if self.close_button is not None:
            close_button_x = (border_and_shadow +
                              self.base_position_rect.width -
                              self.close_button_width)
            self.close_button.set_dimensions((self.close_button_width,
                                              self.base_position_rect.height))
            self.close_button.set_relative_position((close_button_x, border_and_shadow))

    def hide(self):
        """
        Transition from expanded state to closed state.
        """
        self.should_transition = True


class UIClosedDropDownState:
    """
    The closed state of the drop down just displays the currently chosen option and a button that
    will switch the menu to the expanded state.

    :param drop_down_menu_ui: The UIDropDownElement this state belongs to.
    :param selected_option: The currently selected option.
    :param base_position_rect: Position and dimensions rectangle.
    :param open_button_width: Width of open button.
    :param expand_direction: Direction of expansion, 'up' or 'down'.
    :param manager: The UI Manager for the whole UI.
    :param container: The container the element is within.
    :param object_ids: The object IDs for the drop down UI element.
    :param element_ids: The element IDs for the drop down UI element.
    :param visible: Whether the element is visible by default. Warning -
                    container visibility may override this.
    """

    def __init__(self,
                 drop_down_menu_ui: 'UIDropDownMenu',
                 selected_option: str,
                 base_position_rect: Union[pygame.Rect, None],
                 open_button_width: int,
                 expand_direction: Union[str, None],
                 manager: IUIManagerInterface,
                 container: IContainerLikeInterface,
                 object_ids: Union[List[Union[str, None]], None],
                 element_ids: Union[List[str], None],
                 visible: int = 1,
                 expand_on_option_click=True):

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

        self.open_button_width = open_button_width

        self.expand_on_option_click = expand_on_option_click

        self.should_transition = False
        self.target_state = 'expanded'
        self.visible = visible

        self.active_buttons = []

    def disable(self):
        """
        Disables the closed state so that it is no longer interactive.
        """
        if self.selected_option_button is not None:
            self.selected_option_button.disable()
        if self.open_button is not None:
            self.open_button.disable()
        if self.drop_down_menu_ui.drawable_shape is not None:
            self.drop_down_menu_ui.drawable_shape.set_active_state('disabled')

    def enable(self):
        """
        Re-enables the closed state so we can once again interact with it.
        """
        if self.selected_option_button is not None:
            self.selected_option_button.enable()
        if self.open_button is not None:
            self.open_button.enable()
        if self.drop_down_menu_ui.drawable_shape is not None:
            self.drop_down_menu_ui.drawable_shape.set_active_state('normal')

    def rebuild(self):
        """
        Rebuild the closed state from theming parameters and dimensions.

        """
        theming_parameters = {'normal_bg': self.drop_down_menu_ui.background_colour,
                              'normal_border': self.drop_down_menu_ui.border_colour,
                              'disabled_bg': self.drop_down_menu_ui.disabled_background_colour,
                              'disabled_border': self.drop_down_menu_ui.disabled_border_colour,
                              'border_width': self.drop_down_menu_ui.border_width,
                              'shadow_width': self.drop_down_menu_ui.shadow_width,
                              'shape_corner_radius': self.drop_down_menu_ui.shape_corner_radius}

        if self.drop_down_menu_ui.shape == 'rectangle':
            self.drop_down_menu_ui.drawable_shape = RectDrawableShape(self.drop_down_menu_ui.rect,
                                                                      theming_parameters,
                                                                      ['normal', 'disabled'],
                                                                      self.ui_manager)
        elif self.drop_down_menu_ui.shape == 'rounded_rectangle':
            shape_rect = self.drop_down_menu_ui.rect
            self.drop_down_menu_ui.drawable_shape = RoundedRectangleShape(shape_rect,
                                                                          theming_parameters,
                                                                          ['normal', 'disabled'],
                                                                          self.ui_manager)

        self.drop_down_menu_ui._set_image(self.drop_down_menu_ui.drawable_shape.get_fresh_surface())

        # extra
        if self.open_button is not None:
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.open_button.set_text(expand_button_symbol)

    def start(self, should_rebuild: bool = True):
        """
        Called each time we enter the closed state. It creates the necessary elements, the
        selected option and the open button.
        """
        if should_rebuild:
            self.rebuild()

        self.should_transition = False

        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.active_buttons = []
        self.selected_option_button = UIButton(pygame.Rect((border_and_shadow, border_and_shadow),
                                                           (self.base_position_rect.width -
                                                            self.open_button_width,
                                                            self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               parent_element=self.drop_down_menu_ui,
                                               object_id='#selected_option',
                                               visible=self.visible)
        self.drop_down_menu_ui.join_focus_sets(self.selected_option_button)
        self.active_buttons.append(self.selected_option_button)

        if self.open_button_width > 0:
            open_button_x = (border_and_shadow +
                             self.base_position_rect.width -
                             self.open_button_width)
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.open_button = UIButton(pygame.Rect((open_button_x,
                                                     border_and_shadow),
                                                    (self.open_button_width,
                                                     self.base_position_rect.height)),
                                        expand_button_symbol,
                                        self.ui_manager,
                                        self.ui_container,
                                        starting_height=2,
                                        parent_element=self.drop_down_menu_ui,
                                        object_id='#expand_button',
                                        visible=self.visible)
            self.drop_down_menu_ui.join_focus_sets(self.open_button)
            self.active_buttons.append(self.open_button)

    def finish(self):
        """
        Called when we leave the closed state. Kills the open button and the selected option button.
        """
        self.selected_option_button.kill()
        if self.open_button is not None:
            self.open_button.kill()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Processes events for the closed state of the drop down.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.
        """
        if event.type == UI_BUTTON_PRESSED:
            if ((self.expand_on_option_click and event.ui_element in self.active_buttons) or
                    (not self.expand_on_option_click and
                     self.open_button is not None and event.ui_element == self.open_button)):
                self.should_transition = True
                return True

        return False

    def update_position(self):
        """
        Update the position of all the button elements in the closed drop down state.

        Used when the position of the  drop down has been altered directly, rather than when it has
        been moved as a consequence of it's container being moved.
        """

        # update the base position rect
        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.base_position_rect.x = self.drop_down_menu_ui.relative_rect.x + border_and_shadow
        self.base_position_rect.y = self.drop_down_menu_ui.relative_rect.y + border_and_shadow

        # update all the ui elements that depend on the base position
        self.selected_option_button.set_relative_position((border_and_shadow, border_and_shadow))

        if self.open_button is not None:
            open_button_x = (border_and_shadow +
                             self.base_position_rect.width -
                             self.open_button_width)
            self.open_button.set_relative_position((open_button_x, self.base_position_rect.y))

    def update_dimensions(self):
        """
        Update the dimensions of all the button elements in the closed drop down state.

        Used when the dimensions of the drop down have been altered.
        """

        # update the base position rect
        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.base_position_rect.width = (self.drop_down_menu_ui.relative_rect.width -
                                         (2 * border_and_shadow))
        self.base_position_rect.height = (self.drop_down_menu_ui.relative_rect.height -
                                          (2 * border_and_shadow))

        # update all the ui elements that depend on the base position rect
        self.selected_option_button.set_dimensions((self.base_position_rect.width -
                                                    self.open_button_width,
                                                    self.base_position_rect.height))
        if self.open_button is not None:
            open_button_x = (border_and_shadow +
                             self.base_position_rect.width -
                             self.open_button_width)
            self.open_button.set_dimensions((self.open_button_width,
                                             self.base_position_rect.height))
            self.open_button.set_relative_position((open_button_x, border_and_shadow))

    def show(self):
        """
        Show selected_option_button and open_button.
        """
        self.visible = True

        if self.open_button is not None:
            self.open_button.show()
        if self.selected_option_button is not None:
            self.selected_option_button.show()

    def hide(self):
        """
        Hide selected_option_button and open_button.
        """
        self.visible = False

        if self.open_button is not None:
            self.open_button.hide()
        if self.selected_option_button is not None:
            self.selected_option_button.hide()


class UIDropDownMenu(UIContainer):
    """
    A drop down menu lets us choose one text option from a list. That list of options can be
    expanded and hidden at the press of a button. While the element is called a drop down,
    it can also be made to 'climb up' by changing the 'expand_direction' styling option to 'up'
    in the theme file.

    The drop down is implemented through two states, one representing the 'closed' menu state
    and one for when it has been 'expanded'.

    :param options_list: The list of of options to choose from. They must be strings.
    :param starting_option: The starting option, selected when the menu is first created.
    :param relative_rect: The size and position of the element when not expanded.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param expansion_height_limit: Limit on the height that this will expand to, defaults to the
                                   container bounds.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    :param expand_on_option_click: If this is set to False the drop down will only expand when
                                   the open/close button is pressed and not when the selected
                                   option is pressed.
    """

    def __init__(self,
                 options_list: List[str],
                 starting_option: str,
                 relative_rect: pygame.Rect,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 expansion_height_limit: Union[int, None] = None,
                 anchors: Dict[str, Union[str, UIElement]] = None,
                 visible: int = 1,
                 *,
                 expand_on_option_click: bool = True
                 ):
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor
        self.menu_states = None
        self.current_state = None
        super().__init__(relative_rect, manager, container=container,
                         starting_height=0,
                         anchors=anchors,
                         visible=visible,
                         object_id=object_id,
                         element_id=['drop_down_menu'])

        self.__layer_thickness_including_expansion = 4
        self.options_list = options_list
        self.selected_option = starting_option
        self.open_button_width = 20

        self.expansion_height_limit = expansion_height_limit
        self.expand_on_option_click = expand_on_option_click

        self.border_width = None
        self.shadow_width = None

        self.background_colour = None
        self.border_colour = None
        self.disabled_background_colour = None
        self.disabled_border_colour = None

        self.shape = "rectangle"
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
                                                            self,
                                                            self.element_ids,
                                                            self.object_ids,
                                                            self.visible,
                                                            self.expand_on_option_click),
                            'expanded': UIExpandedDropDownState(self,
                                                                self.options_list,
                                                                self.selected_option,
                                                                self.background_rect,
                                                                self.open_button_width,
                                                                self.expand_direction,
                                                                self.ui_manager,
                                                                self,
                                                                self.element_ids,
                                                                self.object_ids,
                                                                self.expand_on_option_click
                                                                )}
        self.current_state = self.menu_states['closed']
        self.current_state.start(should_rebuild=True)

    @property
    def layer_thickness(self):
        return self.__layer_thickness_including_expansion

    @layer_thickness.setter
    def layer_thickness(self, value):
        # ignore passed in value and hardcode to 4
        self.__layer_thickness_including_expansion = 4

    def add_options(self, new_options: List[str]) -> None:
        """
        Add new options to the drop down. Will close the drop down if it is currently open.

        In many cases it may be easier just to recreate the drop down with whatever the new options list is.

        :param new_options: The list of new options to add.
        """
        self.options_list.extend(new_options)
        self.menu_states['expanded'].options_list = self.options_list

        # if we have the dropdown open, close it so it can be reopened with the new options in place
        self._close_dropdown_if_open()

    def remove_options(self, options_to_remove: List[str]) -> None:
        """
        Will remove all instances of the options provided.

        :param options_to_remove: The list of new options to remove.
        """
        self.options_list = [option for option in self.options_list if option not in options_to_remove]
        self.menu_states['expanded'].options_list = self.options_list

        # if we have the dropdown open, close it so it can be reopened with the new options in place
        self._close_dropdown_if_open()

    def _close_dropdown_if_open(self):
        if self.current_state == self.menu_states['expanded']:
            self.current_state.finish()
            self.current_state = self.menu_states['closed']
            self.current_state.selected_option = self.selected_option
            self.current_state.start()

    def kill(self):
        """
        Overrides the standard sprite kill to also properly kill/finish the current state of the
        drop down. Depending on whether it is expanded or closed the drop down menu will have
        different elements to clean up.
        """
        self.current_state.finish()
        super().kill()

    def unfocus(self):
        super().unfocus()
        if self.current_state is self.menu_states['expanded']:
            self.current_state.should_transition = True

    def update(self, time_delta: float):
        """
        The update here deals with transitioning between the two states of the drop down menu and
        then passes the rest of the work onto whichever state is active.

        :param time_delta: The time in second between calls to update.

        """
        super().update(time_delta)
        if self.alive() and self.current_state.should_transition:
            self.current_state.finish()
            self.current_state = self.menu_states[self.current_state.target_state]
            self.current_state.selected_option = self.selected_option
            self.current_state.start()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles various interactions with the drop down menu by passing them along to the
        active state.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False
        if self.is_enabled:
            consumed_event = self.current_state.process_event(event)

        return consumed_event

    def rebuild_from_changed_theme_data(self):
        """
        Triggers the element to rebuild if any of it's theming data has changed, which involves a
        lot of checking and validating it's theming data.

        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='expand_direction',
                                               default_value='down',
                                               casting_func=str,
                                               allowed_values=['up', 'down']):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle']):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='open_button_width',
                                               default_value=20,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='tool_tip_delay',
                                               default_value=1.0,
                                               casting_func=float):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        background_colour = self.ui_theme.get_colour_or_gradient('dark_bg',
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient('normal_border',
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        disabled_background_colour = self.ui_theme.get_colour_or_gradient('disabled_dark_bg',
                                                                          self.combined_element_ids)
        if disabled_background_colour != self.disabled_background_colour:
            self.disabled_background_colour = disabled_background_colour
            has_any_changed = True

        disabled_border_colour = self.ui_theme.get_colour_or_gradient('disabled_border',
                                                                      self.combined_element_ids)
        if disabled_border_colour != self.disabled_border_colour:
            self.disabled_border_colour = disabled_border_colour
            has_any_changed = True

        if has_any_changed:
            border_and_shadow = self.border_width + self.shadow_width
            self.background_rect = pygame.Rect(self.relative_rect.x + border_and_shadow,
                                               self.relative_rect.y + border_and_shadow,
                                               self.relative_rect.width - (2 * border_and_shadow),
                                               self.relative_rect.height - (2 * border_and_shadow))

            for _, state in self.menu_states.items():
                state.expand_direction = self.expand_direction

            self.rebuild()

    def rebuild(self):
        """
        A complete rebuild of the drawable parts of this element.

        """
        if self.current_state is not None:
            self.current_state.rebuild()

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this drop down, updating all subordinate button
        elements at the same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)
        self.current_state.update_position()

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Sets the relative screen position of this drop down, updating all subordinate button
        elements at the same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)
        self.current_state.update_position()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]],
                       clamp_to_container: bool = False):
        """
        Sets the dimensions of this drop down, updating all subordinate button
        elements at the same time.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        super().set_dimensions(dimensions)
        self.current_state.update_dimensions()

    def on_fresh_drawable_shape_ready(self):
        """
        Called by an element's drawable shape when it has a new image surface ready for use,
        normally after a rebuilding/redrawing of some kind.
        """
        self._set_image(self.drawable_shape.get_fresh_surface())

    def disable(self):
        """
        Disables the button so that it is no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            # switch back to the closed state if we are in the expanded state
            if self.current_state is not None:
                if self.current_state is self.menu_states['expanded']:
                    self.current_state.finish()
                    self.current_state = self.menu_states['closed']
                    self.current_state.selected_option = self.selected_option
                    self.current_state.start()
                self.current_state.disable()

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.current_state is not None:
                self.current_state.enable()

    def show(self):
        """
        In addition to the base UIElement.show() - call show() on the closed state -
        showing it's buttons.
        """
        super().show()
        if self.current_state is not None and self.menu_states is not None:
            self.menu_states['closed'].show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - if the current state is 'expanded' call it's
        hide() method, which begins a transition of the UIDropDownMenu to the 'closed' state, and
        call the hide() method of the 'closed' state which hides all it's children widgets.
        """
        super().hide()
        if self.current_state is not None and self.menu_states is not None:
            if self.current_state == self.menu_states['expanded']:
                self.menu_states['expanded'].hide()
            self.menu_states['closed'].hide()
