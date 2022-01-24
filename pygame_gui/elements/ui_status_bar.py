from typing import Union, Dict, Callable

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIStatusBar(UIElement):
    """
    Displays a status/progress bar.

    This is a flexible class that can be used to display status for a sprite (health/mana/fatigue, etc),
    or to provide a status bar on the screen not attached to any particular object. You can use multiple
    status bars for a sprite to show different status items if desired.

    You can use the percent_full attribute to manually set the status, or you can provide a pointer to a method
    that will provide the percentage information.

    :param relative_rect: The rectangle that defines the size of the health bar.
    :param display_sprite: Optional sprite to attach the bar to.
    :param percent_method: Optional method signature to call to get the percent complete. (To provide a method signature,
                           simply reference the method without parenthesis, such as self.health_percent.)
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.

    """

    element_id = 'status_bar'

    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 display_sprite: Union[pygame.sprite.Sprite, None] = None,
                 percent_method: Union[Callable[[], float], None] = None,
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

        # Subclasses may have already set these values.
        # Doing this check allows for more flexibility in subclassing (see UIScreenSpaceHealthBar).
        try:
            self.display_sprite
        except AttributeError:
            self.display_sprite = display_sprite

        try:
            self.percent_method
        except AttributeError:
            self.percent_method = percent_method

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id=self.element_id)

        self._percent_full = 0
        self.status_changed = False

        self.border_colour = None
        self.bar_filled_colour = None
        self.bar_unfilled_colour = None
        self.hover_height = None
        self.border_width = None
        self.shadow_width = None
        self.position = None
        self.border_rect = None
        self.capacity_width = None
        self.capacity_height = None
        self.capacity_rect = None
        self.current_status_rect = None

        self.drawable_shape = None
        self.shape = 'rectangle'
        self.shape_corner_radius = None

        self.set_image(None)

        self.rebuild_from_changed_theme_data()

    @property
    def percent_full(self):
        """ Use this property to directly change the status bar. """
        return self._percent_full

    @percent_full.setter
    def percent_full(self, value):
        # We need a decimal percentage
        if value > 1:
            value = value / 100
        if value != self._percent_full:
            self._percent_full = value
            self.status_changed = True

    def rebuild(self):
        """
        Rebuild the status bar entirely because the theming data has changed.

        """

        if self.display_sprite:
            self.position = [self.display_sprite.rect.x,
                             self.display_sprite.rect.y - self.hover_height]
        else:
            self.position = [self.relative_rect.x,
                             self.relative_rect.y]

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        self.border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                       (self.rect.width - (self.shadow_width * 2),
                                        self.rect.height - (self.shadow_width * 2)))

        self.capacity_width = self.rect.width - (self.shadow_width * 2) - (self.border_width * 2)
        self.capacity_height = self.rect.height - (self.shadow_width * 2) - (self.border_width * 2)
        self.capacity_rect = pygame.Rect((self.border_width + self.shadow_width,
                                          self.border_width + self.shadow_width),
                                         (self.capacity_width, self.capacity_height))

        self.redraw()

    def update(self, time_delta: float):
        """
        Updates the status bar sprite's image and rectangle with the latest status and position
        data from the sprite we are monitoring

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if self.alive():
            if self.display_sprite:
                self.position = [self.display_sprite.rect.x,
                                 self.display_sprite.rect.y - self.hover_height]
            else:
                self.position = [self.relative_rect.x,
                                 self.relative_rect.y]

            self.rect.x = self.position[0]
            self.rect.y = self.position[1]
            self.relative_rect.topleft = self.rect.topleft

            # If they've provided a method to call, we'll track previous value in percent_full.
            if self.percent_method:
                # This triggers status_changed if necessary.
                self.percent_full = self.percent_method()

            if self.status_changed:
                self.status_changed = False
                self.redraw()

    def redraw(self, theming_parameters=None):
        """
        Redraw the status bar when something, other than it's position has changed.

        :param theming_parameters: allows subclasses to fill in their own theming parameters and pass this along.
        """
        if theming_parameters is None:
            theming_parameters = {}

        parameters = {'normal_bg': self.bar_unfilled_colour,
                      'normal_border': self.border_colour,
                      'border_width': self.border_width,
                      'shadow_width': self.shadow_width,
                      'shape_corner_radius': self.shape_corner_radius,
                      'filled_bar': self.bar_filled_colour,
                      'filled_bar_width_percentage': self.percent_full}

        # This allows subclasses to overwrite my values.
        parameters.update(theming_parameters)

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, parameters,
                                                        ['normal'], self.ui_manager)

        self.set_image(self.drawable_shape.get_fresh_surface())

    def rebuild_from_changed_theme_data(self, has_any_changed=False):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.

        :param has_any_changed: allows subclasses to do their own theme check and pass this along.
        """
        super().rebuild_from_changed_theme_data()

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
