import pygame

from pygame_gui.core.text.text_layout_rect import TextLayoutRect


class TextBoxLayoutRow(pygame.Rect):
    """
    A single line of text-like stuff to be used in a text box type layout.
    """

    def __init__(self, row_start_y):
        super().__init__(0, row_start_y, 0, 0)
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
