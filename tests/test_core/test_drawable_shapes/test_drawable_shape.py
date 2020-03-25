import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape, DrawableShapeState, DrawableStateTransition
from pygame_gui.ui_manager import UIManager


class TestDrawableShapeState:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        DrawableShapeState('normal')

    def test_get_surface(self, _init_pygame, default_ui_manager: UIManager,
                         _display_surface_return_none):
        normal_state = DrawableShapeState('normal')
        selected_state = DrawableShapeState('selected')
        states = {'normal': normal_state,
                  'selected': selected_state}
        assert isinstance(normal_state.get_surface(), pygame.Surface)

        normal_state.transition = DrawableStateTransition(states=states,
                                                          start_state_id='normal',
                                                          target_state_id='selected',
                                                          duration=0.8)

        assert isinstance(normal_state.get_surface(), pygame.Surface)

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        normal_state = DrawableShapeState('normal')
        selected_state = DrawableShapeState('selected')
        states = {'normal': normal_state,
                  'selected': selected_state}

        normal_state.transition = DrawableStateTransition(states=states,
                                                          start_state_id='normal',
                                                          target_state_id='selected',
                                                          duration=0.8)
        normal_state.update(0.1)

        assert normal_state.has_fresh_surface

        normal_state.update(0.9)

        assert normal_state.transition is None


class TestDrawableShape:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                      theming_parameters={}, states=['normal'], manager=default_ui_manager)

        DrawableShape(containing_rect=pygame.Rect(0, 0, 0, 0),
                      theming_parameters={}, states=['normal'], manager=default_ui_manager)

        with pytest.raises(NotImplementedError, match="No 'normal' state id supplied for drawable shape"):
            DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                          theming_parameters={}, states=['flipper'], manager=default_ui_manager)

    def test_stub_methods(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        shape.redraw_state('normal')
        shape.set_dimensions((50, 50))
        shape.set_position((50, 50))
        shape.collide_point((25, 25))
        shape.clean_up_temp_shapes()

    def test_set_active_state(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal','hovered'],
                              manager=default_ui_manager)

        shape.set_active_state('hovered')

        assert shape.active_state.state_id == 'hovered'

    def test_set_active_state_with_transitions(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'transitions': {('normal', 'hovered'): 0.5,
                                                                  ('hovered', 'normal'): 0.5}},
                              states=['normal', 'hovered'],
                              manager=default_ui_manager)

        shape.set_active_state('hovered')

        shape.update(0.05)

        shape.set_active_state('normal')

        assert shape.active_state.transition is not None

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal', 'hovered'], manager=default_ui_manager)

        assert len(shape.states_to_redraw_queue) == 0

        shape.states_to_redraw_queue.append('normal')
        shape.states_to_redraw_queue.append('hovered')
        shape.update(0.05)
        assert len(shape.states_to_redraw_queue) == 1
        assert shape.need_to_clean_up

        shape.update(0.05)
        assert not shape.need_to_clean_up

        shape.full_rebuild_countdown = 0.5
        shape.should_trigger_full_rebuild = True
        shape.update(0.5)
        assert not shape.should_trigger_full_rebuild

    def test_full_rebuild_on_size_change(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal', 'hovered'], manager=default_ui_manager)
        shape.full_rebuild_on_size_change()
        assert shape.full_rebuild_countdown == shape.time_until_full_rebuild_after_changing_size

    def test_redraw_all_states(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal', 'hovered'], manager=default_ui_manager)

        shape.redraw_all_states()

        assert len(shape.states_to_redraw_queue) == 1

    def test_compute_aligned_text_rect(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'doop doop',
                                                  'font': default_ui_manager.get_theme().get_font([], []),
                                                  'shadow_width': 0,
                                                  'border_width': 0},
                              states=['normal', 'hovered'], manager=default_ui_manager)

        shape.theming['text_horiz_alignment'] = 'left'
        shape.theming['text_vert_alignment'] = 'top'
        shape.theming['text_horiz_alignment_padding'] = 5
        shape.theming['text_vert_alignment_padding'] = 5
        shape.compute_aligned_text_rect()
        assert shape.aligned_text_rect.x == 5
        assert shape.aligned_text_rect.y == 5

        shape.theming['text_horiz_alignment'] = 'center'
        shape.theming['text_vert_alignment'] = 'center'
        shape.theming['text_horiz_alignment_padding'] = 5
        shape.theming['text_vert_alignment_padding'] = 5
        shape.compute_aligned_text_rect()
        assert shape.aligned_text_rect.x == 14
        assert shape.aligned_text_rect.y == 41

        shape.theming['text_horiz_alignment'] = 'right'
        shape.theming['text_vert_alignment'] = 'bottom'
        shape.theming['text_horiz_alignment_padding'] = 5
        shape.theming['text_vert_alignment_padding'] = 5
        shape.compute_aligned_text_rect()
        assert shape.aligned_text_rect.right == 95
        assert shape.aligned_text_rect.bottom == 95

    def test_get_active_surface(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        assert shape.get_active_state_surface().get_width() == 0

        shape.active_state = None
        assert shape.get_active_state_surface().get_height() == 0

    def test_get_surface(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        assert shape.get_surface('normal').get_width() == 0
        assert shape.get_surface('test_fail').get_height() == 0

    def test_get_fresh_surface(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        assert shape.get_fresh_surface().get_width() == 0

    def test_has_fresh_surface(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        assert not shape.has_fresh_surface()

    def test_apply_colour_to_surface(self, _init_pygame, default_ui_manager: UIManager, default_display_surface):

        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={}, states=['normal'], manager=default_ui_manager)

        test_surface = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        test_surface.fill(pygame.Color(255,255,255,255))

        shape.apply_colour_to_surface(pygame.Color(50, 100, 50, 255),
                                      test_surface)

        after_application_colour = test_surface.get_at((0, 0))

        # multiply blend always appears to be 1 pixel down in every channel
        assert after_application_colour == pygame.Color(50-1, 100-1, 50-1, 255-1)

        test_surface_2 = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        test_surface_2.fill(pygame.Color(255, 255, 255, 255))

        shape.apply_colour_to_surface(pygame.Color(150, 100, 150, 255),
                                      test_surface_2,
                                      pygame.Rect(0, 0, 25, 50))

        after_application_colour = test_surface_2.get_at((0, 0))

        # multiply blend always appears to be 1 pixel down in every channel
        assert after_application_colour == pygame.Color(150 - 1, 100 - 1, 150 - 1, 255 - 1)

        after_application_colour = test_surface_2.get_at((30, 0))
        assert after_application_colour == pygame.Color(255, 255, 255, 255)

    def test_rebuild_images_and_text(self, _init_pygame, default_ui_manager: UIManager):
        shape = DrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'doop doop',
                                                  'font': default_ui_manager.get_theme().get_font([], []),
                                                  'shadow_width': 0,
                                                  'border_width': 0,
                                                  'normal_image': pygame.image.load('tests/data/images/splat.png'),
                                                  'text_shadow': pygame.Color(0,0,0,255)},
                              states=['normal'], manager=default_ui_manager)

        shape.theming['text_horiz_alignment'] = 'left'
        shape.theming['text_vert_alignment'] = 'top'
        shape.theming['text_horiz_alignment_padding'] = 5
        shape.theming['text_vert_alignment_padding'] = 5

        shape.compute_aligned_text_rect()
        shape.rebuild_images_and_text('normal_image', 'normal', 'normal_text')



