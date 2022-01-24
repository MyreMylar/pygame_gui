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
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        self.font = None
        self.text_shadow_colour = None
        self.text_colour = None
        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1
        self.background_text = None
        self.foreground_text = None
        self._sprite_to_monitor = None

        # Set this using the property, for error handling.
        self.sprite_to_monitor = sprite_to_monitor

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         display_sprite=None,
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
        return self.current_health / self.health_capacity

    @property
    def health_percentage(self):
        # Now that we subclass UIStatusBar, this is here for backward compatibility.
        return self.health_percent()

    @property
    def sprite_to_monitor(self):
        """ Sprite to monitor the health of. Must have 'health_capacity' and 'current_health'
        attributes. """
        return self._sprite_to_monitor

    @sprite_to_monitor.setter
    def sprite_to_monitor(self, sprite: pygame.sprite.Sprite):
        if sprite:
            if not hasattr(sprite, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
        self._sprite_to_monitor = sprite

    def set_sprite_to_monitor(self, sprite_to_monitor: pygame.sprite.Sprite):
        # This method is here for backward compatibility.
        self.sprite_to_monitor = sprite_to_monitor

    @property
    def health_display_string(self):
        """ Subclass and override this property to change what text is displayed, or to suppress the text. """
        return f"{self.current_health:0.1f}/{self.health_capacity:0.1f}"

    def redraw(self, theming_parameters=None):
        """
        Redraws the health bar rectangles and text onto the underlying sprite's image surface.
        Takes a little while so we only do it when the health has changed.
        """
        if theming_parameters is None:
            theming_parameters = {}

        parameters = {'font': self.font,
                      'text': self.health_display_string,
                      'normal_text': self.text_colour,
                      'normal_text_shadow': self.text_shadow_colour,
                      'text_shadow': (1,
                                      0,
                                      0,
                                      self.text_shadow_colour,
                                      False),
                      'text_horiz_alignment': self.text_horiz_alignment,
                      'text_vert_alignment': self.text_vert_alignment,
                      'text_horiz_alignment_padding': self.text_horiz_alignment_padding,
                      'text_vert_alignment_padding': self.text_vert_alignment_padding,
                      }

        # If there are duplicate entries, let the subclass's values overwrite mine.
        parameters.update(theming_parameters)
        super().redraw(parameters)

    def rebuild_from_changed_theme_data(self, has_any_changed=False):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.

        :param has_any_changed: allows subclasses to do their own theme check and pass this along.
        """

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        text_shadow_colour = self.ui_theme.get_colour('text_shadow', self.combined_element_ids)
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            has_any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient('normal_text', self.combined_element_ids)
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            has_any_changed = True

        super().rebuild_from_changed_theme_data(has_any_changed)
