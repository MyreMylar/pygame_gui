from abc import ABCMeta, abstractmethod
from typing import Union

import pygame


class IColourGradientInterface(metaclass=ABCMeta):
    """
    A metaclass that defines the interface that a colour gradient uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """

    @abstractmethod
    def apply_gradient_to_surface(
        self,
        input_surface: pygame.surface.Surface,
        rect: Union[pygame.Rect, None] = None,
    ):
        """
        Applies this gradient to a specified input surface using blending multiplication.
        As a result this method works best when the input surface is a mostly white, stencil shape
        type surface.

        :param input_surface:
        :param rect: The rectangle on the surface to apply the gradient to. If None, applies to the
                     whole surface.
        """
