from typing import Union, Dict, Tuple, List, Any

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_SELECTION_LIST_NEW_SELECTION, UI_SELECTION_LIST_DROPPED_SELECTION
from pygame import Rect, USEREVENT
from pygame.event import Event, post
from pygame.math import Vector2

from pygame_gui.core.container_interface import IContainerInterface
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.elements import UIVerticalScrollBar, UIButton


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
                 item_list: List[str],
                 manager: UIManager,
                 *,
                 allow_multiselect: bool = False,
                 container: Union[IContainerInterface, None] = None,
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
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         anchors=anchors)

        self.item_list = [[item, None, False] for item in item_list]  # type: List[List[Any]]
        self.allow_multiselect = allow_multiselect
        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.shape_corner_radius = 0
        self.shape_type = 'rectangle'

        self.scroll_bar = None
        self.total_height_of_list = 0

        self.rebuild_from_changed_theme_data()

        self.list_and_scroll_bar_container = UIContainer(
            Rect(self.relative_rect.left + self.shadow_width + self.border_width,
                 self.relative_rect.top + self.shadow_width + self.border_width,
                 self.relative_rect.width - (2 * self.shadow_width) - (2 * self.border_width),
                 self.relative_rect.height - (2 * self.shadow_width) - (2 * self.border_width)),
            manager=self.ui_manager,
            container=self.ui_container,
            parent_element=parent_element,
            object_id='#selection_list_container')

        self.height_of_single_item_in_list = 20

        self.total_height_of_list = self.height_of_single_item_in_list * len(self.item_list)

        self.lowest_list_pos = self.total_height_of_list - self.list_and_scroll_bar_container.relative_rect.height

        inner_visible_area_height = self.relative_rect.height - (2 * self.shadow_width) - (2 * self.border_width)

        scroll_bar_width = 0
        if self.total_height_of_list > inner_visible_area_height:
            # we need a scroll bar
            scroll_bar_width = 20
            percentage_visible = inner_visible_area_height / max(self.total_height_of_list, 1)
            self.scroll_bar = UIVerticalScrollBar(Rect(-scroll_bar_width,
                                                       0,
                                                       scroll_bar_width,
                                                       inner_visible_area_height),
                                                  visible_percentage=percentage_visible,
                                                  manager=self.ui_manager,
                                                  parent_element=self,
                                                  container=self.list_and_scroll_bar_container,
                                                  anchors={'left': 'right',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'bottom'})

        # create button list container
        self.item_list_container = UIContainer(
            Rect(0, 0,
                 self.list_and_scroll_bar_container.relative_rect.width - scroll_bar_width,
                 self.list_and_scroll_bar_container.relative_rect.height),
            manager=self.ui_manager,
            parent_element=parent_element,
            container=self.list_and_scroll_bar_container,
            object_id='#item_list_container',
            anchors={'left': 'left',
                     'right': 'right',
                     'top': 'top',
                     'bottom': 'bottom'})
        item_y_height = 0
        for item in self.item_list:
            if item_y_height <= self.item_list_container.relative_rect.height:
                item[1] = UIButton(relative_rect=Rect(0, item_y_height,
                                                      self.item_list_container.relative_rect.width,
                                                      self.height_of_single_item_in_list),
                                   text=item[0],
                                   manager=self.ui_manager,
                                   container=self.item_list_container,
                                   object_id='#item_list_item',
                                   anchors={'left': 'left',
                                            'right': 'right',
                                            'top': 'top',
                                            'bottom': 'top'})
                item_y_height += self.height_of_single_item_in_list
            else:
                break

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
            for index, button_item in enumerate(self.item_list):
                new_height = (index * self.height_of_single_item_in_list) - list_height_adjustment
                if -self.height_of_single_item_in_list <= new_height <= self.item_list_container.relative_rect.height:
                    if button_item[1] is not None:
                        button_item[1].set_relative_position((0, new_height))
                    else:
                        button_item[1] = UIButton(relative_rect=Rect(0, new_height,
                                                                     self.item_list_container.relative_rect.width,
                                                                     self.height_of_single_item_in_list),
                                                  text=button_item[0],
                                                  manager=self.ui_manager,
                                                  container=self.item_list_container,
                                                  object_id='#item_list_item',
                                                  anchors={'left': 'left',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})
                        if button_item[2]:
                            button_item[1].select()
                else:
                    if button_item[1] is not None:
                        button_item[1].kill()
                        button_item[1] = None

    def process_event(self, event: Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.
        :return bool: Should return True if this element makes use of this event.
        """
        handled = False
        if (event.type == USEREVENT and event.user_type == UI_BUTTON_PRESSED and
                event.ui_element in self.item_list_container.elements):
            handled = True

            for item in self.item_list:
                if item[1] == event.ui_element:
                    if item[2]:
                        item[2] = False
                        event.ui_element.unselect()

                        event_data = {'user_type': UI_SELECTION_LIST_DROPPED_SELECTION,
                                      'text': event.ui_element.text,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}

                    else:
                        item[2] = True
                        event.ui_element.select()

                        event_data = {'user_type': UI_SELECTION_LIST_NEW_SELECTION,
                                      'text': event.ui_element.text,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}

                    drop_down_changed_event = Event(USEREVENT, event_data)
                    post(drop_down_changed_event)
                elif not self.allow_multiselect:
                    if item[2]:
                        item[2] = False
                        if item[1] is not None:
                            item[1].unselect()

                            event_data = {'user_type': UI_SELECTION_LIST_DROPPED_SELECTION,
                                          'text': item[0],
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            drop_down_changed_event = Event(USEREVENT, event_data)
                            post(drop_down_changed_event)

        return handled

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
