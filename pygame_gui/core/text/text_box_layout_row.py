from typing import Optional, Tuple
import math
import pygame

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont
from pygame_gui.core.text.text_layout_rect import TextFloatPosition


class TextBoxLayoutRow(pygame.Rect):
    """
    A single line of text-like stuff to be used in a text box type layout.
    """

    def __init__(self, row_start_x, row_start_y, row_index, line_spacing, layout):
        super().__init__(row_start_x, row_start_y, 0, 0)
        self.line_spacing = line_spacing
        self.row_index = row_index
        self.layout = layout
        self.items = []

        self.letter_count = 0

        self.y_origin = 0
        self.text_chunk_height = 0

        self.target_surface = None
        self.cursor_rect = pygame.Rect(self.x, row_start_y, 2, self.height - 2)
        self.edit_cursor_active = False
        self.edit_cursor_left_margin = 2
        self.edit_right_margin = 2
        self.cursor_index = 0
        self.cursor_draw_width = 0

    def __hash__(self):
        return self.row_index

    def at_start(self):
        """
        Returns true if this row has no items in it.

        :return: True if we are at the start of the row.
        """
        return not self.items

    def add_item(self, item: TextLayoutRect):
        """
        Add a new item to the row. Items are added left to right.

        If you wanted to built a right to left writing system layout,
        changing this might be a good place to start.

        :param item: The new item to add to the text row
        """
        item.left = self.right
        self.items.append(item)
        self.width += item.width  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        if item.height > self.text_chunk_height:
            self.text_chunk_height = item.height
            if self.layout.layout_rect.height != -1:
                self.height = min(self.layout.layout_rect.height, # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
                                  int(item.height * self.line_spacing))
            else:
                self.height = int(item.height * self.line_spacing) # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

            self.cursor_rect = pygame.Rect(self.x, self.y, 2, self.height - 2)

        if isinstance(item, TextLineChunkFTFont):
            if item.y_origin > self.y_origin:
                self.y_origin = item.y_origin

        self.letter_count += item.letter_count

    def rewind_row(self, layout_rect_queue):
        """
        Use this to add items from the row back onto a layout queue, useful if we've added
        something to the layout that means that this row needs to be re-run through the
        layout code.

        :param layout_rect_queue: A layout queue that contains items to be laid out in order.
        """
        for rect in reversed(self.items):
            layout_rect_queue.appendleft(rect)
        self.clear()
        self.items.clear()
        self.width = 0  # pylint: disable=attribute-defined-outside-init; pylint getting confused
        self.height = 0  # pylint: disable=attribute-defined-outside-init; pylint getting confused
        self.text_chunk_height = 0
        self.letter_count = 0
        self.y_origin = 0

    def horiz_center_row(self, floating_rects, method='rect'):
        """
        Horizontally center this row of text.

        This uses 'rectangular' centering by default, which could also
        be called mathematical centering. Sometimes this type of
        centering looks wrong - e.g. for arrows, so we instead have an
        option to use a 'center of mass' style centering for right
        facing and left facing triangles.

        :param method: this is an ID for the method of centering to use,
                       for almost all cases this will be the default 'rect'
                       style basic centering. However, if you are trying
                       to center an arrow you might try 'right_triangle' or
                       'left_triangle'
        """
        floater_adjustment = 0

        for floater in floating_rects:
            if floater.vertical_overlap(self):
                if floater.float_pos() == TextFloatPosition.LEFT:
                    floater_adjustment += (floater.width * 0.5)
                elif floater.float_pos() == TextFloatPosition.RIGHT:
                    floater_adjustment -= (floater.width * 0.5)

        if method == 'rect':
            self.centerx = self.layout.layout_rect.centerx + floater_adjustment  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
        elif method == 'right_triangle':
            # two lines - from bottom left of triangle at a -60 angle (because y axis is inverted)
            # then from mid left at 90
            m_1 = math.tan(math.radians(-60))
            n_1 = self.centery + int(self.width / 2)
            n_2 = self.centery

            visual_center_x = (n_2 - n_1) / m_1
            visual_center_x += floater_adjustment

            self.left = self.layout.layout_rect.centerx - visual_center_x  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        elif method == 'left_triangle':
            # just flip right_triangle method
            m_1 = math.tan(math.radians(-60))
            n_1 = self.centery + int(self.width / 2)
            n_2 = self.centery

            visual_center_x = (n_2 - n_1) / m_1
            visual_center_x += floater_adjustment

            self.right = self.layout.layout_rect.centerx + visual_center_x  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        current_start_x = self.x
        for item in self.items:
            item.x = current_start_x
            current_start_x += item.width

    def align_left_row(self, start_x: int, floating_rects):
        """
        Align this row to the left.

        :param start_x: Effectively the padding. Indicates how many pixels from the edge
                        to start this row.

        :floating_rects: Floating rectangles we need to align around
        """
        aligned_left_start_x = start_x
        for floater in floating_rects:
            if (floater.vertical_overlap(self)
                    and floater.float_pos() == TextFloatPosition.LEFT):
                aligned_left_start_x = floater.right
        self.left = aligned_left_start_x  # noqa pylint: disable=attribute-defined-outside-init,invalid-name; pylint getting confused
        current_start_x = self.left
        for item in self.items:
            item.x = current_start_x
            current_start_x += item.width

    def align_right_row(self, start_x: int, floating_rects):
        """
        Align this row to the right.

        :param start_x: Effectively the padding. Indicates how many pixels from the right edge
                        of the layout to start this row.
        """
        aligned_right_start_x = start_x
        for floater in floating_rects:
            if (floater.vertical_overlap(self)
                    and floater.float_pos() == TextFloatPosition.RIGHT):
                aligned_right_start_x = floater.left
        self.right = aligned_right_start_x  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
        current_start_x = self.right
        for item in reversed(self.items):
            item.right = current_start_x
            current_start_x -= item.width

    def vert_align_items_to_row(self):
        """
        Align items in this row to the row's vertical position.
        """
        for item in self.items:
            item.y = self.y

    def merge_adjacent_compatible_chunks(self):
        """
        Merge chunks of text next to each other in this row that have identical styles.

        Should leave the minimum possible chunks in a row given the set styles for text.
        """
        index = 0
        while index < len(self.items)-1:
            current_item = self.items[index]
            next_item = self.items[index+1]
            if (isinstance(current_item, TextLineChunkFTFont) and
                    isinstance(next_item, TextLineChunkFTFont) and
                    current_item.style_match(next_item)):
                current_item.add_text(next_item.text)
                self.items.pop(index+1)
            else:
                index += 1

    def finalise(self, surface, current_end_pos: Optional[int] = None,
                 cumulative_letter_count: Optional[int] = None):
        """
        Finalise this row, turning it into pixels on a pygame surface. Generally done once we are
        finished applying styles and laying out the text.

        :param surface: The surface we are finalising this row on to.
        :param current_end_pos: Optional parameter indicating the current end position of
                                the visible text. This lets us do the 'typewriter' effect.
        :param cumulative_letter_count: A count of how many letters we have already finalised.
                                        Also helps with the 'typewriter' effect.
        """
        self.merge_adjacent_compatible_chunks()
        for text_chunk in self.items:
            chunk_view_rect = pygame.Rect(self.layout.layout_rect.left,
                                          0, self.layout.view_rect.width,
                                          self.layout.view_rect.height)
            if isinstance(text_chunk, TextLineChunkFTFont):
                if current_end_pos is not None and cumulative_letter_count is not None:
                    if cumulative_letter_count < current_end_pos:
                        text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                            self.text_chunk_height, self.height,
                                            self.layout.x_scroll_offset,
                                            current_end_pos - cumulative_letter_count)
                        cumulative_letter_count += text_chunk.letter_count
                else:
                    text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                        self.text_chunk_height, self.height,
                                        self.layout.x_scroll_offset)
            else:
                text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                    self.text_chunk_height, self.height,
                                    self.layout.x_scroll_offset)

        if self.edit_cursor_active:
            cursor_surface = pygame.surface.Surface(self.cursor_rect.size,
                                                    flags=pygame.SRCALPHA, depth=32)

            cursor_surface.fill(pygame.Color('#FFFFFFFF'))
            self.cursor_rect = pygame.Rect((self.x +
                                            self.cursor_draw_width -
                                            self.layout.x_scroll_offset),
                                           self.y,
                                           2,
                                           max(0, self.height - 2))
            surface.blit(cursor_surface, self.cursor_rect, special_flags=pygame.BLEND_PREMULTIPLIED)

        self.target_surface = surface

        # pygame.draw.rect(self.target_surface, pygame.Color('#FF0000'), self.layout.layout_rect, 1)
        # pygame.draw.rect(self.target_surface, pygame.Color('#00FF00'), self, 1)

        return cumulative_letter_count

    def set_default_text_colour(self, colour):
        """
        Set the default colour of the text.

        :param colour: The colour to set.
        """
        for chunk in self.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if chunk.using_default_text_colour:
                    chunk.colour = colour

    def set_default_text_shadow_colour(self, colour):
        """
        Set the default colour of the text shadow.

        :param colour: The colour to set.
        """
        for chunk in self.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if chunk.using_default_text_shadow_colour:
                    chunk.shadow_colour = colour

    def toggle_cursor(self):
        """
        Toggles the visibility of the edit cursor/carat.

        Generally used to make it flash on and off to catch the attention of the user.
        """
        if self.edit_cursor_active:
            self.edit_cursor_active = False
        else:
            self.edit_cursor_active = True

        if self.target_surface is not None:
            self.clear()
            self.finalise(self.target_surface)

    def clear(self):
        """
        'Clears' the current row from it's target surface by setting the
         area taken up by this row to transparent black.

         Hopefully the target surface is supposed to be transparent black when empty.
        """
        if self.target_surface is not None:
            slightly_wider_rect = pygame.Rect(self.x, self.y,
                                              self.layout.view_rect.width,
                                              self.height)
            self.target_surface.fill(pygame.Color('#00000000'), slightly_wider_rect)

    def _setup_offset_position_from_edit_cursor(self):
        if self.cursor_draw_width > (self.layout.x_scroll_offset +
                                     self.layout.view_rect.width) - self.edit_right_margin:
            self.layout.x_scroll_offset = (self.cursor_draw_width -
                                           self.layout.view_rect.width) + self.edit_right_margin

        if self.cursor_draw_width < self.layout.x_scroll_offset + self.edit_cursor_left_margin:
            self.layout.x_scroll_offset = max(0, self.cursor_draw_width -
                                              self.edit_cursor_left_margin)

    def set_cursor_from_click_pos(self, click_pos: Tuple[int, int]):
        """
        Set the current edit cursor position from a pixel position - usually
        originating from a mouse click.

        :param click_pos: The pixel position to use.
        """
        letter_acc = 0
        cursor_draw_width = 0
        found_chunk = False
        scrolled_click_pos = (click_pos[0]+self.layout.x_scroll_offset, click_pos[1])
        for chunk in self.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if not found_chunk:
                    if chunk.collidepoint(scrolled_click_pos):
                        letter_index = chunk.x_pos_to_letter_index(scrolled_click_pos[0])
                        cursor_draw_width += sum([char_metric[4]
                                                  for char_metric in
                                                  chunk.font.get_metrics(
                                                      chunk.text[:letter_index])])
                        letter_acc += letter_index
                        found_chunk = True
                    else:
                        cursor_draw_width += sum([char_metric[4]
                                                  for char_metric in
                                                  chunk.font.get_metrics(chunk.text)])
                        letter_acc += chunk.letter_count
        if not found_chunk:
            # not inside chunk so move to start of line
            # if we are on left, should be at end of line already
            if scrolled_click_pos[0] < self.left:
                cursor_draw_width = 0
                letter_acc = 0
        self.cursor_draw_width = cursor_draw_width
        self.cursor_index = min(self.letter_count, max(0, letter_acc))

        self._setup_offset_position_from_edit_cursor()

    def set_cursor_position(self, cursor_pos):
        """
        Set the edit cursor position by a character index.

        :param cursor_pos: the character index in this row to put the edit cursor after.
        """
        self.cursor_index = min(self.letter_count, max(0, cursor_pos))
        letter_acc = 0
        cursor_draw_width = 0
        for chunk in self.items:
            if cursor_pos <= letter_acc + chunk.letter_count:
                chunk_letter_pos = cursor_pos - letter_acc
                cursor_draw_width += sum([char_metric[4]
                                          for char_metric
                                          in chunk.font.get_metrics(chunk.text[:chunk_letter_pos])])

                break

            letter_acc += chunk.letter_count
            cursor_draw_width += sum([char_metric[4]
                                      for char_metric in
                                      chunk.font.get_metrics(chunk.text)])

        self.cursor_draw_width = cursor_draw_width

        self._setup_offset_position_from_edit_cursor()

    def get_cursor_index(self) -> int:
        """
        Get the current character index of the cursor

        :return: the character index the edit cursor currently occupies.
        """
        return self.cursor_index

    def insert_text(self, text: str, letter_row_index: int):
        """
        Insert the provided text into this row at the given location.

        :param text: the text to insert.
        :param letter_row_index: the index in the row at which to insert this text.
        """
        letter_acc = 0
        for chunk in self.items:
            if letter_row_index <= letter_acc + chunk.letter_count:
                chunk_index = letter_row_index - letter_acc
                chunk.insert_text(text, chunk_index)
                break

            letter_acc += chunk.letter_count
