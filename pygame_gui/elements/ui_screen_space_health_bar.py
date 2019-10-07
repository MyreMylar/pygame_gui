import pygame
from typing import List, Union

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement


class UIScreenSpaceHealthBar(UIElement):
    """
    A UI that will display health capacity and current health for a sprite in 'screen space'.
    That means it won't move with the camera. This is a good choice for a user/player sprite.

    :param relative_rect: The rectangle that defines the size and position of the health bar.
    :param manager: The UIManager that manages this element.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param element_ids: A list of ids that describe the 'journey' of UIElements that this UIElement is part of.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 manager: ui_manager.UIManager,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, None]=None,
                 container: ui_container.UIContainer = None,
                 element_ids: Union[List[str], None] = None, object_id: Union[str, None] = None):
        if element_ids is None:
            new_element_ids = ['screen_space_health_bar']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('screen_space_health_bar')

        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_id=object_id)

        self.font = self.ui_theme.get_font(self.object_id, self.element_ids)

        self.background_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_bg')
        self.border_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'border')
        self.bar_unfilled_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'unfilled_bar')
        self.bar_filled_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'filled_bar')
        self.text_shadow_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'text_shadow')
        self.text_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_text')

        self.padding = (3, 3)
        self.border = (1, 1)

        border_rect_width = self.rect.width - (self.padding[0] * 2)
        border_rect_height = self.rect.height - (self.padding[1] * 2)
        self.border_rect = pygame.Rect((self.rect.x + self.padding[0],
                                        self.rect.y + self.padding[1]),
                                       (border_rect_width, border_rect_height))

        self.capacity_width = self.rect.width - (self.padding[0] * 2) - self.border[0] * 2
        self.capacity_height = self.rect.height - (self.padding[1] * 2) - self.border[1] * 2
        self.capacity_rect = pygame.Rect((self.rect.x + self.padding[0] + self.border[0],
                                          self.rect.y + self.padding[1] + self.border[1]),
                                         (self.capacity_width, self.capacity_height))

        self.current_health = 50
        self.health_capacity = 100
        self.health_percentage = self.current_health / self.health_capacity

        self.current_health_rect = pygame.Rect((self.rect.x + self.padding[0] + self.border[0],
                                                self.rect.y + self.padding[1] + self.border[1]),
                                               (int(self.capacity_width * self.health_percentage),
                                                self.capacity_height))

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
        self.image = None
        self.background_text = None
        self.foreground_text = None

        self.redraw()

    def set_sprite_to_monitor(self, sprite_to_monitor: pygame.sprite.Sprite):
        """
        Sprite to monitor the health of. Must have 'health_capacity' and 'current_health' attributes.

        :param sprite_to_monitor:
        """
        if not hasattr(sprite_to_monitor, 'health_capacity'):
            raise AttributeError
        if not hasattr(sprite_to_monitor, 'current_health'):
            raise AttributeError
        self.sprite_to_monitor = sprite_to_monitor

    def redraw(self):
        """
        Redraws the health bar rectangles and text onto the underlying sprite's image surface.
        Takes a little while so we only do it when the health has changed.
        """
        self.image = pygame.Surface((self.rect.w, self.rect.h))
        self.image.fill(self.background_colour)
        self.image.set_alpha(175)

        border = pygame.Surface((self.border_rect.w, self.border_rect.h))
        border.fill(self.border_colour)
        self.image.blit(border, self.padding)

        capacity = pygame.Surface((self.capacity_rect.w, self.capacity_rect.h))
        capacity.fill(self.bar_unfilled_colour)
        self.image.blit(capacity, (self.padding[0] + self.border[0],
                                   self.padding[1] + self.border[1]))

        current_health = pygame.Surface((self.current_health_rect.w, self.current_health_rect.h))
        current_health.fill(self.bar_filled_colour)
        self.image.blit(current_health, (self.padding[0] + self.border[0],
                                         self.padding[1] + self.border[1]))

        self.background_text = self.font.render(
            str(self.current_health) + "/" + str(self.health_capacity),
            True, self.text_shadow_colour)

        self.foreground_text = self.font.render(
            str(self.current_health) + "/" + str(self.health_capacity),
            True, self.text_colour)

        self.image.blit(self.background_text,
                        self.background_text.get_rect(centerx=self.rect.width/2,
                                                      centery=self.rect.height/2 + 1))
        self.image.blit(self.background_text,
                        self.background_text.get_rect(centerx=self.rect.width/2,
                                                      centery=self.rect.height/2 - 1))

        self.image.blit(self.background_text,
                        self.background_text.get_rect(centerx=self.rect.width/2 + 1,
                                                      centery=self.rect.height/2))
        self.image.blit(self.background_text,
                        self.background_text.get_rect(centerx=self.rect.width/2 - 1,
                                                      centery=self.rect.height/2))

        self.image.blit(self.foreground_text,
                        self.foreground_text.get_rect(centerx=self.rect.width/2,
                                                      centery=self.rect.height/2))

    def update(self, time_delta: float):
        """
        Updates the health bar sprite's image with the latest health data from the
        sprite we are monitoring. Only triggers a redraw if the health values have changed.

        :param time_delta: time passed in seconds between one call to this method and the next.
        """
        if self.alive():
            if self.sprite_to_monitor is not None:
                if self.sprite_to_monitor.health_capacity != self.health_capacity or\
                        self.current_health != self.sprite_to_monitor.current_health:
                    self.current_health = self.sprite_to_monitor.current_health
                    self.health_capacity = self.sprite_to_monitor.health_capacity
                    self.health_percentage = self.current_health / self.health_capacity

                    self.current_health_rect = pygame.Rect((self.rect.x + self.padding[0] + self.border[0],
                                                            self.rect.y + self.padding[1] + self.border[1]),
                                                           (int(self.capacity_width * self.health_percentage),
                                                            self.capacity_height))
                    self.redraw()
