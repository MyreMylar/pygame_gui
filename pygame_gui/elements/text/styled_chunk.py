from typing import Tuple, Dict, Any, Union

import pygame
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.ui_font_dictionary import UIFontDictionary

from pygame_gui.elements.text.html_parser import CharStyle


class StyledChunk:
    """
    Takes care of turning styling and some ordinary text into a rendered pygame Surface of the text
    in an appropriate style.

    :param font_size: The size of the font to use.
    :param font_name: The name of the font to use.
    :param chunk: The chunk of normal string text we are styling.
    :param style: The bold/italic/underline style of the text.
    :param color: The colour or gradient of the text.
    :param bg_color: The colour or gradient of the text background.
    :param is_link: True if the chunk is a link.
    :param link_href: The target of the link if it is one.
    :param link_style: The style for link text.
    :param position: Surface position of this chunk of text.
    :param font_dictionary: The UI's font dictionary where all loaded fonts are stored.
    """
    def __init__(self,
                 font_size: int,
                 font_name: str,
                 chunk: str,
                 style: CharStyle,
                 color: Union[pygame.Color, ColourGradient],
                 bg_color: Union[pygame.Color, ColourGradient],
                 is_link: bool,
                 link_href: str,
                 link_style: Dict[str, Any],
                 position: Tuple[int, int],
                 font_dictionary: UIFontDictionary):

        self.style = style
        self.chunk = chunk
        self.font_size = font_size
        self.font_name = font_name
        self.is_link = is_link
        self.link_href = link_href
        self.link_style = link_style

        self.font = font_dictionary.find_font(font_size, font_name,
                                              self.style.bold, self.style.italic)

        if self.is_link:
            self.normal_colour = self.link_style['link_text']
            self.hover_colour = self.link_style['link_hover']
            self.selected_colour = self.link_style['link_selected']
            self.link_normal_underline = self.link_style['link_normal_underline']
            self.link_hover_underline = self.link_style['link_hover_underline']
        else:
            self.normal_colour = color
            self.hover_colour = None
            self.selected_colour = None
            self.link_normal_underline = False
            self.link_hover_underline = False

        self.color = self.normal_colour
        self.bg_color = bg_color
        self.position = position

        self.is_hovered = False
        self.is_selected = False

        if self.style.underline or (self.is_hovered and self.link_hover_underline) or \
                (self.link_normal_underline and not self.is_hovered):
            self.font.set_underline(True)

        if len(self.chunk) > 0:
            if type(self.color) != ColourGradient:
                if type(self.bg_color) == ColourGradient or self.bg_color.a != 255:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True,
                                                           self.color, self.bg_color)
            else:
                self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                self.color.apply_gradient_to_surface(self.rendered_chunk)
        else:
            self.rendered_chunk = pygame.Surface((0, 0))
        metrics = self.font.metrics(self.chunk)
        self.ascent = self.font.get_ascent()
        self.width = self.font.size(self.chunk)[0]
        self.height = self.font.size(self.chunk)[1]
        self.advance = 0
        for i in range(len(self.chunk)):
            if len(metrics[i]) == 5:
                self.advance += metrics[i][4]

        self.rect = pygame.Rect(self.position, (self.width, self.height))
        self.metrics_changed_after_redraw = False

        self.unset_underline_style()

    def unset_underline_style(self):
        """
        Un-sets the underline style. This is a function we have to call on our loaded font before
        rendering.

        """
        self.font.set_underline(False)

    def redraw(self):
        """
        Renders the 'chunk' text to the 'rendered_chunk' surface.

        """
        if self.style.underline or (self.is_hovered and self.link_hover_underline) or \
                (self.link_normal_underline and not self.is_hovered):
            self.font.set_underline(True)

        if len(self.chunk) > 0:
            if type(self.color) == ColourGradient:
                self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                self.color.apply_gradient_to_surface(self.rendered_chunk)
            else:
                if type(self.bg_color) == ColourGradient or self.bg_color.a != 255:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True,
                                                           self.color, self.bg_color)
        else:
            self.rendered_chunk = pygame.Surface((0, 0))

        self.font.set_underline(False)

        new_metrics = self.font.metrics(self.chunk)
        new_ascent = self.font.get_ascent()
        new_width = self.font.size(self.chunk)[0]
        new_height = self.font.size(self.chunk)[1]
        new_advance = sum(new_metrics[i][4] for i in range(len(self.chunk))
                          if len(new_metrics[i]) == 5)
        if (new_ascent == self.ascent and new_width == self.width and
                new_height == self.height and new_advance == self.advance):
            self.metrics_changed_after_redraw = False
        else:
            self.metrics_changed_after_redraw = True
            self.ascent = new_ascent
            self.width = new_width
            self.height = new_height
            self.advance = new_advance
            self.rect = pygame.Rect(self.position, (self.width, self.height))

    def on_hovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not self.is_selected:
            self.color = self.hover_colour
            self.is_hovered = True
            self.redraw()

    def on_unhovered(self):
        """
        Handles hovering over this text chunk with the mouse. Used for links.

        """
        if not self.is_selected:
            self.color = self.normal_colour
            self.is_hovered = False
            self.redraw()

    def on_selected(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.
        TODO: Should this be set_active/set_inactive? To be internally consistent with buttons.

        """
        self.color = self.selected_colour
        self.is_selected = True
        self.redraw()

    def on_unselected(self):
        """
        Handles clicking on this text chunk with the mouse. Used for links.

        """
        self.color = self.normal_colour
        self.is_selected = False
        self.redraw()
