import pygame
from typing import Union, Tuple

from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import ui_tool_tip
from pygame_gui.core.ui_appearance_theme import ColourGradient


class UIButton(UIElement):
    """
    A push button, a lot of the appearance of the button, including images to be displayed, is setup via the theme file.
    This button is designed to be pressed, do something, and then reset - rather than to be toggled on or off.

    The button element is reused throughout the UI as part of other elements as it happens to be a very flexible
    interactive element.

    :param relative_rect: A rectangle describing the position (relative to its container) and dimensions.
    :param text: Text for the button.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param tool_tip_text: Optional tool tip text, can be formatted with HTML. If supplied will appear on hover.
    :param starting_height: The height in layers above it's container that this element will be placed.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: ui_manager.UIManager,
                 container: ui_container.UIContainer = None,
                 tool_tip_text: Union[str, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='button')

        super().__init__(relative_rect, manager, container,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         starting_height=starting_height,
                         layer_thickness=1)

        self.text = text

        self.click_area_shape = self.rect.copy()  # TODO replace this with functionality in DrawableShape

        # support for an optional 'tool tip' element attached to this button
        self.tool_tip_text = tool_tip_text
        self.tool_tip = None
        self.ui_root_container = self.ui_manager.get_window_stack().get_root_window().get_container()

        # Some different states our button can be in, could use a state machine for this if we wanted.
        self.held = False
        self.pressed = False
        self.is_selected = False
        self.pressed_event = False  # Used to check button pressed without going through pygame.Event system

        # time the hovering
        self.hover_time = 0.0

        self.text_surface = None
        self.aligned_text_rect = None

        self.image = None

        # default range at which we 'let go' of a button
        self.hold_range = (0, 0)

        # initialise theme parameters
        self.colours = {}
        self.text_colour = None
        self.background_colour = None
        self.border_colour = None

        self.font = None

        self.normal_image = None
        self.hovered_image = None
        self.selected_image = None
        self.disabled_image = None
        self.current_image = None

        self.tool_tip_delay = 1.0
        self.border_width = 0
        self.shadow_width = 0
        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1

        self.rebuild_from_changed_theme_data()

    def compute_aligned_text_rect(self):
        if len(self.text) > 0:
            # first we need to create rectangle the size of the text, if there is any text to draw
            self.aligned_text_rect = pygame.Rect((0, 0), self.font.size(self.text))

            # horizontal
            if self.text_horiz_alignment == 'center':
                self.aligned_text_rect.centerx = self.rect.width/2
            elif self.text_horiz_alignment == 'left':
                self.aligned_text_rect.x = self.text_horiz_alignment_padding + self.shadow_width + self.border_width
            elif self.text_horiz_alignment == 'right':
                x_pos = (self.click_area_shape.width - self.text_horiz_alignment_padding - self.aligned_text_rect.width
                         - self.shadow_width - self.border_width)
                self.aligned_text_rect. x = x_pos
            else:
                self.aligned_text_rect.centerx = self.rect.width/2
            # vertical
            if self.text_vert_alignment == 'center':
                self.aligned_text_rect.centery = int(self.rect.height/2)
            elif self.text_vert_alignment == 'top':
                self.aligned_text_rect.y = (self.text_vert_alignment_padding + self.shadow_width + self.border_width)
            elif self.text_vert_alignment == 'bottom':
                self.aligned_text_rect.y = (self.rect.height - self.aligned_text_rect.height
                                            - self.text_vert_alignment_padding - self.shadow_width - self.border_width)
            else:
                self.aligned_text_rect.centery = int(self.rect.height/2)

    def set_any_images_from_theme(self):
        """
        Grabs images for this button from the UI theme if any are set.

        :return changed:
        """

        changed = False
        normal_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'normal_image')
        if normal_image is not None and normal_image != self.normal_image:
            self.normal_image = normal_image
            self.hovered_image = normal_image
            self.selected_image = normal_image
            self.disabled_image = normal_image
            self.current_image = normal_image

            changed = True

        hovered_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'hovered_image')
        if hovered_image is not None and hovered_image != self.hovered_image:
            self.hovered_image = hovered_image
            changed = True

        selected_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'selected_image')
        if selected_image is not None and selected_image != self.selected_image:
            self.selected_image = selected_image
            changed = True

        disabled_image = self.ui_theme.get_image(self.object_ids, self.element_ids, 'disabled_image')
        if disabled_image is not None and disabled_image != self.disabled_image:
            self.disabled_image = disabled_image
            changed = True

        return changed

    def kill(self):
        """
        Overrides the standard sprite kill method to also kill any tooltips belonging to this button.
        """
        if self.tool_tip is not None:
            self.tool_tip.kill()
        super().kill()

    def hover_point(self, x, y) -> bool:
        """
        Tests if a position should be considered 'hovering' the button. Normally this just means our mouse pointer
        is inside the buttons rectangle, however if we are holding onto the button for a purpose(e.g. dragging a window
        around by it's menu bar) the hover radius can be made to grow so we don't keep losing touch with whatever we are
        moving.

        :param x: horizontal pixel co-ordinate to test.
        :param y: vertical pixel co-ordinate to test
        :return bool: Returns True if we are hovering.
        """
        if self.held:
            return self.in_hold_range((x, y))
        else:
            return self.click_area_shape.collidepoint(x, y)

    def can_hover(self) -> bool:
        """
        Tests whether we can trigger the hover state for this button, other states take priority over it.

        :return bool: True if we are able to hover this button.
        """
        return not self.is_selected and self.is_enabled and not self.held

    def on_hovered(self):
        """
        Called when we enter the hover state, it sets the colours and image of the button to the appropriate
        values and redraws it.
        """
        self.text_colour = self.colours['hovered_text']
        self.background_colour = self.colours['hovered_bg']
        self.border_colour = self.colours['hovered_border']
        self.current_image = self.hovered_image
        self.redraw()
        self.hover_time = 0.0

    def while_hovering(self, time_delta, mouse_pos):
        """
        Called while we are in the hover state. It will create a tool tip if we've been in the hover state for a while,
        the text exists to create one and we haven't created one already.

        :param time_delta: Time in seconds between calls to update.
        :param mouse_pos: The current position of the mouse.
        """
        if self.tool_tip is None and self.tool_tip_text is not None \
                and self.hover_time > self.tool_tip_delay:
            self.tool_tip = ui_tool_tip.UITooltip(self.tool_tip_text,
                                                  (0, int(self.rect.height / 2)),
                                                  self.ui_manager)
            self.tool_tip.find_valid_position(pygame.math.Vector2(mouse_pos.x, self.rect.centery))

        self.hover_time += time_delta

    def on_unhovered(self):
        """
        Called when we leave the hover state. Resets the colours and images to normal and kills any tooltip that was
        created while we were hovering the button.
        """
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.border_colour = self.colours['normal_border']
        self.current_image = self.normal_image
        self.redraw()
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

    def update(self, time_delta):
        """
        Sets the pressed state for an update cycle if we've pressed this button recently.

        :param time_delta: the time in seconds between one call to update and the next.
        """
        if self.alive():
            # clear pressed state, we only want it to last one update cycle
            self.pressed = False

            if self.pressed_event:
                # if a pressed event has occurred set the button to the pressed state for one update cycle.
                self.pressed_event = False
                self.pressed = True

    def set_position(self, position: pygame.math.Vector2):
        """
        Method to directly set the absolute rect position of a button.

        :param position: The new position to set.
        """
        self.rect.x = position.x
        self.rect.y = position.y
        self.relative_rect.x = position.x - self.ui_container.rect.x
        self.relative_rect.y = position.y - self.ui_container.rect.y

        if self.shadow_width > 0:
            self.click_area_shape = pygame.Rect((self.rect.x + self.shadow_width,
                                                 self.rect.y + self.shadow_width),
                                                (self.rect.width - (2 * self.shadow_width),
                                                 self.rect.height - (2 * self.shadow_width)))
        else:
            self.click_area_shape = self.rect.copy()

    def update_containing_rect_position(self):
        """
        Updates the position of this element based on the position of it's container. Usually called when the container
        has moved.
        """
        self.rect = pygame.Rect((self.ui_container.rect.x + self.relative_rect.x,
                                 self.ui_container.rect.y + self.relative_rect.y),
                                self.relative_rect.size)

        if self.shadow_width > 0:
            self.click_area_shape = pygame.Rect((self.rect.x + self.shadow_width,
                                                 self.rect.y + self.shadow_width),
                                                (self.rect.width - (2 * self.shadow_width),
                                                 self.rect.height - (2 * self.shadow_width)))
        else:
            self.click_area_shape = self.rect.copy()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles interactions with the button.

        :param event: The event to process.
        :return bool: Returns True if we made use of this event.
        """
        processed_event = False
        if self.is_enabled:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if self.click_area_shape.collidepoint(mouse_x, mouse_y):
                        self.held = True
                        self.set_active()
                        processed_event = True
                        self.hover_time = 0.0
                        if self.tool_tip is not None:
                            self.tool_tip.kill()
                            self.tool_tip = None
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos

                    if self.click_area_shape.collidepoint(mouse_x, mouse_y):
                        if self.held:
                            self.held = False
                            self.set_inactive()
                            self.ui_manager.unselect_focus_element()
                            processed_event = True
                            self.pressed_event = True

                            button_pressed_event = pygame.event.Event(pygame.USEREVENT,
                                                                      {'user_type': 'ui_button_pressed',
                                                                       'ui_element': self,
                                                                       'ui_object_id': self.object_ids[-1]})
                            pygame.event.post(button_pressed_event)

                    if self.held:
                        self.held = False
                        self.set_inactive()
                        self.select()
                        processed_event = True

        return processed_event

    def redraw(self):
        """
        Redraws the button from data onto the underlying sprite's image. Only need to call this if something has
        changed with the button (e.g. changed state or the text on it has changed)
        """
        if self.shadow_width > 0:
            self.image = self.ui_manager.get_shadow(self.rect.size)
        else:
            self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        if self.border_width > 0:
            border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                      (self.click_area_shape.width, self.click_area_shape.height))
            if type(self.border_colour) == ColourGradient:
                border_rect_shape_surface = pygame.Surface(border_rect.size)
                border_rect_shape_surface.fill(pygame.Color('#FFFFFFFF'))
                gradient_surface = self.border_colour.apply_gradient_to_surface(border_rect_shape_surface)
                self.image.blit(border_rect_shape_surface, border_rect, special_flags=pygame.BLEND_RGBA_SUB)
                self.image.blit(gradient_surface, border_rect)
            else:
                self.image.fill(self.border_colour, border_rect)

        background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                       self.border_width + self.shadow_width),
                                      (self.click_area_shape.width - (2 * self.border_width),
                                       self.click_area_shape.height - (2 * self.border_width)))

        if type(self.background_colour) == ColourGradient:
            background_rect_shape_surface = pygame.Surface(background_rect.size)
            background_rect_shape_surface.fill(pygame.Color('#FFFFFFFF'))
            gradient_surface = self.background_colour.apply_gradient_to_surface(background_rect_shape_surface)
            self.image.blit(background_rect_shape_surface, background_rect, special_flags=pygame.BLEND_RGBA_SUB)
            self.image.blit(gradient_surface, background_rect)
        else:
            self.image.fill(self.background_colour, background_rect)

        if self.current_image is not None:
            image_rect = self.current_image.get_rect()
            image_rect.center = (self.rect.width/2, self.rect.height/2)
            self.image.blit(self.current_image, image_rect)

        if len(self.text) > 0:
            self.text_surface = self.font.render(self.text, True, self.text_colour)
        else:
            self.text_surface = None

        if self.text_surface is not None and self.aligned_text_rect is not None:
            self.image.blit(self.text_surface, self.aligned_text_rect)

    def check_pressed(self):
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
        self.text_colour = self.colours['disabled_text']
        self.background_colour = self.colours['disabled_bg']
        self.border_colour = self.colours['disabled_border']
        self.current_image = self.disabled_image

    def enable(self):
        """
        Re-enables the button so we can once again interact with it.
        """
        self.is_enabled = True
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.border_colour = self.colours['normal_border']
        self.current_image = self.normal_image

    def set_active(self):
        """
        Called when we are actively clicking on the button. Changes the colours to the appropriate ones for the new
        state then redraws the button.
        """
        self.text_colour = self.colours['active_text']
        self.background_colour = self.colours['active_bg']
        self.border_colour = self.colours['active_border']
        self.redraw()

    def set_inactive(self):
        """
        Called when we stop actively clicking on the button. Restores the colours to the default
        state then redraws the button.
        """
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.border_colour = self.colours['normal_border']
        self.redraw()

    def select(self):
        """
        Called when we select focus this element. Changes the colours and image to the appropriate ones for the new
        state then redraws the button.
        """
        self.is_selected = True
        self.text_colour = self.colours['selected_text']
        self.background_colour = self.colours['selected_bg']
        self.border_colour = self.colours['selected_border']
        self.current_image = self.selected_image
        self.redraw()

    def unselect(self):
        """
        Called when we are no longer select focusing this element. Restores the colours and image to the default
        state then redraws the button.
        """
        self.is_selected = False
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.border_colour = self.colours['normal_border']
        self.current_image = self.normal_image
        self.redraw()

    def set_text(self, text: str):
        """
        Sets the text on the button. The button will redraw.

        :param text: The new text to set.
        """
        if text != self.text:
            self.text = text
            # recompute aligned_text_rect before redraw
            self.compute_aligned_text_rect()
            self.redraw()

    def set_hold_range(self, xy_range: Tuple[int, int]):
        """
        Set x and y values, in pixels, around our button to use as the hold range for time when we want to drag a button
        about but don't want it to slip out of our grasp too easily.

        Imagine it as a large rectangle around our button, larger in all directions by whatever values we specify here.

        :param xy_range: The x and y values used to create our larger 'holding' rectangle.
        """
        self.hold_range = xy_range

    def in_hold_range(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]) -> bool:
        """
        Imagines a potentially larger rectangle around our button in which range we still grip hold of our
        button when moving the mouse. Makes it easier to use scrollbars.

        :param position: The position we are testing.
        :return bool: Returns True if our position is inside the hold range.
        """
        if self.click_area_shape.collidepoint(position[0], position[1]):
            return True
        elif self.hold_range[0] > 0 or self.hold_range[1] > 0:
            hold_rect = pygame.Rect((self.rect.x - self.hold_range[0],
                                     self.rect.y - self.hold_range[1]),
                                    (self.rect.width + (2 * self.hold_range[0]),
                                     self.rect.height + (2 * self.hold_range[1])))
            if hold_rect.collidepoint(position[0], position[1]):
                return True
        else:
            return False

    def rebuild_from_changed_theme_data(self):
        any_changed = False

        font = self.ui_theme.get_font(self.object_ids, self.element_ids)
        if font != self.font:
            self.font = font
            any_changed = True

        colours = {'normal_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                     self.element_ids, 'normal_bg'),
                   'hovered_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                      self.element_ids, 'hovered_bg'),
                   'disabled_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids, 'disabled_bg'),
                   'selected_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                       self.element_ids, 'selected_bg'),
                   'active_bg': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                     self.element_ids, 'active_bg'),
                   'normal_text': self.ui_theme.get_colour(self.object_ids, self.element_ids, 'normal_text'),
                   'hovered_text': self.ui_theme.get_colour(self.object_ids, self.element_ids, 'hovered_text'),
                   'disabled_text': self.ui_theme.get_colour(self.object_ids, self.element_ids, 'disabled_text'),
                   'selected_text': self.ui_theme.get_colour(self.object_ids, self.element_ids, 'selected_text'),
                   'active_text': self.ui_theme.get_colour(self.object_ids, self.element_ids, 'active_text'),
                   'normal_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids, 'normal_border'),
                   'hovered_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                          self.element_ids, 'hovered_border'),
                   'disabled_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                           self.element_ids, 'disabled_border'),
                   'selected_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                           self.element_ids, 'selected_border'),
                   'active_border': self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                         self.element_ids, 'active_border')}

        if colours != self.colours:
            self.colours = colours
            any_changed = True

        if self.set_any_images_from_theme():
            any_changed = True

        # misc
        tool_tip_delay_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'tool_tip_delay')
        if tool_tip_delay_string is not None:
            try:
                tool_tip_delay = float(tool_tip_delay_string)
            except ValueError:
                tool_tip_delay = 1.0

            if tool_tip_delay != self.tool_tip_delay:
                self.tool_tip_delay = tool_tip_delay
                any_changed = True

        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            try:
                border_width = int(border_width_string)
            except ValueError:
                border_width = 0
            if border_width != self.border_width:
                self.border_width = border_width
                any_changed = True

        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if border_width_string is not None:
            try:
                shadow_width = int(shadow_width_string)
            except ValueError:
                shadow_width = 0
            if shadow_width != self.shadow_width:
                self.shadow_width = shadow_width
                any_changed = True

        text_horiz_alignment = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'text_horiz_alignment')
        if text_horiz_alignment != self.text_horiz_alignment:
            self.text_horiz_alignment = text_horiz_alignment
            any_changed = True

        text_horiz_alignment_padding = self.ui_theme.get_misc_data(self.object_ids,
                                                                   self.element_ids, 'text_horiz_alignment_padding')
        if text_horiz_alignment_padding is not None:
            try:
                text_horiz_alignment_padding = int(text_horiz_alignment_padding)
            except ValueError:
                text_horiz_alignment_padding = 1
            if text_horiz_alignment_padding != self.text_horiz_alignment_padding:
                self.text_horiz_alignment_padding = text_horiz_alignment_padding
                any_changed = True

        text_vert_alignment = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'text_vert_alignment')
        if text_vert_alignment != self.text_vert_alignment:
            self.text_vert_alignment = text_vert_alignment
            any_changed = True

        text_vert_alignment_padding = self.ui_theme.get_misc_data(self.object_ids,
                                                                  self.element_ids, 'text_vert_alignment_padding')
        if text_vert_alignment_padding is not None:
            try:
                text_vert_alignment_padding = int(text_vert_alignment_padding)
            except ValueError:
                text_vert_alignment_padding = 1
            if text_vert_alignment_padding != self.text_vert_alignment_padding:
                self.text_vert_alignment_padding = text_vert_alignment_padding
                any_changed = True

        if any_changed:
            if not self.is_enabled:
                self.text_colour = self.colours['disabled_text']
                self.background_colour = self.colours['disabled_bg']
                self.border_colour = self.colours['disabled_border']
                self.current_image = self.disabled_image
            elif self.hovered:
                self.text_colour = self.colours['hovered_text']
                self.background_colour = self.colours['hovered_bg']
                self.border_colour = self.colours['hovered_border']
                self.current_image = self.hovered_image
            elif self.is_selected:
                self.text_colour = self.colours['selected_text']
                self.background_colour = self.colours['selected_bg']
                self.border_colour = self.colours['selected_border']
                self.current_image = self.selected_image
            else:
                self.text_colour = self.colours['normal_text']
                self.background_colour = self.colours['normal_bg']
                self.border_colour = self.colours['normal_border']
                self.current_image = self.normal_image

            if self.shadow_width > 0:
                self.click_area_shape = pygame.Rect((self.rect.x + self.shadow_width,
                                                     self.rect.y + self.shadow_width),
                                                    (self.rect.width - (2 * self.shadow_width),
                                                     self.rect.height - (2 * self.shadow_width)))
            else:
                self.click_area_shape = self.rect.copy()

            # this helps us draw the text aligned
            self.compute_aligned_text_rect()
            self.redraw()
