from typing import Union, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIProgressBar(UIElement):
    """
    A UI that will display a progress bar from 0 to 100%

    :param relative_rect: The rectangle that defines the size and position of the progress bar.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """
    def __init__(self,
                 relative_rect: pygame.Rect,
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
                               element_id='progress_bar')

        self.current_progress = 0.0
        self.maximum_progress = 100.0
        self.progress_percentage = self.current_progress / self.maximum_progress

        self.font = None
        self.border_width = None
        self.shadow_width = None
        self.border_colour = None
        self.bar_unfilled_colour = None
        self.bar_filled_colour = None
        self.text_shadow_colour = None
        self.text_colour = None
        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1

        self.border_rect = None
        self.capacity_width = None
        self.capacity_height = None
        self.capacity_rect = None
        self.current_progress_rect = None

        self.drawable_shape = None
        self.shape = 'rectangle'
        self.shape_corner_radius = None

        self.set_image(None)
        self.background_text = None
        self.foreground_text = None

        self.rebuild_from_changed_theme_data()

    def rebuild(self):
        """
        Rebuild the progress bar entirely because the theming data has changed.

        """
        border_rect_width = self.rect.width - (self.shadow_width * 2)
        border_rect_height = self.rect.height - (self.shadow_width * 2)
        self.border_rect = pygame.Rect((self.shadow_width,
                                        self.shadow_width),
                                       (border_rect_width, border_rect_height))

        self.capacity_width = self.rect.width - (self.shadow_width * 2) - self.border_width * 2
        self.capacity_height = self.rect.height - (self.shadow_width * 2) - self.border_width * 2
        self.capacity_rect = pygame.Rect((self.shadow_width + self.border_width,
                                          self.shadow_width + self.border_width),
                                         (self.capacity_width, self.capacity_height))

        self.current_progress_rect = pygame.Rect((self.shadow_width + self.border_width,
                                                  self.shadow_width + self.border_width),
                                                 (int(self.capacity_width *
                                                      self.progress_percentage),
                                                  self.capacity_height))

        self.redraw()

    def redraw(self):
        """
        Redraws the progress bar rectangles and text onto the underlying sprite's image surface.
        Takes a little while so we only do it when the progress has changed.
        """
        progress_string = "{0:0.1f}/{1:0.1f}".format(self.current_progress, self.maximum_progress)

        theming_parameters = {'normal_bg': self.bar_unfilled_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius,
                              'filled_bar': self.bar_filled_colour,
                              'filled_bar_width_percentage': self.progress_percentage,
                              'font': self.font,
                              'text': progress_string,
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

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.set_image(self.drawable_shape.get_fresh_surface())

    def set_current_progress(self, progress: float):
        """
        Set the current progress of the bar.

        :param progress: The level of progress to set from 0 to 100.0
        """
        if progress != self.current_progress:
            progress = min(progress, self.maximum_progress)
            self.current_progress = progress
            self.progress_percentage = self.current_progress / self.maximum_progress
            rect_width = int(self.capacity_width * self.progress_percentage)
            self.current_progress_rect = pygame.Rect((self.shadow_width + self.border_width,
                                                      self.shadow_width + self.border_width),
                                                     (rect_width,
                                                      self.capacity_height))
            self.redraw()

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

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

        text_shadow_colour = self.ui_theme.get_colour('text_shadow', self.combined_element_ids)
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            has_any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient('normal_text', self.combined_element_ids)
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
