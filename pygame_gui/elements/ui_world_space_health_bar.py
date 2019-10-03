import pygame

from ..core.ui_element import UIElement


class UIWorldSpaceHealthBar(UIElement):
    """
    A UI that will display a sprite's 'health_capacity' and their 'current_health' in 'world space' above the sprite.
    This means that the health bar will move with the camera and the sprite itself.
    """
    def __init__(self, relative_rect, sprite_to_monitor, ui_manager,
                 ui_container=None, element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['screen_space_health_bar']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('screen_space_health_bar')
        super().__init__(relative_rect, ui_manager, ui_container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_id=object_id)

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
            raise AssertionError('Need sprite to monitor')

        self.background_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_bg')
        self.health_empty_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'unfilled_bar')
        self.health_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'filled_bar')

        self.hover_height = 10
        self.horiz_padding = 2
        self.vert_padding = 2

        self.position = [self.sprite_to_monitor.screen_position[0] - self.sprite_to_monitor.rect.width / 2,
                         self.sprite_to_monitor.screen_position[1] - (
                                 self.sprite_to_monitor.rect.height / 2) - self.hover_height]

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        self.background_surface = pygame.Surface((self.rect.w, self.rect.h)).convert()
        self.background_surface.fill(self.background_colour)

        self.image = pygame.Surface((self.rect.w, self.rect.h)).convert()

        self.capacity_width = self.rect.width - (self.horiz_padding * 2)
        self.capacity_height = self.rect.height - (self.vert_padding * 2)
        self.health_capacity_rect = pygame.Rect([self.horiz_padding,
                                                 self.vert_padding],
                                                [self.capacity_width, self.capacity_height])

        self.current_health = 50
        self.health_capacity = 100
        self.health_percentage = self.current_health / self.health_capacity

        self.current_health_rect = pygame.Rect([self.horiz_padding,
                                                self.vert_padding],
                                               [int(self.capacity_width*self.health_percentage),
                                                self.capacity_height])

    def update(self, time_delta):
        if self.alive():
            self.position = [self.sprite_to_monitor.screen_position[0] - self.sprite_to_monitor.rect.width / 2,
                             self.sprite_to_monitor.screen_position[1] - (
                                     self.sprite_to_monitor.rect.height / 2) - self.hover_height]

            self.current_health = self.sprite_to_monitor.current_health
            self.health_capacity = self.sprite_to_monitor.base_health
            self.health_percentage = self.current_health / self.health_capacity
            self.current_health_rect.width = int(self.capacity_width * self.health_percentage)

            self.image.blit(self.background_surface, (0, 0))
            pygame.draw.rect(self.image, self.health_empty_colour, self.health_capacity_rect)
            pygame.draw.rect(self.image, self.health_colour, self.current_health_rect)

            self.rect.x = self.position[0]
            self.rect.y = self.position[1]
