import pygame
from typing import Union, Tuple

from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.elements import ui_button
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIVerticalScrollBar(UIElement):
    """
    A vertical scroll bar allows users to position a smaller visible area within a vertically larger area.

    :param relative_rect: The size and position of the scroll bar.
    :param visible_percentage: The vertical percentage of the larger area that is visible, between 0.0 and 1.0.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 visible_percentage: float,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='vertical_scroll_bar')
        super().__init__(relative_rect, manager, container,
                         layer_thickness=2, starting_height=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids)

        self.button_height = 20
        self.scroll_position = 0.0
        self.top_limit = 0.0
        self.starting_grab_y_difference = 0
        self.visible_percentage = max(0.0, min(visible_percentage, 1.0))
        self.start_percentage = 0.0

        self.grabbed_slider = False
        self.has_moved_recently = False
        self.scroll_wheel_up = False
        self.scroll_wheel_down = False

        self.background_colour = None
        self.border_colour = None
        self.border_width = None
        self.shadow_width = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        self.background_rect = None
        self.border_rect = None
        self.relative_background_rect = None

        self.scrollable_height = None  # type: Union[None, int, float]
        self.bottom_limit = None
        self.sliding_rect_position = None

        self.top_button = None
        self.bottom_button = None
        self.sliding_button = None

        self.rebuild_from_changed_theme_data()

        self.top_button = ui_button.UIButton(pygame.Rect(self.background_rect.topleft,
                                                         (self.background_rect.width, self.button_height)),
                                             '▲', self.ui_manager,
                                             container=self.ui_container,
                                             starting_height=2,
                                             parent_element=self,
                                             object_id="#top_button")

        bottom_button_y = self.background_rect.y + self.background_rect.height - self.button_height
        self.bottom_button = ui_button.UIButton(pygame.Rect((self.background_rect.x,
                                                             bottom_button_y),
                                                            (self.background_rect.width,
                                                             self.button_height)),
                                                '▼', self.ui_manager,
                                                container=self.ui_container,
                                                starting_height=2,
                                                parent_element=self,
                                                object_id="#bottom_button")

        scroll_bar_height = max(5, int(self.scrollable_height * self.visible_percentage))
        self.sliding_button = ui_button.UIButton(pygame.Rect((int(self.sliding_rect_position[0]),
                                                              int(self.sliding_rect_position[1])),
                                                             (self.background_rect.width,
                                                              scroll_bar_height)),
                                                 '', self.ui_manager,
                                                 container=self.ui_container,
                                                 starting_height=2,
                                                 parent_element=self,
                                                 object_id="#sliding_button")

        self.sliding_button.set_hold_range((100, self.background_rect.height))

    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """
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

        self.scrollable_height = self.background_rect.height - (2 * self.button_height)
        self.bottom_limit = self.scrollable_height

        x_pos = self.relative_rect.x + self.shadow_width + self.border_width
        y_pos = self.relative_rect.y + self.scroll_position + self.shadow_width + self.border_width + self.button_height
        self.sliding_rect_position = pygame.math.Vector2(x_pos, y_pos)

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

        if self.top_button is not None:
            self.top_button.set_relative_position(self.background_rect.topleft),
            self.top_button.set_dimensions((self.background_rect.width, self.button_height))

        if self.bottom_button is not None:
            bottom_button_y = self.background_rect.y + self.background_rect.height - self.button_height
            self.bottom_button.set_relative_position((self.background_rect.x, bottom_button_y)),
            self.bottom_button.set_dimensions((self.background_rect.width, self.button_height))

        if self.sliding_button is not None:
            scroll_bar_height = max(5, int(self.scrollable_height * self.visible_percentage))
            self.sliding_button.set_relative_position(self.sliding_rect_position)
            self.sliding_button.set_dimensions((self.background_rect.width, scroll_bar_height))
            self.sliding_button.set_hold_range((100, self.background_rect.height))

    def check_has_moved_recently(self) -> bool:
        """
        Returns True if the scroll bar was moved in the last call to the update function.

        :return bool: True if we've recently moved the scroll bar, False otherwise.
        """
        return self.has_moved_recently

    def kill(self):
        """
        Overrides the kill() method of the UI element class to kill all the buttons in the scroll bar and
        clear any of the parts of the scroll bar that are currently recorded as the 'last focused vertical scroll bar
        element' on the ui manager.

        NOTE: the 'last focused' state on the UI manager is used so that the mouse wheel will move whichever scrollbar
        we last fiddled with even if we've been doing other stuff. This seems to be consistent with the most common
        mousewheel/scrollbar interactions used elsewhere.
        """
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.sliding_button)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.top_button)
        self.ui_manager.clear_last_focused_from_vert_scrollbar(self.bottom_button)
        super().kill()
        self.top_button.kill()
        self.bottom_button.kill()
        self.sliding_button.kill()

    def select(self):
        """
        When we focus select the scroll bar as a whole for any reason we pass that status down to the 'bar' part of
        the scroll bar.
        """
        if self.sliding_button is not None:
            self.ui_manager.unselect_focus_element()
            self.ui_manager.select_focus_element(self.sliding_button)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Checks an event from pygame's event queue to see if the scroll bar needs to react to it. In this case
        it is just mousewheel events, mainly because the buttons that make up the scroll bar will handle the required
        mouse click events.

        :param event: The event to process.
        :return bool: Returns True if we've done something with the input event.
        """

        # pygame.MOUSEWHEEL only defined after pygame 1.9
        try:
            pygame.MOUSEWHEEL
        except AttributeError:
            pygame.MOUSEWHEEL = -1

        processed_event = False
        last_focused_scrollbar_element = self.ui_manager.get_last_focused_vert_scrollbar()
        if ((last_focused_scrollbar_element is self) or (
                    last_focused_scrollbar_element is self.sliding_button) or (
                    last_focused_scrollbar_element is self.top_button) or (
                last_focused_scrollbar_element is self.bottom_button
            )) and event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_wheel_up = True
                processed_event = True
            elif event.y < 0:
                self.scroll_wheel_down = True
                processed_event = True

        return processed_event

    def update(self, time_delta: float):
        """
        Called once per update loop of our UI manager. Deals largely with moving the scroll bar and updating the
        resulting 'start_percentage' variable that is then used by other 'scrollable' UI elements to control the point
        they start drawing.

        Reacts to presses of the up and down arrow buttons, movement of the mouse wheel and dragging of the scroll
        bar itself.

        :param time_delta: A float, roughly representing the time in seconds between calls to this method.
        """
        self.has_moved_recently = False
        if self.alive():
            moved_this_frame = False
            if (self.top_button.held or self.scroll_wheel_up) and self.scroll_position > self.top_limit:
                self.scroll_wheel_up = False
                self.scroll_position -= (250.0 * time_delta)
                self.scroll_position = max(self.scroll_position, self.top_limit)
                x_pos = self.rect.x + self.shadow_width + self.border_width
                y_pos = self.scroll_position + self.rect.y + self.shadow_width + self.border_width + self.button_height
                self.sliding_button.set_position(pygame.math.Vector2(x_pos, y_pos))
                moved_this_frame = True
            elif (self.bottom_button.held or self.scroll_wheel_down) and self.scroll_position < self.bottom_limit:
                self.scroll_wheel_down = False
                self.scroll_position += (250.0 * time_delta)
                self.scroll_position = min(self.scroll_position,
                                           self.bottom_limit - self.sliding_button.rect.height)
                x_pos = self.rect.x + self.shadow_width + self.border_width
                y_pos = self.scroll_position + self.rect.y + self.shadow_width + self.border_width + self.button_height
                self.sliding_button.set_position(pygame.math.Vector2(x_pos, y_pos))

                moved_this_frame = True

            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            if self.sliding_button.held and self.sliding_button.in_hold_range((mouse_x, mouse_y)):

                if not self.grabbed_slider:
                    self.grabbed_slider = True
                    real_scroll_pos = (self.scroll_position + self.rect.y + self.button_height +
                                       self.shadow_width + self.border_width)
                    self.starting_grab_y_difference = mouse_y - real_scroll_pos

                real_scroll_pos = (self.scroll_position + self.rect.y + self.button_height +
                                   self.shadow_width + self.border_width)
                current_grab_difference = mouse_y - real_scroll_pos
                adjustment_required = current_grab_difference - self.starting_grab_y_difference
                self.scroll_position = self.scroll_position + adjustment_required

                self.scroll_position = min(max(self.scroll_position, self.top_limit),
                                           self.bottom_limit - self.sliding_button.rect.height)

                x_pos = self.rect.x + self.shadow_width + self.border_width
                y_pos = self.scroll_position + self.rect.y + self.shadow_width + self.border_width + self.button_height
                self.sliding_button.set_position(pygame.math.Vector2(x_pos, y_pos))
                moved_this_frame = True
            elif not self.sliding_button.held:
                self.grabbed_slider = False

            if moved_this_frame:
                self.start_percentage = self.scroll_position / self.scrollable_height
                if not self.has_moved_recently:
                    self.has_moved_recently = True

    def redraw_scrollbar(self):
        """
        Redraws the 'scrollbar' portion of the whole UI element. Called when we change the visible percentage.
        """
        self.sliding_button.kill()

        self.scrollable_height = (self.rect.height - (2 * self.button_height) -
                                  (2 * self.border_width) - (2 * self.shadow_width))
        scroll_bar_height = max(5, int(self.scrollable_height * self.visible_percentage))
        self.sliding_rect_position.y = (self.rect.y + self.button_height +
                                        self.shadow_width + self.border_width +
                                        int(self.start_percentage * self.scrollable_height))
        self.sliding_button = ui_button.UIButton(pygame.Rect(int(self.sliding_rect_position[0]),
                                                             int(self.sliding_rect_position[1]),
                                                             (self.rect.width - (2 * self.border_width) -
                                                              (2 * self.shadow_width)),
                                                             scroll_bar_height),
                                                 '', self.ui_manager,
                                                 container=self.ui_container,
                                                 starting_height=2,
                                                 parent_element=self,
                                                 object_id="#sliding_button")

    def set_visible_percentage(self, percentage: float):
        """
        Sets the percentage of the total 'scrollable area' that is currently visible. This will affect the size of
        the scrollbar and should be called if the vertical size of the 'scrollable area' or the vertical size of the
        visible area change.

        :param percentage: A float between 0.0 and 1.0 representing the percentage that is visible.
        """
        self.visible_percentage = max(0.0, min(1.0, percentage))
        if 1.0 - self.start_percentage < self.visible_percentage:
            self.start_percentage = 1.0 - self.visible_percentage

        self.redraw_scrollbar()

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
