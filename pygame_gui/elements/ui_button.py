from typing import Union, Tuple, Dict

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import EllipseDrawableShape, RoundedRectangleShape
from pygame_gui.core.drawable_shapes import RectDrawableShape


class UIButton(UIElement):
    """
    A push button, a lot of the appearance of the button, including images to be displayed, is
    setup via the theme file. This button is designed to be pressed, do something, and then reset -
    rather than to be toggled on or off.

    The button element is reused throughout the UI as part of other elements as it happens to be a
    very flexible interactive element.

    :param relative_rect: A rectangle describing the position (relative to its container) and
                          dimensions.
    :param text: Text for the button.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param tool_tip_text: Optional tool tip text, can be formatted with HTML. If supplied will
                          appear on hover.
    :param starting_height: The height in layers above it's container that this element will be
                            placed.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param allow_double_clicks: Enables double clicking on buttons which will generate a
                                unique event.

    """
    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 tool_tip_text: Union[str, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None,
                 allow_double_clicks: bool = False
                 ):

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='button')

        super().__init__(relative_rect, manager, container,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors)

        self.text = text

        # support for an optional 'tool tip' element attached to this button
        self.tool_tip_text = tool_tip_text
        self.tool_tip = None
        self.ui_root_container = self.ui_manager.get_root_container()

        # Some different states our button can be in, could use a state machine for this
        # if we wanted.
        self.held = False
        self.pressed = False
        self.is_selected = False
        # Used to check button pressed without going through pygame.Event system
        self.pressed_event = False

        # time the hovering
        self.hover_time = 0.0

        # timer for double clicks
        self.allow_double_clicks = allow_double_clicks
        self.double_click_timer = self.ui_manager.get_double_click_time() + 1.0

        self.text_surface = None
        self.aligned_text_rect = None

        self.set_image(None)

        # default range at which we 'let go' of a button
        self.hold_range = (0, 0)

        # initialise theme parameters
        self.colours = {}

        self.font = None

        self.normal_image = None
        self.hovered_image = None
        self.selected_image = None
        self.disabled_image = None

        self.tool_tip_delay = 1.0

        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1
        self.shape_type = 'rectangle'

        self.state_transitions = {}

        self.rebuild_from_changed_theme_data()

    def set_any_images_from_theme(self) -> bool:
        """
        Grabs images for this button from the UI theme if any are set.

        :return: True if any of the images have changed since last time they were set.

        """

        changed = False
        normal_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'normal_image')
        if normal_image is not None and normal_image != self.normal_image:
            self.normal_image = normal_image
            self.hovered_image = normal_image
            self.selected_image = normal_image
            self.disabled_image = normal_image
            changed = True

        hovered_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'hovered_image')
        if hovered_image is not None and hovered_image != self.hovered_image:
            self.hovered_image = hovered_image
            changed = True

        selected_image = self.ui_theme.get_image(self.object_ids,
                                                 self.element_ids, 'selected_image')
        if selected_image is not None and selected_image != self.selected_image:
            self.selected_image = selected_image
            changed = True

        disabled_image = self.ui_theme.get_image(self.object_ids,
                                                 self.element_ids, 'disabled_image')
        if disabled_image is not None and disabled_image != self.disabled_image:
            self.disabled_image = disabled_image
            changed = True

        return changed

    def kill(self):
        """
        Overrides the standard sprite kill method to also kill any tooltips belonging to
        this button.
        """
        if self.tool_tip is not None:
            self.tool_tip.kill()
        super().kill()

    def hover_point(self, hover_x: int, hover_y: int) -> bool:
        """
        Tests if a position should be considered 'hovering' the button. Normally this just means
        our mouse pointer is inside the buttons rectangle, however if we are holding onto the
        button for a purpose(e.g. dragging a window around by it's menu bar) the hover radius can
        be made to grow so we don't keep losing touch with whatever we are moving.

        :param hover_x: horizontal pixel co-ordinate to test.
        :param hover_y: vertical pixel co-ordinate to test

        :return: Returns True if we are hovering.

        """
        if self.held:
            return self.in_hold_range((hover_x, hover_y))
        else:
            return (self.drawable_shape.collide_point((hover_x, hover_y)) and
                    bool(self.ui_container.rect.collidepoint(hover_x, hover_y)))

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
        self.drawable_shape.set_active_state('hovered')
        self.hover_time = 0.0

    def while_hovering(self, time_delta: float,
                       mouse_pos: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Called while we are in the hover state. It will create a tool tip if we've been in the
        hover state for a while, the text exists to create one and we haven't created one already.

        :param time_delta: Time in seconds between calls to update.
        :param mouse_pos: The current position of the mouse.

        """
        if (self.tool_tip is None and self.tool_tip_text is not None and
                self.hover_time > self.tool_tip_delay):
            hover_height = int(self.rect.height / 2)
            self.tool_tip = self.ui_manager.create_tool_tip(text=self.tool_tip_text,
                                                            position=(mouse_pos[0],
                                                                      self.rect.centery),
                                                            hover_distance=(0,
                                                                            hover_height))

        self.hover_time += time_delta

    def on_unhovered(self):
        """
        Called when we leave the hover state. Resets the colours and images to normal and kills any
        tooltip that was created while we were hovering the button.
        """
        self.drawable_shape.set_active_state('normal')
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

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
        if self.is_enabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                    int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))
                if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                    if (self.allow_double_clicks and
                            self.double_click_timer <= self.ui_manager.get_double_click_time()):
                        event_data = {'user_type': UI_BUTTON_DOUBLE_CLICKED,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
                    else:
                        self.double_click_timer = 0.0
                        self.held = True
                        self.set_active()
                        self.hover_time = 0.0
                        if self.tool_tip is not None:
                            self.tool_tip.kill()
                            self.tool_tip = None
                    consumed_event = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                    int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))
                if self.drawable_shape.collide_point(scaled_mouse_pos) and self.held:
                    self.held = False
                    self.set_inactive()
                    self.ui_manager.unset_focus_element()
                    consumed_event = True
                    self.pressed_event = True

                    event_data = {'user_type': UI_BUTTON_PRESSED,
                                  'ui_element': self,
                                  'ui_object_id': self.most_specific_combined_id}
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                if self.held:
                    self.held = False
                    self.set_inactive()
                    consumed_event = True

        return consumed_event

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
        self.is_enabled = False
        self.drawable_shape.set_active_state('disabled')

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        self.is_enabled = True
        self.drawable_shape.set_active_state('normal')

    def set_active(self):
        """
        Called when we are actively clicking on the button. Changes the colours to the appropriate
        ones for the new state then redraws the button.
        """
        self.drawable_shape.set_active_state('active')

    def set_inactive(self):
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

    def set_text(self, text: str):
        """
        Sets the text on the button. The button will rebuild.

        :param text: The new text to set.

        """
        if text != self.text:
            self.text = text
            self.drawable_shape.theming['text'] = self.text
            # recompute aligned_text_rect before rebuild
            self.drawable_shape.compute_aligned_text_rect()
            self.drawable_shape.redraw_all_states()

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
        has_any_changed = False

        font = self.ui_theme.get_font(self.object_ids, self.element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        colours = {'normal_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                     self.element_ids,
                                                                     'normal_bg'),
                   'hovered_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                      self.element_ids,
                                                                      'hovered_bg'),
                   'disabled_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids,
                                                                       'disabled_bg'),
                   'selected_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids,
                                                                       'selected_bg'),
                   'active_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                     self.element_ids,
                                                                     'active_bg'),
                   'normal_text': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids,
                                                                       'normal_text'),
                   'hovered_text': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                        self.element_ids,
                                                                        'hovered_text'),
                   'disabled_text': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids,
                                                                         'disabled_text'),
                   'selected_text': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids,
                                                                         'selected_text'),
                   'active_text': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids,
                                                                       'active_text'),
                   'normal_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids,
                                                                         'normal_border'),
                   'hovered_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                          self.element_ids,
                                                                          'hovered_border'),
                   'disabled_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                           self.element_ids,
                                                                           'disabled_border'),
                   'selected_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                           self.element_ids,
                                                                           'selected_border'),
                   'active_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids,
                                                                         'active_border')}

        if colours != self.colours:
            self.colours = colours
            has_any_changed = True

        if self.set_any_images_from_theme():
            has_any_changed = True

        # misc
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if (shape_type_string is not None and shape_type_string in ['rectangle',
                                                                    'ellipse',
                                                                    'rounded_rectangle'] and
                shape_type_string != self.shape_type):
            self.shape_type = shape_type_string
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        tool_tip_delay_string = self.ui_theme.get_misc_data(self.object_ids,
                                                            self.element_ids,
                                                            'tool_tip_delay')
        if tool_tip_delay_string is not None:
            try:
                tool_tip_delay = float(tool_tip_delay_string)
            except ValueError:
                tool_tip_delay = 1.0

            if tool_tip_delay != self.tool_tip_delay:
                self.tool_tip_delay = tool_tip_delay
                has_any_changed = True

        if self._check_text_alignment_theming():
            has_any_changed = True

        state_transitions = self.ui_theme.get_misc_data(self.object_ids,
                                                        self.element_ids,
                                                        'state_transitions')
        if state_transitions is not None and isinstance(state_transitions, dict):
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
        text_horiz_alignment = self.ui_theme.get_misc_data(self.object_ids,
                                                           self.element_ids,
                                                           'text_horiz_alignment')
        if text_horiz_alignment != self.text_horiz_alignment:
            self.text_horiz_alignment = text_horiz_alignment
            has_any_changed = True
        text_horiz_alignment_padding = self.ui_theme.get_misc_data(self.object_ids,
                                                                   self.element_ids,
                                                                   'text_horiz_alignment_padding')
        if text_horiz_alignment_padding is not None:
            try:
                text_horiz_alignment_padding = int(text_horiz_alignment_padding)
            except ValueError:
                text_horiz_alignment_padding = 1
            if text_horiz_alignment_padding != self.text_horiz_alignment_padding:
                self.text_horiz_alignment_padding = text_horiz_alignment_padding
                has_any_changed = True
        text_vert_alignment = self.ui_theme.get_misc_data(self.object_ids,
                                                          self.element_ids,
                                                          'text_vert_alignment')
        if text_vert_alignment != self.text_vert_alignment:
            self.text_vert_alignment = text_vert_alignment
            has_any_changed = True
        text_vert_alignment_padding = self.ui_theme.get_misc_data(self.object_ids,
                                                                  self.element_ids,
                                                                  'text_vert_alignment_padding')
        if text_vert_alignment_padding is not None:
            try:
                text_vert_alignment_padding = int(text_vert_alignment_padding)
            except ValueError:
                text_vert_alignment_padding = 1
            if text_vert_alignment_padding != self.text_vert_alignment_padding:
                self.text_vert_alignment_padding = text_vert_alignment_padding
                has_any_changed = True
        return has_any_changed

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this button.

        """
        theming_parameters = {'normal_bg': self.colours['normal_bg'],
                              'normal_text': self.colours['normal_text'],
                              'normal_border': self.colours['normal_border'],
                              'normal_image': self.normal_image,
                              'hovered_bg': self.colours['hovered_bg'],
                              'hovered_text': self.colours['hovered_text'],
                              'hovered_border': self.colours['hovered_border'],
                              'hovered_image': self.hovered_image,
                              'disabled_bg': self.colours['disabled_bg'],
                              'disabled_text': self.colours['disabled_text'],
                              'disabled_border': self.colours['disabled_border'],
                              'disabled_image': self.disabled_image,
                              'selected_bg': self.colours['selected_bg'],
                              'selected_text': self.colours['selected_text'],
                              'selected_border': self.colours['selected_border'],
                              'selected_image': self.selected_image,
                              'active_bg': self.colours['active_bg'],
                              'active_border': self.colours['active_border'],
                              'active_text': self.colours['active_text'],
                              'active_image': self.selected_image,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'font': self.font,
                              'text': self.text,
                              'text_horiz_alignment': self.text_horiz_alignment,
                              'text_vert_alignment': self.text_vert_alignment,
                              'text_horiz_alignment_padding': self.text_horiz_alignment_padding,
                              'text_vert_alignment_padding': self.text_vert_alignment_padding,
                              'shape_corner_radius': self.shape_corner_radius,
                              'transitions': self.state_transitions}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal', 'hovered', 'disabled',
                                                     'selected', 'active'], self.ui_manager)
        elif self.shape_type == 'ellipse':
            self.drawable_shape = EllipseDrawableShape(self.rect, theming_parameters,
                                                       ['normal', 'hovered', 'disabled',
                                                        'selected', 'active'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal', 'hovered', 'disabled',
                                                         'selected', 'active'], self.ui_manager)

        self.on_fresh_drawable_shape_ready()
