from typing import Union, Tuple, Protocol

from pygame import Vector2, Rect, FRect, Surface

Coordinate = Union[Vector2, Tuple[float, float]]
RectLike = Union[Rect, FRect, Tuple[float, float, float, float]]


class SpriteWithHealth(Protocol):
    current_health: int
    health_capacity: int
    rect: Rect
    image: Surface


