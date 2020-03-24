from collections import deque
from typing import Dict, List, Union, Tuple

import pygame

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.colour_gradient import ColourGradient


class DrawableShapeState:
    """
    Represents a single state of a drawable shape.

    :param state_id: The ID/name of this state.

    """
    def __init__(self, state_id: str):

        self.state_id = state_id
        self.surface = pygame.Surface((0, 0))  # type: pygame.Surface
        self.has_fresh_surface = False
        self.cached_background_id = None  # type: Union[str, None]
        self.transition = None  # type: Union[DrawableStateTransition, None]

    def get_surface(self) -> pygame.Surface:
        """
        Gets the pygame.Surface of this state. Will be a blend of this state and the previous one
        if we are in a transition.

        :return: A pygame Surface for this state.

        """
        if self.transition is not None:
            return self.transition.produce_blended_result()
        else:
            return self.surface

    def update(self, time_delta: float):
        """
        Updates any transitions this state is in

        :param time_delta: The time passed between frames, measured in seconds.

        """
        if self.transition is not None:
            self.transition.update(time_delta)
            self.has_fresh_surface = True
            if self.transition.finished:
                self.transition = None


class DrawableStateTransition:
    """
    Starts & controls a transition between two states of a drawable shape.

    :param states: A dictionary of all the drawable states.
    :param start_state_id: The state to start from.
    :param target_state_id: The state to transition to.
    :param duration: The length of the transition
    :param progress: The initial progress along the transition.

    """
    def __init__(self, states: Dict[str, DrawableShapeState],
                 start_state_id: str, target_state_id: str,
                 duration: float, *, progress: float = 0.0):

        self.states = states
        self.duration = duration
        self.remaining_time = self.duration - progress
        self.percentage_start_state = 1.0
        self.percentage_target_state = 0.0
        self.start_stat_id = start_state_id
        self.target_state_id = target_state_id
        self.finished = False

    def update(self, time_delta: float):
        """
        Updates the timer for this transition.

        :param time_delta: The time passed between frames, measured in seconds.

        """
        self.remaining_time -= time_delta
        if self.remaining_time > 0.0 and self.duration > 0.0:
            self.percentage_start_state = self.remaining_time / self.duration
            self.percentage_target_state = 1.0 - self.percentage_start_state
        else:
            self.finished = True

    def produce_blended_result(self) -> pygame.Surface:
        """
        Produces a blend between the images of our start state and our target state. The
        progression of the blend is dictated by the progress of time through the transition.

        :return: The blended surface.

        """
        result = self.states[self.start_stat_id].surface.copy()
        blended_target = self.states[self.target_state_id].surface.copy()
        start_multiply_surface = pygame.Surface(self.states[self.start_stat_id].surface.get_size(),
                                                flags=pygame.SRCALPHA, depth=32)
        target_multiply_surface = start_multiply_surface.copy()

        start_alpha = int(round(255.0*self.percentage_start_state))
        target_alpha = 255 - start_alpha

        start_multiply_surface.fill(pygame.Color(start_alpha, start_alpha, start_alpha, 255))
        target_multiply_surface.fill(pygame.Color(target_alpha, target_alpha, target_alpha, 255))

        result.blit(start_multiply_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        blended_target.blit(target_multiply_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        result.blit(blended_target, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return result


class DrawableShape:
    """
    Base class for a graphical 'shape' that we can use for many different UI elements. The intent
    is to make it easy to switch between UI elements having normal rectangles, circles or rounded
    rectangles as their visual shape while having the same non-shape related functionality.

    :param containing_rect: The rectangle which this shape is entirely contained within (including
                            shadows, borders etc)
    :param theming_parameters: A dictionary of user supplied data that alters the appearance of
                               the shape.
    :param states: Names for the different states the shape can be in, each may have different
                   sets of colours & images.
    :param manager: The UI manager for this UI.

    """
    def __init__(self,
                 containing_rect: pygame.Rect,
                 theming_parameters: Dict,
                 states: List[str],
                 manager: IUIManagerInterface):

        self.containing_rect = containing_rect.copy()
        if self.containing_rect.width < 1:
            self.containing_rect.width = 1
        if self.containing_rect.height < 1:
            self.containing_rect.height = 1

        self.theming = theming_parameters

        self.shadow_width = 0
        self.border_width = 0

        self.states = {}
        for state in states:
            self.states[state] = DrawableShapeState(state)

        if 'normal' in states:
            self.active_state = self.states['normal']
        else:
            raise NotImplementedError("No 'normal' state id supplied for drawable shape")

        self.previous_state = None

        if 'transitions' in self.theming:
            self.state_transition_times = self.theming['transitions']
        else:
            self.state_transition_times = {}

        self.ui_manager = manager
        self.shape_cache = self.ui_manager.get_theme().shape_cache

        self.aligned_text_rect = None
        self.click_area_shape = None

        self.states_to_redraw_queue = deque([])
        self.need_to_clean_up = True

        self.should_trigger_full_rebuild = True
        self.time_until_full_rebuild_after_changing_size = 0.35
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

        self.click_area_shape = None
        self.border_rect = None
        self.background_rect = None
        self.aligned_text_rect = None
        self.base_surface = None

    def set_active_state(self, state_id: str):
        """
        Changes the currently active state for the drawable shape and, if setup in the theme,
        creates a transition blend from the previous state to the newly active one.

        :param state_id: the ID of the new state to make active.

        """
        if state_id in self.states and self.active_state.state_id != state_id:
            self.previous_state = self.active_state
            self.active_state = self.states[state_id]
            self.active_state.has_fresh_surface = True

            if self.previous_state is not None and ((self.previous_state.state_id,
                                                     self.active_state.state_id) in
                                                    self.state_transition_times):
                prev_id = self.previous_state.state_id
                next_id = self.active_state.state_id
                duration = self.state_transition_times[(self.previous_state.state_id,
                                                        self.active_state.state_id)]
                if self.previous_state.transition is None:
                    # completely fresh transition
                    self.active_state.transition = DrawableStateTransition(self.states,
                                                                           prev_id,
                                                                           next_id,
                                                                           duration)
                else:
                    # check to see if we are reversing an in-progress transition.
                    if self.previous_state.transition.start_stat_id == self.active_state.state_id:
                        progress_time = self.previous_state.transition.remaining_time
                        transition = DrawableStateTransition(self.states,
                                                             prev_id,
                                                             next_id,
                                                             duration,
                                                             progress=progress_time)
                        self.active_state.transition = transition

    def update(self, time_delta: float):
        """
        Updates the drawable shape to process rebuilds and update blends between states.

        :param time_delta: amount fo time passed between now and the previous frame in seconds.

        """
        if len(self.states_to_redraw_queue) > 0:
            state = self.states_to_redraw_queue.popleft()
            self.redraw_state(state)
        if self.need_to_clean_up and len(self.states_to_redraw_queue) == 0:
            # last state so clean up
            self.clean_up_temp_shapes()
            self.need_to_clean_up = False

        if self.full_rebuild_countdown > 0.0:
            self.full_rebuild_countdown -= time_delta

        if self.should_trigger_full_rebuild and self.full_rebuild_countdown <= 0.0:
            self.full_rebuild_on_size_change()

        self.active_state.update(time_delta)

    def full_rebuild_on_size_change(self):
        """
        Triggered when we've changed the size of the shape and need to rebuild basically everything
        to account for it.

        """
        if 'shadow_width' in self.theming:
            self.shadow_width = self.theming['shadow_width']
        if 'border_width' in self.theming:
            self.border_width = self.theming['border_width']
        self.should_trigger_full_rebuild = False
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def redraw_all_states(self):
        """
        Starts the redrawing process for all states of this shape. Redrawing is done one state at
        a time so will take a few loops of the game to complete if this shape has many states.

        """
        self.states_to_redraw_queue = deque(self.states)
        initial_state = self.states_to_redraw_queue.popleft()
        self.redraw_state(initial_state)

    def compute_aligned_text_rect(self):
        """
        Aligns the text drawing position correctly according to our theming options.

        """
        if ('text' not in self.theming or
                len(self.theming['text']) <= 0 or
                'font' not in self.theming):
            return
        # first we need to create rectangle the size of the text, if there is any text to draw
        self.aligned_text_rect = pygame.Rect((0, 0),
                                             self.theming['font'].size(self.theming['text']))

        if (self.theming['text_horiz_alignment'] == 'center' or
                self.theming['text_horiz_alignment'] not in ['left', 'right']):
            self.aligned_text_rect.centerx = int(self.containing_rect.width / 2)
        elif self.theming['text_horiz_alignment'] == 'left':
            self.aligned_text_rect.x = (self.theming['text_horiz_alignment_padding'] +
                                        self.shadow_width + self.border_width)
        else:
            x_pos = (self.containing_rect.width - self.theming['text_horiz_alignment_padding'] -
                     self.aligned_text_rect.width - self.shadow_width - self.border_width)
            self.aligned_text_rect.x = x_pos
        if (self.theming['text_vert_alignment'] == 'center' or
                self.theming['text_vert_alignment'] not in ['top', 'bottom']):
            self.aligned_text_rect.centery = int(self.containing_rect.height / 2)
        elif self.theming['text_vert_alignment'] == 'top':
            self.aligned_text_rect.y = (self.theming['text_vert_alignment_padding'] +
                                        self.shadow_width + self.border_width)
        else:
            self.aligned_text_rect.y = (self.containing_rect.height - self.aligned_text_rect.height
                                        - self.theming['text_vert_alignment_padding'] -
                                        self.shadow_width - self.border_width)

    def get_active_state_surface(self) -> pygame.Surface:
        """
        Get the main surface from the active state.

        :return: The surface asked for, or the best available substitute.

        """
        if self.active_state is not None:
            return self.active_state.get_surface()
        else:
            return self.ui_manager.get_universal_empty_surface()

    def get_surface(self, state_name: str) -> pygame.Surface:
        """
        Get the main surface from a specific state.

        :param state_name: The state we are trying to get the surface from.

        :return: The surface asked for, or the best available substitute.

        """
        if state_name in self.states and self.states[state_name].surface is not None:
            return self.states[state_name].surface
        elif state_name in self.states and self.states['normal'].surface is not None:
            return self.states['normal'].surface
        else:
            return pygame.Surface((0, 0))

    def get_fresh_surface(self) -> pygame.Surface:
        """
        Gets the surface of the active state and resets the state's 'has_fresh_surface' variable.

        :return: The active state's main pygame.Surface.

        """
        self.active_state.has_fresh_surface = False
        return self.get_active_state_surface()

    def has_fresh_surface(self) -> bool:
        """
        Lets UI elements find out when a state has finished building a fresh surface for times
        when we have to delay it for whatever reason.

        :return: True if there is a freshly built surface waiting, False if the shape has not
                 changed.

        """
        return self.active_state.has_fresh_surface

    @staticmethod
    def apply_colour_to_surface(colour: pygame.Color,
                                shape_surface: pygame.Surface,
                                rect: Union[pygame.Rect, None] = None):
        """
        Apply a colour to a shape surface by multiplication blend. This works best when the shape
        surface is predominantly white.

        :param colour: The colour to apply.
        :param shape_surface: The shape surface to apply the colour to.
        :param rect: A rectangle to apply the colour inside of.

        """
        if rect is not None:
            colour_surface = pygame.Surface(rect.size, flags=pygame.SRCALPHA, depth=32)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, rect, special_flags=pygame.BLEND_RGBA_MULT)
        else:
            colour_surface = pygame.Surface(shape_surface.get_size(),
                                            flags=pygame.SRCALPHA, depth=32)
            colour_surface.fill(colour)
            shape_surface.blit(colour_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def rebuild_images_and_text(self,
                                image_state_str: str,
                                state_str: str,
                                text_colour_state_str: str):
        """
        Rebuilds any text or image used by a specific state in the drawable shape. Effectively
        this means adding them on top of whatever is already in the state's surface. As such it
        should generally be called last in the process of building up a finished drawable shape
        state.

        :param image_state_str: image ID of the state we are going to be adding images and text to.
        :param state_str: normal ID of the state we are going to be adding images and text to.
        :param text_colour_state_str: text ID of the state we are going to be adding images and
                                      text to.

        """
        # Draw any themed images
        if image_state_str in self.theming and self.theming[image_state_str] is not None:
            image_rect = self.theming[image_state_str].get_rect()
            image_rect.center = (int(self.containing_rect.width / 2),
                                 int(self.containing_rect.height / 2))
            self.states[state_str].surface.blit(self.theming[image_state_str], image_rect)
        # Draw any text
        if 'text' in self.theming and 'font' in self.theming and self.theming['text'] is not None:
            if len(self.theming['text']) > 0 and text_colour_state_str in self.theming:
                if not isinstance(self.theming[text_colour_state_str], ColourGradient):
                    text_surface = self.theming['font'].render(self.theming['text'], True,
                                                               self.theming[text_colour_state_str])
                else:
                    text_surface = self.theming['font'].render(self.theming['text'], True,
                                                               pygame.Color('#FFFFFFFF'))
                    self.theming[text_colour_state_str].apply_gradient_to_surface(text_surface)
            else:
                text_surface = None

            if 'text_shadow' in self.theming:
                text_shadow = self.theming['font'].render(self.theming['text'],
                                                          True, self.theming['text_shadow'])

                self.states[state_str].surface.blit(text_shadow,
                                                    (self.aligned_text_rect.x,
                                                     self.aligned_text_rect.y + 1))
                self.states[state_str].surface.blit(text_shadow,
                                                    (self.aligned_text_rect.x,
                                                     self.aligned_text_rect.y - 1))
                self.states[state_str].surface.blit(text_shadow,
                                                    (self.aligned_text_rect.x + 1,
                                                     self.aligned_text_rect.y))
                self.states[state_str].surface.blit(text_shadow,
                                                    (self.aligned_text_rect.x - 1,
                                                     self.aligned_text_rect.y))

            if text_surface is not None and self.aligned_text_rect is not None:
                self.states[state_str].surface.blit(text_surface, self.aligned_text_rect)

    def redraw_state(self, state_str: str):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param state_str: The ID/name of the state to redraw.

        """

    def clean_up_temp_shapes(self):
        """
        This method is declared for derived classes to implement but has no default implementation.
        """

    def collide_point(self, point: Union[pygame.math.Vector2,
                                         Tuple[int, int],
                                         Tuple[float, float]]):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param point: A point to collide with this shape.

        """

    def set_position(self, point: Union[pygame.math.Vector2,
                                        Tuple[int, int],
                                        Tuple[float, float]]):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param point: A point to set this shapes position to.

        """

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param dimensions: The new dimensions for our shape.

        """
