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

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

    @property
    def progress_percentage(self):
        return self.current_progress / self.maximum_progress

    def status_text(self):
        """ Subclass and override this method to change what text is displayed, or to suppress the text. """
        return f"{self.current_progress:0.1f}/{self.maximum_progress:0.1f}"

    def set_current_progress(self, progress: float):
        # Now that we subclass UIStatusBar, set_current_progress() and self.current_progress are mostly here for backward compatibility.
        self.current_progress = progress

        # Setting this triggers updating if necessary.
        self.percent_full = progress
