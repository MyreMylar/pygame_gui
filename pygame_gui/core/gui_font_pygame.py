from typing import Union, IO, Optional, Dict, Tuple, Any
from os import PathLike

import pygame
from pygame.font import Font
from pygame import Color, Surface, Rect

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface


AnyPath = Union[str, bytes, PathLike]
FileArg = Union[AnyPath, IO]


class GUIFontPygame(IGUIFontInterface):
    """
    A GUI Font wrapping the Font class from pygame-ce to a common interface with the 'freetype' based Font class
    also from pygame-ce. This was to facilitate easy switching between the two when testing features.

    NB: At this point the SDL based Font class seems clearly superior so the freetype implementation will be removed
        in a future version

    :param file: the font file
    :param size: the font point size
    :param force_style: whether we force the styling when the available font does not support it.
    :param style: a style dictionary to set styling parameters like bold and italic
    """

    def __init__(
        self,
        file: Optional[FileArg],
        size: Union[int, float],
        force_style: bool = False,
        style: Optional[Dict[str, Any]] = None,
    ):
        self.point_size = int(size)
        self.__internal_font: Font = Font(
            file, self.point_size
        )  # no resolution option for pygame font?

        self.__internal_font.set_point_size(self.point_size)
        self.pad = True
        self.origin = True
        self.__underline = False  # pylint: disable=unused-private-member
        self.__underline_adjustment = 0.0

        self.antialiased = True
        self.direction = pygame.DIRECTION_LTR

        if style is not None:
            self.antialiased = style["antialiased"]
            self.italic = style["italic"]
            self.bold = style["bold"]

            if "script" in style:
                self.__internal_font.set_script(style["script"])

            if "direction" in style:
                self.__internal_font.set_direction(style["direction"])
                self.direction = style["direction"]

            if force_style:
                self.__internal_font.bold = style["bold"]
                self.__internal_font.italic = style["italic"]

    def size(self, text: str) -> Tuple[int, int]:
        return self.get_rect(text).size

    @property
    def underline(self) -> bool:
        return self.__internal_font.underline

    @underline.setter
    def underline(self, value: bool):
        self.__internal_font.underline = value

    @property
    def underline_adjustment(self) -> float:
        # underline adjustment is missing in pygame.font. Would need to be added to SDL ttf
        return self.__underline_adjustment

    @underline_adjustment.setter
    def underline_adjustment(self, value: float):
        self.__underline_adjustment = value

    def get_point_size(self) -> int:
        return self.point_size

    def get_rect(self, text: str) -> Rect:
        # only way to get accurate font layout data with kerning is to render it ourselves it seems
        if text != "":
            text_surface = self.__internal_font.render(
                text, self.antialiased, pygame.Color("white")
            )
            ascent = self.__internal_font.get_ascent()
            return pygame.Rect((0, ascent), text_surface.get_size())
        else:
            return pygame.Rect(0, 0, 0, 0)

    def get_metrics(self, text: str):
        # this may need to be broken down further in the wrapper
        return self.__internal_font.metrics(text)

    def render_premul(self, text: str, text_color: Color) -> Surface:
        text_surface = self.__internal_font.render(text, self.antialiased, text_color)
        text_surface = text_surface.convert_alpha()
        if text_surface.get_width() > 0 and text_surface.get_height() > 0:
            text_surface = text_surface.premul_alpha()
        return text_surface

    def render_premul_to(
        self,
        text: str,
        text_colour: Color,
        surf_size: Tuple[int, int],
        surf_position: Tuple[int, int],
    ) -> Surface:
        text_surface = pygame.Surface(surf_size, depth=32, flags=pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))
        temp_surf = self.__internal_font.render(text, self.antialiased, text_colour)
        temp_surf = temp_surf.convert_alpha()
        if temp_surf.get_width() > 0 and temp_surf.get_height() > 0:
            temp_surf = temp_surf.premul_alpha()
            text_surface.blit(
                temp_surf,
                (
                    surf_position[0],
                    surf_position[1] - self.__internal_font.get_ascent(),
                ),
                special_flags=pygame.BLEND_PREMULTIPLIED,
            )
        return text_surface

    def get_padding_height(self) -> int:
        # 'font padding' this determines the amount of padding that
        # font.pad adds to the top of text excluding
        # any padding added to make glyphs even - this is useful
        # for 'base-line centering' when we want to center text
        # that doesn't drop below the baseline (no y's, g's, p's etc.)
        # but also don't want it to flicker on and off. Base-line
        # centering is the default for chunks on a single style row.

        descender = -self.__internal_font.get_descent()
        return descender + 1

    def get_direction(self) -> int:
        """

        :return:
        """
        return self.direction
