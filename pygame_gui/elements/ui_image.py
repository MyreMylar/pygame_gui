import pygame
from typing import Union, Tuple

from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.ui_element import UIElement


class UIImage(UIElement):
    """
    Displays a pygame surface as a UI element, intended for an image but it can serve other purposes.

    :param relative_rect: The rectangle that contains, positions and scales the image relative to it's container.
    :param image_surface:
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 image_surface: pygame.Surface,
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

        self.original_image = image_surface
        if self.original_image.get_width() != self.rect.width or self.original_image.get_height() != self.rect.height:
            self.image = pygame.transform.smoothscale(self.original_image, self.rect.size)
        else:
            self.image = image_surface

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_dimensions(dimensions)

        if self.rect.size != self.image.get_size():
            self.image = pygame.transform.smoothscale(self.original_image, self.rect.size)

