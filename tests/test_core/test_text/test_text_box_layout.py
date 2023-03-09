from collections import deque
import pygame
import pytest

from pygame_gui.ui_manager import UIManager

from pygame_gui.core.text.text_box_layout import TextBoxLayout, TextFloatPosition
from pygame_gui.core.text import SimpleTestLayoutRect, TextLineChunkFTFont, HyperlinkTextChunk
from pygame_gui.core.text import ImageLayoutRect, HorizRuleLayoutRect
from pygame_gui.core.text.text_layout_rect import Padding


class TestTextBoxLayout:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        TextBoxLayout(input_data_queue=input_data,
                      layout_rect=pygame.Rect(0, 0, 200, 300),
                      view_rect=pygame.Rect(0, 0, 200, 150),
                      line_spacing=1.0,
                      default_font_data=default_font_data)

    def test_creation_with_data(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            HorizRuleLayoutRect(height=1, colour_or_gradient=pygame.Color(255, 255, 255)),
                            SimpleTestLayoutRect(dimensions=(110, 20)),
                            SimpleTestLayoutRect(dimensions=(100, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(20, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(22, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(32, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(32, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(100, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(20, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(20, 30), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(33, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(32, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(22, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20))
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 110),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        assert len(layout.layout_rows) > 0

        input_data = deque([SimpleTestLayoutRect(dimensions=(25, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(25, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(25, 30), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(21, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(22, 20), float_pos=TextFloatPosition.LEFT),
                            SimpleTestLayoutRect(dimensions=(23, 20), float_pos=TextFloatPosition.LEFT)])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 110),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        assert len(layout.layout_rows) > 0

        input_data = deque([SimpleTestLayoutRect(dimensions=(25, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(25, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(25, 30), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(21, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(22, 20), float_pos=TextFloatPosition.RIGHT),
                            SimpleTestLayoutRect(dimensions=(23, 20), float_pos=TextFloatPosition.RIGHT)])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 110),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        assert len(layout.layout_rows) > 0

        input_data = deque([ImageLayoutRect(image_path='tests/data/images/test_emoji.png',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0)),
                            ImageLayoutRect(image_path='tests/data/images/test_emoji.png',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0)),
                            ImageLayoutRect(image_path='tests/data/images/test_emoji.png',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0)),
                            ImageLayoutRect(image_path='tests/data/images/test_emoji.png',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0)),
                            ImageLayoutRect(image_path='tests/data/images/test_emoji.png',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0))])

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 90),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        assert len(layout.layout_rows) > 0

    def test_too_wide_image(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            ImageLayoutRect(image_path='tests/data/images/space_1.jpg',
                                            float_position=TextFloatPosition.RIGHT,
                                            padding=Padding(0, 0, 0, 0))])

        with pytest.warns(UserWarning, match="too wide for text layout"):
            default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
            default_font_data = {"font": default_font,
                                 "font_colour": pygame.Color("#FFFFFF"),
                                 "bg_colour": pygame.Color("#00000000")
                                 }
            TextBoxLayout(input_data_queue=input_data,
                          layout_rect=pygame.Rect(0, 0, 200, 300),
                          view_rect=pygame.Rect(0, 0, 200, 150),
                          line_spacing=1.0,
                          default_font_data=default_font_data)

    def test_reprocess_layout_queue(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        assert len(layout.layout_rows) == 4
        layout.reprocess_layout_queue(pygame.Rect(0, 0, 100, 300))
        assert len(layout.layout_rows) == 9

    def test_finalise_to_surf(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        layout.finalise_to_surf(layout_surface)

        assert layout_surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 0)

    def test_finalise_to_new(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20)),
                            SimpleTestLayoutRect(dimensions=(50, 20)),
                            SimpleTestLayoutRect(dimensions=(30, 20)),
                            SimpleTestLayoutRect(dimensions=(90, 20)),
                            SimpleTestLayoutRect(dimensions=(175, 20))])

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout_surface = layout.finalise_to_new()

        assert layout_surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 0)

    def test_update_text_with_new_text_end_pos(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([TextLineChunkFTFont(text='hello',
                                                font=pygame.Font("tests/data/Roboto-Regular.ttf", 20),
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000'))])

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

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

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

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

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout_surface = layout.finalise_to_new()

        assert layout_surface.get_at((4, 4)) != pygame.Color(0, 0, 0, 0)
        layout.set_alpha(128)
        layout_surface = layout.finalised_surface
        # this is now properly fixed in the next version of pygame (2.1.3)
        if pygame.vernum.minor > 1 or (pygame.vernum.minor == 1 and pygame.vernum.patch >= 3):
            assert layout_surface.get_at((4, 4)).a == 128
        else:
            assert layout_surface.get_at((4, 4)).a == 127

    def test_add_chunks_to_hover_group(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        input_data = deque([TextLineChunkFTFont(text='hello',
                                                font=pygame.Font("tests/data/Roboto-Regular.ttf", 20),
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            HyperlinkTextChunk(href='test',
                                               text='a link',
                                               font=pygame.Font("tests/data/Roboto-Regular.ttf", 20),
                                               underlined=False,
                                               colour=pygame.Color('#FFFFFF'),
                                               bg_colour=pygame.Color('#FF0000'),
                                               hover_colour=pygame.Color('#0000FF'),
                                               active_colour=pygame.Color('#FFFF00'),
                                               hover_underline=False)
                            ])

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 200, 300),
                               view_rect=pygame.Rect(0, 0, 200, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        links_found = []
        layout.add_chunks_to_hover_group(links_found)
        assert len(links_found) == 1

    def test_insert_layout_rects(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 300, 150),
                               view_rect=pygame.Rect(0, 0, 300, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

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
        chunk = row.items[0]

        assert chunk.text == 'hello this is an insertion test'

        layout_surface = layout.finalise_to_new()

        insert_data = deque([TextLineChunkFTFont(text=' with more text',
                                                 font=the_font,
                                                 underlined=False,
                                                 colour=pygame.Color('#FFFFFF'),
                                                 using_default_text_colour=False,
                                                 bg_colour=pygame.Color('#FF0000'))])

        layout.insert_layout_rects(layout_rects=insert_data,
                                   row_index=0,
                                   item_index=0,
                                   chunk_index=50)  # deliberately high, our find function should clamp this

        row = layout.layout_rows[1]
        chunk = row.items[0]

        assert chunk.text == 'with more text'

        insert_data = deque([TextLineChunkFTFont(text=' and then even more text, text forever. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.',
                                                 font=the_font,
                                                 underlined=False,
                                                 colour=pygame.Color('#FFFFFF'),
                                                 using_default_text_colour=False,
                                                 bg_colour=pygame.Color('#FF0000'))])

        layout.insert_layout_rects(layout_rects=insert_data,
                                   row_index=0,
                                   item_index=0,
                                   chunk_index=46)

    def test_horiz_centre_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.horiz_center_all_rows()
        assert row.x != 0
        assert row.centerx == 250

    def test_align_left_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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

        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.horiz_center_all_rows()
        assert row.x != 0
        assert row.centerx == 250

        layout.align_left_all_rows(x_padding=5)
        assert row.x == 5
        assert row.centerx != 250

    def test_align_right_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.x == 0

        layout.align_right_all_rows(x_padding=5)
        assert row.right == 495

    def test_vert_center_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.y == 0

        layout.vert_center_all_rows()
        assert row.centery == 150

    def test_vert_align_top_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.y == 0
        layout.vert_center_all_rows()
        assert row.centery == 150
        layout.vert_align_top_all_rows(y_padding=10)
        assert row.y == 10

    def test_vert_align_bottom_all_rows(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        row = layout.layout_rows[0]
        assert row.y == 0
        layout.vert_align_bottom_all_rows(y_padding=8)
        assert row.bottom == 292

    def test_set_cursor_position(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_cursor_position(13)

        assert layout.cursor_text_row is not None
        assert layout.cursor_text_row.cursor_index == 2
        assert layout.cursor_text_row.cursor_draw_width == 17

        layout.cursor_text_row.edit_cursor_active = True
        layout.set_cursor_position(10)

    def test_set_cursor_from_click_pos(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_cursor_from_click_pos((17, 24))
        assert layout.cursor_text_row is not None
        assert layout.cursor_text_row.cursor_index == 2
        assert layout.cursor_text_row.cursor_draw_width == 17

        layout.cursor_text_row.edit_cursor_active = True
        layout.set_cursor_from_click_pos((17, 24))

    def test_toggle_cursor(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_cursor_from_click_pos((17, 24))

        assert layout.cursor_text_row is not None
        assert not layout.cursor_text_row.edit_cursor_active
        layout.toggle_cursor()
        assert layout.cursor_text_row.edit_cursor_active
        layout.toggle_cursor()
        assert not layout.cursor_text_row.edit_cursor_active

    def test_set_text_selection(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                            TextLineChunkFTFont(text=' end chunk',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FF0000'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000'))
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_text_selection(5, 17)

        assert len(layout.selected_rows) == 2
        assert len(layout.selected_chunks) == 4

        selected_text = ""
        for chunk in layout.selected_chunks:
            selected_text += chunk.text

        assert selected_text == ' this is a t'

        layout.set_text_selection(5, 20)

    def test_set_default_text_colour(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                                                using_default_text_colour=True,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_default_text_colour(pygame.Color('#00FF00'))
        default_chunk_colour = layout.layout_rows[0].items[1].colour
        assert default_chunk_colour == pygame.Color('#00FF00')

    def test_insert_text(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                                                using_default_text_colour=True,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.insert_text('nother insertion', 15)

        row = layout.layout_rows[0]
        chunk = row.items[0]

        assert chunk.text == 'hello this is another insertion test'

        layout.insert_text('text on the end', 51)  # deliberately high number that should get clamped

        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 500, 300),
                               view_rect=pygame.Rect(0, 0, 500, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.layout_rows = []

        with pytest.raises(RuntimeError, match="no rows in text box layout"):
            layout.insert_text('this should fail', 0)

    def test_delete_selected_text(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                                                using_default_text_colour=True,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_text_selection(5, 17)

        assert len(layout.selected_rows) == 2
        assert len(layout.selected_chunks) == 4

        selected_text = ""
        for chunk in layout.selected_chunks:
            selected_text += chunk.text

        assert selected_text == ' this is a t'

        layout.delete_selected_text()

        assert len(layout.selected_rows) == 0
        assert len(layout.selected_chunks) == 0

        selected_text = ""
        for chunk in layout.selected_chunks:
            selected_text += chunk.text

        assert selected_text == ''

        remaining_text = ''
        for row in layout.layout_rows:
            for chunk in row.items:
                remaining_text += chunk.text

        assert remaining_text == 'helloest'

        layout.set_text_selection(0, 0)

        with pytest.raises(IndexError, match='No selected rows.'):
            layout.delete_selected_text()

        insert_data = deque([TextLineChunkFTFont(text=' and then even more text, text forever. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. <a href=none>loads of text</a>. '
                                                      'loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text. '
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.'
                                                      'loads of text. loads of text. loads of text. loads of text.',
                                                 font=the_font,
                                                 underlined=False,
                                                 colour=pygame.Color('#FFFFFF'),
                                                 using_default_text_colour=False,
                                                 bg_colour=pygame.Color('#FF0000'))])

        layout.insert_layout_rects(layout_rects=insert_data,
                                   row_index=0,
                                   item_index=0,
                                   chunk_index=8)

        layout.set_text_selection(62, 112)
        layout.delete_selected_text()

    def test_delete_at_cursor(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                                                using_default_text_colour=True,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_cursor_position(14)
        layout.delete_at_cursor()
        # need to reset the cursor position before deleting again as chunks will have merged and been re-processed
        layout.set_cursor_position(14)
        layout.delete_at_cursor()

        remaining_text = ''
        for row in layout.layout_rows:
            for chunk in row.items:
                remaining_text += chunk.text

        assert remaining_text == 'hello this is test'

    def test_backspace_at_cursor(self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager):
        the_font = pygame.Font("tests/data/Roboto-Regular.ttf", 20)
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
                                                using_default_text_colour=True,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        default_font = default_ui_manager.get_theme().get_font_dictionary().get_default_font()
        default_font_data = {"font": default_font,
                             "font_colour": pygame.Color("#FFFFFF"),
                             "bg_colour": pygame.Color("#00000000")
                             }
        layout = TextBoxLayout(input_data_queue=input_data,
                               layout_rect=pygame.Rect(0, 0, 100, 300),
                               view_rect=pygame.Rect(0, 0, 100, 150),
                               line_spacing=1.0,
                               default_font_data=default_font_data)

        layout.set_cursor_position(16)
        layout.backspace_at_cursor()
        # need to reset the cursor position before backspacing again as chunks will have merged and been re-processed
        layout.set_cursor_position(15)
        layout.backspace_at_cursor()

        remaining_text = ''
        for row in layout.layout_rows:
            for chunk in row.items:
                remaining_text += chunk.text

        assert remaining_text == 'hello this is test'


if __name__ == '__main__':
    pytest.console_main()
