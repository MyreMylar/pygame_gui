"""
A bit of renderable text that fits on a single line and all in the same style.

Blocks of text are made up of many text chunks. At the simplest level there would be one per line.

On creation a text chunk calculates how much space it will take up when rendered to a surface and
stores this size information in a rectangle. These rectangles can then be used in layout
calculations.

Once a layout for the text chunk is finalised the chunk's render function can be called to add the
chunk onto it's final destination.

TODO:
  - Experiment with being font type agnostic as much as possible. I have a suspicion that freetype
    font might be more useful here because of render_to() and maybe the background colour default
    but it's worth testing all these assumptions and the speed of both.
  - Do we need an intermediate type that links together - chunks, the html parser and the layout
    managers? Mainly thinking about new lines like <br> and /n. Seems unlikely so far?
  - Performance comparison tests & functionality comparison tests between current system and new.
    Need to set these up early.
"""

from pygame.font import Font
from pygame.color import Color
from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class TextLineChunk_Font(TextLayoutRect):
    """

    """

    def __init__(self, text: str, font: Font, colour: Color):

        dimensions = font.size(text)
        super().__init__(dimensions, can_split=True)

        self.text = text
        self.font = font
        self.colour = colour

        # we split text stings based on spaces
        self.split_points = [pos+1 for pos, char in enumerate(self.text) if char == ' ']

    def finalise(self, target_surface: Surface):
        surface = self.font.render(self.text, True, self.colour)
        target_surface.blit(surface, self)

    def split(self, requested_x: int):
        # starting heuristic: find the percentage through the chunk width of this split request
        percentage_split = float(requested_x)/float(self.width)
        closest_split_index = int(percentage_split * len(self.split_points))

        # Now we need to search for the perfect split point
        # perfect split point is a) less than or equal requested x, b) as close to it as possible
        # because split points will be in order we can test and decided to move left or right until
        # we find the optimum point.
        current_split_point_index = closest_split_index
        tested_points = []
        valid_points = []
        found_optimum = False

        optimum_split_point = 0

        while not found_optimum and len(self.split_points) > 0:
            optimum_split_point = self.split_points[current_split_point_index]

            if optimum_split_point in tested_points:
                # already tested this one so we must have changed direction after crossing the
                # requested_x line. the last valid point must be the optimum split point.
                if not valid_points:
                    raise RuntimeError('Unable to find valid split point for text layout')
                found_optimum = True
                optimum_split_point = valid_points[-1]
            else:
                width, _ = self.font.size(self.text[:optimum_split_point])
                if width < requested_x:
                    # we are below the required width so we move right
                    valid_points.append(optimum_split_point)
                    current_split_point_index += 1
                elif width > requested_x:
                    current_split_point_index -= 1
                else:
                    # the split point is right on the requested width
                    found_optimum = True
                tested_points.append(optimum_split_point)

        # What we need to consider is the case when there are no split points in a chunk and the
        # chunk is wider than the maximum width, in that case moving the chunk to the next line
        # will not work
        if optimum_split_point != 0:
            # split the text
            left_side = self.text[:optimum_split_point]
            right_side = self.text[optimum_split_point:]

            # update the data for this chunk
            self.text = left_side
            self.size = self.font.size(self.text)
            self.split_points = [pos + 1 for pos, char in enumerate(self.text) if char == ' ']

            return TextLineChunk_Font(right_side, self.font, self.colour)
        else:
            return None
