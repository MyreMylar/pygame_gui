from typing import Union, Dict, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.gui_type_hints import Coordinate, RectLike


class UIImage(UIElement):
    """
    Displays a pygame surface as a UI element, intended for an image, but it can serve
    other purposes.

    :param relative_rect: The rectangle that contains, positions and scales the image relative to
                          its container.
    :param image_surface: A pygame surface to display.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """
    def __init__(self,
                 relative_rect: RectLike,
                 image_surface: pygame.surface.Surface,
                 manager: Optional[IUIManagerInterface] = None,
                 image_is_alpha_premultiplied: bool = False,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1,
                 *,
                 starting_height: int = 1,
                 scale_func=pygame.transform.smoothscale):

        super().__init__(relative_rect, manager, container,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['image'])

        self.original_image = None
        self.scale_func = scale_func
        self.set_image(image_surface, image_is_alpha_premultiplied, self.scale_func)
        self.rebuild_from_changed_theme_data()

    def rebuild_from_changed_theme_data(self):
        self._check_misc_theme_data_changed(attribute_name='tool_tip_delay',
                                            default_value=1.0,
                                            casting_func=float)

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Set the dimensions of this image, scaling the image surface to match.

        :param dimensions: The new dimensions of the image.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        super().set_dimensions(dimensions)

        if self.rect.size != self.image.get_size():
            if self.original_image is None:
                if self._pre_clipped_image is not None:
                    self.original_image = self._pre_clipped_image
                else:
                    self.original_image = self.image
            self._set_image(self.scale_func(self.original_image, self.rect.size))

    def set_image(self,
                  new_image: Union[pygame.surface.Surface, None],
                  image_is_alpha_premultiplied: bool = False,
                  scale_func=pygame.transform.smoothscale) -> None:
        """
        Allows users to change the image displayed on a UIImage element during run time, without recreating
        the element.

        GUI images are converted to the correct format for the GUI if the supplied image is not the dimensions
        of the UIImage element it will be scaled to fit. In this situation, an original size image is retained
        as well in case of future resizing events.

        :param new_image: the new image surface to use in the UIImage element.
        :param image_is_alpha_premultiplied: set to True if the image is already in alpha multiplied colour format.
        :param scale_func: the function used for scaling the image, defaults to smoothscale.
        """
        self.scale_func = scale_func
        image_surface = new_image.convert_alpha()
        if not image_is_alpha_premultiplied:
            image_surface = image_surface.premul_alpha()
        if (image_surface.get_width() != self.rect.width or
                image_surface.get_height() != self.rect.height):
            self.original_image = image_surface
            self._set_image(self.scale_func(self.original_image, self.rect.size))
        else:
            self._set_image(image_surface)
