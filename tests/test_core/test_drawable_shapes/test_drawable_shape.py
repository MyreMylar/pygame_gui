import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape
from pygame_gui.ui_manager import UIManager


class TestDrawableShape:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                      theming_parameters={}, states=['normal'], manager=default_ui_manager)

    def test_stub_methods(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        shape.redraw_state('normal')
        shape.set_dimensions((50, 50))
        shape.set_position((50, 50))
        shape.collide_point((25, 25))

    def test_get_surface(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        assert shape.get_surface('normal').get_width() == 0
        assert shape.get_surface('test_fail').get_height() == 0

    def test_compute_aligned_text_rect_centered(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 0,
                                                  'border_width': 0,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)

        shape.compute_aligned_text_rect()

    def test_compute_aligned_text_rect_bottom_right(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 0,
                                                  'border_width': 0,
                                                  'text_horiz_alignment': 'right',
                                                  'text_vert_alignment': 'bottom',
                                                  'text_horiz_alignment_padding': 0,
                                                  'text_vert_alignment_padding': 0},
                              states=['normal'], manager=default_ui_manager)

        shape.compute_aligned_text_rect()
