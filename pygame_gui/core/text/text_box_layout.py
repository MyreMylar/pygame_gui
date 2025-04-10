from typing import Deque, List, Optional, Dict, Any, Tuple
from collections import deque
from bisect import bisect_left

import warnings
import pygame

from pygame.surface import Surface

from pygame_gui.core.interfaces import IColourGradientInterface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect, TextFloatPosition
from pygame_gui.core.text.line_break_layout_rect import LineBreakLayoutRect
from pygame_gui.core.text.hyperlink_text_chunk import HyperlinkTextChunk
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont
from pygame_gui.core.text.image_layout_rect import ImageLayoutRect

from pygame_gui.core.text.text_box_layout_row import TextBoxLayoutRow
from pygame_gui.core.text.html_parser import HTMLParser

from pygame_gui.core.utility import basic_blit


class TextBoxLayout:
    """
    Class to layout multiple lines of text to fit in a defined column.

    The base of the 'column' rectangle is set once the data supplied has been laid out
    to fit in the width provided.
    """

    def __init__(
        self,
        input_data_queue: Deque[TextLayoutRect],
        layout_rect: pygame.Rect,
        view_rect: pygame.Rect,
        line_spacing: float,
        default_font_data: Dict[str, Any],
        allow_split_dashes: bool = True,
        text_direction: int = pygame.DIRECTION_LTR,
        text_x_scroll_enabled: bool = False,
        editable: bool = False,
    ):
        # TODO: supply only a width and create final rect shape or just a final height?
        self.input_data_rect_queue = input_data_queue.copy()
        self.layout_rect = layout_rect.copy()
        self.line_spacing = line_spacing
        self.text_direction = text_direction
        self.text_x_scroll_enabled = text_x_scroll_enabled
        self.editable = editable

        self.edit_cursor_width = 1

        # this is the font used when we don't have anything else
        self.default_font_data = default_font_data
        self.default_font = default_font_data["font"]

        self.allow_split_dashes = allow_split_dashes
        self.last_row_height = int(round(14 * self.line_spacing))

        self.view_rect = view_rect

        self.expand_width = False
        if self.layout_rect.width == -1:
            self.layout_rect.width = 0
            self.expand_width = True
            for rect in self.input_data_rect_queue:
                self.layout_rect.width += rect.width

        self.dynamic_width = self.view_rect.width == -1
        self.dynamic_height = self.view_rect.height == -1

        self.finalised_surface: Optional[pygame.Surface] = None
        self.floating_rects: List[TextLayoutRect] = []
        self.layout_rows: List[TextBoxLayoutRow] = []
        self.row_lengths: List[int] = []
        self.row_lengths_no_end_spaces: List[int] = []
        self.link_chunks: List[HyperlinkTextChunk] = []
        self.letter_count = 0
        self.current_end_pos = 0

        self.alpha = 255
        self.pre_alpha_final_surf: Optional[pygame.Surface] = (
            None  # only need this if we apply non-255 alpha
        )

        self.plain_text = ""

        self.layout_rect_queue = self.input_data_rect_queue.copy()
        current_row = TextBoxLayoutRow(
            row_start_x=self.layout_rect.x,
            row_start_y=self.layout_rect.y,
            row_index=0,
            layout=self,
            line_spacing=self.line_spacing,
        )
        if len(self.layout_rect_queue) > 0:
            self._process_layout_queue(self.layout_rect_queue, current_row)
        else:
            empty_text_chunk = TextLineChunkFTFont(
                "",
                self.default_font,
                False,
                self.default_font_data["font_colour"],
                True,
                self.default_font_data["bg_colour"],
            )
            current_row.add_item(empty_text_chunk)
            self._add_row_to_layout(current_row, True)

        self.edit_buffer = 2
        self.cursor_text_row: Optional[TextBoxLayoutRow] = None
        self.last_horiz_cursor_row_pos = 0

        self.selection_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            128, 128, 200, 255
        )
        self.selection_text_colour: pygame.Color | IColourGradientInterface = (
            pygame.Color(255, 255, 255, 255)
        )
        self.selected_chunks: List[TextLayoutRect] = []
        self.selected_rows: List[TextBoxLayoutRow] = []
        self.selection_start_index = 0
        self.selection_end_index = 0

        self.x_scroll_offset = 0

        self.cursor_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            "#FFFFFFFF"
        )

    def _update_plain_text(self):
        plain_text = ""
        for row in self.layout_rows:
            for item in row.items:
                if isinstance(item, (TextLineChunkFTFont, HyperlinkTextChunk)):
                    plain_text += item.text
                if isinstance(item, LineBreakLayoutRect):
                    plain_text += "\n"
        self.plain_text = plain_text

    def _reprocess_layout_rows(self, from_index, row_to_process_from):
        temp_layout_queue: Deque[TextLayoutRect] = deque([])
        for row in reversed(self.layout_rows[from_index:]):
            row.rewind_row(temp_layout_queue)
        self.layout_rows = self.layout_rows[:from_index]
        self._merge_adjacent_compatible_chunks(temp_layout_queue)
        self._process_layout_queue(temp_layout_queue, row_to_process_from)

    def reprocess_layout_queue(self, layout_rect):
        """
        Re-lays out already parsed text data. Useful to call if the layout requirements have
        changed but the text data hasn't.

        :param layout_rect: The new layout rectangle.
        """
        self.layout_rect = layout_rect
        self.finalised_surface = None
        self.floating_rects = []
        self.layout_rows = []
        self.row_lengths = []

        self.layout_rect_queue = self.input_data_rect_queue.copy()
        current_row = TextBoxLayoutRow(
            row_start_x=self.layout_rect.x,
            row_start_y=self.layout_rect.y,
            row_index=0,
            layout=self,
            line_spacing=self.line_spacing,
        )
        self._process_layout_queue(self.layout_rect_queue, current_row)

    def _process_layout_queue(self, input_queue, current_row):
        while input_queue:
            text_layout_rect = input_queue.popleft()
            text_layout_rect.topleft = tuple(current_row.topright)

            if isinstance(text_layout_rect, LineBreakLayoutRect):
                current_row = self._handle_line_break_rect(
                    current_row, text_layout_rect
                )
            elif text_layout_rect.should_span():
                current_row = self._handle_span_rect(current_row, text_layout_rect)
            elif text_layout_rect.float_pos() != TextFloatPosition.NONE:
                if (
                    isinstance(text_layout_rect, ImageLayoutRect)
                    and text_layout_rect.width > self.layout_rect.width
                ):
                    warnings.warn(
                        "Image at path: "
                        + text_layout_rect.image_path
                        + " too wide for text layout. Layout width = "
                        + str(self.layout_rect.width)
                        + ", Image width = "
                        + str(text_layout_rect.width)
                    )
                else:
                    current_row = self._handle_float_rect(
                        current_row, text_layout_rect, input_queue
                    )
            else:
                current_row = self._handle_regular_rect(
                    current_row, text_layout_rect, input_queue
                )
        # make sure we add the last row to the layout
        self._add_row_to_layout(current_row, last_row=True)
        if self.dynamic_width:
            self.view_rect.width = self.layout_rect.width
        if self.dynamic_height:
            self.view_rect.height = self.layout_rect.height

        self._update_plain_text()

    def _add_row_to_layout(self, current_row: TextBoxLayoutRow, last_row=False):
        # handle an empty row being added to layout
        # otherwise we add infinite rows with no height
        # instead add a line break rect to an empty row.
        if len(current_row.items) == 0 and not last_row:
            current_row.add_item(
                LineBreakLayoutRect(
                    dimensions=(4, self.last_row_height),
                    font=current_row.fall_back_font,
                )
            )
        if current_row not in self.layout_rows:
            self.layout_rows.append(current_row)
        self.layout_rect.height = max(
            self.layout_rect.height, current_row.bottom - self.layout_rect.y
        )
        self._refresh_row_letter_counts()
        if len(current_row.items) != 0:
            self.last_row_height = current_row.items[-1].height
        else:
            self.last_row_height = current_row.height

    def _handle_regular_rect(self, current_row, text_layout_rect, input_queue):
        rhs_limit = self.layout_rect.right
        if self.editable:
            rhs_limit -= self.edit_cursor_width
        for floater in self.floating_rects:
            if floater.vertical_overlap(text_layout_rect):
                if (
                    current_row.at_start()
                    and floater.float_pos() == TextFloatPosition.LEFT
                ):
                    # if we are at the start of a new line see if this rectangle
                    # will overlap with any left aligned floating rectangles
                    text_layout_rect.left = floater.right
                    current_row.left = floater.right
                elif floater.float_pos() == TextFloatPosition.RIGHT:
                    rhs_limit = min(rhs_limit, floater.left)
        # See if this rectangle will fit on the current line
        # also check whether this layout rect is a final unsplittable rectangle that is wider than the layout.
        if (
            not self.expand_width
            and text_layout_rect.right > rhs_limit
            and not (
                len(input_queue) == 0
                and not text_layout_rect.can_split()
                and current_row.x == 0
            )
        ):
            # move to next line and try to split if we can
            current_row = self._split_rect_and_move_to_next_line(
                current_row, rhs_limit, text_layout_rect, input_queue
            )
        else:
            current_row.add_item(text_layout_rect)
            if isinstance(text_layout_rect, HyperlinkTextChunk):
                self.link_chunks.append(text_layout_rect)
            if self.expand_width:
                self.layout_rect.width = max(self.layout_rect.width, current_row.width)
        return current_row

    def _handle_float_rect(self, current_row, test_layout_rect, input_queue):
        max_floater_line_height = current_row.height
        if test_layout_rect.float_pos() == TextFloatPosition.LEFT:
            test_layout_rect.left = 0
            for floater in self.floating_rects:
                if (
                    floater.vertical_overlap(test_layout_rect)
                    and floater.float_pos() == TextFloatPosition.LEFT
                ):
                    test_layout_rect.left = floater.right
                    max_floater_line_height = max(
                        max_floater_line_height, floater.height
                    )
            if (
                not self.expand_width
                and test_layout_rect.right > self.layout_rect.width
            ):
                # If this rectangle doesn't fit, we see if we can split it
                current_row = self._split_rect_and_move_to_next_line(
                    current_row,
                    self.layout_rect.width,
                    test_layout_rect,
                    input_queue,
                    max_floater_line_height,
                )
            else:
                self.floating_rects.append(test_layout_rect)
                # expand overall rect bottom to fit if needed
                self.layout_rect.height = max(
                    self.layout_rect.height,
                    test_layout_rect.bottom - self.layout_rect.y,
                )
                # rewind current text row, so we can account for new floating rect
                current_row.rewind_row(input_queue)

        else:  # TextFloatPosition.right
            rhs_limit = self.layout_rect.width
            for floater in self.floating_rects:
                if (
                    floater.vertical_overlap(test_layout_rect)
                    and floater.float_pos() == TextFloatPosition.RIGHT
                    and floater.left < rhs_limit
                ):
                    rhs_limit = floater.left
                    max_floater_line_height = max(
                        max_floater_line_height, floater.height
                    )
            test_layout_rect.right = rhs_limit
            if test_layout_rect.left < 0:
                # If this rectangle doesn't fit, we see if we can split it
                current_row = self._split_rect_and_move_to_next_line(
                    current_row,
                    self.layout_rect.width,
                    test_layout_rect,
                    input_queue,
                    max_floater_line_height,
                )
            else:
                self._add_floating_rect(current_row, test_layout_rect, input_queue)
        return current_row

    def _add_floating_rect(self, current_row, test_layout_rect, input_queue):
        self.floating_rects.append(test_layout_rect)
        # expand overall rect bottom to fit if needed
        self.layout_rect.height = max(
            self.layout_rect.height, test_layout_rect.bottom - self.layout_rect.y
        )
        # rewind current text row, so we can account for new floating rect
        current_row.rewind_row(input_queue)

    def _handle_span_rect(self, current_row, test_layout_rect):
        if not current_row.at_start():
            # not at start of line so end current row...
            prev_row_font = current_row.fall_back_font
            self._add_row_to_layout(current_row)
            # ...and start new one
            current_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=current_row.top + current_row.line_spacing_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
            current_row.fall_back_font = prev_row_font

        # Make the rect span the current row's full width & add it to the row
        test_layout_rect.width = self.layout_rect.width  # TODO: floating rects?
        current_row.add_item(test_layout_rect)

        # add the row to the layout since it's now full up after spanning the full width...
        prev_row_font = current_row.fall_back_font
        self._add_row_to_layout(current_row)
        # ...then start a new row
        current_row = TextBoxLayoutRow(
            row_start_x=self.layout_rect.x,
            row_start_y=current_row.top + current_row.line_spacing_height,
            row_index=len(self.layout_rows),
            layout=self,
            line_spacing=self.line_spacing,
        )
        current_row.fall_back_font = prev_row_font
        return current_row

    def _handle_line_break_rect(self, current_row, line_break_layout_rect):
        rhs_limit = self.layout_rect.right
        if line_break_layout_rect.right > rhs_limit:
            # can't split a line break so, two new rows
            prev_row_font = current_row.fall_back_font
            self._add_row_to_layout(current_row)
            first_empty_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=current_row.top + current_row.line_spacing_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
            first_empty_row.fall_back_font = prev_row_font
            first_empty_row.add_item(line_break_layout_rect)
            self._add_row_to_layout(first_empty_row)

            # ...then start a second new row
            new_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=first_empty_row.top + first_empty_row.line_spacing_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
            new_row.fall_back_font = prev_row_font
        else:
            # line break, so first end current row...
            current_row.add_item(line_break_layout_rect)
            prev_row_font = current_row.fall_back_font
            self._add_row_to_layout(current_row)

            # ...then start a new row
            new_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=current_row.top + current_row.line_spacing_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
            new_row.fall_back_font = prev_row_font
        return new_row

    def _split_rect_and_move_to_next_line(
        self, current_row, rhs_limit, test_layout_rect, input_queue, floater_height=None
    ):
        # TODO: move floating rect stuff out of here? Right now there is no splitting and the height
        #       is different

        if test_layout_rect.can_split():
            split_point = rhs_limit - test_layout_rect.left
            try:
                new_layout_rect = test_layout_rect.split(
                    split_point, rhs_limit, self.layout_rect.x, self.allow_split_dashes
                )
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
                warnings.warn(
                    "Unable to split word into chunks because text box is too narrow"
                )
                current_row.add_item(test_layout_rect)

                if isinstance(test_layout_rect, HyperlinkTextChunk):
                    self.link_chunks.append(test_layout_rect)

        else:
            # can't split, have to move whole chunk down a line.
            input_queue.appendleft(test_layout_rect)

        # whether we split successfully or not, we need to end the current row...
        prev_row_font = current_row.fall_back_font
        self._add_row_to_layout(current_row)

        # And then start a new one.
        if floater_height is not None:
            new_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=floater_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
        else:
            new_row = TextBoxLayoutRow(
                row_start_x=self.layout_rect.x,
                row_start_y=current_row.top + current_row.line_spacing_height,
                row_index=len(self.layout_rows),
                layout=self,
                line_spacing=self.line_spacing,
            )
        new_row.fall_back_font = prev_row_font
        return new_row

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
                cumulative_letter_count = row.finalise(
                    surface, self.current_end_pos, cumulative_letter_count
                )
        else:
            for row in self.layout_rows:
                row.finalise(surface)
                # pygame.draw.rect(surface, pygame.Color("blue"), row, 1)
                # print("row height:", row.height)

        for floating_rect in self.floating_rects:
            floating_rect.finalise(surface, self.view_rect, 0, 0, 0, 0)

        self.finalised_surface = surface

    def blit_finalised_text_to_surf(self, surface: Surface):
        """
        Lets us blit a finalised text surface to an arbitrary surface.
        Useful for doing stuff with text effects.

        :param surface: the target surface to blit onto.
        """
        if self.finalised_surface is not None:
            basic_blit(surface, self.finalised_surface, (0, 0))

    def finalise_to_new(self):
        """
        Finalises our layout to a brand-new surface that this method creates.
        """
        self.finalised_surface = pygame.surface.Surface(
            (self.layout_rect.width + self.edit_buffer, self.layout_rect.height),
            depth=32,
            flags=pygame.SRCALPHA,
        )
        self.finalised_surface.fill("#00000000")
        self.finalise_to_surf(self.finalised_surface)

        return self.finalised_surface

    def update_text_with_new_text_end_pos(self, new_end_pos: int):
        """
        Sets a new end position for the text in this block and redraws it,
        so we can display a 'typing' type effect. The text will only be displayed
        up to the index position set here.

        :param new_end_pos: The new ending index for the text string.
        """
        found_chunk_to_update = False
        self.current_end_pos = new_end_pos

        row, index_in_row = self._find_row_from_text_box_index(new_end_pos)
        if row is not None:
            cumulative_row_letter_count = 0
            for rect in row.items:
                if not found_chunk_to_update:
                    if cumulative_row_letter_count + rect.letter_count < index_in_row:
                        cumulative_row_letter_count += rect.letter_count
                    else:
                        found_chunk_to_update = True
                        if self.finalised_surface is not None:
                            rect.clear()
                            rect.finalise(
                                self.finalised_surface,
                                self.view_rect,
                                row.y_origin,
                                row.text_chunk_height,
                                row.height,
                                row.line_spacing_height,
                                self.x_scroll_offset,
                                index_in_row - cumulative_row_letter_count,
                            )

    def clear_final_surface(self):
        """
        Clears the finalised surface.
        """
        if self.finalised_surface is not None:
            self.finalised_surface.fill("#00000000")

    def set_alpha(self, alpha: int):
        """
        Set the overall alpha level of this text box from 0 to 255.
        This allows us to fade text in and out of view.

        :param alpha: integer from 0 to 255.
        """
        if self.alpha == 255 and alpha != 255 and self.finalised_surface is not None:
            self.pre_alpha_final_surf = self.finalised_surface.copy()

        self.alpha = alpha

        if self.pre_alpha_final_surf is not None:
            self.finalised_surface = self.pre_alpha_final_surf.copy()
            pre_mul_alpha_colour = pygame.Color(
                self.alpha, self.alpha, self.alpha, self.alpha
            )
            self.finalised_surface.fill(
                pre_mul_alpha_colour, special_flags=pygame.BLEND_RGBA_MULT
            )

    def add_chunks_to_hover_group(self, link_hover_chunks: List[HyperlinkTextChunk]):
        """
        Pass in a list of HyperlinkTextChunk chunks to add to a hover-able group.
        Used for hyperlinks.

        :param link_hover_chunks:
        """
        link_hover_chunks.extend(iter(self.link_chunks))

    def insert_layout_rects(
        self,
        layout_rects: Deque[TextLayoutRect],
        row_index: int,
        item_index: int,
        chunk_index: int,
    ):
        """
        Insert some new layout rectangles from a queue at specific place in the current layout.
        Hopefully this means we only need to redo the layout after this point... we shall see.

        Warning: this is a test function, it may not be up-to-date with current text layout features

        :param layout_rects: the new TextLayoutRects to insert.
        :param row_index: which row we are sticking them on.
        :param item_index: which chunk we are sticking them into.
        :param chunk_index: where in the chunk we are sticking them.
        """
        row = self.layout_rows[row_index]
        item = row.items[item_index]

        if isinstance(item, TextLineChunkFTFont):
            for input_rect in layout_rects:
                if isinstance(input_rect, TextLineChunkFTFont) and item.style_match(
                    input_rect
                ):
                    item.insert_text(input_rect.text, chunk_index)

        self._reprocess_layout_rows(row_index, row)

        if self.finalised_surface is not None:
            if (
                self.layout_rect.width + self.edit_buffer,
                self.layout_rect.height,
            ) != self.finalised_surface.get_size():
                self.finalise_to_new()
            else:
                for row in self.layout_rows[row_index:]:
                    for rect in row.items:
                        rect.finalise(
                            self.finalised_surface,
                            self.view_rect,
                            row.y_origin,
                            row.text_chunk_height,
                            row.height,
                            self.x_scroll_offset,
                        )

    def horiz_center_all_rows(self, method="rect"):
        """
        Horizontally center all rows of text in the layout. This uses 'rectangular' centering
        by default, which could also be called mathematical centering. Sometimes this type of
        centering looks wrong - e.g. for arrows, so we instead have an option to use a 'center
        of mass' style centering for right facing and left facing triangles.

        :param method: this is an ID for the method of centering to use, for almost all cases
                       this will be the default 'rect' style basic centering. However, if you are
                       trying to center an arrow you might try 'right_triangle' or 'left_triangle'
        """
        for row in self.layout_rows:
            row.horiz_center_row(self.floating_rects, method)

    def align_left_all_rows(self, x_padding):
        """
        Align all rows to the left hand side of the layout.

        :param x_padding: the amount of padding to insert to on the left
                          before the text starts.
        """
        start_left = self.layout_rect.left + x_padding
        for row in self.layout_rows:
            row.align_left_row(start_left, self.floating_rects)

    def align_right_all_rows(self, x_padding):
        """
        Align all rows to the right hand side of the layout.

        :param x_padding: the amount of padding to insert to on the right
                          before the text starts.
        """
        start_right = self.layout_rect.width - x_padding
        for row in self.layout_rows:
            row.align_right_row(start_right, self.floating_rects)

    def vert_center_all_rows(self):
        """
        Vertically center all rows of text in the layout.

        TODO: I expect we should have the arrow centering methods in here too.
        """
        total_row_height = 0
        if len(self.layout_rows) > 1:
            for row in self.layout_rows:
                total_row_height += row.line_spacing_height
        elif len(self.layout_rows) == 1:
            total_row_height = self.layout_rows[0].height

        all_row_rect = pygame.Rect(0, 0, 1, total_row_height)
        all_row_rect.centery = self.layout_rect.centery

        new_y = all_row_rect.y
        for row in self.layout_rows:
            row.y = new_y
            row.vert_align_items_to_row()
            new_y += row.line_spacing_height

    def vert_align_top_all_rows(self, y_padding):
        """
        Align all rows to the top of the layout.

        :param y_padding: the amount of padding to insert above
                          before the text starts.
        """
        new_y = self.layout_rect.top + y_padding
        for row in self.layout_rows:
            row.y = new_y
            row.vert_align_items_to_row()
            new_y += row.line_spacing_height

    def vert_align_bottom_all_rows(self, y_padding):
        """
        Align all rows to the bottom of the layout.

        :param y_padding: the amount of padding to insert below
                          before the text starts.
        """
        new_y = self.layout_rect.bottom - y_padding
        for row in reversed(self.layout_rows):
            row.bottom = new_y
            row.vert_align_items_to_row()
            new_y -= row.line_spacing_height

    def set_cursor_to_end_of_current_row(self):
        """
        Set the edit cursor position in the text layout to the end of the current row and returns the overall
        position in the text

        :return: the overall position of the cursor in the text layout, after setting it to the end of the current row
        """
        if self.cursor_text_row is not None:
            is_last_row = self.cursor_text_row == self.layout_rows[-1]
            self.cursor_text_row.set_cursor_to_end(is_last_row)
        return self.get_cursor_index()

    def set_cursor_to_start_of_current_row(self):
        """
        Set the edit cursor position in the text layout to the end of the current row and returns the overall
        position in the text

        :return: the overall position of the cursor in the text layout, after setting it to the end of the current row
        """
        if self.cursor_text_row is not None:
            self.cursor_text_row.set_cursor_to_start()
        return self.get_cursor_index()

    def set_cursor_position(self, cursor_pos):
        """
        Set the edit cursor position in the text layout.

        :param cursor_pos: This is the index of the character the cursor should appear before.
        """
        if self.cursor_text_row is not None:
            if self.cursor_text_row.edit_cursor_active:
                self.cursor_text_row.toggle_cursor()
            self.cursor_text_row = None

        # we figure out how many edit positions there are in the text
        # each letter counts as one additional position, but so does the start of a new row
        edit_pos_accumulator = 0
        for row in self.layout_rows:
            if cursor_pos < edit_pos_accumulator + row.letter_count:
                row.set_cursor_position(cursor_pos - edit_pos_accumulator)
                self.cursor_text_row = row
                break
            if cursor_pos == edit_pos_accumulator + row.letter_count:
                # if the last character in a row is a space, we have more than one row and this isn't the last row
                # we want to jump to the start of the next row
                if len(row.items) > 0:
                    last_chunk = row.items[-1]
                    if len(self.layout_rows) > 1 and isinstance(
                        last_chunk, TextLineChunkFTFont
                    ):
                        if (
                            len(last_chunk.text) > 0
                            and last_chunk.text[-1] == " "
                            and row.row_index != (len(self.layout_rows) - 1)
                        ):
                            edit_pos_accumulator += row.letter_count
                        else:
                            row.set_cursor_position(cursor_pos - edit_pos_accumulator)
                            self.cursor_text_row = row
                            break
                    elif (
                        len(self.layout_rows) > 1
                        and isinstance(last_chunk, LineBreakLayoutRect)
                        and row.row_index != (len(self.layout_rows) - 1)
                    ):
                        # if the last chunk in a row is a line break, and we have more than one row and this isn't
                        # the last row we want to jump to the start of the next row
                        edit_pos_accumulator += row.letter_count
                    else:
                        row.set_cursor_position(cursor_pos - edit_pos_accumulator)
                        self.cursor_text_row = row
                        break

            else:
                edit_pos_accumulator += row.letter_count

        if edit_pos_accumulator == self.letter_count and len(self.layout_rows) > 0:
            last_row = self.layout_rows[-1]
            last_row.set_cursor_position(last_row.letter_count)

    def _find_cursor_row_from_click(self, click_pos):
        found_row = None
        cursor_click_pos = (click_pos[0], click_pos[1])
        for count, row in enumerate(self.layout_rows):
            if count < len(self.layout_rows) - 1:
                if (
                    cursor_click_pos[1] < row.top
                    or cursor_click_pos[1] >= self.layout_rows[count + 1].top
                ):
                    continue
            elif cursor_click_pos[1] < row.top or cursor_click_pos[1] > row.bottom:
                continue
            found_row = row

        if found_row is None and len(self.layout_rows) > 0:
            if cursor_click_pos[1] > self.layout_rows[-1].bottom:
                # we are assuming here that the rows are in height order
                # TODO: check this is always true
                found_row = self.layout_rows[-1]
                cursor_click_pos = found_row.midright

            if cursor_click_pos[1] < self.layout_rows[0].top:
                # we are assuming here that the rows are in height order
                # TODO: check this is always true
                found_row = self.layout_rows[0]
                cursor_click_pos = (cursor_click_pos[0], found_row.centery)

        return found_row, cursor_click_pos

    def set_cursor_from_click_pos(self, click_pos):
        """
        Set the edit cursor position in the text layout from a pixel position. Generally used
        to set the text editing cursor position from a mouse click.

        :param click_pos: This is the pixel position we want the cursor to appear near to.
        """
        if self.cursor_text_row is not None:
            if self.cursor_text_row.edit_cursor_active:
                self.cursor_text_row.toggle_cursor()
            self.cursor_text_row = None

        found_row, final_click_pos = self._find_cursor_row_from_click(click_pos)
        self.cursor_text_row = found_row
        if self.cursor_text_row is not None:
            self.cursor_text_row.set_cursor_from_click_pos(
                final_click_pos, len(self.layout_rows)
            )

    def find_cursor_position_from_click_pos(self, click_pos) -> int:
        """
        Find an edit text cursor position in the text from a click.

        Here we don't set it, we just find it and return it.

        :param click_pos: This is the pixel position we want to find the nearest cursor spot to.
        :return: an integer representing the character index position in the text
        """
        found_row, final_click_pos = self._find_cursor_row_from_click(click_pos)

        if found_row is not None:
            cursor_index = 0
            for row in self.layout_rows:
                if row == found_row:
                    cursor_index += found_row.find_cursor_pos_from_click_pos(
                        final_click_pos, len(self.layout_rows)
                    )[0]
                    break
                cursor_index += row.letter_count
            return cursor_index

        return 0

    def get_cursor_index(self):
        """
        Get the current character index, in the text layout's text, of the current edit cursor
        position.

        Essentially the reverse of 'set_cursor_position()'.
        """
        cursor_index = 0
        if self.cursor_text_row is not None:
            for row in self.layout_rows:
                if row == self.cursor_text_row:
                    cursor_index += self.cursor_text_row.get_cursor_index()
                    break
                cursor_index += row.letter_count
        return cursor_index

    def toggle_cursor(self):
        """
        Toggle the visibility of the edit cursor.

        Used routinely by editable text boxes to make the cursor flash to catch user attention.
        """
        if self.cursor_text_row is not None:
            self.cursor_text_row.toggle_cursor()

    def turn_off_cursor(self):
        """
        Makes the edit test cursor invisible.
        """
        if self.cursor_text_row is not None:
            self.cursor_text_row.turn_off_cursor()

    def turn_on_cursor(self):
        """
        Makes the edit test cursor visible.
        """
        if self.cursor_text_row is not None:
            self.cursor_text_row.turn_on_cursor()

    def set_text_selection(self, start_index, end_index):
        """
        Set a portion of the text layout as 'selected'. This is useful when editing chunks
        of text all at once (e.g. copying to a memory 'clipboard', deleting a block of text).

        :param start_index: the character index to start the selection area at.
        :param end_index: the character index to end the selection area at.
        """
        rows_to_finalise = set([])

        # first clear the current selection
        for chunk in self.selected_chunks:
            if isinstance(chunk, TextLineChunkFTFont):
                chunk.selection_rect = None
                chunk.selected_text = None
                chunk.selection_start_index = 0
            if isinstance(
                chunk, (TextLineChunkFTFont, LineBreakLayoutRect, ImageLayoutRect)
            ):
                chunk.is_selected = False
        self.selected_chunks.clear()
        for row in self.selected_rows:
            row.clear()
            rows_to_finalise.add(row)
        self.selected_rows.clear()

        self.selection_start_index = start_index
        self.selection_end_index = end_index
        # We need to check if the indexes are at the
        # start/end of a chunk and if not, split the chunk
        if start_index != end_index:
            # step 1: find the start chunk
            start_chunk, start_chunk_x_pos, start_letter_index, start_row_index = (
                self._find_chunk_and_chunk_x(start_index)
            )

            # step 2: find the end chunk
            end_chunk, end_chunk_x_pos, end_letter_index, end_row_index = (
                self._find_chunk_and_chunk_x(end_index)
            )

            start_selection = False
            end_selection = False
            for i in range(start_row_index, end_row_index + 1):
                row = self.layout_rows[i]

                row.clear()
                self.selected_rows.append(row)
                rows_to_finalise.add(row)
                for chunk in row.items:
                    if chunk is None:
                        print(
                            "found None chunk in row: ",
                            row.row_index,
                            " with items: ",
                            row.items,
                        )

                    elif isinstance(chunk, TextLineChunkFTFont):
                        if chunk == start_chunk and chunk == end_chunk:
                            start_selection = True
                            end_selection = True
                            # should probably check for text rect here
                            chunk.selected_text = chunk.text[
                                start_letter_index:end_letter_index
                            ]
                            chunk.selection_rect = pygame.Rect(
                                (start_chunk_x_pos, 0),
                                (end_chunk_x_pos - start_chunk_x_pos, chunk.height),
                            )
                            self._set_chunk_selection_data(chunk, start_letter_index)
                        elif chunk == start_chunk:
                            start_selection = True
                            chunk.selected_text = chunk.text[
                                start_letter_index:
                            ]  # should probably check for text rect here
                            chunk.selection_rect = pygame.Rect(
                                (start_chunk_x_pos, 0),
                                (chunk.width - start_chunk_x_pos, chunk.height),
                            )
                            self._set_chunk_selection_data(chunk, start_letter_index)
                        elif chunk == end_chunk:
                            end_selection = True
                            if end_letter_index != 0:
                                chunk.selected_text = chunk.text[
                                    :end_letter_index
                                ]  # should probably check for text rect here
                                chunk.selection_rect = pygame.Rect(
                                    (0, 0), (end_chunk_x_pos, chunk.height)
                                )
                                chunk.is_selected = self._set_selection_colours(
                                    chunk, True
                                )
                                self.selected_chunks.append(chunk)

                        if (
                            start_selection
                            and not end_selection
                            and chunk != start_chunk
                        ):
                            # middle text chunks
                            chunk.selected_text = chunk.text[:]
                            chunk.selection_rect = pygame.Rect((0, 0), chunk.size)
                            chunk.is_selected = self._set_selection_colours(chunk, True)
                            self.selected_chunks.append(chunk)
                    elif isinstance(chunk, (LineBreakLayoutRect, ImageLayoutRect)):
                        if chunk == start_chunk:
                            start_selection = True
                        if (
                            start_selection
                            and not end_selection
                            and (chunk != end_chunk or end_letter_index != 0)
                        ):
                            chunk.is_selected = True
                            if isinstance(chunk, LineBreakLayoutRect):
                                chunk.selection_colour = self.selection_colour
                            self.selected_chunks.append(chunk)
                        if chunk == end_chunk:
                            end_selection = True
        if self.finalised_surface is not None:
            for row in rows_to_finalise:
                row.finalise(self.finalised_surface)
            for floating_rect in self.floating_rects:
                floating_rect.finalise(
                    self.finalised_surface, self.view_rect, 0, 0, 0, 0
                )

    def _set_selection_colours(self, chunk, is_selected):
        chunk.selection_colour = self.selection_colour
        chunk.selection_text_colour = self.selection_text_colour
        return is_selected

    def _set_chunk_selection_data(self, chunk, start_letter_index):
        chunk.selection_start_index = start_letter_index
        chunk.is_selected = self._set_selection_colours(chunk, True)
        self.selected_chunks.append(chunk)

    def _find_chunk_and_chunk_x(self, index: int):
        found_chunk: Optional[
            LineBreakLayoutRect | TextLineChunkFTFont | HyperlinkTextChunk
        ] = None
        letter_index = 0
        letter_accumulator = 0
        row_index = 0
        x_pos_in_chunk = 0
        chunk_row, index_in_row = self._find_row_from_text_box_index(index)
        if chunk_row is not None:
            row_index = chunk_row.row_index
            chunk_in_row_index = 0
            for chunk in chunk_row.items:
                if isinstance(chunk, TextLineChunkFTFont) and found_chunk is None:
                    if index_in_row < letter_accumulator + chunk.letter_count:
                        letter_index = index_in_row - letter_accumulator
                        found_chunk = chunk
                        break
                    letter_accumulator += chunk.letter_count
                    chunk_in_row_index += 1
                elif isinstance(chunk, LineBreakLayoutRect):
                    if index_in_row < letter_accumulator + chunk.letter_count:
                        letter_index = index_in_row - letter_accumulator
                        found_chunk = chunk
                        break
            if found_chunk is None and row_index + 1 < len(self.layout_rows):
                chunk_row = self.layout_rows[row_index + 1]
                row_index = chunk_row.row_index
                letter_index = 0

                for chunk in chunk_row.items:
                    if isinstance(chunk, (TextLineChunkFTFont, LineBreakLayoutRect)):
                        found_chunk = chunk
                        break
        if found_chunk is not None and isinstance(found_chunk, TextLineChunkFTFont):
            x_pos_in_chunk = found_chunk.font.size(found_chunk.text[:letter_index])[0]
        return found_chunk, x_pos_in_chunk, letter_index, row_index

    def _find_and_split_chunk(self, index: int, return_rhs: bool = False):
        found_chunk: Optional[
            LineBreakLayoutRect | TextLineChunkFTFont | HyperlinkTextChunk
        ] = None
        letter_index = 0
        letter_accumulator = 0
        chunk_in_row_index = 0
        row_index = 0
        chunk_row, index_in_row = self._find_row_from_text_box_index(index)
        if chunk_row is not None:
            row_index = chunk_row.row_index
            for chunk in chunk_row.items:
                if isinstance(chunk, TextLineChunkFTFont) and found_chunk is None:
                    if index_in_row < letter_accumulator + chunk.letter_count:
                        letter_index = index_in_row - letter_accumulator
                        found_chunk = chunk
                        break
                    letter_accumulator += chunk.letter_count
                    chunk_in_row_index += 1
                elif isinstance(chunk, LineBreakLayoutRect):
                    if index_in_row < letter_accumulator + chunk.letter_count:
                        letter_index = index_in_row - letter_accumulator
                        found_chunk = chunk
                        break
            if found_chunk is None:
                chunk_in_row_index = 0
                # couldn't find it on this row so use the first chunk of row below
                if row_index + 1 < len(self.layout_rows):
                    chunk_row = self.layout_rows[row_index + 1]
                    row_index = chunk_row.row_index
                    letter_index = 0

                    for chunk in chunk_row.items:
                        if isinstance(
                            chunk, (TextLineChunkFTFont, LineBreakLayoutRect)
                        ):
                            found_chunk = chunk
                            break
        if (
            found_chunk is not None
            and isinstance(found_chunk, TextLineChunkFTFont)
            and found_chunk.can_split()
        ):
            # split the chunk

            # for the start chunk we want the right hand side of the split
            new_chunk = found_chunk.split_index(letter_index)
            chunk_row.items.insert(chunk_in_row_index + 1, new_chunk)

            # first_half = found_chunk
            # second_half = new_chunk
            # if isinstance(first_half, TextLineChunkFTFont):
            #     first_half = first_half.text
            # if isinstance(second_half, TextLineChunkFTFont):
            #     second_half = second_half.text

            if return_rhs:
                found_chunk = new_chunk

        return found_chunk, letter_index, row_index

    def set_default_text_colour(self, colour):
        """
        Set the default text colour, used when no other colour is set for a portion of the text.

        :param colour: the colour to use as the default text colour.
        """
        for row in self.layout_rows:
            row.set_default_text_colour(colour)

    def set_default_text_shadow_colour(self, colour):
        """
        Set the default text shadow colour, used when no other colour is set for
        the shadow of a portion of the text.

        :param colour: the colour to use as the default text shadow colour.
        """
        for row in self.layout_rows:
            row.set_default_text_shadow_colour(colour)

    def insert_text(
        self, text: str, layout_index: int, parser: Optional[HTMLParser] = None
    ):
        """
        Insert some text into the text layout at a given point. Handy when e.g. pasting a chunk
        of text into an existing layout.

        :param text: the text to insert.
        :param layout_index: the character index at which to insert the text.
        :param parser: An optional HTML parser for text styling data
        """
        current_row, index_in_row = self._find_row_from_text_box_index(layout_index)
        if current_row is None:
            raise RuntimeError("no rows in text box layout")
        if (
            index_in_row == current_row.letter_count
            and current_row.row_index < (len(self.layout_rows) - 1)
            and current_row.last_chunk_is_line_break()
        ):
            current_row = self.layout_rows[current_row.row_index + 1]
            index_in_row = 0

        current_row.insert_text(text, index_in_row, parser)

        row_to_process_from = current_row
        row_to_process_from_index = current_row.row_index
        if current_row.row_index > 0:
            row_to_process_from = self.layout_rows[current_row.row_index - 1]
            row_to_process_from_index = row_to_process_from.row_index

        temp_layout_queue: Deque[TextLayoutRect] = deque([])
        for row in reversed(self.layout_rows[row_to_process_from_index:]):
            row.rewind_row(temp_layout_queue)

        self.layout_rows = self.layout_rows[:row_to_process_from_index]
        self._merge_adjacent_compatible_chunks(temp_layout_queue)
        self._process_layout_queue(temp_layout_queue, row_to_process_from)

        if self.finalised_surface is not None:
            for row in self.layout_rows[row_to_process_from_index:]:
                row.finalise(self.finalised_surface)

    def insert_line_break(self, layout_index: int, parser: Optional[HTMLParser]):
        """
        Insert a line break into the text layout at a given point.

        :param layout_index: the character index at which to insert the line break.
        :param parser: An optional HTML parser for text styling data
        """
        found_chunk, _, row_index = self._find_and_split_chunk(layout_index)

        if len(self.layout_rows) > 0 and found_chunk is not None:
            self._insert_line_break_into_row_by_index(row_index, found_chunk, parser)
        if found_chunk is None:
            if layout_index == self.letter_count:
                if len(self.layout_rows) > 0:
                    last_row = self.layout_rows[-1]
                    last_chunk = last_row.get_last_text_or_line_break_chunk()
                    if last_chunk is not None and parser is not None:
                        last_row.insert_linebreak_after_chunk(last_chunk, parser)

                        temp_layout_queue: Deque[TextLayoutRect] = deque([])
                        for row in reversed(self.layout_rows[last_row.row_index :]):
                            row.rewind_row(temp_layout_queue)

                        self.layout_rows = self.layout_rows[: last_row.row_index]
                        self._finish_new_row_after_line_break(
                            temp_layout_queue, last_row
                        )
            else:
                print("couldn't find chunk to split at layout index: ", layout_index)

    def _finish_new_row_after_line_break(self, temp_layout_queue, arg1):
        self._merge_adjacent_compatible_chunks(temp_layout_queue)
        self._process_layout_queue(temp_layout_queue, arg1)

        if self.finalised_surface is not None:
            for row in self.layout_rows[arg1.row_index :]:
                row.finalise(self.finalised_surface)

    def _insert_line_break_into_row_by_index(self, row_index, found_chunk, parser):
        current_row = self.layout_rows[row_index]
        current_row.insert_linebreak_after_chunk(found_chunk, parser)

        temp_layout_queue: Deque[TextLayoutRect] = deque([])
        for row in reversed(self.layout_rows[row_index:]):
            row.rewind_row(temp_layout_queue)

        self.layout_rows = self.layout_rows[:row_index]
        self._finish_new_row_after_line_break(temp_layout_queue, current_row)

    def delete_selected_text(self):
        """
        Delete the currently selected text.
        """
        # clear out current selection ready for split selection
        for chunk in self.selected_chunks:
            if isinstance(chunk, TextLineChunkFTFont):
                chunk.selection_rect = None
                chunk.selected_text = None
                chunk.selection_start_index = 0
            if isinstance(
                chunk, (TextLineChunkFTFont, LineBreakLayoutRect, ImageLayoutRect)
            ):
                chunk.is_selected = False
        self.selected_chunks.clear()
        for row in self.selected_rows:
            row.clear()
        self.selected_rows.clear()

        if self.selection_start_index != self.selection_end_index:
            # step 1: find the start chunk
            start_chunk, _, start_row_index = self._find_and_split_chunk(
                self.selection_start_index, return_rhs=True
            )

            # step 2: find the end chunk
            end_chunk, end_letter_index, end_row_index = self._find_and_split_chunk(
                self.selection_end_index
            )
            start_selection = False
            end_selection = False
            for i in range(start_row_index, end_row_index + 1):
                row = self.layout_rows[i]

                row.clear()
                self.selected_rows.append(row)
                for chunk in row.items:
                    if chunk is not None:
                        if chunk == start_chunk:
                            start_selection = True
                        if (
                            start_selection
                            and not end_selection
                            and (chunk != end_chunk or end_letter_index != 0)
                        ):
                            if isinstance(chunk, TextLineChunkFTFont):
                                chunk.selected_text = chunk.text[:]
                                chunk.selection_rect = pygame.Rect((0, 0), chunk.size)
                                chunk.is_selected = True
                            elif isinstance(
                                chunk, (ImageLayoutRect, LineBreakLayoutRect)
                            ):
                                chunk.is_selected = True
                            self.selected_chunks.append(chunk)

                        if chunk == end_chunk:
                            end_selection = True
                    else:
                        print(
                            "found None chunk in row: ",
                            row.row_index,
                            " with items: ",
                            row.items,
                        )

        max_row_index = 0
        if self.selected_rows:
            current_row = self.selected_rows[0]
        else:
            raise IndexError("No selected rows.")
        self.cursor_text_row = current_row
        letter_acc = 0
        for chunk in current_row.items:
            if (
                isinstance(chunk, TextLineChunkFTFont)
                and chunk.selection_rect is not None
            ):
                current_row.set_cursor_position(letter_acc)
                break

            letter_acc += chunk.letter_count

        current_row_starting_chunk = self.selected_rows[0].items[0]
        for row in reversed(self.selected_rows):
            row.items = [
                chunk
                for chunk in row.items
                if not (
                    isinstance(
                        chunk,
                        (TextLineChunkFTFont, ImageLayoutRect, LineBreakLayoutRect),
                    )
                    and chunk.is_selected
                )
            ]
            max_row_index = max(max_row_index, row.row_index)

        row_to_process_from = current_row
        row_to_process_from_index = current_row.row_index
        if current_row.row_index > 0:
            row_to_process_from = self.layout_rows[current_row.row_index - 1]
            row_to_process_from_index = row_to_process_from.row_index

        temp_layout_queue: Deque[TextLayoutRect] = deque([])
        for row in reversed(self.layout_rows[row_to_process_from_index:]):
            row.rewind_row(temp_layout_queue)

        newly_empty_rows = self.layout_rows[row_to_process_from_index:]

        if self.finalised_surface is not None:
            for row in newly_empty_rows:
                row.clear()

        self.layout_rows = self.layout_rows[:row_to_process_from_index]
        self._merge_adjacent_compatible_chunks(temp_layout_queue)
        self._process_layout_queue(temp_layout_queue, row_to_process_from)

        if len(current_row.items) == 0:
            self._setup_and_add_empty_chunk(current_row_starting_chunk, current_row)
        if self.finalised_surface is not None:
            for row in self.layout_rows[row_to_process_from_index:]:
                row.finalise(self.finalised_surface)

        self.selected_rows = []
        self.selected_chunks = []

    @staticmethod
    def _setup_and_add_empty_chunk(
        current_row_starting_chunk: TextLayoutRect, current_row: TextBoxLayoutRow
    ):
        current_row_starting_chunk.width = 0

        if isinstance(
            current_row_starting_chunk,
            (TextLineChunkFTFont, LineBreakLayoutRect, ImageLayoutRect),
        ):
            current_row_starting_chunk.is_selected = False

        if isinstance(current_row_starting_chunk, TextLineChunkFTFont):
            current_row_starting_chunk.text = ""
            current_row_starting_chunk.letter_count = 0
            current_row_starting_chunk.split_points = []
            current_row_starting_chunk.selection_rect = None
            current_row_starting_chunk.selected_text = None
            current_row_starting_chunk.selection_start_index = 0

        current_row.add_item(current_row_starting_chunk)

    def delete_at_cursor(self):
        """
        Deletes a single character in front of the edit cursor. Mimics a standard word
        processor 'delete' operation.
        """
        if self.cursor_text_row is None:
            return
        current_row = self.cursor_text_row
        current_row_index = current_row.row_index
        cursor_pos = self.cursor_text_row.cursor_index
        letter_acc = 0
        deleted_character = False
        chunk_to_remove = None
        for chunk in self.cursor_text_row.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if cursor_pos <= letter_acc + (chunk.letter_count - 1):
                    chunk_letter_pos = cursor_pos - letter_acc
                    chunk.delete_letter_at_index(chunk_letter_pos)
                    deleted_character = True
                    break
            elif isinstance(chunk, LineBreakLayoutRect):
                # delete this chunk
                if cursor_pos <= letter_acc + (chunk.letter_count - 1):
                    chunk_to_remove = chunk
                    deleted_character = True
                    break

            letter_acc += chunk.letter_count
        if chunk_to_remove is not None:
            current_row.items.remove(chunk_to_remove)
        if not deleted_character and current_row_index + 1 < len(self.layout_rows):
            row_below = self.layout_rows[current_row_index + 1]
            for chunk in row_below.items:
                if isinstance(chunk, TextLineChunkFTFont):
                    chunk.delete_letter_at_index(0)

        row_to_process_from = current_row
        row_to_process_from_index = current_row.row_index
        if current_row.row_index > 0:
            row_to_process_from = self.layout_rows[current_row.row_index - 1]
            row_to_process_from_index = row_to_process_from.row_index

        self._reprocess_layout_rows(row_to_process_from_index, row_to_process_from)

        if self.finalised_surface is not None:
            for row in self.layout_rows[row_to_process_from_index:]:
                row.finalise(self.finalised_surface)

    def backspace_at_cursor(self):
        """
        Deletes a single character behind the edit cursor. Mimics a standard word
        processor 'backspace' operation.
        """
        if self.cursor_text_row is None:
            return
        current_row = self.cursor_text_row
        current_row_index = current_row.row_index
        cursor_pos = self.cursor_text_row.cursor_index
        letter_acc = 0
        if current_row_index > 0 and cursor_pos == 0:
            # at start of row with rows above
            # need to delete from end of row above
            current_row_index = current_row_index - 1
            current_row = self.layout_rows[current_row_index]
            cursor_pos = current_row.letter_count

        chunk_to_remove = None
        for chunk in current_row.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if cursor_pos <= letter_acc + chunk.letter_count:
                    chunk_letter_pos = cursor_pos - letter_acc
                    chunk.backspace_letter_at_index(chunk_letter_pos)
                    break
            elif isinstance(chunk, LineBreakLayoutRect):
                # delete this chunk, line break has an edit pos length of 1
                if cursor_pos <= letter_acc + chunk.letter_count:
                    chunk_to_remove = chunk
                    break

            letter_acc += chunk.letter_count
        if chunk_to_remove is not None:
            current_row.items.remove(chunk_to_remove)
        current_row.set_cursor_position(cursor_pos - 1)

        row_to_process_from = current_row
        row_to_process_from_index = current_row.row_index
        if current_row.row_index > 0:
            row_to_process_from = self.layout_rows[current_row.row_index - 1]
            row_to_process_from_index = row_to_process_from.row_index

        self._reprocess_layout_rows(row_to_process_from_index, row_to_process_from)

        if self.finalised_surface is not None:
            for row in self.layout_rows[row_to_process_from_index:]:
                row.finalise(self.finalised_surface)

    def _find_row_from_text_box_index(self, text_box_index: int):
        if len(self.layout_rows) != 0:
            row_index = bisect_left(self.row_lengths, text_box_index)
            if row_index >= len(self.layout_rows):
                row_index = len(self.layout_rows) - 1
            index_in_row = min(
                text_box_index
                - (self.row_lengths[row_index - 1] if row_index != 0 else 0),
                self.row_lengths[row_index],
            )
            return self.layout_rows[row_index], index_in_row

        return None, 0

    def _refresh_row_letter_counts(self):
        self.row_lengths = []
        cumulative_length = 0
        for row in self.layout_rows:
            cumulative_length += row.letter_count
            self.row_lengths.append(cumulative_length)
        self.letter_count = cumulative_length
        self.current_end_pos = self.letter_count

    def append_layout_rects(self, new_queue):
        """
        Add some LayoutRects on to the end of the current layout. This should be relatively fast
        as we don't have to rejig everything before the additions, and some of the time don't need
        to redraw everything either.

        This is new so there may still be some bugs to iron out.

        :param new_queue:
        """
        last_row = self.layout_rows[-1]
        self._process_layout_queue(new_queue, last_row)
        if self.finalised_surface is not None:
            if (
                self.layout_rect.width + self.edit_buffer,
                self.layout_rect.height,
            ) != self.finalised_surface.get_size():
                self.finalise_to_new()
            else:
                for row in self.layout_rows[last_row.row_index :]:
                    row.finalise(self.finalised_surface)

    def redraw_other_chunks(self, not_these_chunks):
        """
        Useful for text effects.
        TODO: no idea how this will play with images? Probably badly.

        :param not_these_chunks: The chunks not to redraw
        :return:
        """
        for row in self.layout_rows:
            for chunk in row.items:
                if chunk not in not_these_chunks and isinstance(
                    chunk, TextLineChunkFTFont
                ):
                    chunk.redraw()

    def clear_effects(self):
        """
        Clear text layout level text effect parameters.
        """
        self.alpha = 255
        self.current_end_pos = self.letter_count

    def set_cursor_colour(self, colour: pygame.Color | IColourGradientInterface):
        """
        Set the colour of the editing carat/text cursor for this text layout.

        :param colour: The colour to set it to.
        """
        self.cursor_colour = colour

    def get_cursor_colour(self) -> pygame.Color | IColourGradientInterface:
        """
        Get the current colour of the editing carat/text cursor.

        :return: a pygame.Color object containing the current colour.
        """
        return self.cursor_colour

    @staticmethod
    def _merge_adjacent_compatible_chunks(chunk_list: deque):
        index = 0
        while index < len(chunk_list) - 1:
            current_item = chunk_list[index]
            next_item = chunk_list[index + 1]
            if (
                isinstance(current_item, TextLineChunkFTFont)
                and isinstance(next_item, TextLineChunkFTFont)
                and current_item.style_match(next_item)
            ):
                current_item.add_text(next_item.text)
                del chunk_list[index + 1]
            else:
                index += 1

    def fit_layout_rect_height_to_rows(self):
        """
        Fit the layout rect height to the height of all the current layout rows.

        """
        if len(self.layout_rows) > 0:
            self.layout_rect.height = max(
                self.layout_rows[-1].bottom - self.layout_rect.top,
                self.view_rect.height,
            )

    def get_cursor_y_pos(self) -> Tuple[int, int]:
        """
        Get the top and bottom position of the edit cursor.

        :return: a tuple of two integers representing the current top and bottom y positions of the edit cursor
        """
        if self.cursor_text_row is not None:
            return self.cursor_text_row.top, self.cursor_text_row.bottom
        else:
            return 0, 0

    def get_cursor_pos_move_up_one_row(self, last_cursor_horiz_index):
        """
        Returns a cursor character position in the row directly above the last horizontal cursor position
        if possible.
        """
        if self.cursor_text_row is None:
            return 0
        cursor_index = 0
        for i, row in enumerate(self.layout_rows):
            if row == self.cursor_text_row:
                if i >= 1:
                    row_above = self.layout_rows[i - 1]
                    cursor_index -= row_above.letter_count
                    row_above_end = row_above.letter_count
                    if row_above.row_text_ends_with_a_single_space() or (
                        len(row_above.items) > 0
                        and isinstance(row_above.items[-1], LineBreakLayoutRect)
                    ):
                        row_above_end = row_above.letter_count - 1
                    cursor_index += min(last_cursor_horiz_index, row_above_end)
                else:
                    cursor_index += last_cursor_horiz_index
                break
            cursor_index += row.letter_count
        return cursor_index

    def get_cursor_pos_move_down_one_row(self, last_cursor_horiz_index):
        """
        Returns a cursor character position in the row directly above the current cursor position
        if possible.
        """
        if self.cursor_text_row is None:
            return 0
        cursor_index = 0
        for i, row in enumerate(self.layout_rows):
            if row == self.cursor_text_row:
                if (i + 1) < len(self.layout_rows):
                    row_below = self.layout_rows[i + 1]
                    cursor_index += row.letter_count
                    row_below_end = row_below.letter_count
                    if row_below.row_text_ends_with_a_single_space() or (
                        len(row_below.items) > 0
                        and isinstance(row_below.items[-1], LineBreakLayoutRect)
                    ):
                        row_below_end = row_below.letter_count - 1
                    cursor_index += min(last_cursor_horiz_index, row_below_end)
                else:
                    cursor_index += last_cursor_horiz_index
                break
            cursor_index += row.letter_count
        return min(cursor_index, self.letter_count)
