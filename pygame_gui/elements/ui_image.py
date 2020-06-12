from typing import Union, Tuple, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.utility import premul_alpha_surface


class UIImage(UIElement):
    """
    Displays a pygame surface as a UI element, intended for an image but it can serve
    other purposes.

    :param relative_rect: The rectangle that contains, positions and scales the image relative to
                          it's container.
    :param image_surface: A pygame surface to display.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility may override this.
    """
    def __init__(self,
                 relative_rect: pygame.Rect,
                 image_surface: pygame.surface.Surface,
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
                               element_id='image')

        self.original_image = None
        # GUI images must support an alpha channel & must have their alpha channel pre-multiplied
        # with their colours.
        image_surface = premul_alpha_surface(image_surface.convert_alpha())
        if (image_surface.get_width() != self.rect.width or
                image_surface.get_height() != self.rect.height):
            self.original_image = image_surface
            self.set_image(pygame.transform.smoothscale(self.original_image, self.rect.size))
        else:
            self.set_image(image_surface)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Set the dimensions of this image, scaling the image surface to match.

        :param dimensions: The new dimensions of the image.

        """
        super().set_dimensions(dimensions)

        if self.rect.size != self.image.get_size():
            if self.original_image is None:
                if self._pre_clipped_image is not None:
                    self.original_image = self._pre_clipped_image
                else:
                    self.original_image = self.image
            self.set_image(pygame.transform.smoothscale(self.original_image, self.rect.size))
