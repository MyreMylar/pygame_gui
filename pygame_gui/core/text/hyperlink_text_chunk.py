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
                 line_height: int,
                 colour: Color,
                 bg_colour: Color,
                 hover_colour: Color,
                 selected_colour: Color,
                 hover_underline: bool):
        super().__init__(text, font, underlined, line_height, colour, bg_colour)

        self.href = href
        self.is_hovered = False
        self.is_selected = False

        self.normal_colour = colour
        self.hover_colour = hover_colour
        self.selected_colour = selected_colour

        self.normal_underline = underlined
        self.hover_underline = hover_underline

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

    def redraw(self):
        if self.target_surface is not None:
            self.target_surface.fill(self.bg_color, self)
            self.finalise(self.target_surface)

    def _split_at(self, right_side):
        return HyperlinkTextChunk(self.href,
                                  right_side,
                                  self.font,
                                  self.underlined,
                                  self.line_height,
                                  self.colour,
                                  self.bg_color,
                                  self.hover_colour,
                                  self.selected_colour,
                                  self.hover_underline)
