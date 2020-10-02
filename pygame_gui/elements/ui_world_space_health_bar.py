from typing import Union, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIWorldSpaceHealthBar(UIElement):
    """
    A UI that will display a sprite's 'health_capacity' and their 'current_health' in 'world space'
    above the sprite. This means that the health bar will move with the camera and the sprite
    itself.

    A sprite passed to this class must have the attributes 'health_capacity' and 'current_health'.

    :param relative_rect: The rectangle that defines the size of the health bar.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    class ExampleHealthSprite(pygame.sprite.Sprite):
        """
        An example sprite with health instance attributes.

        :param groups: Sprite groups to put the sprite in.

        """
        def __init__(self, *groups):
            super().__init__(*groups)
            self.current_health = 50
            self.health_capacity = 100
            self.rect = pygame.Rect(0, 0, 32, 64)

    def __init__(self,
                 relative_rect: pygame.Rect,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, ExampleHealthSprite],
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='world_space_health_bar')

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
        self.shape = 'rectangle'
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
        Updates the health bar sprite's image and rectangle with the latest health and position
        data from the sprite we are monitoring

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if self.alive():
            self.position = [self.sprite_to_monitor.rect.x,
                             self.sprite_to_monitor.rect.y - self.hover_height]

            self.rect.x = self.position[0]
            self.rect.y = self.position[1]
            self.relative_rect.topleft = self.rect.topleft

            if (self.current_health != self.sprite_to_monitor.current_progress) or (
                    self.health_capacity != self.sprite_to_monitor.maximum_progress):

                self.current_health = self.sprite_to_monitor.current_progress
                self.health_capacity = self.sprite_to_monitor.maximum_progress
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

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.set_image(self.drawable_shape.get_fresh_surface())

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()

        has_any_changed = False

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

        if self._check_misc_theme_data_changed(attribute_name='hover_height',
                                               default_value=1,
                                               casting_func=int):
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient('normal_border',
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        bar_unfilled_colour = self.ui_theme.get_colour_or_gradient('unfilled_bar',
                                                                   self.combined_element_ids)
        if bar_unfilled_colour != self.bar_unfilled_colour:
            self.bar_unfilled_colour = bar_unfilled_colour
            has_any_changed = True

        bar_filled_colour = self.ui_theme.get_colour_or_gradient('filled_bar',
                                                                 self.combined_element_ids)
        if bar_filled_colour != self.bar_filled_colour:
            self.bar_filled_colour = bar_filled_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
