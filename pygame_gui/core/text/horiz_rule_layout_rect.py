from typing import Tuple

import pygame

from pygame.rect import Rect
from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class HorizRuleLayoutRect(TextLayoutRect):
    ALIGN_CENTER = 0
    ALIGN_LEFT = 1
    ALIGN_RIGHT = 2

    def __init__(self, height: int,
                 colour_or_gradient: Color,
                 rule_dimensions: Tuple[int, int] = (-1, 1),
                 has_shade: bool = True,
                 alignment=ALIGN_CENTER):
        super().__init__(dimensions=(-1, height), should_span=True)
        self.colour_or_gradient = colour_or_gradient
        self.rule_dimensions = list(rule_dimensions)
        self.shade = has_shade
        self.alignment = alignment

        if self.shade and isinstance(self.colour_or_gradient, Color):
            self.med_shade_colour = Color('#00000000')
            self.light_shade_colour = Color('#00000000')
            self.med_shade_colour.hsla = (self.colour_or_gradient.hsla[0],
                                          self.colour_or_gradient.hsla[1],
                                          self.colour_or_gradient.hsla[2],
                                          self.colour_or_gradient.hsla[3] * 0.5)
            self.light_shade_colour.hsla = (self.colour_or_gradient.hsla[0],
                                            self.colour_or_gradient.hsla[1],
                                            self.colour_or_gradient.hsla[2],
                                            self.colour_or_gradient.hsla[3] * 0.25)

    def finalise(self, target_surface: Surface):

        x_start = self.left
        y_start = self.centery - int(self.rule_dimensions[1] / 2)

        # figure out alignment and the actual width of the rule.
        if self.rule_dimensions[0] != -1 and self.rule_dimensions[0] < self.width:
            if self.alignment == HorizRuleLayoutRect.ALIGN_CENTER:
                x_start = int((self.width - self.rule_dimensions[0]) / 2)
            elif self.alignment == HorizRuleLayoutRect.ALIGN_RIGHT:
                x_start = self.width - self.rule_dimensions[0]
        else:
            self.rule_dimensions[0] = self.width

        # draw the rule to our target surface
        if self.shade:
            self._draw_shaded_rule(x_start, y_start, target_surface)
        else:  # no shade
            pygame.draw.rect(target_surface,
                             color=self.colour_or_gradient,
                             rect=Rect((x_start, y_start),
                                       (self.rule_dimensions[0], self.rule_dimensions[1])))

    def _draw_shaded_rule(self, x_start, y_start, target_surface):
        """
         # TODO: need to draw this better at some point

        :param x_start:
        :param y_start:
        :param target_surface:
        """
        top_left = (x_start, y_start)
        top_right = (x_start + self.rule_dimensions[0], y_start)
        bottom_left = (x_start, y_start + self.rule_dimensions[1])
        bottom_right = (x_start + self.rule_dimensions[0], y_start + self.rule_dimensions[1])

        pygame.draw.line(target_surface, color=self.colour_or_gradient,
                         start_pos=top_left,
                         end_pos=top_right)
        if self.rule_dimensions[1] > 1:
            pygame.draw.line(target_surface, color=self.med_shade_colour,
                             start_pos=top_left,
                             end_pos=bottom_left)
        pygame.draw.line(target_surface, color=self.light_shade_colour,
                         start_pos=bottom_left,
                         end_pos=bottom_right)
        if self.rule_dimensions[1] > 1:
            pygame.draw.line(target_surface, color=self.med_shade_colour,
                             start_pos=top_right,
                             end_pos=bottom_right)
