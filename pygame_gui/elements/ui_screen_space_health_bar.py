from typing import Union, Dict, Optional


from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IUIElementInterface,
)
from pygame_gui.core import UIElement
from pygame_gui.elements.ui_status_bar import UIStatusBar
from pygame_gui.core.gui_type_hints import RectLike, SpriteWithHealth


class UIScreenSpaceHealthBar(UIStatusBar):
    """
    A UI that will display health capacity and current health for a sprite in 'screen space'.
    That means it won't move with the camera. This is a good choice for a user/player sprite.

    :param relative_rect: The rectangle that defines the size and position of the health bar.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    element_id = "screen_space_health_bar"

    def __init__(
        self,
        relative_rect: RectLike,
        manager: Optional[IUIManagerInterface] = None,
        sprite_to_monitor: Optional[SpriteWithHealth] = None,
        container: Optional[IContainerLikeInterface] = None,
        parent_element: Optional[UIElement] = None,
        object_id: Optional[Union[ObjectID, str]] = None,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
    ):
        # Setting this here because UIProgressBar doesn't accept a percent_method in __init__.
        self.percent_method = self.health_percent

        # Set this using the property, for error handling.
        self.set_sprite_to_monitor(sprite_to_monitor)

        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            sprite=sprite_to_monitor,
            follow_sprite=False,
            percent_method=self.health_percent,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

    @property
    def current_health(self):
        """
        Returns the current health of the monitored sprite

        :return: an integer representing current health
        """
        return self.sprite.current_health if self.sprite else 50

    @property
    def health_capacity(self):
        """
        Returns the current health capacity of the monitored sprite

        :return: an integer representing current health capacity
        """
        return self.sprite.health_capacity if self.sprite else 100

    def health_percent(self):
        """
        Returns the current health percentage of the monitored sprite

        :return: a float representing current health capacity
        """
        return self.current_health / max(self.health_capacity, 1)

    @property
    def health_percentage(self):
        """
        Returns the current health percentage of the monitored sprite

        :return: a float representing current health capacity
        """
        # Now that we subclass UIStatusBar, this is here for backward compatibility.
        return self.health_percent()

    def set_sprite_to_monitor(self, sprite_to_monitor: Optional[SpriteWithHealth]):
        """
        Set the sprite which this health bar will display the health values of

        :param sprite_to_monitor: the sprite to monitor the health values of
        """
        if sprite_to_monitor:
            if not hasattr(sprite_to_monitor, "health_capacity"):
                raise AttributeError("Sprite does not have health_capacity attribute")
            if not hasattr(sprite_to_monitor, "current_health"):
                raise AttributeError("Sprite does not have current_health attribute")
        self.sprite = sprite_to_monitor

    def status_text(self):
        """Subclass and override this method to change what text is displayed, or to suppress the text."""
        return f"{int(self.current_health)}/{int(self.health_capacity)}"
