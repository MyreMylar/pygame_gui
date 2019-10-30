import pygame
from typing import List, Union

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement


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
    def __init__(self, relative_rect: pygame.Rect,
                 sprite_to_monitor: pygame.sprite.Sprite,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='world_space_health_bar')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids)

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
            raise AssertionError('Need sprite to monitor')

        self.border_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'border')
        self.health_empty_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'unfilled_bar')
        self.health_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'filled_bar')

        self.hover_height = 10
        hover_height_param = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'hover_height')
        if hover_height_param is not None:
            self.hover_height = int(hover_height_param)

        self.border_width = 1
        border_width_param = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_param is not None:
            self.border_width = int(border_width_param)

        self.shadow_width = 1
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            self.shadow_width = int(shadow_width_string)

        self.position = [self.sprite_to_monitor.rect.x,
                         self.sprite_to_monitor.rect.y - self.hover_height]

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        self.image = pygame.Surface((self.rect.w, self.rect.h), flags=pygame.SRCALPHA)

        self.border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                       (self.rect.width - (self.shadow_width * 2),
                                        self.rect.height - (self.shadow_width * 2)))

        self.capacity_width = self.rect.width - (self.shadow_width * 2) - (self.border_width * 2)
        self.capacity_height = self.rect.height - (self.shadow_width * 2) - (self.border_width * 2)
        self.health_capacity_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                 self.border_width + self.shadow_width),
                                                (self.capacity_width, self.capacity_height))

        self.current_health = 0
        self.health_capacity = 0
        self.health_percentage = 0.0

        self.current_health_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                self.border_width + self.shadow_width),
                                               (int(self.capacity_width*self.health_percentage),
                                                self.capacity_height))

    def update(self, time_delta: float):
        """
        Updates the health bar sprite's image and rectangle with the latest health and position data from the
        sprite we are monitoring

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        if self.alive():
            self.position = [self.sprite_to_monitor.rect.x,
                             self.sprite_to_monitor.rect.y - self.hover_height]

            self.rect.x = self.position[0]
            self.rect.y = self.position[1]

            if (self.current_health != self.sprite_to_monitor.current_health) or (
                    self.health_capacity != self.sprite_to_monitor.health_capacity):

                self.current_health = self.sprite_to_monitor.current_health
                self.health_capacity = self.sprite_to_monitor.health_capacity
                self.health_percentage = self.current_health / self.health_capacity
                self.current_health_rect.width = int(self.capacity_width * self.health_percentage)

                if self.shadow_width > 0:
                    self.image = self.ui_manager.get_shadow(self.rect.size)
                else:
                    self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

                self.image.fill(self.border_colour, self.border_rect)
                self.image.fill(self.health_empty_colour, self.health_capacity_rect)
                self.image.fill(self.health_colour, self.current_health_rect)
