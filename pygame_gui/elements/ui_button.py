from typing import Union, Tuple, Dict, Iterable, Callable, Optional, Any
from inspect import signature

import pygame

from pygame_gui.core.utility import translate
from pygame_gui._constants import UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED, OldType
from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, UI_BUTTON_START_PRESS
from pygame_gui.core import ObjectID
from pygame_gui.core.drawable_shapes import EllipseDrawableShape, RoundedRectangleShape
from pygame_gui.core.drawable_shapes import RectDrawableShape
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement


class UIButton(UIElement):
    """
    A push button, a lot of the appearance of the button, including images to be displayed, is
    setup via the theme file. This button is designed to be pressed, do something, and then reset -
    rather than to be toggled on or off.

    The button element is reused throughout the UI as part of other elements as it happens to be a
    very flexible interactive element.

    :param relative_rect: Normally a rectangle describing the position (relative to its container) and
                          dimensions. Also accepts a position Tuple, or Vector2 where the dimensions
                          will be dynamic depending on the button's contents. Dynamic dimensions can
                          be requested by setting the required dimension to -1.
    :param text: Text for the button.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param tool_tip_text: Optional tool tip text, can be formatted with HTML. If supplied will
                          appear on hover.
    :param starting_height: The height in layers above it's container that this element will be
                            placed.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param allow_double_clicks: Enables double clicking on buttons which will generate a
                                unique event.
    :param visible: Whether the element is visible by default. Warning - container visibility may
                    override this.
    :param command: Functions to be called when an event is triggered by this element.
    :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                        useful when you have multiple translations that need variables inserted
                        in the middle.
    """

    def __init__(self, relative_rect: Union[pygame.Rect, Tuple[float, float], pygame.Vector2],
                 text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 tool_tip_text: Union[str, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, Union[str, UIElement]] = None,
                 allow_double_clicks: bool = False,
                 generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
                 visible: int = 1,
                 *,
                 command: Union[Callable, Dict[int, Callable]] = None,
                 tool_tip_object_id: Optional[ObjectID] = None,
                 text_kwargs: Optional[Dict[str, str]] = None,
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None,
                 max_dynamic_width: Optional[int] = None
                 ):

        rel_rect = (relative_rect if isinstance(relative_rect, pygame.Rect)
                    else pygame.Rect(relative_rect, (-1, -1)))
        super().__init__(rel_rect,
                         manager, container,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['button'])

        self.text = text
        self.text_kwargs = {}
        if text_kwargs is not None:
            self.text_kwargs = text_kwargs

        self.dynamic_dimensions_orig_top_left = rel_rect.topleft
        # support for an optional 'tool tip' element attached to this button
        self.set_tooltip(tool_tip_text, tool_tip_object_id, tool_tip_text_kwargs)
        self.ui_root_container = self.ui_manager.get_root_container()

        # Some different states our button can be in, could use a state machine for this
        # if we wanted.
        self.held = False
        self.pressed = False
        self.is_selected = False
        # Used to check button pressed without going through pygame.Event system
        self.pressed_event = False

        # timer for double clicks
        self.last_click_button = None
        self.allow_double_clicks = allow_double_clicks
        self.double_click_timer = self.ui_manager.get_double_click_time() + 1.0

        self.generate_click_events_from = generate_click_events_from

        self.text_surface = None
        self.aligned_text_rect = None

        self._set_image(None)

        # default range at which we 'let go' of a button
        self.hold_range = (0, 0)

        # initialise theme parameters
        self.colours = {}

        self.font = None

        self.normal_image = None
        self.hovered_image = None
        self.selected_image = None
        self.disabled_image = None

        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 0
        self.text_vert_alignment_padding = 0
        self.text_horiz_alignment_method = 'rect'
        self.shape = 'rectangle'
        self.text_shadow_size = 0
        self.text_shadow_offset = (0, 0)
        self.max_dynamic_width = max_dynamic_width

        self.state_transitions = {}
        
        self._handler = {}
        if command is not None:
            if callable(command):
                self.bind(UI_BUTTON_PRESSED, command)
            else:
                for key, value in command.items():
                    self.bind(key, value)
                        
        if UI_BUTTON_DOUBLE_CLICKED in self._handler:
            self.allow_double_clicks = True

        self.rebuild_from_changed_theme_data()

    def _set_any_images_from_theme(self) -> bool:
        """
        Grabs images for this button from the UI theme if any are set.

        :return: True if any of the images have changed since last time they were set.

        """

        changed = False
        normal_image = None
        try:
            normal_image = self.ui_theme.get_image('normal_image', self.combined_element_ids)
        except LookupError:
            normal_image = None
        finally:
            if normal_image != self.normal_image:
                self.normal_image = normal_image
                self.hovered_image = normal_image
                self.selected_image = normal_image
                self.disabled_image = normal_image
                changed = True

        hovered_image = None
        try:
            hovered_image = self.ui_theme.get_image('hovered_image', self.combined_element_ids)
        except LookupError:
            hovered_image = self.normal_image
        finally:
            if hovered_image != self.hovered_image:
                self.hovered_image = hovered_image
                changed = True

        selected_image = None
        try:
            selected_image = self.ui_theme.get_image('selected_image', self.combined_element_ids)
        except LookupError:
            selected_image = self.normal_image
        finally:
            if selected_image != self.selected_image:
                self.selected_image = selected_image
                changed = True

        disabled_image = None
        try:
            disabled_image = self.ui_theme.get_image('disabled_image', self.combined_element_ids)
        except LookupError:
            disabled_image = self.normal_image
        finally:
            if disabled_image != self.disabled_image:
                self.disabled_image = disabled_image
                changed = True

        return changed

    def kill(self):
        """
        Overrides the standard sprite kill method to also kill any tooltips belonging to
        this button.
        """
        super().kill()

    def hover_point(self, hover_x: int, hover_y: int) -> bool:
        """
        Tests if a position should be considered 'hovering' the button. Normally this just means
        our mouse pointer is inside the buttons rectangle, however if we are holding onto the
        button for a purpose(e.g. dragging a window around by it's menu bar) the hover radius can
        be made to grow so we don't keep losing touch with whatever we are moving.

        :param hover_x: horizontal pixel coordinate to test.
        :param hover_y: vertical pixel coordinate to test

        :return: Returns True if we are hovering.

        """
        if self.held:
            return self.in_hold_range((hover_x, hover_y))
        else:
            return super().hover_point(hover_x, hover_y)

    def can_hover(self) -> bool:
        """
        Tests whether we can trigger the hover state for this button, other states take
        priority over it.

        :return: True if we are able to hover this button.

        """
        return not self.is_selected and self.is_enabled and not self.held

    def on_hovered(self):
        """
        Called when we enter the hover state, it sets the colours and image of the button
        to the appropriate values and redraws it.
        """
        super().on_hovered()
        self.drawable_shape.set_active_state('hovered')

        # old event to remove in 0.8.0
        event_data = {'user_type': OldType(UI_BUTTON_ON_HOVERED),
                      'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
        # new event
        event_data = {'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(UI_BUTTON_ON_HOVERED, event_data))

    def on_unhovered(self):
        """
        Called when we leave the hover state. Resets the colours and images to normal and kills any
        tooltip that was created while we were hovering the button.
        """
        super().on_unhovered()
        if self.drawable_shape is not None:
            self.drawable_shape.set_active_state(self._get_appropriate_state_name())

        # old event to remove in 0.8.0
        event_data = {'user_type': OldType(UI_BUTTON_ON_UNHOVERED),
                      'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

        # new event
        event_data = {'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(UI_BUTTON_ON_UNHOVERED, event_data))

    def _get_appropriate_state_name(self):
        """
        Returns a string representing the appropriate state for the widgets DrawableShapes.
        Currently only returns either 'normal' or 'disabled' based on is_enabled.
        """

        if self.is_enabled:
            if self.is_selected:
                return "selected"
            elif self.hovered:
                return "hovered"
            else:
                return "normal"
        return "disabled"

    def update(self, time_delta: float):
        """
        Sets the pressed state for an update cycle if we've pressed this button recently.

        :param time_delta: the time in seconds between one call to update and the next.

        """
        super().update(time_delta)
        if self.alive():
            # clear pressed state, we only want it to last one update cycle
            self.pressed = False

            if self.pressed_event:
                # if a pressed event has occurred set the button to the pressed state for one cycle.
                self.pressed_event = False
                self.pressed = True

            if (self.allow_double_clicks and
                    self.double_click_timer < self.ui_manager.get_double_click_time()):
                self.double_click_timer += time_delta

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles various interactions with the button.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in self.generate_click_events_from:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                if self.is_enabled:
                    if (self.allow_double_clicks and self.last_click_button == event.button and
                            self.double_click_timer <= self.ui_manager.get_double_click_time()):
                        self.on_self_event(UI_BUTTON_DOUBLE_CLICKED, {'mouse_button':event.button})
                    else:
                        self.on_self_event(UI_BUTTON_START_PRESS, {'mouse_button':event.button})
                        self.double_click_timer = 0.0
                        self.last_click_button = event.button
                        self.held = True
                        self.hovered = False
                        self.on_unhovered()
                        self._set_active()

                consumed_event = True
        if event.type == pygame.MOUSEBUTTONUP and event.button in self.generate_click_events_from:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if (self.is_enabled and
                    self.drawable_shape.collide_point(scaled_mouse_pos) and
                    self.held):
                self.held = False
                self._set_inactive()
                consumed_event = True
                self.pressed_event = True
                self.on_self_event(UI_BUTTON_PRESSED, {'mouse_button':event.button})

            if self.is_enabled and self.held:
                self.held = False
                self._set_inactive()
                consumed_event = True

        return consumed_event
    
    def bind(self, event:int, function:Callable = None):
        """
        Bind a function to an element event.

        :param event: The event to bind.

        :param function: The function to bind. None to unbind.

        """
        if function is None:
            self._handler.pop(event, None)
            return

        if callable(function):
            num_params = len(signature(function).parameters)
            if num_params == 1:
                self._handler[event] = function
            elif num_params == 0:
                self._handler[event] = lambda _:function()
            else:
                raise ValueError("Command function signatures can have 0 or 1 parameter. "
                                 "If one parameter is set it will contain data for the id of the mouse button used "
                                 "to trigger this click event.")
        else:
            raise TypeError("Command function must be callable")
    
    def on_self_event(self, event:int, data:Dict[str, Any]=None):
        """
        Called when an event is triggered by this element. Handles these events either by posting the event back
        to the event queue, or by running a function supplied by the user.

        :param event: The event triggered.

        :param data: event data

        """
        if data is None:
            data = {}
            
        if event in self._handler:
            self._handler[event](data)
        else:
            # old event to remove in 0.8.0
            event_data = {'user_type': OldType(event),
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

            # new event
            event_data = data
            event_data.update({'ui_element': self,
                               'ui_object_id': self.most_specific_combined_id})
            pygame.event.post(pygame.event.Event(event, event_data))

    def check_pressed(self) -> bool:
        """
        A direct way to check if this button has been pressed in the last update cycle.

        :return: True if the button has been pressed.

        """
        return self.pressed

    def disable(self):
        """
        Disables the button so that it is no longer interactive.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state('disabled')

            # clear other button state
            self.held = False
            self.pressed = False
            self.is_selected = False
            self.pressed_event = False

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state('normal')

    def _set_active(self):
        """
        Called when we are actively clicking on the button. Changes the colours to the appropriate
        ones for the new state then redraws the button.
        """
        self.drawable_shape.set_active_state('active')

    def _set_inactive(self):
        """
        Called when we stop actively clicking on the button. Restores the colours to the default
        state then redraws the button.
        """
        self.drawable_shape.set_active_state('normal')

    def select(self):
        """
        Called when we select focus this element. Changes the colours and image to the appropriate
        ones for the new state then redraws the button.
        """
        self.is_selected = True
        self.drawable_shape.set_active_state('selected')

    def unselect(self):
        """
        Called when we are no longer select focusing this element. Restores the colours and image
        to the default state then redraws the button.
        """
        self.is_selected = False
        self.drawable_shape.set_active_state('normal')

    def set_text(self, text: str, *, text_kwargs: Optional[Dict[str, str]] = None):
        """
        Sets the text on the button. The button will rebuild.

        :param text: The new text to set.
        :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                        useful when you have multiple translations that need variables inserted
                        in the middle.

        """
        any_changed = False
        if text != self.text:
            self.text = text
            any_changed = True

        if text_kwargs is not None:
            if text_kwargs != self.text_kwargs:
                self.text_kwargs = text_kwargs
                any_changed = True
        elif self.text_kwargs != {}:
            self.text_kwargs = {}
            any_changed = True

        if any_changed:
            if self.dynamic_width or self.dynamic_height:
                self.rebuild()
            else:
                self.drawable_shape.set_text(translate(self.text, **self.text_kwargs))

    def set_hold_range(self, xy_range: Tuple[int, int]):
        """
        Set x and y values, in pixels, around our button to use as the hold range for time when we
        want to drag a button about but don't want it to slip out of our grasp too easily.

        Imagine it as a large rectangle around our button, larger in all directions by whatever
        values we specify here.

        :param xy_range: The x and y values used to create our larger 'holding' rectangle.

        """
        self.hold_range = xy_range

    def in_hold_range(self, position: Union[pygame.math.Vector2,
                                            Tuple[int, int],
                                            Tuple[float, float]]) -> bool:
        """
        Imagines a potentially larger rectangle around our button in which range we still grip
        hold of our button when moving the mouse. Makes it easier to use scrollbars.

        :param position: The position we are testing.

        :return bool: Returns True if our position is inside the hold range.

        """
        if self.drawable_shape.collide_point(position):
            return True
        elif self.hold_range[0] > 0 or self.hold_range[1] > 0:
            hold_rect = pygame.Rect((self.rect.x - self.hold_range[0],
                                     self.rect.y - self.hold_range[1]),
                                    (self.rect.width + (2 * self.hold_range[0]),
                                     self.rect.height + (2 * self.hold_range[1])))
            return bool(hold_rect.collidepoint(int(position[0]), int(position[1])))
        else:
            return False

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the
        button's drawable shape
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        cols = {'normal_bg':
                self.ui_theme.get_colour_or_gradient('normal_bg', self.combined_element_ids),
                'hovered_bg':
                self.ui_theme.get_colour_or_gradient('hovered_bg', self.combined_element_ids),
                'disabled_bg':
                self.ui_theme.get_colour_or_gradient('disabled_bg', self.combined_element_ids),
                'selected_bg':
                self.ui_theme.get_colour_or_gradient('selected_bg', self.combined_element_ids),
                'active_bg':
                self.ui_theme.get_colour_or_gradient('active_bg', self.combined_element_ids),
                'normal_text':
                self.ui_theme.get_colour_or_gradient('normal_text', self.combined_element_ids),
                'hovered_text':
                self.ui_theme.get_colour_or_gradient('hovered_text', self.combined_element_ids),
                'disabled_text':
                self.ui_theme.get_colour_or_gradient('disabled_text', self.combined_element_ids),
                'selected_text':
                self.ui_theme.get_colour_or_gradient('selected_text', self.combined_element_ids),
                'active_text':
                self.ui_theme.get_colour_or_gradient('active_text', self.combined_element_ids),
                'normal_text_shadow':
                self.ui_theme.get_colour_or_gradient('normal_text_shadow',
                                                     self.combined_element_ids),
                'hovered_text_shadow':
                self.ui_theme.get_colour_or_gradient('hovered_text_shadow',
                                                     self.combined_element_ids),
                'disabled_text_shadow':
                self.ui_theme.get_colour_or_gradient('disabled_text_shadow',
                                                     self.combined_element_ids),
                'selected_text_shadow':
                self.ui_theme.get_colour_or_gradient('selected_text_shadow',
                                                     self.combined_element_ids),
                'active_text_shadow':
                self.ui_theme.get_colour_or_gradient('active_text_shadow',
                                                     self.combined_element_ids),
                'normal_border':
                self.ui_theme.get_colour_or_gradient('normal_border',
                                                     self.combined_element_ids),
                'hovered_border':
                self.ui_theme.get_colour_or_gradient('hovered_border',
                                                     self.combined_element_ids),
                'disabled_border':
                self.ui_theme.get_colour_or_gradient('disabled_border',
                                                     self.combined_element_ids),
                'selected_border':
                self.ui_theme.get_colour_or_gradient('selected_border',
                                                     self.combined_element_ids),
                'active_border':
                self.ui_theme.get_colour_or_gradient('active_border',
                                                     self.combined_element_ids)}

        if cols != self.colours:
            self.colours = cols
            has_any_changed = True

        if self._set_any_images_from_theme():
            has_any_changed = True

        # misc
        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle',
                                                               'ellipse']):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': [2, 2, 2, 2]}):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='tool_tip_delay',
                                               default_value=1.0,
                                               casting_func=float):
            has_any_changed = True

        if self._check_text_alignment_theming():
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_size',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_offset',
                                               default_value=(0, 0),
                                               casting_func=self.tuple_extract):
            has_any_changed = True

        try:
            state_transitions = self.ui_theme.get_misc_data('state_transitions',
                                                            self.combined_element_ids)
        except LookupError:
            self.state_transitions = {}
        else:
            if isinstance(state_transitions, dict):
                for key in state_transitions:
                    states = key.split('_')
                    if len(states) == 2:
                        start_state = states[0]
                        target_state = states[1]
                        try:
                            duration = float(state_transitions[key])
                        except ValueError:
                            duration = 0.0
                        self.state_transitions[(start_state, target_state)] = duration

        if has_any_changed:
            self.rebuild()

    def _check_text_alignment_theming(self) -> bool:
        """
        Checks for any changes in the theming data related to text alignment.

        :return: True if changes found.

        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment',
                                               default_value='center',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment_method',
                                               default_value='rect',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment',
                                               default_value='center',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        return has_any_changed

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this button.

        """

        theming_parameters = {'normal_bg': self.colours['normal_bg'],
                              'normal_text': self.colours['normal_text'],
                              'normal_text_shadow': self.colours['normal_text_shadow'],
                              'normal_border': self.colours['normal_border'],
                              'normal_image': self.normal_image,
                              'hovered_bg': self.colours['hovered_bg'],
                              'hovered_text': self.colours['hovered_text'],
                              'hovered_text_shadow': self.colours['hovered_text_shadow'],
                              'hovered_border': self.colours['hovered_border'],
                              'hovered_image': self.hovered_image,
                              'disabled_bg': self.colours['disabled_bg'],
                              'disabled_text': self.colours['disabled_text'],
                              'disabled_text_shadow': self.colours['disabled_text_shadow'],
                              'disabled_border': self.colours['disabled_border'],
                              'disabled_image': self.disabled_image,
                              'selected_bg': self.colours['selected_bg'],
                              'selected_text': self.colours['selected_text'],
                              'selected_text_shadow': self.colours['selected_text_shadow'],
                              'selected_border': self.colours['selected_border'],
                              'selected_image': self.selected_image,
                              'active_bg': self.colours['active_bg'],
                              'active_border': self.colours['active_border'],
                              'active_text': self.colours['active_text'],
                              'active_text_shadow': self.colours['active_text_shadow'],
                              'active_image': self.selected_image,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'font': self.font,
                              'text': translate(self.text, **self.text_kwargs),
                              'text_shadow': (self.text_shadow_size,
                                              self.text_shadow_offset[0],
                                              self.text_shadow_offset[1],
                                              self.colours['normal_text_shadow'],
                                              True),
                              'text_horiz_alignment': self.text_horiz_alignment,
                              'text_vert_alignment': self.text_vert_alignment,
                              'text_horiz_alignment_padding': self.text_horiz_alignment_padding,
                              'text_horiz_alignment_method': self.text_horiz_alignment_method,
                              'text_vert_alignment_padding': self.text_vert_alignment_padding,
                              'shape_corner_radius': self.shape_corner_radius,
                              'transitions': self.state_transitions}

        drawable_shape_rect = self.rect.copy()
        if self.dynamic_width:
            drawable_shape_rect.width = -1
            if self.max_dynamic_width is not None:
                theming_parameters["max_text_width"] = self.max_dynamic_width
        if self.dynamic_height:
            drawable_shape_rect.height = -1

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(drawable_shape_rect, theming_parameters,
                                                    ['normal', 'hovered', 'disabled',
                                                     'selected', 'active'], self.ui_manager)
        elif self.shape == 'ellipse':
            self.drawable_shape = EllipseDrawableShape(drawable_shape_rect, theming_parameters,
                                                       ['normal', 'hovered', 'disabled',
                                                        'selected', 'active'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(drawable_shape_rect, theming_parameters,
                                                        ['normal', 'hovered', 'disabled',
                                                         'selected', 'active'], self.ui_manager)

        if not self.is_enabled:
            if self.drawable_shape is not None:
                self.drawable_shape.set_active_state('disabled')

        self.on_fresh_drawable_shape_ready()

        self._on_contents_changed()

    def _calc_dynamic_size(self):
        if self.dynamic_width or self.dynamic_height:
            if self.image.get_size() == (0, 0):
                self._set_dimensions(self._get_pre_clipped_image_size())
            else:
                self._set_dimensions(self.image.get_size())

            # if we have anchored the left side of our button to the right of its container then
            # changing the width is going to mess up the horiz position as well.
            new_left = self.relative_rect.left
            new_top = self.relative_rect.top
            if 'left' in self.anchors and self.anchors['left'] == 'right' and self.dynamic_width:
                left_offset = self.dynamic_dimensions_orig_top_left[0]
                new_left = left_offset - self.relative_rect.width
            # if we have anchored the top side of our button to the bottom of it's container then
            # changing the height is going to mess up the vert position as well.
            if 'top' in self.anchors and self.anchors['top'] == 'bottom' and self.dynamic_height:
                top_offset = self.dynamic_dimensions_orig_top_left[1]
                new_top = top_offset - self.relative_rect.height

            self.set_relative_position((new_left, new_top))

    def hide(self):
        """
        In addition to the base UIElement.hide() - Change the hovered state to a normal state.
        """
        super().hide()

        self.on_unhovered()

    def on_locale_changed(self):
        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            self.rebuild()
        else:
            if self.dynamic_width or self.dynamic_height:
                self.rebuild()
            else:
                self.drawable_shape.set_text(translate(self.text, **self.text_kwargs))
