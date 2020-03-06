from typing import Union, Dict, Tuple, List

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED
from pygame_gui._constants import UI_SELECTION_LIST_NEW_SELECTION, UI_SELECTION_LIST_DROPPED_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
from pygame import Rect, USEREVENT
from pygame.event import Event, post
from pygame.math import Vector2

from pygame_gui.core.interfaces import IContainerInterface, IUIManagerInterface
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar


class UISelectionList(UIElement):
    """
    A rectangular element that holds any number of selectable text items displayed as a list.

    :param relative_rect: The positioning and sizing rectangle for the panel. See the layout guide for details.
    :param manager: The GUI manager that handles drawing and updating the UI and interactions between elements.
    :param container: The container this element is inside of (by default the root container) distinct from this panel's container.
    :param parent_element: A hierarchical 'parent' used for signifying belonging and used in theming and events.
    :param object_id: An identifier that can be used to help distinguish this particular element from others with the same hierarchy.
    :param anchors: Used to layout elements and dictate what the relative_rect is relative to. Defaults to the top left.
    """

    def __init__(self,
                 relative_rect: Rect,
                 item_list: Union[List[str], List[Tuple[str, str]]],
                 manager: IUIManagerInterface,
                 *,
                 allow_multiselect: bool = False,
                 allow_doubleclicks: bool = True,
                 container: Union[IContainerInterface, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None
                 ):
        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='selection_list')
        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=starting_height,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         anchors=anchors)

        self.item_list_container = None
        self.item_list = []
        self.allow_multiselect = allow_multiselect
        self.allow_doubleclicks = allow_doubleclicks

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.shape_corner_radius = 0
        self.shape_type = 'rectangle'

        self.scroll_bar = None  # type: Union[UIVerticalScrollBar, None]
        self.lowest_list_pos = 0
        self.total_height_of_list = 0
        self.list_item_height = 20
        self.scroll_bar_width = 20
        self.current_scroll_bar_width = 0

        self.rebuild_from_changed_theme_data()

        self.list_and_scroll_bar_container = UIContainer(
            Rect(self.relative_rect.left + self.shadow_width + self.border_width,
                 self.relative_rect.top + self.shadow_width + self.border_width,
                 self.relative_rect.width - (2 * self.shadow_width) - (2 * self.border_width),
                 self.relative_rect.height - (2 * self.shadow_width) - (2 * self.border_width)),
            manager=self.ui_manager,
            starting_height=starting_height,
            container=self.ui_container,
            parent_element=parent_element,
            object_id='#selection_list_container')

        self.set_item_list(item_list)

    def get_single_selection(self) -> str:
        if not self.allow_multiselect:
            selected_list = [item['text'] for item in self.item_list if item['selected']]
            if len(selected_list) == 1:
                return selected_list[0]
            else:
                raise RuntimeError('More than one item selected in single-selection, selection list')
        else:
            raise RuntimeError('Requesting single selection, from multi-selection list')

    def get_multi_selection(self) -> List[str]:
        if self.allow_multiselect:
            selected_list = [item['text'] for item in self.item_list if item['selected']]
            return selected_list[0]
        else:
            raise ValueError('Requesting multi selection, from single-selection list')

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived classes
        but also has a little functionality to make sure the panel's layer 'thickness' is accurate and to handle
        window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        super().update(time_delta)

        if self.scroll_bar is not None and self.scroll_bar.check_has_moved_recently():
            list_height_adjustment = min(self.scroll_bar.start_percentage * self.total_height_of_list,
                                         self.lowest_list_pos)
            for index, item in enumerate(self.item_list):
                new_height = (index * self.list_item_height) - list_height_adjustment
                if -self.list_item_height <= new_height <= self.item_list_container.relative_rect.height:
                    if item['button_element'] is not None:
                        item['button_element'].set_relative_position((0, new_height))
                    else:
                        item['button_element'] = UIButton(relative_rect=Rect(0, new_height,
                                                                             self.item_list_container.relative_rect.width,
                                                                             self.list_item_height),
                                                          text=item['text'],
                                                          manager=self.ui_manager,
                                                          parent_element=self,
                                                          container=self.item_list_container,
                                                          object_id=item['object_id'],
                                                          allow_double_clicks=self.allow_doubleclicks,
                                                          anchors={'left': 'left',
                                                                   'right': 'right',
                                                                   'top': 'top',
                                                                   'bottom': 'top'})
                        if item['selected']:
                            item['button_element'].select()
                else:
                    if item['button_element'] is not None:
                        item['button_element'].kill()
                        item['button_element'] = None

    def set_item_list(self, new_item_list: Union[List[str], List[Tuple[str, str]]]):
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
        self.lowest_list_pos = self.total_height_of_list - self.list_and_scroll_bar_container.relative_rect.height
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
                self.scroll_bar = UIVerticalScrollBar(Rect(-self.scroll_bar_width,
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
        else:
            if self.scroll_bar is not None:
                self.scroll_bar.kill()
                self.scroll_bar = None
            self.current_scroll_bar_width = 0

        # create button list container
        if self.item_list_container is not None:
            self.item_list_container.clear()
            if (self.item_list_container.relative_rect.width !=
                    (self.list_and_scroll_bar_container.relative_rect.width - self.current_scroll_bar_width)):
                self.item_list_container.set_dimensions((self.list_and_scroll_bar_container.relative_rect.width
                                                         - self.current_scroll_bar_width,
                                                         self.list_and_scroll_bar_container.relative_rect.height))
        else:
            self.item_list_container = UIContainer(
                Rect(0, 0,
                     self.list_and_scroll_bar_container.relative_rect.width - self.current_scroll_bar_width,
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
        item_y_height = 0
        for item in self.item_list:
            if item_y_height <= self.item_list_container.relative_rect.height:
                item['button_element'] = UIButton(relative_rect=Rect(0, item_y_height,
                                                                     self.item_list_container.relative_rect.width,
                                                                     self.list_item_height),
                                                  text=item['text'],
                                                  manager=self.ui_manager,
                                                  parent_element=self,
                                                  container=self.item_list_container,
                                                  object_id=item['object_id'],
                                                  allow_double_clicks=self.allow_doubleclicks,
                                                  anchors={'left': 'left',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})
                item_y_height += self.list_item_height
            else:
                break

    def process_event(self, event: Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.
        :return bool: Should return True if this element makes use of this event.
        """
        consumed_event = False
        if (event.type == USEREVENT and event.user_type in [UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED] and
                event.ui_element in self.item_list_container.elements):
            for item in self.item_list:
                if item['button_element'] == event.ui_element:
                    if event.user_type == UI_BUTTON_DOUBLE_CLICKED:
                        event_data = {'user_type': UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                                      'text': event.ui_element.text,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                    else:
                        if item['selected']:
                            item['selected'] = False
                            event.ui_element.unselect()

                            event_data = {'user_type': UI_SELECTION_LIST_DROPPED_SELECTION,
                                          'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}

                        else:
                            item['selected'] = True
                            event.ui_element.select()

                            event_data = {'user_type': UI_SELECTION_LIST_NEW_SELECTION,
                                          'text': event.ui_element.text,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}

                    selection_list_event = Event(USEREVENT, event_data)
                    post(selection_list_event)
                elif not self.allow_multiselect:
                    if item['selected']:
                        item['selected'] = False
                        if item['button_element'] is not None:
                            item['button_element'].unselect()

                            event_data = {'user_type': UI_SELECTION_LIST_DROPPED_SELECTION,
                                          'text': item['text'],
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            drop_down_changed_event = Event(USEREVENT, event_data)
                            post(drop_down_changed_event)

        return consumed_event

    def set_dimensions(self, dimensions: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the size of this panel and then resizes and shifts the contents of the panel container to fit the new
        size.

        :param dimensions:
        """
        # Don't use a basic gate on this set dimensions method because the container may be a different size to the
        # window
        super().set_dimensions(dimensions)

    def set_relative_position(self, position: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_relative_position(position)

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI elements in this panel.

        """
        self.list_and_scroll_bar_container.kill()
        super().kill()

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the button's drawable shape
        """
        has_any_changed = False

        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        # misc
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if (shape_type_string is not None and shape_type_string in ['rectangle', 'rounded_rectangle'] and
                shape_type_string != self.shape_type):
            self.shape_type = shape_type_string
            has_any_changed = True

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

        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            try:
                border_width = int(border_width_string)
            except ValueError:
                border_width = 1
            if border_width != self.border_width:
                self.border_width = border_width
                has_any_changed = True

        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            try:
                shadow_width = int(shadow_width_string)
            except ValueError:
                shadow_width = 2
            if shadow_width != self.shadow_width:
                self.shadow_width = shadow_width
                has_any_changed = True

        list_item_height_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'list_item_height')
        if list_item_height_string is not None:
            try:
                list_item_height = int(list_item_height_string)
            except ValueError:
                list_item_height = 20
            if list_item_height != self.list_item_height:
                self.list_item_height = list_item_height
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

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.on_fresh_drawable_shape_ready()
