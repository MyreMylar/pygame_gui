from collections import deque

import pytest
import pygame

from pygame_gui.core.gui_font_freetype import GUIFontFreetype
from pygame_gui.core.text import HTMLParser, TextBoxLayoutRow, TextBoxLayout, TextFloatPosition
from pygame_gui.core.text import SimpleTestLayoutRect, TextLineChunkFTFont
from pygame_gui.ui_manager import UIManager


class TestTextBoxLayoutRow:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=1.25,
                                      layout=text_box_layout)

        assert layout_row.width == 0
        assert layout_row.height == 0

    def test_at_start(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=1.25,
                                      layout=text_box_layout)

        assert layout_row.at_start()
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))
        layout_row.add_item(simple_rect)
        assert not layout_row.at_start()

    def test_add_item(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))
        layout_row.add_item(simple_rect)

        assert len(layout_row.items) == 1
        assert layout_row.width == simple_rect.width
        assert layout_row.text_chunk_height == simple_rect.height
        assert layout_row.height == int(simple_rect.height * line_spacing)

    def test_rewind_row(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(100, 30))
        simple_rect_3 = SimpleTestLayoutRect(dimensions=(80, 30))
        layout_row.add_item(simple_rect)
        layout_row.add_item(simple_rect_2)
        layout_row.add_item(simple_rect_3)

        rewound_data = deque([])
        layout_row.rewind_row(rewound_data)

        assert rewound_data.pop().width == simple_rect_3.width
        assert rewound_data.pop().width == simple_rect_2.width
        assert rewound_data.pop().width == simple_rect.width

    def test_horiz_center_row(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        simple_rect = SimpleTestLayoutRect(dimensions=(20, 30))
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(50, 30))
        simple_rect_3 = SimpleTestLayoutRect(dimensions=(30, 30))
        layout_row.add_item(simple_rect)
        layout_row.add_item(simple_rect_2)
        layout_row.add_item(simple_rect_3)

        layout_row.horiz_center_row(text_box_layout.floating_rects)

        assert layout_row.left == 50
        assert layout_row.items[0].x == 50
        assert layout_row.items[1].x == 70
        assert layout_row.items[2].x == 120
        assert layout_row.items[2].right == 150
        assert layout_row.right == 150

        simple_rect = SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.LEFT)
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.RIGHT)
        text_box_layout.floating_rects.append(simple_rect)
        text_box_layout.floating_rects.append(simple_rect_2)

        layout_row.horiz_center_row(text_box_layout.floating_rects)

    def test_align_left_row(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        simple_rect = SimpleTestLayoutRect(dimensions=(20, 30))
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(50, 30))
        simple_rect_3 = SimpleTestLayoutRect(dimensions=(30, 30))
        layout_row.add_item(simple_rect)
        layout_row.add_item(simple_rect_2)
        layout_row.add_item(simple_rect_3)

        layout_row.horiz_center_row(text_box_layout.floating_rects)
        layout_row.align_left_row(floating_rects=text_box_layout.floating_rects, start_x=5)

        assert layout_row.left == 5
        assert layout_row.items[0].x == 5
        assert layout_row.items[1].x == 25
        assert layout_row.items[2].x == 75
        assert layout_row.items[2].right == 105
        assert layout_row.right == 105

    def test_align_right_row(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        simple_rect = SimpleTestLayoutRect(dimensions=(20, 30))
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(50, 30))
        simple_rect_3 = SimpleTestLayoutRect(dimensions=(30, 30))
        layout_row.add_item(simple_rect)
        layout_row.add_item(simple_rect_2)
        layout_row.add_item(simple_rect_3)

        layout_row.horiz_center_row(text_box_layout.floating_rects)
        layout_row.align_right_row(floating_rects=text_box_layout.floating_rects,
                                   start_x=text_box_layout.layout_rect.width - 5)

        assert layout_row.left == 95
        assert layout_row.items[0].x == 95
        assert layout_row.items[1].x == 115
        assert layout_row.items[2].x == 165
        assert layout_row.items[2].right == 195
        assert layout_row.right == 195

        simple_rect = SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.LEFT)
        simple_rect_2 = SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.RIGHT)
        text_box_layout.floating_rects.append(simple_rect)
        text_box_layout.floating_rects.append(simple_rect_2)

        layout_row.align_right_row(floating_rects=text_box_layout.floating_rects,
                                   start_x=text_box_layout.layout_rect.width - 5)

    def test_vert_align_items_to_row(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)
        font_2 = GUIFontFreetype(None, 20)
        font_3 = GUIFontFreetype(None, 10)
        text_chunk_1 = TextLineChunkFTFont(text='hello ',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_2 = TextLineChunkFTFont(text='this is a',
                                           font=font_2,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_3 = TextLineChunkFTFont(text=' test',
                                           font=font_3,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        layout_row.add_item(text_chunk_1)
        layout_row.add_item(text_chunk_2)
        layout_row.add_item(text_chunk_3)

        # not sure this is right, need to do some more visual testing of vertical
        # alignment of text rects with different height text on a single row.
        assert layout_row.items[0].y == 0
        assert layout_row.items[1].y == 8
        assert layout_row.items[2].y == 16

        layout_row.vert_align_items_to_row()

        assert layout_row.items[0].y == 0
        assert layout_row.items[1].y == 8
        assert layout_row.items[2].y == 16

    def test_merge_adjacent_compatible_chunks(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)
        font_2 = GUIFontFreetype(None, 20)
        text_chunk_1 = TextLineChunkFTFont(text='hello ',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_2 = TextLineChunkFTFont(text='this is a',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_3 = TextLineChunkFTFont(text=' test',
                                           font=font_2,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        layout_row.add_item(text_chunk_1)
        layout_row.add_item(text_chunk_2)
        layout_row.add_item(text_chunk_3)

        assert len(layout_row.items) == 3

        layout_row.merge_adjacent_compatible_chunks()

        assert len(layout_row.items) == 2

    def test_finalise(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)
        font_2 = GUIFontFreetype(None, 20)
        text_chunk_1 = TextLineChunkFTFont(text='hello ',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_2 = TextLineChunkFTFont(text='this is a',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        text_chunk_3 = TextLineChunkFTFont(text=' test',
                                           font=font_2,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#FF0000'))
        layout_row.add_item(text_chunk_1)
        layout_row.add_item(text_chunk_2)
        layout_row.add_item(text_chunk_3)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)

        assert layout_surface.get_at((3, 3)) == pygame.Color(255, 0, 0, 255)

    def test_set_default_text_colour(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)
        text_chunk_1 = TextLineChunkFTFont(text='D',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=True,
                                           bg_colour=pygame.Color('#000000'))

        layout_row.add_item(text_chunk_1)

        layout_row.set_default_text_colour(pygame.Color('#00FF00'))

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)

        assert layout_surface.get_at((18, 18)) == pygame.Color('#00FF00')

    def test_toggle_cursor(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)

        text_chunk_1 = TextLineChunkFTFont(text='test',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#00000000'))

        layout_row.add_item(text_chunk_1)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)

        assert layout_row.edit_cursor_active is False
        assert layout_surface.get_at((1, 5)) == pygame.Color('#00000000')

        layout_row.toggle_cursor()

        assert layout_row.edit_cursor_active is True
        assert layout_surface.get_at((1, 5)) == pygame.Color('#FFFFFF')

        # for x in range(0, 30):
        #     for y in range(0, 30):
        #         print(x, y, ':', layout_surface.get_at((x, y)))

    def test_clear(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)

        text_chunk_1 = TextLineChunkFTFont(text='D',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#00000000'))

        layout_row.add_item(text_chunk_1)
        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)
        assert layout_surface.get_at((18, 18)) == pygame.Color('#FFFFFF')

        layout_row.clear()
        assert layout_surface.get_at((18, 18)) == pygame.Color('#00000000')

    def test_set_cursor_from_click_pos(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)

        text_chunk_1 = TextLineChunkFTFont(text='test',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#00000000'))

        layout_row.add_item(text_chunk_1)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)
        layout_row.toggle_cursor()

        assert layout_row.edit_cursor_active is True
        assert layout_surface.get_at((1, 5)) == pygame.Color('#FFFFFF')
        assert layout_row.cursor_index == 0

        layout_row.set_cursor_from_click_pos((44, 5), num_rows=1)

        layout_row.toggle_cursor()
        layout_row.toggle_cursor()

        assert layout_row.edit_cursor_active is True
        assert layout_surface.get_at((1, 5)) == pygame.Color('#00000000')
        assert layout_row.cursor_index == 3
        assert layout_row.cursor_draw_width == 44

        layout_row.set_cursor_from_click_pos((180, 5), num_rows=1)

        assert layout_row.cursor_index == 4

        layout_row.set_cursor_from_click_pos((-1, 5), num_rows=1)

        assert layout_row.left == 0
        assert layout_row.cursor_index == 0

    def test_set_cursor_position(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        font_1 = GUIFontFreetype(None, 30)

        text_chunk_1 = TextLineChunkFTFont(text='test',
                                           font=font_1,
                                           underlined=False,
                                           colour=pygame.Color('#FFFFFF'),
                                           using_default_text_colour=False,
                                           bg_colour=pygame.Color('#00000000'))

        layout_row.add_item(text_chunk_1)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout_row.finalise(layout_surface)
        layout_row.toggle_cursor()

        assert layout_row.edit_cursor_active is True
        assert layout_surface.get_at((1, 5)) == pygame.Color('#FFFFFF')
        assert layout_row.cursor_index == 0
        assert layout_row.cursor_draw_width == 0

        layout_row.set_cursor_position(3)

        layout_row.toggle_cursor()
        layout_row.toggle_cursor()

        assert layout_row.edit_cursor_active is True
        assert layout_surface.get_at((1, 5)) == pygame.Color('#00000000')
        assert layout_row.cursor_index == 3
        assert layout_row.cursor_draw_width == 44

    def test_insert_text(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        combined_ids = default_ui_manager.get_theme().build_all_combined_ids(['text_box'],
                                                                             ['@test_text'],
                                                                             ['#test_text_1'])
        link_style = {'link_text': pygame.Color('#80A0F0'),
                      'link_hover': pygame.Color('#5080C0'),
                      'link_selected': pygame.Color('#8050C0'),
                      'link_normal_underline': True,
                      'link_hover_underline': True}
        parser = HTMLParser(ui_theme=default_ui_manager.get_theme(),
                            combined_ids=combined_ids,
                            link_style=link_style,
                            line_spacing=1.25)

        input_data = deque([])
        line_spacing = 1.25
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing,
                                        default_font_data=default_font_data)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=line_spacing,
                                      layout=text_box_layout)

        with pytest.raises(AttributeError, match="Trying to insert into empty text row with no Parser"):
            layout_row.insert_text('bad text', 0)

        layout_row.insert_text('test', 0, parser=parser)

        # font_1 = pygame.freetype.Font(None, 30)
        # font_1.origin = True
        # font_1.pad = True
        # text_chunk_1 = TextLineChunkFTFont(text='test',
        #                                    font=font_1,
        #                                    underlined=False,
        #                                    colour=pygame.Color('#FFFFFF'),
        #                                    using_default_text_colour=False,
        #                                    bg_colour=pygame.Color('#00000000'))
        #
        # layout_row.add_item(text_chunk_1)

        layout_row.insert_text(' this', 4)

        assert layout_row.items[0].text == 'test this'


if __name__ == '__main__':
    pytest.console_main()
