import pygame
from typing import Union

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
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect, image_surface: pygame.Surface,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='image')

        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids)
        self.image = image_surface
