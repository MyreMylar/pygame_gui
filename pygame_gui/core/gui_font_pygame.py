import pygame

from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame.font import Font
from typing import Union, IO, Optional, Dict, Tuple
from os import PathLike
from pygame import Color, Surface, Rect

AnyPath = Union[str, bytes, PathLike]
FileArg = Union[AnyPath, IO]


class GUIFontPygame(IGUIFontInterface):

    def __init__(self, file: Optional[FileArg], size: Union[int, float],
                 force_style: bool = False, style: Optional[Dict[str, bool]] = None):
        self.__internal_font: Font = Font(file, size)  # no resolution option for pygame font?

        self.__internal_font.set_point_size(size)
        self.pad = True
        self.origin = True
        self.__underline = False
        self.__underline_adjustment = 0.0

        self.point_size = size
        self.antialiased = True
        self.direction = pygame.DIRECTION_LTR

        if style is not None:
            self.antialiased = style['antialiased']
            self.italic = style['italic']
            self.bold = style['bold']

            if 'script' in style:
                self.__internal_font.set_script(style['script'])

            if 'direction' in style:
                self.__internal_font.set_direction(style['direction'])
                self.direction = style['direction']

            if force_style:
                self.__internal_font.bold = style['bold']
                self.__internal_font.italic = style['italic']

    def size(self, text: str):
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

    def get_point_size(self):
        return self.point_size

    def get_rect(self, text: str) -> Rect:
        # only way to get accurate font layout data with kerning is to render it ourselves it seems
        if len(text) > 0:
            text_surface = self.__internal_font.render(text, self.antialiased, pygame.Color("white"))
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

    def render_premul_to(self, text: str, text_colour: Color,
                         surf_size: Tuple[int, int], surf_position: Tuple[int, int]) -> Surface:
        text_surface = pygame.Surface(surf_size, depth=32, flags=pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))
        temp_surf = self.__internal_font.render(text, self.antialiased, text_colour)
        temp_surf = temp_surf.convert_alpha()
        if temp_surf.get_width() > 0 and temp_surf.get_height() > 0:
            temp_surf = temp_surf.premul_alpha()
            text_surface.blit(temp_surf, (surf_position[0], surf_position[1]-self.__internal_font.get_ascent()),
                              special_flags=pygame.BLEND_PREMULTIPLIED)
        return text_surface

    def get_padding_height(self):
        # 'font padding' this determines the amount of padding that
        # font.pad adds to the top of text excluding
        # any padding added to make glyphs even - this is useful
        # for 'base-line centering' when we want to center text
        # that doesn't drop below the base line (no y's, g's, p's etc)
        # but also don't want it to flicker on and off. Base-line
        # centering is the default for chunks on a single style row.

        descender = -self.__internal_font.get_descent()
        return descender + 1

    def get_direction(self) -> int:
        """

        :return:
        """
        return self.direction


