from typing import Union, Dict, Tuple

from pygame import Rect
from pygame.math import Vector2
from pygame.event import Event
from pygame.constants import MOUSEBUTTONDOWN

from pygame_gui.core.container_interface import IContainerInterface
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIPanel(UIElement, IContainerInterface):
    """
    A rectangular panel that holds a UI container and is designed to overlap other elements. It acts a little like a
    window that is not shuffled about in a stack - instead remaining at the same layer distance from the container
    it was initially placed in.

    It's primary purpose is for things like involved HUDs in games that want to always sit on top of UI elements that
    may be present 'inside' the game world (e.g. player health bars). By creating a UI Panel at a height above the
    highest layer used by the game world's UI elements we can ensure that all elements added to the panel are always
    above the fray.

    :param relative_rect: The positioning and sizing rectangle for the panel. See the layout guide for details.
    :param manager: The GUI manager that handles drawing and updating the UI and interactions between elements.
    :param panel_container_margins: Margins indicating the distance between the edge of the panel and where it's container should begin.
    :param container: The container this panel is inside of (by default the root container) distinct from this panel's container.
    :param parent_element: A hierarchical 'parent' used for signifying belonging and used in theming and events.
    :param object_id: An identifier that can be used to help distinguish this particular panel from others with the same hierarchy.
    :param anchors: Used to layout elements and dictate what the relative_rect is relative to. Defaults to the top left.
    """
    def __init__(self, relative_rect: Rect,
                 starting_layer_height: int,
                 manager: UIManager,
                 *,
                 element_id: str = 'panel',
                 panel_container_margins: Dict[str, int] = None,
                 container: Union[IContainerInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None
                 ):
        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id=element_id)
        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=starting_layer_height, layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         anchors=anchors)

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.shape_corner_radius = 0
        self.shape_type = 'rectangle'

        self.rebuild_from_changed_theme_data()

        if panel_container_margins is None:
            self.container_margins = {'left': self.shadow_width + self.border_width,
                                      'right': self.shadow_width + self.border_width,
                                      'top': self.shadow_width + self.border_width,
                                      'bottom': self.shadow_width + self.border_width}
        else:
            self.container_margins = panel_container_margins

        relative_container_rect = Rect(self.relative_rect.left + self.container_margins['left'],
                                       self.relative_rect.top + self.container_margins['top'],
                                       self.relative_rect.width - (self.container_margins['left'] +
                                                                   self.container_margins['right']),
                                       self.relative_rect.height - (self.container_margins['top'] +
                                                                    self.container_margins['bottom']))

        self.panel_container = UIContainer(relative_container_rect, manager,
                                           starting_height=starting_layer_height,
                                           parent_element=self, object_id='#panel_container')

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived classes
        but also has a little functionality to make sure the panel's layer 'thickness' is accurate and to handle
        window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        super().update(time_delta)
        if self.get_container().layer_thickness != self.layer_thickness:
            self.layer_thickness = self.get_container().layer_thickness

    def process_event(self, event: Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.
        :return bool: Should return True if this element makes use of this event.
        """
        consumed_event = False
        if self is not None and event.type == MOUSEBUTTONDOWN and event.button in [1, 3]:
            scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))

            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                consumed_event = True

        return consumed_event

    def get_container(self) -> UIContainer:
        """
        Returns the container that should contain all the UI elements in this panel.

        :return UIContainer: The panel's container.
        """
        return self.panel_container

    def set_dimensions(self, dimensions: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Set the size of this panel and then resizes and shifts the contents of the panel container to fit the new
        size.

        :param dimensions:
        """
        # Don't use a basic gate on this set dimensions method because the container may be a different size to the
        # window
        super().set_dimensions(dimensions)

        new_container_dimensions = (self.relative_rect.width - (self.container_margins['left'] +
                                                                self.container_margins['right']),
                                    self.relative_rect.height - (self.container_margins['top'] +
                                                                 self.container_margins['bottom']))
        if new_container_dimensions != self.get_container().relative_rect.size:
            self.get_container().set_dimensions(new_container_dimensions)
            self.get_container().set_relative_position((self.relative_rect.x + self.container_margins['left'],
                                                        self.relative_rect.y + self.container_margins['top']))

    def set_relative_position(self, position: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_relative_position(position)

        self.get_container().set_relative_position((self.relative_rect.x + self.container_margins['left'],
                                                    self.relative_rect.y + self.container_margins['top']))

    def set_position(self, position: Union[Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_position(position)

        self.get_container().set_relative_position((self.relative_rect.x + self.container_margins['left'],
                                                    self.relative_rect.y + self.container_margins['top']))

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI elements in this panel.

        """
        self.get_container().kill()
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

        background_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'background_image')
        if background_image is not None and background_image != self.background_image:
            self.background_image = background_image
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
        A complete rebuild of the drawable shape used by this button.

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
