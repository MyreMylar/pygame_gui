from typing import Union, Dict, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.elements.ui_status_bar import UIStatusBar
from pygame_gui.core.gui_type_hints import RectLike


class UIWorldSpaceHealthBar(UIStatusBar):
    """
    A UI that will display a sprite's 'health_capacity' and their 'current_health' in 'world space'
    above the sprite. This means that the health bar will move with the camera and the sprite
    itself.

    A sprite passed to this class must have the attributes 'health_capacity' and 'current_health'.

    :param relative_rect: The rectangle that defines the size of the health bar.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
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

    element_id = 'world_space_health_bar'

    def __init__(self,
                 relative_rect: RectLike,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, ExampleHealthSprite],
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
            if self.__class__ == UIWorldSpaceHealthBar:
                raise AssertionError('Need sprite to monitor')

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         sprite=sprite_to_monitor,
                         percent_method=self.health_percent,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

    @property
    def current_health(self):
        return self.sprite_to_monitor.current_health

    @property
    def health_capacity(self):
        return self.sprite_to_monitor.health_capacity

    def health_percent(self):
        return self.current_health / max(self.health_capacity, 1)
