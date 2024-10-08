from typing import Optional, Tuple, List, Union
import math
import pygame
from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont
from pygame_gui.core.text.text_layout_rect import TextFloatPosition
from pygame_gui.core.text.html_parser import HTMLParser
from pygame_gui.core.text.line_break_layout_rect import LineBreakLayoutRect


class TextBoxLayoutRow(pygame.Rect):
    """
    A single line of text-like stuff to be used in a text box type layout.
    """

    def __init__(self, row_start_x, row_start_y, row_index, line_spacing, layout):
        super().__init__(row_start_x, row_start_y, 0, 0)
        self.line_spacing = line_spacing
        self.row_index = row_index
        self.layout = layout
        self.items: List[TextLayoutRect] = []
        self.text_x_scroll_enabled = layout.text_x_scroll_enabled

        self.letter_count = 0

        self.y_origin = 0
        self.text_chunk_height = 0

        self.target_surface = None
        self.cursor_rect = pygame.Rect(self.x, row_start_y, self.layout.edit_cursor_width, self.height - 2)
        self.edit_cursor_active = False
        self.edit_cursor_left_margin = 2
        self.edit_right_margin = 2
        self.cursor_index = 0
        self.cursor_draw_width = 0
        # if we add an empty row and then start adding text, what font do we use?
        # this one.
        self.fall_back_font = self.layout.default_font
        self.surf_row_dirty = False
        self.line_spacing_height = 0

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

        If you wanted to build a right to left writing system layout,
        changing this might be a good place to start.

        :param item: The new item to add to the text row
        """
        item.pre_row_rect = pygame.Rect(item.topleft, item.size)
        item.left = self.right
        self.items.append(item)
        self.width += item.width  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused

        if item.row_chunk_height > self.text_chunk_height:
            self.text_chunk_height = item.row_chunk_height
            if not self.layout.dynamic_height:
                self.height = min(self.layout.layout_rect.height, # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
                                  item.row_chunk_height)
                self.line_spacing_height = min(self.layout.layout_rect.height, # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
                                  int(round(item.row_chunk_height * self.line_spacing)))
            else:
                self.height = int(item.row_chunk_height) # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
                self.line_spacing_height = int(round(item.row_chunk_height * self.line_spacing)) # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
            self.cursor_rect = pygame.Rect(self.x, self.y, self.layout.edit_cursor_width, self.height - 2)

        if isinstance(item, TextLineChunkFTFont):
            if item.y_origin > self.y_origin:
                self.y_origin = item.y_origin

            for origin_item in self.items:
                if isinstance(origin_item, TextLineChunkFTFont):
                    origin_item.origin_row_y_adjust = self.y_origin - origin_item.y_origin
                    origin_item.top = origin_item.pre_row_rect.top + origin_item.origin_row_y_adjust

            self.fall_back_font = item.font

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
        self.line_spacing_height = 0
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

        :param floating_rects: Any floating rects in the row.
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
            self.centerx = (self.layout.layout_rect.centerx +  # noqa pylint: disable=attribute-defined-outside-init; pylint getting confused
                            floater_adjustment)
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

    def align_left_row(self, start_x: int, floating_rects: List[TextLayoutRect]):
        """
        Align this row to the left.

        :param start_x: Effectively the padding. Indicates how many pixels from the edge
                        to start this row.

        :param floating_rects: Floating rectangles we need to align around
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

        :param floating_rects: Any floating rects in the row
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
        direction_list = self.items
        if self.layout.text_direction == pygame.DIRECTION_LTR:
            direction_list = reversed(self.items)
        for item in direction_list:
            item.right = current_start_x
            current_start_x -= item.width

    def vert_align_items_to_row(self):
        """
        Align items in this row to the row's vertical position.
        """
        for item in self.items:
            origin_adjust = 0
            if isinstance(item, TextLineChunkFTFont):
                origin_adjust = self.y_origin - item.y_origin
            item.y = self.y + origin_adjust

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

    def finalise(self, surface: pygame.Surface, current_end_pos: Optional[int] = None,
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
        if self.width > self.layout.layout_rect.width:
            assert RuntimeError("Row longer than layout")
        self.merge_adjacent_compatible_chunks()
        if self.width > self.layout.layout_rect.width:
            assert RuntimeError("Row longer than layout")
        if surface == self.layout.finalised_surface and self.layout.layout_rect.height > surface.get_height():
            self.layout.finalise_to_new()
        else:
            if self.surf_row_dirty:
                self.clear()
            for text_chunk in self.items:
                if text_chunk is not None:
                    chunk_view_rect = pygame.Rect(self.layout.layout_rect.left,
                                                  0, self.layout.view_rect.width,
                                                  self.layout.view_rect.height)
                    if isinstance(text_chunk, TextLineChunkFTFont):
                        if current_end_pos is not None and cumulative_letter_count is not None:
                            if cumulative_letter_count < current_end_pos:
                                text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                                    self.text_chunk_height, self.height, self.line_spacing_height,
                                                    self.layout.x_scroll_offset,
                                                    current_end_pos - cumulative_letter_count)
                                cumulative_letter_count += text_chunk.letter_count
                        else:
                            text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                                self.text_chunk_height, self.height, self.line_spacing_height,
                                                self.layout.x_scroll_offset)
                    else:
                        text_chunk.finalise(surface, chunk_view_rect, self.y_origin,
                                            self.text_chunk_height, self.height, self.line_spacing_height,
                                            self.layout.x_scroll_offset)
                else:
                    print(self.items)

            if self.edit_cursor_active:
                cursor_surface = pygame.surface.Surface(self.cursor_rect.size,
                                                        flags=pygame.SRCALPHA, depth=32)

                cursor_surface.fill(self.layout.get_cursor_colour())
                self.cursor_rect = pygame.Rect((self.x +
                                                self.cursor_draw_width -
                                                self.layout.x_scroll_offset),
                                               self.y,
                                               self.layout.edit_cursor_width,
                                               max(0, self.height - 2))
                surface.blit(cursor_surface, self.cursor_rect, special_flags=pygame.BLEND_PREMULTIPLIED)

            self.target_surface = surface

        # pygame.draw.rect(self.target_surface, pygame.Color('#FF0000'), self.layout.layout_rect, 1)
        # pygame.draw.rect(self.target_surface, pygame.Color('#00FF00'), self, 1)
        self.surf_row_dirty = True
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

    def turn_off_cursor(self):
        """
        Makes the edit test cursor invisible.
        """
        self.edit_cursor_active = False
        if self.target_surface is not None:
            self.clear()
            self.finalise(self.target_surface)

    def turn_on_cursor(self):
        """
        Makes the edit test cursor visible.
        """
        self.edit_cursor_active = True
        if self.target_surface is not None:
            self.clear()
            self.finalise(self.target_surface)

    def clear(self):
        """
        'Clears' the current row from its target surface by setting the
         area taken up by this row to transparent black.

         Hopefully the target surface is supposed to be transparent black when empty.
        """
        if self.target_surface is not None and self.surf_row_dirty:
            slightly_wider_rect = pygame.Rect(self.x, self.y,
                                              self.width + + self.layout.edit_cursor_width,
                                              self.height)
            self.target_surface.fill(pygame.Color('#00000000'), slightly_wider_rect)
            self.surf_row_dirty = False

    def _setup_offset_position_from_edit_cursor(self):
        if self.text_x_scroll_enabled:
            if self.cursor_draw_width > (self.layout.x_scroll_offset +
                                         self.layout.view_rect.width) - self.edit_right_margin:
                self.layout.x_scroll_offset = (self.cursor_draw_width -
                                               self.layout.view_rect.width) + self.edit_right_margin

            if self.cursor_draw_width < self.layout.x_scroll_offset + self.edit_cursor_left_margin:
                self.layout.x_scroll_offset = max(0, self.cursor_draw_width -
                                                  self.edit_cursor_left_margin)

    def set_cursor_from_click_pos(self, click_pos: Tuple[int, int], num_rows: int):
        """
        Set the current edit cursor position from a pixel position - usually
        originating from a mouse click.

        :param num_rows:
        :param click_pos: The pixel position to use.
        """
        self.cursor_index, self.cursor_draw_width = self.find_cursor_pos_from_click_pos(click_pos, num_rows)

        self._setup_offset_position_from_edit_cursor()

    def find_cursor_pos_from_click_pos(self, click_pos: Tuple[int, int], num_rows: int):
        """
        Find an edit cursor position from a pixel position - usually
        originating from a mouse click.

        :param num_rows:
        :param click_pos: The pixel position to use.
        """
        letter_acc = 0
        cursor_draw_width = 0
        found_chunk = False
        scrolled_click_pos = (click_pos[0]+self.layout.x_scroll_offset, click_pos[1])
        for chunk in self.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if not found_chunk:
                    # we only care about the X position at this point.
                    if chunk == self.items[0] and scrolled_click_pos[0] < chunk.left:
                        letter_index = 0
                        cursor_draw_width = 0
                        letter_acc += letter_index
                        found_chunk = True
                    elif chunk.collidepoint((scrolled_click_pos[0], chunk.centery)):
                        letter_index = chunk.x_pos_to_letter_index(scrolled_click_pos[0])
                        cursor_draw_width += chunk.font.size(chunk.text[:letter_index])[0]
                        letter_acc += letter_index
                        found_chunk = True
                    else:
                        cursor_draw_width += chunk.font.size(chunk.text)[0]
                        letter_acc += chunk.letter_count
                        
        if (not found_chunk and scrolled_click_pos[0] >= self.right) or (letter_acc == self.letter_count):
            # if we have more than two rows check if we are on right of whole row and if row has space at the end.
            # If so stick the edit cursor before the space because this is how it works.
            space_count = self.row_text_count_final_whitespace()
            if num_rows > 1 and self.row_text_count_final_whitespace():
                letter_acc -= space_count
                last_chunk = self.get_last_text_chunk()
                if last_chunk is not None:
                    cursor_draw_width -= last_chunk.font.size(" ")[0] * space_count
                    
        cursor_index = min(self.letter_count, max(0, letter_acc))
        return cursor_index, cursor_draw_width

    def row_text_count_final_whitespace(self):
        count = 0
        for item in reversed(self.items):
            if isinstance(item, TextLineChunkFTFont):
                cnt = 0
                for l in reversed(item.text):
                    if l != " ":
                        return count + cnt
                    cnt += 1
                count += cnt
        return count

    def get_last_text_chunk(self):
        for item in reversed(self.items):
            if isinstance(item, TextLineChunkFTFont):
                return item
        return None

    def set_cursor_position(self, cursor_pos):
        """
        Set the edit cursor position by a character index.

        :param cursor_pos: the character index in this row to put the edit cursor after.
        """
        self.cursor_index = min(self.letter_count, max(0, cursor_pos))
        letter_acc = 0
        cursor_draw_width = 0
        for chunk in self.items:
            if isinstance(chunk, TextLineChunkFTFont):
                if cursor_pos <= letter_acc + chunk.letter_count:
                    chunk_letter_pos = cursor_pos - letter_acc
                    cursor_draw_width += chunk.font.size(chunk.text[:chunk_letter_pos])[0]
                    break

                letter_acc += chunk.letter_count
                cursor_draw_width += chunk.font.size(chunk.text)[0]
            elif isinstance(chunk, LineBreakLayoutRect):
                pass

        self.cursor_draw_width = cursor_draw_width

        self._setup_offset_position_from_edit_cursor()

    def set_cursor_to_end(self, is_last_row):
        end_pos = self.letter_count
        # we need to ignore the trailing space on line-wrapped rows,
        # or we will spill over to the row below
        if not is_last_row and len(self.items) > 0:
            last_chunk = self.items[-1]
            if (isinstance(last_chunk, TextLineChunkFTFont) and
                    (len(last_chunk.text) > 0 and last_chunk.text[-1] == " ")):
                end_pos -= 1
            if isinstance(last_chunk, LineBreakLayoutRect):
                end_pos -= 1
        end_pos = max(0, end_pos)
        self.set_cursor_position(end_pos)

    def set_cursor_to_start(self):
        self.set_cursor_position(0)

    def get_cursor_index(self) -> int:
        """
        Get the current character index of the cursor

        :return: the character index the edit cursor currently occupies.
        """
        return self.cursor_index

    def insert_text(self, text: str, letter_row_index: int,
                    parser: Optional[HTMLParser] = None):
        """
        Insert the provided text into this row at the given location.

        :param text: the text to insert.
        :param letter_row_index: the index in the row at which to insert this text.
        :param parser: An optional HTML parser for text styling data
        """
        letter_acc = 0
        if len(self.items) > 0:
            for chunk in self.items:
                if isinstance(chunk, TextLineChunkFTFont):
                    if letter_row_index <= letter_acc + chunk.letter_count:
                        chunk_index = letter_row_index - letter_acc
                        chunk.insert_text(text, chunk_index)
                        break

                letter_acc += chunk.letter_count
        elif parser is not None:
            text_chunk = parser.create_styled_text_chunk(text)
            self.add_item(text_chunk)
        else:
            raise AttributeError("Trying to insert into empty text row with no Parser"
                                 " for style data - fix this later?")

    def insert_linebreak_after_chunk(self, chunk_to_insert_after: Union[TextLineChunkFTFont, LineBreakLayoutRect], parser: HTMLParser):
        if len(self.items) > 0:
            chunk_insert_index = 0
            for chunk_index, chunk in enumerate(self.items):
                if chunk == chunk_to_insert_after:
                    chunk_insert_index = chunk_index + 1
                    break
            current_font: IGUIFontInterface = chunk_to_insert_after.font
            current_font_size = current_font.get_point_size()
            dimensions = (current_font.get_rect(' ').width,
                          int(round(current_font_size *
                                    self.line_spacing)))
            self.items.insert(chunk_insert_index, LineBreakLayoutRect(dimensions, current_font))
            empty_text_chunk = parser.create_styled_text_chunk('')
            self.items.insert(chunk_insert_index + 1, empty_text_chunk)

    def get_last_text_or_line_break_chunk(self):
        for item in reversed(self.items):
            if isinstance(item, TextLineChunkFTFont) or isinstance(item, LineBreakLayoutRect):
                return item
        return None

    def last_chunk_is_line_break(self):
        if len(self.items) > 0:
            if isinstance(self.items[-1], LineBreakLayoutRect):
                return True
        return False
