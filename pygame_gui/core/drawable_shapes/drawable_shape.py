import math

from collections import deque
from typing import Dict, List, Union, Tuple, Optional, Deque

import pygame

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import basic_blit

from pygame_gui.core.text import TextLineChunkFTFont, TextBoxLayout
from pygame_gui.core.text.html_parser import HTMLParser


class DrawableShapeState:
    """
    Represents a single state of a drawable shape.

    :param state_id: The ID/name of this state.

    """

    def __init__(self, state_id: str):
        self.state_id = state_id
        self.surface = pygame.surface.Surface((0, 0), flags=pygame.SRCALPHA, depth=32)
        self.has_fresh_surface = False
        self.cached_background_id = None  # type: Union[str, None]
        self.transition = None  # type: Union[DrawableStateTransition, None]

        self.should_auto_pregen = self.state_id != "disabled"
        self.generated = False

        # created if we have text
        self.text_surface: Optional[pygame.Surface] = None
        self.pre_text_surface: Optional[pygame.Surface] = None

    def get_surface(self) -> pygame.surface.Surface:
        """
        Gets the pygame.surface.Surface of this state. Will be a blend of this state and
        the previous one if we are in a transition.

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

    def __init__(
        self,
        states: Dict[str, DrawableShapeState],
        start_state_id: str,
        target_state_id: str,
        duration: float,
        *,
        progress: float = 0.0,
    ):
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

    def produce_blended_result(self) -> pygame.surface.Surface:
        """
        Produces a blend between the images of our start state and our target state. The
        progression of the blend is dictated by the progress of time through the transition.

        :return: The blended surface.

        """
        result = self.states[self.start_stat_id].surface.copy()
        blended_target = self.states[self.target_state_id].surface.copy()
        start_multiply_surface = pygame.surface.Surface(
            self.states[self.start_stat_id].surface.get_size(),
            flags=pygame.SRCALPHA,
            depth=32,
        )
        target_multiply_surface = start_multiply_surface.copy()

        start_alpha = int(round(255.0 * self.percentage_start_state))
        target_alpha = 255 - start_alpha

        start_multiply_surface.fill(
            pygame.Color(start_alpha, start_alpha, start_alpha, 255)
        )
        target_multiply_surface.fill(
            pygame.Color(target_alpha, target_alpha, target_alpha, 255)
        )

        result.blit(start_multiply_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        blended_target.blit(
            target_multiply_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT
        )
        result.blit(blended_target, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return result


class DrawableShape:
    """
    Base class for a graphical 'shape' that we can use for many different UI elements. The intent
    is to make it easy to switch between UI elements having normal rectangles, circles or rounded
    rectangles as their visual shape while having the same non-shape related functionality.

    :param containing_rect: The rectangle which this shape is entirely contained within (including
                            shadows, borders etc.)
    :param theming_parameters: A dictionary of user supplied data that alters the appearance of
                               the shape.
    :param states: Names for the different states the shape can be in, each may have different
                   sets of colours & images.
    :param manager: The UI manager for this UI.

    """

    def __init__(
        self,
        containing_rect: pygame.Rect,
        theming_parameters: Dict,
        states: List[str],
        manager: IUIManagerInterface,
        *,
        allow_text_outside_width_border=True,
        allow_text_outside_height_border=True,
        text_x_scroll_enabled=False,
        editable_text=False,
    ):
        self.theming = theming_parameters
        self.containing_rect = containing_rect.copy()
        self.dynamic_width = self.containing_rect.width == -1
        self.dynamic_height = self.containing_rect.height == -1
        self.text_view_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.allow_text_outside_width_border = allow_text_outside_width_border
        self.allow_text_outside_height_border = allow_text_outside_height_border
        self.text_x_scroll_enabled = text_x_scroll_enabled
        self.editable_text = editable_text

        self.shadow_width = 0
        self.border_width = 0
        self.shape_corner_radius = [0, 0, 0, 0]
        self.rounded_corner_width_offsets = [0, 0]
        self.rounded_corner_height_offsets = [0, 0]
        if "shadow_width" in self.theming:
            self.shadow_width = self.theming["shadow_width"]
        if "border_width" in self.theming:
            self.border_width = self.theming["border_width"]
        if "shape_corner_radius" in self.theming:
            self.shape_corner_radius = self.theming["shape_corner_radius"]
            tl_offset = round(
                self.shape_corner_radius[0]
                - (math.sin(math.pi / 4) * self.shape_corner_radius[0])
            )
            tr_offset = round(
                self.shape_corner_radius[1]
                - (math.sin(math.pi / 4) * self.shape_corner_radius[1])
            )
            bl_offset = round(
                self.shape_corner_radius[2]
                - (math.sin(math.pi / 4) * self.shape_corner_radius[2])
            )
            br_offset = round(
                self.shape_corner_radius[3]
                - (math.sin(math.pi / 4) * self.shape_corner_radius[3])
            )
            self.rounded_corner_width_offsets = [
                max(tl_offset, bl_offset),
                max(tr_offset, br_offset),
            ]
            self.rounded_corner_height_offsets = [
                max(tl_offset, tr_offset),
                max(bl_offset, br_offset),
            ]

        self.text_box_layout: Optional[TextBoxLayout] = None
        self.build_text_layout()

        self._evaluate_contents_for_containing_rect()
        self.containing_rect.width = max(self.containing_rect.width, 1)
        self.containing_rect.height = max(self.containing_rect.height, 1)

        self.initial_text_layout_size = (
            self.containing_rect.width,
            self.containing_rect.height,
        )

        self.states = {}
        for state in states:
            self.states[state] = DrawableShapeState(state)

        if "normal" in states:
            self.active_state = self.states["normal"]
        else:
            raise NotImplementedError(
                "No 'normal' state id supplied for drawable shape"
            )

        self.previous_state: Optional[DrawableShapeState] = None

        if "transitions" in self.theming:
            self.state_transition_times = self.theming["transitions"]
        else:
            self.state_transition_times = {}

        self.ui_manager = manager
        self.shape_cache = self.ui_manager.get_theme().shape_cache

        self.states_to_redraw_queue: Deque[str] = deque([])
        self.need_to_clean_up = True

        self.should_trigger_full_rebuild = True
        self.time_until_full_rebuild_after_changing_size = 0.35
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

        self.click_area_shape = self.containing_rect.copy()
        self.border_rect = self.containing_rect.copy()
        self.background_rect = self.containing_rect.copy()
        self.base_surface: Optional[pygame.Surface] = None

        self.only_text_changed = False

    def _evaluate_contents_for_containing_rect(self):
        if self.dynamic_width and self.text_box_layout is not None:
            text_width = self.text_box_layout.layout_rect.width

            horiz_padding = 0
            if (
                "text_horiz_alignment" in self.theming
                and self.theming["text_horiz_alignment"] in ["left", "right"]
                and "text_horiz_alignment_padding" in self.theming
            ):
                horiz_padding = self.theming["text_horiz_alignment_padding"]
            # As well as the text width we want to throw in the borders,
            # shadows and any text padding
            final_width = (
                text_width
                + (2 * self.shadow_width)
                + (2 * self.border_width)
                + self.rounded_corner_width_offsets[0]
                + self.rounded_corner_width_offsets[1]
                + horiz_padding
            )

            self.text_view_rect.width = text_width
            self.text_box_layout.view_rect.width = self.text_view_rect.width
            self.containing_rect.width = final_width
        if self.dynamic_height and self.text_box_layout is not None:
            text_height = self.text_box_layout.layout_rect.height

            vert_padding = 0
            if (
                "text_horiz_alignment" in self.theming
                and self.theming["text_horiz_alignment"] in ["top", "bottom"]
                and "text_vert_alignment_padding" in self.theming
            ):
                vert_padding = self.theming["text_vert_alignment_padding"]
            # As well as the text height we want to throw in the borders,
            # shadows and any text padding
            final_height = (
                text_height
                + (2 * self.shadow_width)
                + (2 * self.border_width)
                + self.rounded_corner_height_offsets[0]
                + self.rounded_corner_height_offsets[1]
                + vert_padding
            )
            self.text_view_rect.height = text_height
            self.text_box_layout.view_rect.height = self.text_view_rect.height
            self.containing_rect.height = final_height

    def set_active_state(self, state_id: str):
        """
        Changes the currently active state for the drawable shape and, if setup in the theme,
        creates a transition blend from the previous state to the newly active one.

        :param state_id: the ID of the new state to make active.

        """

        # make sure this state is generated before we set it.
        # should ensure that some more rarely used states are only generated if we use them
        if not self.states[state_id].generated:
            if state_id in self.states_to_redraw_queue:
                self.states_to_redraw_queue.remove(state_id)
            self.redraw_state(state_id)

        if state_id in self.states and self.active_state.state_id != state_id:
            self.previous_state = self.active_state
            self.active_state = self.states[state_id]
            self.active_state.has_fresh_surface = True

            if self.previous_state is not None and (
                (self.previous_state.state_id, self.active_state.state_id)
                in self.state_transition_times
            ):
                prev_id = self.previous_state.state_id
                next_id = self.active_state.state_id
                duration = self.state_transition_times[
                    (self.previous_state.state_id, self.active_state.state_id)
                ]
                if self.previous_state.transition is None:
                    # completely fresh transition
                    self.active_state.transition = DrawableStateTransition(
                        self.states, prev_id, next_id, duration
                    )
                elif (
                    self.previous_state.transition.start_stat_id
                    == self.active_state.state_id
                ):
                    progress_time = self.previous_state.transition.remaining_time
                    transition = DrawableStateTransition(
                        self.states, prev_id, next_id, duration, progress=progress_time
                    )
                    self.active_state.transition = transition

    def update(self, time_delta: float):
        """
        Updates the drawable shape to process rebuilds and update blends between states.

        :param time_delta: amount of time passed between now and the previous frame in seconds.

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
        shape_params_changed = False
        if (
            "shadow_width" in self.theming
            and self.shadow_width != self.theming["shadow_width"]
        ):
            self.shadow_width = self.theming["shadow_width"]
            shape_params_changed = True
        if (
            "border_width" in self.theming
            and self.border_width != self.theming["border_width"]
        ):
            self.border_width = self.theming["border_width"]
            shape_params_changed = True
        if (
            "shape_corner_radius" in self.theming
            and self.shape_corner_radius != self.theming["shape_corner_radius"]
        ):
            shape_params_changed = self._set_corner_params()
        if (
            shape_params_changed
            or self.initial_text_layout_size != self.containing_rect.size
        ):
            self.build_text_layout()
        self.should_trigger_full_rebuild = False
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def _set_corner_params(self):
        self.shape_corner_radius = self.theming["shape_corner_radius"]
        tl_offset = round(
            self.shape_corner_radius[0]
            - (math.sin(math.pi / 4) * self.shape_corner_radius[0])
        )
        tr_offset = round(
            self.shape_corner_radius[1]
            - (math.sin(math.pi / 4) * self.shape_corner_radius[1])
        )
        bl_offset = round(
            self.shape_corner_radius[2]
            - (math.sin(math.pi / 4) * self.shape_corner_radius[2])
        )
        br_offset = round(
            self.shape_corner_radius[3]
            - (math.sin(math.pi / 4) * self.shape_corner_radius[3])
        )
        self.rounded_corner_width_offsets = [
            max(tl_offset, bl_offset),
            max(tr_offset, br_offset),
        ]
        self.rounded_corner_height_offsets = [
            max(tl_offset, tr_offset),
            max(bl_offset, br_offset),
        ]
        return True

    def redraw_all_states(self, force_full_redraw: bool = False):
        """
        Starts the redrawing process for all states of this shape that auto pre-generate.
        Redrawing is done one state at a time so will take a few loops of the game to
        complete if this shape has many states.
        """
        self.states_to_redraw_queue = deque(
            [
                state_id
                for state_id, state in self.states.items()
                if (state.should_auto_pregen or force_full_redraw)
            ]
        )
        initial_state = self.states_to_redraw_queue.popleft()
        self.redraw_state(initial_state)

    def align_all_text_rows(self):
        """
        Aligns the text drawing position correctly according to our theming options.

        """
        if self.text_box_layout is None:
            return
        # Horizontal alignment
        if "text_horiz_alignment" in self.theming:
            if self.theming["text_horiz_alignment"] == "center" or self.theming[
                "text_horiz_alignment"
            ] not in ["left", "right"]:
                method = "rect"
                if "text_horiz_alignment_method" in self.theming:
                    method = self.theming["text_horiz_alignment_method"]
                self.text_box_layout.horiz_center_all_rows(method)
            elif self.theming["text_horiz_alignment"] == "left":
                self.text_box_layout.align_left_all_rows(0)
            else:
                self.text_box_layout.align_right_all_rows(0)
        else:
            self.text_box_layout.horiz_center_all_rows("rect")

        # Vertical alignment
        if "text_vert_alignment" in self.theming:
            if self.theming["text_vert_alignment"] == "center" or self.theming[
                "text_vert_alignment"
            ] not in ["top", "bottom"]:
                self.text_box_layout.vert_center_all_rows()
            elif self.theming["text_vert_alignment"] == "top":
                self.text_box_layout.vert_align_top_all_rows(0)
            else:
                self.text_box_layout.vert_align_bottom_all_rows(0)
        else:
            self.text_box_layout.vert_center_all_rows()

    def get_active_state_surface(self) -> pygame.surface.Surface:
        """
        Get the main surface from the active state.

        :return: The surface asked for, or the best available substitute.

        """
        if self.active_state is not None:
            return self.active_state.get_surface()
        else:
            return self.ui_manager.get_universal_empty_surface()

    def get_surface(self, state_name: str) -> pygame.surface.Surface:
        """
        Get the main surface from a specific state.

        :param state_name: The state we are trying to get the surface from.

        :return: The surface asked for, or the best available substitute.

        """
        if state_name in self.states and self.states[state_name].surface is not None:
            return self.states[state_name].surface
        elif state_name in self.states and self.states["normal"].surface is not None:
            return self.states["normal"].surface
        else:
            return pygame.surface.Surface((0, 0), flags=pygame.SRCALPHA, depth=32)

    def get_fresh_surface(self) -> pygame.surface.Surface:
        """
        Gets the surface of the active state and resets the state's 'has_fresh_surface' variable.

        :return: The active state's main pygame.surface.Surface.

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

    def finalise_images_and_text(
        self,
        image_state_str: str,
        state_str: str,
        text_colour_state_str: str,
        text_shadow_colour_state_str: str,
        add_text: bool,
    ):
        """
        Rebuilds any text or image used by a specific state in the drawable shape. Effectively
        this means adding them on top of whatever is already in the state's surface. As such it
        should generally be called last in the process of building up a finished drawable shape
        state.

        :param add_text:
        :param image_state_str: image ID of the state we are going to be adding images and text to.
        :param state_str: normal ID of the state we are going to be adding images and text to.
        :param text_colour_state_str: text colour ID of the state we are going to be adding
                                      images and text to.
        :param text_shadow_colour_state_str: text shadow colour ID of the state we are going to
                                             be adding images and text to.

        """
        # Handle images - always look for list-based image parameters
        images_key = image_state_str
        if images_key in self.theming:
            images = self.theming[images_key]
            if images:  # Only process if there are actually images
                state_surface = self.states[state_str].surface

                # Get corresponding position data
                positions_key = images_key.replace("_images", "_image_positions")
                positions = self.theming.get(positions_key, [])

                # Draw each image in layer order (they should already be sorted by layer)
                for i, image in enumerate(images):
                    if image is not None:
                        # Get position for this image (default to center if not specified)
                        if i < len(positions):
                            pos_x, pos_y = positions[i]
                        else:
                            pos_x, pos_y = 0.5, 0.5  # Default to center

                        # Calculate actual pixel position
                        surface_rect = state_surface.get_rect()
                        image_rect = image.get_rect()

                        # Position represents where to place the image based on relative coordinates
                        # (1.0, 1.0) should place the bottom-right corner of the image at the
                        # bottom-right of the element
                        target_x = surface_rect.width * pos_x - image_rect.width * pos_x
                        target_y = (
                            surface_rect.height * pos_y - image_rect.height * pos_y
                        )

                        # Set the image position
                        image_rect.x = int(target_x)
                        image_rect.y = int(target_y)

                        state_surface.blit(image, image_rect)

        # Handle text
        if add_text:
            self.finalise_text(
                state_str, text_colour_state_str, text_shadow_colour_state_str
            )

    def build_text_layout(self):
        """
        Build a text box layout for this drawable shape if it has some text.
        """
        containing_rect_when_text_built = self.containing_rect.copy()
        # Draw any text
        if (
            "text" in self.theming
            and "font" in self.theming
            and self.theming["text"] is not None
        ):
            # we need two rectangles for the text. One has actual area the
            # text surface takes up, which may be larger than the displayed area,
            # and its position on the final surface. The other is the amount of
            # area of the text surface which we blit from, which may be much smaller
            # than the total text area.

            horiz_padding = 0
            if "text_horiz_alignment" in self.theming and (
                self.theming["text_horiz_alignment"] in ["left", "right"]
                and "text_horiz_alignment_padding" in self.theming
            ):
                horiz_padding = self.theming["text_horiz_alignment_padding"]

            vert_padding = 0
            if (
                "text_vert_alignment" in self.theming
                and self.theming["text_vert_alignment"] in ["top", "bottom"]
                and "text_vert_alignment_padding" in self.theming
            ):
                vert_padding = self.theming["text_vert_alignment_padding"]
            total_text_buffer = (
                (self.shadow_width * 2)
                + (self.border_width * 2)
                + self.rounded_corner_width_offsets[0]
                + self.rounded_corner_width_offsets[1]
            )
            self.text_view_rect = self.containing_rect.copy()
            self.text_view_rect.x = 0
            self.text_view_rect.y = 0
            if self.dynamic_width:
                self.text_view_rect.width = -1
            else:
                self.text_view_rect.width = max(
                    0, self.text_view_rect.width - (total_text_buffer + horiz_padding)
                )

            if self.dynamic_height:
                self.text_view_rect.height = -1
            else:
                self.text_view_rect.height = max(
                    0, self.text_view_rect.height - (total_text_buffer + vert_padding)
                )

            text_actual_area_rect = self.text_view_rect.copy()
            text_actual_area_rect.x = (
                self.shadow_width
                + self.border_width
                + self.rounded_corner_width_offsets[0]
            )
            if "text_horiz_alignment" in self.theming and self.theming[
                "text_horiz_alignment"
            ] in ["left"]:
                text_actual_area_rect.x += horiz_padding
            text_actual_area_rect.y = (
                self.shadow_width
                + self.border_width
                + self.rounded_corner_height_offsets[0]
            )
            if "text_vert_alignment" in self.theming and self.theming[
                "text_vert_alignment"
            ] in ["top"]:
                text_actual_area_rect.y += vert_padding

            text_shadow_data = (0, 0, 0, pygame.Color("#10101070"), False)
            if "text_shadow" in self.theming:
                text_shadow_data = self.theming["text_shadow"]

            # gather any override parameters for text_width and text_height now
            # as we need to feed them into max_dimensions
            max_dimensions = [self.containing_rect.width, self.containing_rect.height]
            if "max_text_width" in self.theming:
                max_dimensions[0] = self.theming["max_text_width"]
            if "max_text_height" in self.theming:
                max_dimensions[1] = self.theming["max_text_height"]
            text_chunk = TextLineChunkFTFont(
                self.theming["text"],
                self.theming["font"],
                underlined=False,
                colour=pygame.Color("#FFFFFFFF"),
                using_default_text_colour=True,
                bg_colour=pygame.Color("#00000000"),
                text_shadow_data=text_shadow_data,
                max_dimensions=max_dimensions,
            )

            # if our text chunk doesn't fit in the space inside the shadow, border and padding
            # expand available text space to the whole button area - this is helpful for very small
            # and oddly shaped buttons
            if (
                self.allow_text_outside_height_border
                and not self.dynamic_height
                and text_chunk.height > text_actual_area_rect.height
            ):
                text_actual_area_rect.height = self.containing_rect.height
                # if we are centred clear out the padding entirely,
                # if top aligned add just the padding (might help give
                # a bit of manual control in some odd cases)
                text_actual_area_rect.y = 0
                if "text_vert_alignment" in self.theming and self.theming[
                    "text_vert_alignment"
                ] in ["top"]:
                    text_actual_area_rect.y = vert_padding
                self.text_view_rect.height = self.containing_rect.height
            if (
                self.allow_text_outside_width_border
                and not self.dynamic_width
                and text_chunk.width > text_actual_area_rect.width
            ):
                text_actual_area_rect.width = self.containing_rect.width
                text_actual_area_rect.x = 0
                if "text_horiz_alignment" in self.theming and self.theming[
                    "text_horiz_alignment"
                ] in ["left"]:
                    text_actual_area_rect.x = horiz_padding
                self.text_view_rect.width = self.containing_rect.width

            # still allow overriding of text area with theming parameters
            if "text_width" in self.theming:
                text_actual_area_rect.width = self.theming["text_width"]
            if "text_height" in self.theming:
                text_actual_area_rect.height = self.theming["text_height"]

            min_text_width = 0
            if "min_text_width" in self.theming:
                min_text_width = self.theming["min_text_width"]

            horiz_alignment = "left"
            if "text_horiz_alignment" in self.theming:
                horiz_alignment = self.theming["text_horiz_alignment"]

            horiz_alignment_method = "rect"
            if "text_horiz_alignment_method" in self.theming:
                horiz_alignment_method = self.theming["text_horiz_alignment_method"]

            text_chunk.should_centre_from_baseline = True
            default_font_data = {
                "font": self.theming["font"],
                "font_colour": (
                    self.theming["normal_text"]
                    if "normal_text" in self.theming
                    else self.ui_manager.get_theme().get_colour("normal_text", None)
                ),
                "bg_colour": pygame.Color("#00000000"),
            }
            self.text_box_layout = TextBoxLayout(
                deque([text_chunk]),
                text_actual_area_rect,
                self.text_view_rect,
                line_spacing=1.25,
                default_font_data=default_font_data,
                text_x_scroll_enabled=self.text_x_scroll_enabled,
                editable=self.editable_text,
                min_layout_rect_width=min_text_width,
                horiz_alignment=horiz_alignment,
                horiz_alignment_method=horiz_alignment_method,
            )
            if "selected_bg" in self.theming:
                self.text_box_layout.selection_colour = self.theming["selected_bg"]
            if "selected_text" in self.theming:
                self.text_box_layout.selection_text_colour = self.theming[
                    "selected_text"
                ]
            if "text_cursor_colour" in self.theming:
                self.text_box_layout.set_cursor_colour(
                    self.theming["text_cursor_colour"]
                )
            self.align_all_text_rows()
        return containing_rect_when_text_built

    def finalise_text(
        self,
        state_str,
        text_colour_state_str: str = "",
        text_shadow_colour_state_str: str = "",
        only_text_changed: bool = False,
    ):
        """
        Finalise the text to a surface with some last-minute data that doesn't require the text
        be re-laid out.

        :param only_text_changed:
        :param state_str: The name of the shape's state we are finalising.
        :param text_colour_state_str: The string identifying the text colour to use.
        :param text_shadow_colour_state_str: The string identifying the text shadow
                                             colour to use.
        """
        if self.text_box_layout is not None:
            # copy the pre-text surface & create a new empty text surface for this state
            self.states[state_str].pre_text_surface = self.states[
                state_str
            ].surface.copy()
            self.states[state_str].text_surface = pygame.surface.Surface(
                self.states[state_str].surface.get_size(),
                flags=pygame.SRCALPHA,
                depth=32,
            )
            text_surface = self.states[state_str].text_surface
            if text_surface is not None:
                text_surface.fill("#00000000")

                if only_text_changed:
                    self.text_box_layout.blit_finalised_text_to_surf(text_surface)
                else:
                    self.text_box_layout.set_default_text_colour(
                        self.theming[text_colour_state_str]
                    )
                    self.text_box_layout.set_default_text_shadow_colour(
                        self.theming[text_shadow_colour_state_str]
                    )
                    self.text_box_layout.finalise_to_surf(text_surface)

                basic_blit(
                    self.states[state_str].surface,
                    text_surface,
                    (0, 0),
                )

    def apply_active_text_changes(self):
        """
        Updates the shape surface with any changes to the text surface. Useful when we've made
        small edits to the text surface.

        This may be bugged.

        """
        if self.text_box_layout is not None:
            for _, state in self.states.items():
                if (
                    state.pre_text_surface is not None
                    and state.text_surface is not None
                ):
                    state.surface = state.pre_text_surface.copy()
                    basic_blit(state.surface, state.text_surface, (0, 0))

    def set_text(self, text: str):
        """
        Set the visible text that the drawable shape has on it. This call will build a text
        layout and then redraw the final shape with the new, laid out text on top.

        :param text: the new string of text to stick on the shape.
        """
        self.theming["text"] = text
        self.build_text_layout()
        if "disabled" in self.states:
            self.redraw_all_states(force_full_redraw=True)
        else:
            self.redraw_all_states()

    def set_text_alpha(self, alpha: int):
        """
        Set the alpha of just the text and redraw the shape with the new text on top.

        :param alpha: the alpha to set.
        """
        if self.text_box_layout is not None:
            self.text_box_layout.set_alpha(alpha)
            self.redraw_state(self.active_state.state_id, add_text=False)
            self.finalise_text(
                self.active_state.state_id,
                f"{self.active_state.state_id}_text",
                f"{self.active_state.state_id}_text_shadow",
                only_text_changed=False,
            )

    def redraw_active_state_no_text(self):
        """
        Redraw the currently active state with no text.
        """
        self.redraw_state(self.active_state.state_id, add_text=False)

    def finalise_text_onto_active_state(self):
        """
        Lets us draw the active state with no text and then paste the finalised surface from the
        text layout on top. Handy if we are doing some text effects in the text layout we don't want
        to lose by recreating the text from scratch.
        """
        self.redraw_state(self.active_state.state_id, add_text=False)
        self.finalise_text(
            self.active_state.state_id,
            f"{self.active_state.state_id}_text",
            f"{self.active_state.state_id}_text_shadow",
            only_text_changed=False,
        )

    def insert_text(
        self, text: str, layout_index: int, parser: Optional[HTMLParser] = None
    ):
        """
        Update the theming when we insert text, then pass down to the layout to do the actual
        inserting.
        :param text: the text to insert
        :param layout_index: where to insert it
        :param parser: an optional parser
        :return:
        """
        self.theming["text"] = (
            self.theming["text"][:layout_index]
            + text
            + self.theming["text"][layout_index:]
        )
        if self.text_box_layout is not None:
            self.text_box_layout.insert_text(text, layout_index, parser)

    def toggle_text_cursor(self):
        """
        Toggle the edit text cursor/carat between visible and invisible. Usually this is run to
        make the cursor appear to flash, so it catches user attention.
        """
        if self.text_box_layout is not None:
            self.text_box_layout.toggle_cursor()
            self.finalise_text_onto_active_state()
            self.active_state.has_fresh_surface = True

    def redraw_state(self, state_str: str, add_text: bool = True):
        """
        This method is declared for derived classes to implement but has no default
        implementation.

        :param add_text:
        :param state_str: The ID/name of the state to redraw.

        """

    def clean_up_temp_shapes(self):
        """
        This method is declared for derived classes to implement but has no default implementation.
        """

    def collide_point(
        self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]
    ):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param point: A point to collide with this shape.

        """

    def set_position(
        self, point: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]
    ):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param point: A point to set this shapes position to.

        """

    def set_dimensions(
        self,
        dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]],
    ):
        """
        This method is declared for derived classes to implement but has no default implementation.

        :param dimensions: The new dimensions for our shape.

        """
