from typing import Deque, List
from collections import deque

import warnings
import pygame

from pygame.surface import Surface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.text.line_break_layout_rect import LineBreakLayoutRect
from pygame_gui.core.text.hyperlink_text_chunk import HyperlinkTextChunk
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont

from pygame_gui.core.text.text_box_layout_row import TextBoxLayoutRow


class TextBoxLayout:
    """
    Class to layout multiple lines of text to fit in a defined column.

    The base of the 'column' rectangle is set once the data supplied has been laid out
    to fit in the width provided.
    """
    def __init__(self,
                 input_data_queue: Deque[TextLayoutRect],
                 layout_rect: pygame.Rect):
        # TODO: supply only a width and create final rect shape or just a final height?
        self.input_data_rect_queue = input_data_queue.copy()
        self.layout_rect = layout_rect.copy()

        if self.layout_rect.width == -1:
            self.layout_rect.width = 0
            for rect in self.input_data_rect_queue:
                self.layout_rect.width += rect.width

        self.layout_rect_queue = None
        self.finalised_surface = None
        self.floating_rects = []
        self.layout_rows = []
        self.link_chunks = []
        self.letter_count = 0
        self.current_end_pos = 0

        self.alpha = 255
        self.pre_alpha_final_surf = None  # only need this if we apply non-255 alpha

        self.layout_rect_queue = self.input_data_rect_queue.copy()
        current_row = TextBoxLayoutRow(row_start_y=0, layout=self)
        self._process_layout_queue(self.layout_rect_queue, current_row)

        self.cursor_text_chunk = None

        self.selection_colour = pygame.Color(128, 128, 200, 255)

    def reprocess_layout_queue(self, layout_rect):
        """
        Re-lays out already parsed text data. Useful to call if the layout requirements have
        changed but the text data hasn't.

        :param layout_rect: The new layout rectangle.
        """
        self.layout_rect = layout_rect
        self.layout_rect_queue = None
        self.finalised_surface = None
        self.floating_rects = []
        self.layout_rows = []

        self.layout_rect_queue = self.input_data_rect_queue.copy()
        current_row = TextBoxLayoutRow(row_start_y=0, layout=self)
        self._process_layout_queue(self.layout_rect_queue, current_row)

    def _process_layout_queue(self, input_queue, current_row):

        while input_queue:

            text_layout_rect = input_queue.popleft()
            text_layout_rect.topleft = tuple(current_row.topright)

            if isinstance(text_layout_rect, LineBreakLayoutRect):
                current_row = self._handle_line_break_rect(current_row, text_layout_rect)
            elif text_layout_rect.should_span():
                current_row = self._handle_span_rect(current_row, text_layout_rect)
            elif text_layout_rect.float_pos() != TextLayoutRect.FLOAT_NONE:
                current_row = self._handle_float_rect(current_row, text_layout_rect, input_queue)
            else:
                current_row = self._handle_regular_rect(current_row, text_layout_rect, input_queue)
        # make sure we add the last row to the layout
        self._add_row_to_layout(current_row)

    def _add_row_to_layout(self, current_row):
        self.layout_rows.append(current_row)
        if current_row.bottom > self.layout_rect.height:
            self.layout_rect.height = current_row.bottom
        self.letter_count += current_row.letter_count
        self.current_end_pos = self.letter_count

    def _handle_regular_rect(self, current_row, text_layout_rect, input_queue):

        rhs_limit = self.layout_rect.width
        for floater in self.floating_rects:
            if floater.vertical_overlap(text_layout_rect):
                if (current_row.at_start() and
                        floater.float_pos() == TextLayoutRect.FLOAT_LEFT):
                    # if we are at the start of a new line see if this rectangle
                    # will overlap with any left aligned floating rectangles
                    text_layout_rect.left = floater.right
                elif floater.float_pos() == TextLayoutRect.FLOAT_RIGHT:
                    if floater.left < rhs_limit:
                        rhs_limit = floater.left
        # See if this rectangle will fit on the current line
        if text_layout_rect.right > rhs_limit:
            # move to next line and try to split if we can
            current_row = self._split_rect_and_move_to_next_line(current_row,
                                                                 rhs_limit,
                                                                 text_layout_rect,
                                                                 input_queue)
        else:
            current_row.add_item(text_layout_rect)
            if isinstance(text_layout_rect, HyperlinkTextChunk):
                self.link_chunks.append(text_layout_rect)
        return current_row

    def _handle_float_rect(self, current_row, test_layout_rect, input_queue):
        max_floater_line_height = current_row.height
        if test_layout_rect.float_pos() == TextLayoutRect.FLOAT_LEFT:
            test_layout_rect.left = 0
            for floater in self.floating_rects:
                if (floater.vertical_overlap(test_layout_rect)
                        and floater.float_pos() == TextLayoutRect.FLOAT_LEFT):
                    test_layout_rect.left = floater.right
                    if max_floater_line_height < floater.height:
                        max_floater_line_height = floater.height
            if test_layout_rect.right > self.layout_rect.width:
                # If this rectangle won't fit, we see if we can split it
                current_row = self._split_rect_and_move_to_next_line(
                    current_row,
                    self.layout_rect.width,
                    test_layout_rect,
                    max_floater_line_height)
            else:
                self.floating_rects.append(test_layout_rect)
                # expand overall rect bottom to fit if needed
                if test_layout_rect.bottom > self.layout_rect.height:
                    self.layout_rect.height = test_layout_rect.bottom
                # rewind current text row so we can account for new floating rect
                current_row.rewind_row(input_queue)

        else:  # FLOAT_RIGHT
            rhs_limit = self.layout_rect.width
            for floater in self.floating_rects:
                if (floater.vertical_overlap(test_layout_rect)
                        and floater.float_pos() == TextLayoutRect.FLOAT_RIGHT
                        and floater.left < rhs_limit):
                    rhs_limit = floater.left
                    if max_floater_line_height < floater.height:
                        max_floater_line_height = floater.height
            test_layout_rect.right = rhs_limit
            if test_layout_rect.left < 0:
                # If this rectangle won't fit, we see if we can split it
                current_row = self._split_rect_and_move_to_next_line(
                    current_row,
                    self.layout_rect.width,
                    test_layout_rect,
                    max_floater_line_height)
            else:
                self._add_floating_rect(current_row, test_layout_rect, input_queue)
        return current_row

    def _add_floating_rect(self, current_row, test_layout_rect, input_queue):
        self.floating_rects.append(test_layout_rect)
        # expand overall rect bottom to fit if needed
        if test_layout_rect.bottom > self.layout_rect.height:
            self.layout_rect.height = test_layout_rect.bottom
        # rewind current text row so we can account for new floating rect
        current_row.rewind_row(input_queue)

    def _handle_span_rect(self, current_row, test_layout_rect):
        if not current_row.at_start():
            # not at start of line so end current row...
            self._add_row_to_layout(current_row)
            # ...and start new one
            current_row = TextBoxLayoutRow(row_start_y=current_row.bottom, layout=self)

        # Make the rect span the current row's full width & add it to the row
        test_layout_rect.width = self.layout_rect.width  # TODO: floating rects?
        current_row.add_item(test_layout_rect)

        # add the row to the layout since it's now full up after spanning the full width...
        self._add_row_to_layout(current_row)
        # ...then start a new row
        current_row = TextBoxLayoutRow(row_start_y=current_row.bottom, layout=self)
        return current_row

    def _handle_line_break_rect(self, current_row, test_layout_rect):
        # line break, so first end current row...
        current_row.add_item(test_layout_rect)
        self._add_row_to_layout(current_row)

        # ...then start a new row
        return TextBoxLayoutRow(row_start_y=current_row.bottom, layout=self)

    def _split_rect_and_move_to_next_line(self, current_row, rhs_limit,
                                          test_layout_rect,
                                          input_queue,
                                          floater_height=None):
        # TODO: move floating rect stuff out of here? Right now there is no splitting and the height
        #       is different

        if test_layout_rect.can_split():
            split_point = rhs_limit - test_layout_rect.left
            try:
                new_layout_rect = test_layout_rect.split(split_point, self.layout_rect.width)
                if new_layout_rect is not None:
                    # split successfully...

                    # add left side of rect onto current line
                    current_row.add_item(test_layout_rect)
                    # put right of rect back on the queue and move layout position down a line
                    input_queue.appendleft(new_layout_rect)
                else:
                    # failed to split, have to move whole chunk down a line.
                    input_queue.appendleft(test_layout_rect)
            except ValueError:
                warnings.warn('Unable to split word into'
                              ' chunks because text box is too narrow')

        else:
            # can't split, have to move whole chunk down a line.
            input_queue.appendleft(test_layout_rect)

        # whether we split successfully or not, we need to end the current row...
        self._add_row_to_layout(current_row)

        # And then start a new one.
        if floater_height is not None:
            return TextBoxLayoutRow(row_start_y=floater_height, layout=self)
        else:
            return TextBoxLayoutRow(row_start_y=current_row.bottom, layout=self)

    def finalise_to_surf(self, surface: Surface):
        """
        Take this layout, with everything positioned in the correct place and finalise it to
        a surface.

        May be called again after changes to the layout? Update surf?

        :param surface: The surface we are going to blit the contents of this layout onto.
        """
        if self.current_end_pos != self.letter_count:
            cumulative_letter_count = 0
            # calculate the y-origin of all the rows
            for row in self.layout_rows:
                cumulative_letter_count = row.finalise(surface, self.current_end_pos, cumulative_letter_count)
        else:
            for row in self.layout_rows:
                row.finalise(surface)

        for floating_rect in self.floating_rects:
            floating_rect.finalise(surface)

        self.finalised_surface = surface

    def finalise_to_new(self):
        """
        Finalises our layout to a brand new surface that this method creates.
        """
        self.finalised_surface = pygame.Surface(self.layout_rect.size,
                                                depth=32, flags=pygame.SRCALPHA)
        self.finalised_surface.fill('#00000000')
        self.finalise_to_surf(self.finalised_surface)

        return self.finalised_surface

    def update_text_with_new_text_end_pos(self, new_end_pos: int):
        """
        Sets a new end position for the text in this block and redraws it
        so we can display a 'typing' type effect. The text will only be displayed
        up to the index position set here.

        :param new_end_pos: The new ending index for the text string.
        """
        cumulative_letter_count = 0
        found_row_to_update = False
        found_chunk_to_update = False
        self.current_end_pos = new_end_pos
        for row in self.layout_rows:
            if not found_row_to_update:
                if cumulative_letter_count + row.letter_count < new_end_pos:
                    cumulative_letter_count += row.letter_count
                else:
                    found_row_to_update = True
                    for rect in row.items:
                        if not found_chunk_to_update:
                            if cumulative_letter_count + rect.letter_count < new_end_pos:
                                cumulative_letter_count += rect.letter_count
                            else:
                                found_chunk_to_update = True
                                rect.clear()
                                rect.finalise(self.finalised_surface, row.y_origin, row.height,
                                              new_end_pos - cumulative_letter_count)

    def clear_final_surface(self):
        """
        Clears the finalised surface.
        """
        if self.finalised_surface is not None:
            self.finalised_surface.fill('#00000000')

    def set_alpha(self, alpha: int):
        """
        Set the overall alpha level of this text box from 0 to 255.
        This allows us to fade text in and out of view.

        :param alpha: integer from 0 to 255.
        """
        if self.alpha == 255 and alpha != 255:
            self.pre_alpha_final_surf = self.finalised_surface.copy()

        self.alpha = alpha

        if self.pre_alpha_final_surf is not None:
            self.finalised_surface = self.pre_alpha_final_surf.copy()
            pre_mul_alpha_colour = pygame.Color(self.alpha, self.alpha,
                                                self.alpha, self.alpha)
            self.finalised_surface.fill(pre_mul_alpha_colour,
                                        special_flags=pygame.BLEND_RGBA_MULT)

    def add_chunks_to_hover_group(self, link_hover_chunks: List[TextLayoutRect]):
        """
        Pass in a list of layout rectangles to add to a hoverable group.
        Usually used for hyperlinks.

        :param link_hover_chunks:
        """
        for chunk in self.link_chunks:
            link_hover_chunks.append(chunk)

    def insert_layout_rects(self, layout_rects: Deque[TextLayoutRect],
                            row_index: int, item_index: int, chunk_index: int):
        """
        Insert some new layout rectangles from a queue at specific place in the current layout.
        Hopefully this means we only need to redo the layout after this point... we shall see.

        :param layout_rects: the new TextLayoutRects to insert.
        :param row_index: which row we are sticking them on.
        :param item_index: which chunk we are sticking them into.
        :param chunk_index: where in the chunk we are sticking them.
        """
        row = self.layout_rows[row_index]
        item = row.items[item_index]

        for input_rect in layout_rects:
            if isinstance(input_rect, TextLineChunkFTFont) and item.style_match(input_rect):
                item.insert_text(input_rect.text, chunk_index)

        temp_layout_queue = deque([])
        for row in reversed(self.layout_rows[row_index:]):
            row.rewind_row(temp_layout_queue)

        self.layout_rows = self.layout_rows[:row_index]

        self._process_layout_queue(temp_layout_queue, row)

        if self.finalised_surface is not None:
            if self.layout_rect.size != self.finalised_surface.get_size():
                self.finalise_to_new()
            else:
                for row in self.layout_rows[row_index:]:
                    for rect in row.items:
                        rect.finalise(self.finalised_surface, row.y_origin, row.height)

    def horiz_center_all_rows(self):
        for row in self.layout_rows:
            row.horiz_center_row()

    def align_left_all_rows(self, x_padding):
        start_left = x_padding
        for row in self.layout_rows:
            row.align_left_row(start_left)

    def align_right_all_rows(self, x_padding):
        start_right = self.layout_rect.width - x_padding
        for row in self.layout_rows:
            row.align_right_row(start_right)

    def vert_center_all_rows(self):
        total_row_height = 0
        for row in self.layout_rows:
            total_row_height += row.height

        half_total_row_height = int(round(total_row_height/2.0))
        half_total_layout_height = int(round(self.layout_rect.height/2.0))
        centered_start_y = half_total_layout_height - half_total_row_height
        new_y = centered_start_y
        for row in self.layout_rows:
            row.y = new_y
            row.vert_align_items_to_row()
            new_y += row.height

    def vert_align_top_all_rows(self, y_padding):
        new_y = y_padding
        for row in self.layout_rows:
            row.y = new_y
            row.vert_align_items_to_row()
            new_y += row.height

    def vert_align_bottom_all_rows(self, y_padding):
        new_y = self.layout_rect.height - y_padding
        for row in reversed(self.layout_rows):
            row.bottom = new_y
            row.vert_align_items_to_row()
            new_y -= row.height

    def set_cursor_from_click_pos(self, click_pos):
        if self.cursor_text_chunk is not None:
            if self.cursor_text_chunk.edit_cursor_active:
                self.cursor_text_chunk.toggle_cursor()
            self.cursor_text_chunk = None

        layout_space_click_pos = pygame.Vector2(click_pos[0] - self.layout_rect.x,
                                                click_pos[1] - self.layout_rect.y)

        for row in self.layout_rows:
            if row.collidepoint(layout_space_click_pos):
                for chunk in row.items:
                    if isinstance(chunk, TextLineChunkFTFont) and chunk.collidepoint(layout_space_click_pos):
                        letter_index = chunk.x_pos_to_letter_index(layout_space_click_pos.x)
                        chunk.set_cursor_position(letter_index)
                        self.cursor_text_chunk = chunk

    def toggle_cursor(self):
        if self.cursor_text_chunk is not None:
            self.cursor_text_chunk.toggle_cursor()

    def set_text_selection(self, start_index, end_index):
        # We need to check if the indexes are at the start/end of a chunk and if not, split the chunk

        start_chunk = None
        start_chunk_row = None
        start_row_index = 0
        start_chunk_index = 0

        end_chunk = None
        end_chunk_row = None
        end_row_index = 0
        end_chunk_index = 0
        # step 1: find the start chunk
        letter_accumulator = 0

        for row in self.layout_rows:
            if start_chunk is None:
                if start_index < letter_accumulator + row.letter_count:
                    start_chunk_row = row
                    for chunk in row.items:
                        if isinstance(chunk, TextLineChunkFTFont) and start_chunk is None:
                            if start_index < letter_accumulator + chunk.letter_count:
                                start_chunk_index = start_index - letter_accumulator
                                start_chunk = chunk
                                break
                            else:
                                letter_accumulator += chunk.letter_count

                else:
                    letter_accumulator += row.letter_count
                    start_row_index += 1
            else:
                break

        if start_chunk_index != 0:
            # split the chunk

            # for the start chunk we want the right hand side of the split
            start_chunk = start_chunk.split_index(start_chunk_index)
            start_chunk_row.items.insert(start_row_index+1, start_chunk)
            start_chunk_index = 0

        # step 1: find the end chunk
        letter_accumulator = 0
        for row in self.layout_rows:
            if end_chunk is None:
                if end_index < letter_accumulator + row.letter_count:
                    end_chunk_row = row
                    for chunk in row.items:
                        if isinstance(chunk, TextLineChunkFTFont) and end_chunk is None:
                            if end_index < letter_accumulator + chunk.letter_count:
                                end_chunk_index = end_index - letter_accumulator
                                end_chunk = chunk
                                break
                            else:
                                letter_accumulator += chunk.letter_count

                else:
                    letter_accumulator += row.letter_count
                    end_row_index += 1
            else:
                break

        if end_chunk_index != 0:
            # split the chunk

            # for the start chunk we want the right hand side of the split
            new_chunk = end_chunk.split_index(end_chunk_index)
            end_chunk_row.items.insert(end_row_index + 1, new_chunk)

        for i in range(start_row_index, end_row_index + 1):
            start_selection = False
            end_selection = False
            row = self.layout_rows[i]
            for chunk in row.items:
                if chunk == start_chunk:
                    start_selection = True

                if start_selection and not end_selection:
                    chunk.is_selected = True
                    chunk.selection_colour = self.selection_colour

                if chunk == end_chunk:
                    end_selection = True

                chunk.clear()

            row.finalise(self.finalised_surface)
