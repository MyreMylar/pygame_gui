from typing import Tuple, Optional

import pygame

from pygame.rect import Rect
from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class HorizRuleLayoutRect(TextLayoutRect):
    """
    Represents a horizontal rule in the HTML style. This is normally a line across the width
    of the layout block area, but styling options can provide some variation on that theme.

    :param height: the current line height of the layout/font we are using when invoking the rule.
    :param colour_or_gradient: the colour or gradient of the rule.
    :param rule_dimensions: the dimensions of the rule itself, normally it is 1 pixel tall
                            and the width of the text block layout wide.
    :param has_shade: whether the rule has 'shading' which by default is just another
                      alpha'd line beneath it to add some depth. Doesn't work great if the line has
                      more height to it.
    :param alignment: ALIGN_CENTER, ALIGN_LEFT or ALIGN_RIGHT. ALIGN_CENTER is the default.
    """

    ALIGN_CENTER = 0
    ALIGN_LEFT = 1
    ALIGN_RIGHT = 2

    def __init__(
        self,
        height: int,
        colour_or_gradient: Color,
        rule_dimensions: Tuple[int, int] = (-1, 1),
        has_shade: bool = True,
        alignment=ALIGN_CENTER,
    ):
        super().__init__(dimensions=(-1, height), should_span=True)
        self.colour_or_gradient = colour_or_gradient
        self.rule_dimensions = list(rule_dimensions)
        self.shade = has_shade
        self.alignment = alignment
        self.med_shade_colour = Color("#00000000")
        self.light_shade_colour = Color("#00000000")

        if self.shade and isinstance(self.colour_or_gradient, Color):
            self.med_shade_colour.hsla = (
                self.colour_or_gradient.hsla[0],
                self.colour_or_gradient.hsla[1],
                self.colour_or_gradient.hsla[2],
                round(self.colour_or_gradient.hsla[3] * 0.5),
            )
            self.light_shade_colour.hsla = (
                self.colour_or_gradient.hsla[0],
                self.colour_or_gradient.hsla[1],
                self.colour_or_gradient.hsla[2],
                round(self.colour_or_gradient.hsla[3] * 0.25),
            )

    def finalise(
        self,
        target_surface: Surface,
        target_area: Rect,
        row_chunk_origin: int,
        row_chunk_height: int,
        row_bg_height: int,
        row_line_spacing_height: int,
        x_scroll_offset: int = 0,
        letter_end: Optional[int] = None,
    ):
        x_start = self.left
        y_start = self.centery - int(self.rule_dimensions[1] / 2)
        draw_width = self.rule_dimensions[0]
        # figure out alignment and the actual width of the rule.
        if draw_width != -1 and draw_width < self.width:
            if self.alignment == HorizRuleLayoutRect.ALIGN_CENTER:
                x_start = int((self.width - draw_width) / 2)
            elif self.alignment == HorizRuleLayoutRect.ALIGN_RIGHT:
                x_start = self.width - draw_width
        else:
            draw_width = self.width

        # draw the rule to our target surface
        if self.shade:
            self._draw_shaded_rule(x_start, y_start, target_surface, draw_width)
        else:  # no shade
            pygame.draw.rect(
                target_surface,
                color=self.colour_or_gradient,
                rect=Rect((x_start, y_start), (draw_width, self.rule_dimensions[1])),
            )

    def _draw_shaded_rule(self, x_start, y_start, target_surface, draw_width):
        """
         # TODO: need to draw this better at some point

        :param x_start:
        :param y_start:
        :param target_surface:
        """
        top_left = (x_start, y_start)
        top_right = (x_start + draw_width, y_start)
        bottom_left = (x_start, y_start + self.rule_dimensions[1])
        bottom_right = (x_start + draw_width, y_start + self.rule_dimensions[1])

        pygame.draw.line(
            target_surface,
            color=self.colour_or_gradient,
            start_pos=top_left,
            end_pos=top_right,
        )
        if self.rule_dimensions[1] > 1:
            pygame.draw.line(
                target_surface,
                color=self.med_shade_colour,
                start_pos=top_left,
                end_pos=bottom_left,
            )
        pygame.draw.line(
            target_surface,
            color=self.light_shade_colour,
            start_pos=bottom_left,
            end_pos=bottom_right,
        )
        if self.rule_dimensions[1] > 1:
            pygame.draw.line(
                target_surface,
                color=self.med_shade_colour,
                start_pos=top_right,
                end_pos=bottom_right,
            )
