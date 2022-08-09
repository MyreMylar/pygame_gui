from typing import Union, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.elements.ui_status_bar import UIStatusBar


class UIScreenSpaceHealthBar(UIStatusBar):
    """
    A UI that will display health capacity and current health for a sprite in 'screen space'.
    That means it won't move with the camera. This is a good choice for a user/player sprite.

    :param relative_rect: The rectangle that defines the size and position of the health bar.
    :param manager: The UIManager that manages this element.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """
    element_id = 'screen_space_health_bar'

    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, None] = None,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, Union[str, UIElement]] = None,
                 visible: int = 1):

        # Setting this here because UIProgressBar doesn't accept a percent_method in __init__.
        self.percent_method = self.health_percent

        # Set this using the property, for error handling.
        self.set_sprite_to_monitor(sprite_to_monitor)

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         sprite=sprite_to_monitor,
                         follow_sprite=False,
                         percent_method=self.health_percent,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

    @property
    def current_health(self):
        if not self.sprite:
            return 50
        return self.sprite.current_health

    @property
    def health_capacity(self):
        if not self.sprite:
            return 100
        return self.sprite.health_capacity

    def health_percent(self):
        return self.current_health / self.health_capacity

    @property
    def health_percentage(self):
        # Now that we subclass UIStatusBar, this is here for backward compatibility.
        return self.health_percent()

    def set_sprite_to_monitor(self, sprite_to_monitor: pygame.sprite.Sprite):
        if sprite_to_monitor:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
        self.sprite = sprite_to_monitor

    def status_text(self):
        """ Subclass and override this method to change what text is displayed, or to suppress the text. """
        return f"{int(self.current_health)}/{int(self.health_capacity)}"

