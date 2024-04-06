import pygame

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame.freetype import Font
from typing import Union, IO, Optional, Dict, Tuple
from os import PathLike
from pygame import Color, Surface, Rect

AnyPath = Union[str, bytes, PathLike]
FileArg = Union[AnyPath, IO]


class GUIFontFreetype(IGUIFontInterface):

    def __init__(self, file: Optional[FileArg], size: Union[int, float],
                 force_style: bool = False, style: Optional[Dict[str, bool]] = None):
        self.__internal_font: Font = Font(file, size, resolution=72)
        self.__internal_font.pad = True
        self.__internal_font.origin = True
        self.__internal_font.kerning = True

        self.__underline = False
        self.__underline_adjustment = 0.0

        self.point_size = size

        if style is not None:
            self.__internal_font.antialiased = style['antialiased']

            if force_style:
                self.__internal_font.strong = style['bold']
                self.__internal_font.oblique = style['italic']


    @property
    def underline(self) -> bool:
        return self.__internal_font.underline

    @underline.setter
    def underline(self, value: bool):
        self.__internal_font.underline = value

    @property
    def underline_adjustment(self) -> float:
        return self.__internal_font.underline_adjustment

    @underline_adjustment.setter
    def underline_adjustment(self, value: float):
        self.__internal_font.underline_adjustment = value

    def get_point_size(self):
        return self.point_size

    def get_rect(self, text: str) -> Rect:
        supposed_rect = self.__internal_font.get_rect(text)
        text_surface, text_rect = self.__internal_font.render(text, pygame.Color("white"))
        return pygame.Rect(supposed_rect.topleft, text_surface.get_size())

    def get_metrics(self, text: str):
        return self.__internal_font.get_metrics(text)

    def render_premul(self, text: str, text_color: Color) -> Surface:
        text_surface, text_rect = self.__internal_font.render(text, text_color)
        text_surface = text_surface.convert_alpha()
        if text_surface.get_width() > 0 and text_surface.get_height() > 0:
            text_surface = text_surface.premul_alpha()
        return text_surface

    def render_premul_to(self, text: str, text_colour: Color,
                         surf_size: Tuple[int, int], surf_position: Tuple[int, int]) -> Surface:
        text_surface = pygame.Surface(surf_size, depth=32, flags=pygame.SRCALPHA)
        self.__internal_font.render_to(text_surface, surf_position, text, fgcolor=text_colour)
        if text_surface.get_width() > 0 and text_surface.get_height() > 0:
            text_surface = text_surface.premul_alpha()
        return text_surface

    def get_padding_height(self):
        # 'font padding' this determines the amount of padding that
        # font.pad adds to the top of text excluding
        # any padding added to make glyphs even - this is useful
        # for 'base-line centering' when we want to center text
        # that doesn't drop below the base line (no y's, g's, p's etc)
        # but also don't want it to flicker on and off. Base-line
        # centering is the default for chunks on a single style row.

        return -self.__internal_font.get_sized_descender(self.point_size)

    def get_direction(self) -> int:
        """

        :return:
        """
        return pygame.DIRECTION_LTR
