from typing import Union, Tuple, Protocol

from pygame import Vector2, Rect, FRect, Surface

Coordinate = Union[Vector2, Tuple[float, float]]
RectLike = Union[Rect, FRect, Tuple[float, float, float, float]]


class SpriteWithHealth(Protocol):
    """
    A protocol for sprites that have health. This protocol defines the required attributes for
    sprites that have health, including current health, health capacity, rect, and image.

    Attributes:
        current_health: The current health of the sprite.
        health_capacity: The maximum health of the sprite.
        rect: The rectangular area of the sprite.
        image: The image of the sprite.
    """
    current_health: int
    health_capacity: int
    rect: Rect
    image: Surface
