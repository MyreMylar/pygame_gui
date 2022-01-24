from typing import Union, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.elements.ui_status_bar import UIStatusBar


class UIProgressBar(UIStatusBar):
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
    element_id = 'progress_bar'

    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        self.current_progress = 0.0
        self.maximum_progress = 100.0

        self.font = None
        self.text_shadow_colour = None
        self.text_colour = None
        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1
        self.background_text = None
        self.foreground_text = None

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         display_sprite=None,
                         percent_method=None,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

    @property
    def progress_percentage(self):
        return self.current_progress / self.maximum_progress

    @property
    def progress_string(self):
        """ Subclass and override this property to change what text is displayed, or to suppress the text. """
        return f"{self.current_progress:0.1f}/{self.maximum_progress:0.1f}"

    def redraw(self, theming_parameters: dict = None):
        """
        Redraws the progress bar rectangles and text onto the underlying sprite's image surface.
        Takes a little while so we only do it when the progress has changed.

        :param theming_parameters: allows subclasses to fill in their own theming parameters and pass this along.
        """
        if theming_parameters is None:
            theming_parameters = {}

        parameters = {'font': self.font,
                      'text': self.progress_string,
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

    def set_current_progress(self, progress: float):
        """
        Set the current progress of the bar.

        :param progress: The level of progress to set from 0 to 100.0
        """
        # Now that we subclass UIStatusBar, set_current_progress() and self.current_progress are mostly here for backward compatibility.
        self.current_progress = progress

        # Setting this triggers updating if necessary.
        self.percent_full = progress

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
