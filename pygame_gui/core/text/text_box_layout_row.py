from typing import Optional

import pygame

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class TextBoxLayoutRow(pygame.Rect):
    """
    A single line of text-like stuff to be used in a text box type layout.
    """

    def __init__(self, row_start_y, layout):
        super().__init__(0, row_start_y, 0, 0)
        self.layout = layout
        self.items = []

        self.letter_count = 0

        self.y_origin = 0

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
        if not self.items:
            # first item
            self.left = item.left  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
        self.items.append(item)
        self.width += item.width  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        if item.height > self.height:
            self.height = item.height  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        self.letter_count += item.letter_count

    def rewind_row(self, layout_rect_queue):
        """
        Use this to add items from the row back onto a layout queue, useful if we've added
        something to the layout that means that this row needs to be re-run through the
        layout code.

        :param layout_rect_queue: A layout queue that contains items to be laid out in order.
        """
        for rect in reversed(self.items):
            rect.clear()
            layout_rect_queue.appendleft(rect)

        self.items.clear()
        self.width = 0  # pylint: disable=attribute-defined-outside-init; pylint getting confused
        self.height = 0  # pylint: disable=attribute-defined-outside-init; pylint getting confused
        self.x = 0  # noqa pylint: disable=attribute-defined-outside-init,invalid-name; this name is inherited from the base class
        self.letter_count = 0

    def horiz_center_row(self):
        self.centerx = int(round(self.layout.layout_rect.width/2.0))
        current_start_x = self.x
        for item in self.items:
            item.x = current_start_x
            current_start_x += item.width

    def align_left_row(self, start_x: int):
        self.x = start_x
        current_start_x = self.x
        for item in self.items:
            item.x = current_start_x
            current_start_x += item.width

    def align_right_row(self, start_x: int):
        self.right = start_x
        current_start_x = start_x
        for item in self.items:
            item.right = current_start_x
            current_start_x += item.width

    def vert_align_items_to_row(self):
        for item in self.items:
            item.y = self.y

    def merge_adjacent_compatible_chunks(self):
        index = 0
        while index < len(self.items)-1:
            current_item = self.items[index]
            next_item = self.items[index+1]
            if (isinstance(current_item, TextLineChunkFTFont) and
                    isinstance(next_item, TextLineChunkFTFont) and
                    current_item.style_match(next_item)):
                current_item.text += next_item.text
                self.items.pop(index+1)
            else:
                index += 1

    def finalise(self, surface, current_end_pos: Optional[int] = None, cumulative_letter_count: Optional[int] = None):
        self.merge_adjacent_compatible_chunks()

        # Can't merge these two loops because we need to calculate the row origin based on each chunk before blitting
        for text_chunk in self.items:
            if isinstance(text_chunk, TextLineChunkFTFont):
                new_y_origin = text_chunk.y_origin
                if new_y_origin > self.y_origin:
                    self.y_origin = new_y_origin

        for text_chunk in self.items:
            if isinstance(text_chunk, TextLineChunkFTFont):
                if current_end_pos is not None and cumulative_letter_count is not None:
                    if cumulative_letter_count < current_end_pos:
                        text_chunk.finalise(surface, self.y_origin, self.height,
                                            current_end_pos - cumulative_letter_count)
                        cumulative_letter_count += text_chunk.letter_count
                else:
                    text_chunk.finalise(surface, self.y_origin, self.height)

        return cumulative_letter_count
