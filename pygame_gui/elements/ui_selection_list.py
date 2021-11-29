from typing import Union, Dict, Tuple, List

import pygame

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, OldType
from pygame_gui._constants import UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DROPPED_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar


class UISelectionList(UIElement):
    """
    A rectangular element that holds any number of selectable text items displayed as a list.

    :param relative_rect: The positioning and sizing rectangle for the panel. See the layout guide
                          for details.
    :param item_list: A list of items as strings (item name only), or tuples of two strings (name,
                      theme_object_id).
    :param manager: The GUI manager that handles drawing and updating the UI and interactions
                    between elements.
    :param allow_multi_select: True if we are allowed to pick multiple things from the selection
                               list.
    :param allow_double_clicks: True if we can double click on items in the selection list.
    :param container: The container this element is inside of (by default the root container)
                      distinct from this panel's container.
    :param starting_height: The starting height up from it's container where this list is placed
                            into a layer.
    :param parent_element: A hierarchical 'parent' used for signifying belonging and used in
                           theming and events.
    :param object_id: An identifier that can be used to help distinguish this particular element
                      from others with the same hierarchy.
    :param anchors: Used to layout elements and dictate what the relative_rect is relative to.
                    Defaults to the top left.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(self,
                 relative_rect: pygame.Rect,
                 item_list: Union[List[str], List[Tuple[str, str]]],
                 manager: IUIManagerInterface,
                 *,
                 allow_multi_select: bool = False,
                 allow_double_clicks: bool = True,
                 container: Union[IContainerLikeInterface, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1
                 ):

        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='selection_list')

        self._parent_element = parent_element
        self.list_and_scroll_bar_container = None
        self.item_list_container = None
        self._raw_item_list = item_list
        self.item_list = []
        self.allow_multi_select = allow_multi_select
        self.allow_double_clicks = allow_double_clicks

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.shape_corner_radius = 0
        self.shape = 'rectangle'

        self.scroll_bar = None  # type: Union[UIVerticalScrollBar, None]
        self.lowest_list_pos = 0
        self.total_height_of_list = 0
        self.list_item_height = 20
        self.scroll_bar_width = 20
        self.current_scroll_bar_width = 0

        self.rebuild_from_changed_theme_data()

    def get_single_selection(self) -> Union[str, None]:
        """
        Get the selected item in a list, if any. Only works if this is a single-selection list.

        :return: A single item name as a string or None.

        """
        if not self.allow_multi_select:
            selected_list = [item['text'] for item in self.item_list if item['selected']]
            if len(selected_list) == 1:
                return selected_list[0]
            elif len(selected_list) == 0:
                return None
            else:
                raise RuntimeError('More than one item selected in single-selection,'
                                   ' selection list')
        else:
            raise RuntimeError('Requesting single selection,'
                               ' from multi-selection list')

    def get_multi_selection(self) -> List[str]:
        """
        Get all the selected items in our selection list. Only works if this is a
        multi-selection list.

        :return: A list of the selected items in our selection list. May be empty if nothing
                 selected.

        """
        if self.allow_multi_select:
            return [item['text'] for item in self.item_list if item['selected']]
        else:
            raise RuntimeError('Requesting multi selection, from single-selection list')

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by
        derived classes but also has a little functionality to make sure the panel's layer
        'thickness' is accurate and to handle window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)

        if self.scroll_bar is not None and self.scroll_bar.check_has_moved_recently():
            list_height_adjustment = min(self.scroll_bar.start_percentage *
                                         self.total_height_of_list,
                                         self.lowest_list_pos)
            for index, item in enumerate(self.item_list):
                new_height = int((index * self.list_item_height) - list_height_adjustment)
                if (-self.list_item_height
                        <= new_height <=
                        self.item_list_container.relative_rect.height):
                    if item['button_element'] is not None:
                        item['button_element'].set_relative_position((0, new_height))
                    else:
                        button_rect = pygame.Rect(0,
                                                  new_height,
                                                  self.item_list_container.relative_rect.width,
                                                  self.list_item_height)
                        button = UIButton(relative_rect=button_rect,
                                          text=item['text'],
                                          manager=self.ui_manager,
                                          parent_element=self,
                                          container=self.item_list_container,
                                          object_id=ObjectID(object_id=item['object_id'],
                                                             class_id='@selection_list_item'),
                                          allow_double_clicks=self.allow_double_clicks,
                                          anchors={'left': 'left',
                                                   'right': 'right',
                                                   'top': 'top',
                                                   'bottom': 'top'})
                        self.join_focus_sets(button)
                        item['button_element'] = button
                        if item['selected']:
                            item['button_element'].select()
                else:
                    if item['button_element'] is not None:
                        item['button_element'].kill()
                        item['button_element'] = None

    def set_item_list(self, new_item_list: Union[List[str], List[Tuple[str, str]]]):
        """
        Set a new string list (or tuple of strings & ids list) as the item list for this selection
        list. This will change what is displayed in the list.

        Tuples should be arranged like so:

         (list_text, object_ID)

         - list_text: displayed in the UI
         - object_ID: used for theming and events

        :param new_item_list: The new list to switch to. Can be a list of strings or tuples.

        """
        self._raw_item_list = new_item_list
        self.item_list = []  # type: List[Dict]
        for new_item in new_item_list:
            if isinstance(new_item, str):
                new_item_list_item = {'text': new_item,
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': '#item_list_item'}
            elif isinstance(new_item, tuple):
                new_item_list_item = {'text': new_item[0],
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': new_item[1]}
            else:
                raise ValueError('Invalid item list')

            self.item_list.append(new_item_list_item)

        self.total_height_of_list = self.list_item_height * len(self.item_list)
        self.lowest_list_pos = (self.total_height_of_list -
                                self.list_and_scroll_bar_container.relative_rect.height)
        inner_visible_area_height = self.list_and_scroll_bar_container.relative_rect.height

        if self.total_height_of_list > inner_visible_area_height:
            # we need a scroll bar
            self.current_scroll_bar_width = self.scroll_bar_width
            percentage_visible = inner_visible_area_height / max(self.total_height_of_list, 1)

            if self.scroll_bar is not None:
                self.scroll_bar.reset_scroll_position()
                self.scroll_bar.set_visible_percentage(percentage_visible)
                self.scroll_bar.start_percentage = 0
            else:
                self.scroll_bar = UIVerticalScrollBar(pygame.Rect(-self.scroll_bar_width,
                                                                  0,
                                                                  self.scroll_bar_width,
                                                                  inner_visible_area_height),
                                                      visible_percentage=percentage_visible,
                                                      manager=self.ui_manager,
                                                      parent_element=self,
                                                      container=self.list_and_scroll_bar_container,
                                                      anchors={'left': 'right',
                                                               'right': 'right',
                                                               'top': 'top',
                                                               'bottom': 'bottom'})
                self.join_focus_sets(self.scroll_bar)
        else:
            if self.scroll_bar is not None:
                self.scroll_bar.kill()
                self.scroll_bar = None
            self.current_scroll_bar_width = 0

        # create button list container
        if self.item_list_container is not None:
            self.item_list_container.clear()
            if (self.item_list_container.relative_rect.width !=
                    (self.list_and_scroll_bar_container.relative_rect.width -
                     self.current_scroll_bar_width)):
                container_dimensions = (self.list_and_scroll_bar_container.relative_rect.width -
                                        self.current_scroll_bar_width,
                                        self.list_and_scroll_bar_container.relative_rect.height)
                self.item_list_container.set_dimensions(container_dimensions)
        else:
            self.item_list_container = UIContainer(
                pygame.Rect(0, 0,
                            self.list_and_scroll_bar_container.relative_rect.width -
                            self.current_scroll_bar_width,
                            self.list_and_scroll_bar_container.relative_rect.height),
                manager=self.ui_manager,
                starting_height=0,
                parent_element=self,
                container=self.list_and_scroll_bar_container,
                object_id='#item_list_container',
                anchors={'left': 'left',
                         'right': 'right',
                         'top': 'top',
                         'bottom': 'bottom'})
            self.join_focus_sets(self.item_list_container)
        item_y_height = 0
        for item in self.item_list:
            if item_y_height <= self.item_list_container.relative_rect.height:
                button_rect = pygame.Rect(0, item_y_height,
                                          self.item_list_container.relative_rect.width,
                                          self.list_item_height)
                item['button_element'] = UIButton(relative_rect=button_rect,
                                                  text=item['text'],
                                                  manager=self.ui_manager,
                                                  parent_element=self,
                                                  container=self.item_list_container,
                                                  object_id=ObjectID(
                                                      object_id=item['object_id'],
                                                      class_id='@selection_list_item'),
                                                  allow_double_clicks=self.allow_double_clicks,
                                                  anchors={'left': 'left',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})
                self.join_focus_sets(item['button_element'])
                item_y_height += self.list_item_height
            else:
                break

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.

        :return: Should return True if this element makes use of this event.

        """
        if self.is_enabled and (
                event.type in [UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED]
                and event.ui_element in self.item_list_container.elements):
            for item in self.item_list:
                if item['button_element'] == event.ui_element:
                    if event.type == UI_BUTTON_DOUBLE_CLICKED:

                        # old event - to be removed in 0.8.0
                        event_data = {
                            'user_type': OldType(UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION),
                            'text': event.ui_element.text,
                            'ui_element': self,
                            'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                        # new event
                        event_data = {
                            'text': event.ui_element.text,
                            'ui_element': self,
                            'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(
                            pygame.event.Event(UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                                               event_data))
                    else:
                        if item['selected']:
                            item['selected'] = False
                            event.ui_element.unselect()

                            # old event - to be removed in 0.8.0
                            event_data = {'user_type': OldType(UI_SELECTION_LIST_DROPPED_SELECTION),
                                          'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                            # new event
                            event_data = {'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(
                                pygame.event.Event(UI_SELECTION_LIST_DROPPED_SELECTION, event_data))

                        else:
                            item['selected'] = True
                            event.ui_element.select()

                            # old event - to be removed in 0.8.0
                            event_data = {'user_type': OldType(UI_SELECTION_LIST_NEW_SELECTION),
                                          'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                            # new event
                            event_data = {'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(pygame.event.Event(UI_SELECTION_LIST_NEW_SELECTION,
                                                                 event_data))

                elif not self.allow_multi_select:
                    if item['selected']:
                        item['selected'] = False
                        if item['button_element'] is not None:
                            item['button_element'].unselect()

                            # old event - to be removed in 0.8.0
                            event_data = {'user_type': OldType(UI_SELECTION_LIST_DROPPED_SELECTION),
                                          'text': item['text'],
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            drop_down_changed_event = pygame.event.Event(pygame.USEREVENT,
                                                                         event_data)
                            pygame.event.post(drop_down_changed_event)

                            # new event
                            event_data = {'text': item['text'],
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            drop_down_changed_event = pygame.event.Event(
                                UI_SELECTION_LIST_DROPPED_SELECTION, event_data)
                            pygame.event.post(drop_down_changed_event)

        return False  # Don't consume any events

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Set the size of this panel and then resizes and shifts the contents of the panel container
        to fit the new size.

        :param dimensions: The new dimensions to set.

        """
        # Don't use a basic gate on this set dimensions method because the container may be a
        # different size to the window
        super().set_dimensions(dimensions)

        border_and_shadow = self.border_width + self.shadow_width
        container_width = self.relative_rect.width - (2 * border_and_shadow)
        container_height = self.relative_rect.height - (2 * border_and_shadow)
        self.list_and_scroll_bar_container.set_dimensions((container_width, container_height))

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        super().set_relative_position(position)
        border_and_shadow = self.border_width + self.shadow_width
        container_left = self.relative_rect.left + border_and_shadow
        container_top = self.relative_rect.top + border_and_shadow
        self.list_and_scroll_bar_container.set_relative_position((container_left, container_top))

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this slider, updating all subordinate button
        elements at the same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)
        border_and_shadow = self.border_width + self.shadow_width
        container_left = self.relative_rect.left + border_and_shadow
        container_top = self.relative_rect.top + border_and_shadow
        self.list_and_scroll_bar_container.set_relative_position((container_left, container_top))

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this panel.

        """
        self.list_and_scroll_bar_container.kill()
        super().kill()

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the
        button's drawable shape
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

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

        # misc
        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle']):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='list_item_height',
                                               default_value=20,
                                               casting_func=int):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this element.

        """
        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'normal_image': self.background_image,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.on_fresh_drawable_shape_ready()

        if self.list_and_scroll_bar_container is None:
            self.list_and_scroll_bar_container = UIContainer(
                pygame.Rect(self.relative_rect.left + self.shadow_width + self.border_width,
                            self.relative_rect.top + self.shadow_width + self.border_width,
                            self.relative_rect.width -
                            (2 * self.shadow_width) -
                            (2 * self.border_width),
                            self.relative_rect.height -
                            (2 * self.shadow_width) -
                            (2 * self.border_width)),
                manager=self.ui_manager,
                starting_height=self.starting_height,
                container=self.ui_container,
                parent_element=self._parent_element,
                object_id='#selection_list_container',
                anchors=self.anchors,
                visible=self.visible
            )
            self.join_focus_sets(self.list_and_scroll_bar_container)
        else:
            self.list_and_scroll_bar_container.set_dimensions((self.relative_rect.width -
                                                               (2 * self.shadow_width) -
                                                               (2 * self.border_width),
                                                               self.relative_rect.height -
                                                               (2 * self.shadow_width) -
                                                               (2 * self.border_width)))
            self.list_and_scroll_bar_container.set_relative_position((self.relative_rect.left +
                                                                      self.shadow_width +
                                                                      self.border_width,
                                                                      self.relative_rect.top +
                                                                      self.shadow_width +
                                                                      self.border_width))

        self.set_item_list(self._raw_item_list)

    def disable(self):
        """
        Disables all elements in the selection list so they are no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            self.list_and_scroll_bar_container.disable()

            # clear selections
            for item in self.item_list:
                item['selected'] = False

    def enable(self):
        """
        Enables all elements in the selection list so they are interactive again.
        """
        if not self.is_enabled:
            self.is_enabled = True
            self.list_and_scroll_bar_container.enable()

    def show(self):
        """
        In addition to the base UIElement.show() - call show() of owned container -
        list_and_scroll_bar_container. All other subelements (item_list_container, scrollbar) are
        children of list_and_scroll_bar_container, so it's visibility will propagate to them -
        there is no need to call their show() methods separately.
        """
        super().show()

        self.list_and_scroll_bar_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - call hide() of owned container -
        list_and_scroll_bar_container. All other subelements (item_list_container, scrollbar) are
        children of list_and_scroll_bar_container, so it's visibility will propagate to them -
        there is no need to call their hide() methods separately.
        """
        super().hide()

        self.list_and_scroll_bar_container.hide()
