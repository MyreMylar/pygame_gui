from collections import deque
import pygame
import pygame.freetype
import pytest

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.text import TextBoxLayoutRow, TextBoxLayout, SimpleTestLayoutRect


class TestTextBoxLayoutRow:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=1.25,
                                      layout=text_box_layout)

        assert layout_row.width == 0
        assert layout_row.height == 0

    def test_at_start(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        layout_row = TextBoxLayoutRow(row_start_x=0,
                                      row_start_y=0,
                                      row_index=0,
                                      line_spacing=1.25,
                                      layout=text_box_layout)

        assert layout_row.at_start()
        simple_rect = SimpleTestLayoutRect(dimensions=(200, 30))
        layout_row.add_item(simple_rect)
        assert not layout_row.at_start()

    def test_add_item(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing)
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

    def test_rewind_row(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing)
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

    def test_horiz_center_row(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing)
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

        layout_row.horiz_center_row()

        assert layout_row.left == 50
        assert layout_row.items[0].x == 50
        assert layout_row.items[1].x == 70
        assert layout_row.items[2].x == 120
        assert layout_row.items[2].right == 150
        assert layout_row.right == 150

    def test_align_left_row(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing)
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

        layout_row.horiz_center_row()
        layout_row.align_left_row(start_x=5)

        assert layout_row.left == 5
        assert layout_row.items[0].x == 5
        assert layout_row.items[1].x == 25
        assert layout_row.items[2].x == 75
        assert layout_row.items[2].right == 105
        assert layout_row.right == 105

    def test_align_right_row(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        line_spacing = 1.25
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=line_spacing)
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

        layout_row.horiz_center_row()
        layout_row.align_right_row(start_x=5)

        assert layout_row.left == 95
        assert layout_row.items[0].x == 95
        assert layout_row.items[1].x == 115
        assert layout_row.items[2].x == 165
        assert layout_row.items[2].right == 195
        assert layout_row.right == 195




if __name__ == '__main__':
    pytest.console_main()
