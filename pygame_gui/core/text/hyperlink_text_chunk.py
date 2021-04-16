from typing import Optional, Tuple

import pygame.freetype

from pygame.color import Color


from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class HyperlinkTextChunk(TextLineChunkFTFont):
    """
    Represents a hyperlink to the layout system..

    """
    def __init__(self,
                 href: str,
                 text: str,
                 font: pygame.freetype.Font,
                 underlined: bool,
                 colour: Color,
                 bg_colour: Color,
                 hover_colour: Color,
                 active_colour: Color,
                 hover_underline: bool,
                 text_shadow_data: Optional[Tuple[int, int, int]] = None):
        super().__init__(text, font, underlined, colour, False, bg_colour, text_shadow_data)

        self.href = href
        self.is_hovered = False

        self.normal_colour = colour
        self.hover_colour = hover_colour
        self.active_colour = active_colour

        self.normal_underline = underlined
        self.hover_underline = hover_underline

        self.last_row_origin = 0
        self.last_row_height = 0

    def on_hovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not (self.is_active or self.is_selected):
            self.colour = self.hover_colour
            self.underlined = self.hover_underline
            self.is_hovered = True
            self.redraw()

    def on_unhovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not (self.is_active or self.is_selected):
            self.colour = self.normal_colour
            self.underlined = self.normal_underline
            self.is_hovered = False
            self.redraw()

    def set_active(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.

        """
        self.colour = self.active_colour
        self.is_active = True
        self.redraw()

    def set_inactive(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.

        """
        self.colour = self.normal_colour
        self.is_active = False
        self.redraw()

    def _split_at(self, right_side, split_pos, target_surface, target_surface_area, baseline_centred):
        right_side_chunk = HyperlinkTextChunk(self.href,
                                              right_side,
                                              self.font,
                                              self.underlined,
                                              self.colour,
                                              self.bg_colour,
                                              self.hover_colour,
                                              self.active_colour,
                                              self.hover_underline,
                                              self.text_shadow_data)

        right_side_chunk.topleft = split_pos
        right_side_chunk.target_surface = target_surface
        right_side_chunk.target_surface_area = target_surface_area
        right_side_chunk.should_centre_from_baseline = baseline_centred
        return right_side_chunk
