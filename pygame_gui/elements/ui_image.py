import pygame
from typing import List, Union

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement


class UIImage(UIElement):
    """
    Displays a pygame surface as a UI element, intended for an image but it can serve other purposes.

    :param relative_rect: The rectangle that contains and positions the image relative to it's container.
    :param image_surface:
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param element_ids: A list of ids that describe the 'journey' of UIElements that this UIElement is part of.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect, image_surface: pygame.Surface,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer=None,
                 element_ids: Union[List[str], None] = None, object_id: Union[str, None] = None):

        if element_ids is None:
            new_element_ids = ['image']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('image')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_id=object_id,
                         element_ids=new_element_ids)
        self.image = image_surface
