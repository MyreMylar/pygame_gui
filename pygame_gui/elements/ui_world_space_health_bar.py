import pygame
from typing import Union, Dict

from pygame_gui import ui_manager
from pygame_gui.core.container_interface import IContainerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIWorldSpaceHealthBar(UIElement):
    """
    A UI that will display a sprite's 'health_capacity' and their 'current_health' in 'world space' above the sprite.
    This means that the health bar will move with the camera and the sprite itself.

    A sprite passed to this class must have the attributes 'health_capacity' and 'current_health'.

    :param relative_rect: The rectangle that defines the size of the health bar.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """

    class ExampleHealthSprite(pygame.sprite.Sprite):
        def __init__(self, *groups):
            super().__init__(*groups)
            self.current_health = 50
            self.health_capacity = 100
            self.rect = pygame.Rect(0, 0, 32, 64)

    def __init__(self, relative_rect: pygame.Rect,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, ExampleHealthSprite],
                 manager: ui_manager.UIManager,
                 container: Union[IContainerInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='world_space_health_bar')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids,
                         anchors=anchors)

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
            raise AssertionError('Need sprite to monitor')

        self.current_health = self.sprite_to_monitor.current_health
        self.health_capacity = self.sprite_to_monitor.health_capacity
        self.health_percentage = self.current_health / self.health_capacity

        self.border_colour = None
        self.health_empty_colour = None
        self.bar_filled_colour = None
        self.bar_unfilled_colour = None
        self.health_colour = None
        self.hover_height = None
        self.border_width = None
        self.shadow_width = None
        self.position = None
        self.border_rect = None
        self.capacity_width = None
        self.capacity_height = None
        self.health_capacity_rect = None
        self.current_health_rect = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        self.set_image(None)

        self.rebuild_from_changed_theme_data()

    def rebuild(self):
        """
        Rebuild the health bar entirely because the theming data has changed.

        """

        self.position = [self.sprite_to_monitor.rect.x,
                         self.sprite_to_monitor.rect.y - self.hover_height]

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        self.border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                       (self.rect.width - (self.shadow_width * 2),
                                        self.rect.height - (self.shadow_width * 2)))

        self.capacity_width = self.rect.width - (self.shadow_width * 2) - (self.border_width * 2)
        self.capacity_height = self.rect.height - (self.shadow_width * 2) - (self.border_width * 2)
        self.health_capacity_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                 self.border_width + self.shadow_width),
                                                (self.capacity_width, self.capacity_height))

        self.current_health_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                self.border_width + self.shadow_width),
                                               (int(self.capacity_width * self.health_percentage),
                                                self.capacity_height))

        self.redraw()

    def update(self, time_delta: float):
        """
        Updates the health bar sprite's image and rectangle with the latest health and position data from the
        sprite we are monitoring

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        super().update(time_delta)
        if self.alive():
            self.position = [self.sprite_to_monitor.rect.x,
                             self.sprite_to_monitor.rect.y - self.hover_height]

            self.rect.x = self.position[0]
            self.rect.y = self.position[1]
            self.relative_rect.topleft = self.rect.topleft

            if (self.current_health != self.sprite_to_monitor.current_health) or (
                    self.health_capacity != self.sprite_to_monitor.health_capacity):

                self.current_health = self.sprite_to_monitor.current_health
                self.health_capacity = self.sprite_to_monitor.health_capacity
                self.health_percentage = self.current_health / self.health_capacity

                self.redraw()

    def redraw(self):
        """
        Redraw the health bar when something, other than it's position has changed.
        """
        self.current_health_rect.width = int(self.capacity_width * self.health_percentage)

        theming_parameters = {'normal_bg': self.bar_unfilled_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius,
                              'filled_bar': self.bar_filled_colour,
                              'filled_bar_width_percentage': self.health_percentage}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.set_image(self.drawable_shape.get_surface('normal'))

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

        hover_height = 1
        hover_height_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'hover_height')
        if hover_height_string is not None:
            try:
                hover_height = int(hover_height_string)
            except ValueError:
                hover_height = 1

        if hover_height != self.hover_height:
            self.hover_height = hover_height
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

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        bar_unfilled_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'unfilled_bar')
        if bar_unfilled_colour != self.bar_unfilled_colour:
            self.bar_unfilled_colour = bar_unfilled_colour
            has_any_changed = True

        bar_filled_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'filled_bar')
        if bar_filled_colour != self.bar_filled_colour:
            self.bar_filled_colour = bar_filled_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
