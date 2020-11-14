from collections import deque
import pygame
import pygame.freetype
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from pygame_gui.ui_manager import UIManager

from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.text import SimpleTestLayoutRect, TextLineChunkFTFont, HyperlinkTextChunk
from pygame_gui.core.text import TextBoxLayoutRow


class TestTextBoxLayout:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        TextBoxLayout(input_data_queue=input_data,
                      layout_rect=pygame.Rect(0, 0, 200, 300),
                      view_rect=pygame.Rect(0, 0, 200, 150),
                      line_spacing=1.0)

    def test_creation_with_data(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        assert len(layout.layout_rows) > 0

    def test_reprocess_layout_queue(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        assert len(layout.layout_rows) == 4
        layout.reprocess_layout_queue(pygame.Rect(0, 0, 100, 300))
        assert len(layout.layout_rows) == 8

    def test_finalise_to_surf(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout.finalise_to_surf(layout_surface)

        assert layout_surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 0)

    def test_finalise_to_new(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        layout_surface = layout.finalise_to_new()

        assert layout_surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 0)

    def test_update_text_with_new_text_end_pos(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([TextLineChunkFTFont(text='hello',
                                                font=pygame.freetype.Font(None, 20),
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000'))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        layout_surface = layout.finalise_to_new()
        layout.update_text_with_new_text_end_pos(0)  # this does nothing unless we pass in text
        assert layout_surface.get_at((10, 10)) == pygame.Color(0, 0, 0, 0)

        layout.update_text_with_new_text_end_pos(3)
        assert layout_surface.get_at((10, 10)) == pygame.Color(255, 0, 0, 255)

    def test_clear_final_surface(self,  _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        layout_surface = layout.finalise_to_new()

        assert layout_surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 0)
        layout.clear_final_surface()
        assert layout_surface.get_at((10, 10)) == pygame.Color(0, 0, 0, 0)

    def test_set_alpha(self,  _init_pygame, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        layout_surface = layout.finalise_to_new()

        assert layout_surface.get_at((4, 4)) != pygame.Color(0, 0, 0, 0)
        layout.set_alpha(128)
        layout_surface = layout.finalised_surface
        assert layout_surface.get_at((4, 4)).a == 127

    def test_add_chunks_to_hover_group(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([TextLineChunkFTFont(text='hello',
                                                font=pygame.freetype.Font(None, 20),
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            HyperlinkTextChunk(href='boop',
                                               text='a link',
                                               font=pygame.freetype.Font(None, 20),
                                               underlined=False,
                                               colour=pygame.Color('#FFFFFF'),
                                               bg_colour=pygame.Color('#FF0000'),
                                               hover_colour=pygame.Color('#0000FF'),
                                               selected_colour=pygame.Color('#FFFF00'),
                                               hover_underline=False)
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0)

        links_found = deque([])
        layout.add_chunks_to_hover_group(links_found)
        assert len(links_found) == 1

    def test_insert_layout_rects(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        insert_data = deque([TextLineChunkFTFont(text='n insertion',
                                                 font=the_font,
                                                 underlined=False,
                                                 colour=pygame.Color('#FFFFFF'),
                                                 using_default_text_colour=False,
                                                 bg_colour=pygame.Color('#FF0000'))])

        layout.insert_layout_rects(layout_rects=insert_data,
                                   row_index=0,
                                   item_index=1,
                                   chunk_index=9)

        row = layout.layout_rows[0]
        chunk = row.items[1]

        assert chunk.text == 'this is an insertion'

    def test_horiz_centre_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.horiz_center_all_rows()
        assert row.x != 0
        assert row.centerx == 250

    def test_align_left_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.horiz_center_all_rows()
        assert row.x != 0
        assert row.centerx == 250

        layout.align_left_all_rows(x_padding=5)
        assert row.x == 5
        assert row.centerx != 250

    def test_align_right_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.align_right_all_rows(x_padding=5)
        assert row.right == 495

    def test_vert_center_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.y == 0

        layout.vert_center_all_rows()
        assert row.centery == 150

    def test_vert_align_top_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.y == 0
        layout.vert_center_all_rows()
        assert row.centery == 150
        layout.vert_align_top_all_rows(y_padding=10)
        assert row.y == 10

    def test_vert_align_bottom_all_rows(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0)

        row = layout.layout_rows[0]
        assert row.y == 0
        layout.vert_align_bottom_all_rows(y_padding=8)
        assert row.bottom == 292

    def test_set_cursor_position(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0)

        layout.set_cursor_position(13)

        assert layout.cursor_text_row is not None
        assert layout.cursor_text_row.cursor_position == 2
        assert layout.cursor_text_row.cursor_draw_width == 17

    def test_set_cursor_from_click_pos(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 20)
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0)

        layout.set_cursor_from_click_pos((17, 24))
        assert layout.cursor_text_row is not None
        assert layout.cursor_text_row.cursor_position == 2
        assert layout.cursor_text_row.cursor_draw_width == 17


if __name__ == '__main__':
    pytest.console_main()
