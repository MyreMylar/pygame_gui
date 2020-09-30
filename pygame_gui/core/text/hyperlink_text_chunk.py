from typing import Optional, Tuple

import pygame.freetype

from pygame.color import Color
from pygame.surface import Surface


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
                 selected_colour: Color,
                 hover_underline: bool,
                 text_shadow_data: Optional[Tuple[int, int, int]] = None):
        super().__init__(text, font, underlined, colour, False, bg_colour, text_shadow_data)

        self.href = href
        self.is_hovered = False
        self.is_selected = False

        self.normal_colour = colour
        self.hover_colour = hover_colour
        self.selected_colour = selected_colour

        self.normal_underline = underlined
        self.hover_underline = hover_underline

        self.last_row_origin = 0
        self.last_row_height = 0

    def on_hovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not self.is_selected:
            self.colour = self.hover_colour
            self.underlined = self.hover_underline
            self.is_hovered = True
            self.redraw()

    def on_unhovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not self.is_selected:
            self.colour = self.normal_colour
            self.underlined = self.normal_underline
            self.is_hovered = False
            self.redraw()

    def on_selected(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.
        TODO: Should this be set_active/set_inactive? To be internally consistent with buttons.

        """
        self.colour = self.selected_colour
        self.is_selected = True
        self.redraw()

    def on_unselected(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.

        """
        self.colour = self.normal_colour
        self.is_selected = False
        self.redraw()

    def _split_at(self, right_side, split_pos, target_surface, baseline_centred):
        right_side_chunk = HyperlinkTextChunk(self.href,
                                              right_side,
                                              self.font,
                                              self.underlined,
                                              self.colour,
                                              self.bg_colour,
                                              self.hover_colour,
                                              self.selected_colour,
                                              self.hover_underline,
                                              self.text_shadow_data)

        right_side_chunk.topleft = split_pos
        right_side_chunk.target_surface = target_surface
        right_side_chunk.should_centre_from_baseline = baseline_centred
        return right_side_chunk
