import pygame
from pygame_gui.core.ui_element import UIElement
import pygame_gui.elements.ui_tool_tip


class UIButton(UIElement):
    def __init__(self, relative_rect, text, ui_manager,
                 ui_container=None, tool_tip_text=None, starting_height=1, object_id=None, element_ids=None):
        """
        A basic button, a lot of the appearance of the button, including images to be displayed

        :param relative_rect:
        :param text:
        :param ui_manager:
        :param ui_container:
        :param tool_tip_text:
        :param starting_height:
        :param object_id:
        :param element_ids:
        """
        if element_ids is None:
            new_element_ids = ['button']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('button')
        super().__init__(relative_rect, ui_manager, ui_container,
                         object_id=object_id,
                         element_ids=new_element_ids,
                         starting_height=starting_height,
                         layer_thickness=1)

        self.font = self.ui_theme.get_font(self.object_id, self.element_ids)
        self.text = text

        # support for an optional 'tool tip' element attached to this button
        self.tool_tip_text = tool_tip_text
        self.tool_tip = None
        self.ui_root_container = self.ui_manager.get_window_stack().get_root_window().get_container()

        # colours, we could grab these from a separate colour theme class that we use across pygame_gui elements, much like a
        # css file provides colours and styles to a group of HTML we pages

        self.colours = {'normal_bg': self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_bg'),
                        'hovered_bg': self.ui_theme.get_colour(self.object_id, self.element_ids, 'hovered_bg'),
                        'disabled_bg': self.ui_theme.get_colour(self.object_id, self.element_ids, 'disabled_bg'),
                        'selected_bg': self.ui_theme.get_colour(self.object_id, self.element_ids, 'selected_bg'),
                        'active_bg': self.ui_theme.get_colour(self.object_id, self.element_ids, 'active_bg'),
                        'normal_text': self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_text'),
                        'hovered_text': self.ui_theme.get_colour(self.object_id, self.element_ids, 'hovered_text'),
                        'disabled_text': self.ui_theme.get_colour(self.object_id, self.element_ids, 'disabled_text'),
                        'selected_text': self.ui_theme.get_colour(self.object_id, self.element_ids, 'selected_text'),
                        'active_text': self.ui_theme.get_colour(self.object_id, self.element_ids, 'active_text')}

        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']

        # different states our button can be in, could use a state machine for this if you wanted
        # could also add a 'selected' state like windows has.
        self.hovered = False
        self.held = False
        self.pressed = False

        self.is_selected = False

        # time the hovering
        self.hover_time = 0.0

        tool_tip_delay_string = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'tool_tip_delay')
        if tool_tip_delay_string is not None:
            self.tool_tip_delay = float(tool_tip_delay_string)
        else:
            self.tool_tip_delay = 1.0

        self.text_surface = self.font.render(self.text, True, self.text_colour)

        self.image = pygame.Surface(self.rect.size)

        text_horiz_alignment = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'text_horiz_alignment')
        text_horiz_alignment_padding = self.ui_theme.get_misc_data(self.object_id,
                                                                   self.element_ids, 'text_horiz_alignment_padding')
        if text_horiz_alignment_padding is None:
            text_horiz_alignment_padding = 1
        else:
            text_horiz_alignment_padding = int(text_horiz_alignment_padding)

        # this helps us draw the text aligned
        if text_horiz_alignment == 'center':
            self.aligned_text_rect = self.text_surface.get_rect(centerx=self.rect.centerx - self.rect.x,
                                                                centery=self.rect.centery - self.rect.y)
        elif text_horiz_alignment == 'left':
            self.aligned_text_rect = self.text_surface.get_rect(x=text_horiz_alignment_padding,
                                                                centery=self.rect.centery - self.rect.y)
        elif text_horiz_alignment == 'right':
            x_pos = self.rect.width - text_horiz_alignment_padding - self.text_surface.get_width()
            self.aligned_text_rect = self.text_surface.get_rect(x=x_pos,
                                                                centery=self.rect.centery - self.rect.y)
        else:
            self.aligned_text_rect = self.text_surface.get_rect(centerx=self.rect.centerx - self.rect.x,
                                                                centery=self.rect.centery - self.rect.y)

        text_vert_alignment = self.ui_theme.get_misc_data(self.object_id, self.element_ids, 'text_vert_alignment')
        text_vert_alignment_padding = self.ui_theme.get_misc_data(self.object_id,
                                                                  self.element_ids, 'text_vert_alignment_padding')
        if text_vert_alignment_padding is None:
            text_vert_alignment_padding = 1
        else:
            text_vert_alignment_padding = int(text_vert_alignment_padding)

        if text_vert_alignment == 'center':
            self.aligned_text_rect.centery = int(self.rect.height/2)
        elif text_vert_alignment == 'top':
            self.aligned_text_rect.y = text_vert_alignment_padding
        elif text_vert_alignment == 'bottom':
            self.aligned_text_rect.y = self.rect.height - self.text_surface.get_height() - text_vert_alignment_padding
        else:
            self.aligned_text_rect.centery = int(self.rect.height/2)

        # default range at which we 'let go' of a button
        self.hold_range = (0, 0)

        self.normal_image = None
        self.hovered_image = None
        self.selected_image = None
        self.disabled_image = None
        self.current_image = None

        self.set_any_images_from_theme()

        self.redraw()

    def set_any_images_from_theme(self):
        normal_image = self.ui_theme.get_image(self.object_id, self.element_ids, 'normal_image')
        if normal_image is not None:
            self.normal_image = normal_image
            self.hovered_image = normal_image
            self.selected_image = normal_image
            self.disabled_image = normal_image
            self.current_image = normal_image

        hovered_image = self.ui_theme.get_image(self.object_id, self.element_ids, 'hovered_image')
        if hovered_image is not None:
            self.hovered_image = hovered_image

        selected_image = self.ui_theme.get_image(self.object_id, self.element_ids, 'selected_image')
        if selected_image is not None:
            self.selected_image = selected_image

        disabled_image = self.ui_theme.get_image(self.object_id, self.element_ids, 'disabled_image')
        if disabled_image is not None:
            self.disabled_image = disabled_image

    def kill(self):
        if self.tool_tip is not None:
            self.tool_tip.kill()
        super().kill()

    def hover_point(self, x, y):
        if self.held:
            return self.in_hold_range((x, y))
        else:
            return self.rect.collidepoint(x, y)

    def can_hover(self):
        return not self.is_selected and self.is_enabled and not self.held

    def on_hovered(self):
        self.text_colour = self.colours['hovered_text']
        self.background_colour = self.colours['hovered_bg']
        self.current_image = self.hovered_image
        self.redraw()
        self.hover_time = 0.0

    def while_hovering(self, time_delta, mouse_pos):
        if self.tool_tip is None and self.tool_tip_text is not None \
                and self.hover_time > self.tool_tip_delay:
            self.tool_tip = pygame_gui.elements.ui_tool_tip.UITooltip(self.tool_tip_text,
                                                                      (0, int(self.rect.height / 2)),
                                                                      self.ui_manager)
            self.tool_tip.find_valid_position(pygame.math.Vector2(mouse_pos.x, self.rect.centery))

        self.hover_time += time_delta

    def on_unhovered(self):
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.current_image = self.normal_image
        self.redraw()
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

    # def update(self, time_delta):
    #     if self.alive():
    #         mouse_x, mouse_y = pygame.mouse.get_pos()
    #         if self.held and not self.in_hold_range((mouse_x, mouse_y)):
    #             self.held = False

    def process_event(self, event):
        processed_event = False
        if self.is_enabled:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if self.rect.collidepoint(mouse_x, mouse_y):
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

                    if self.rect.collidepoint(mouse_x, mouse_y):
                        if self.held:
                            self.held = False
                            self.set_inactive()
                            self.pressed = True
                            self.ui_manager.unselect_focus_element()
                            processed_event = True

                    if self.held:
                        self.held = False
                        self.set_inactive()
                        self.select()
                        processed_event = True

        return processed_event

    def redraw(self):
        self.image.fill(self.background_colour)
        if self.current_image is not None:
            image_rect = self.current_image.get_rect()
            image_rect.center = (self.rect.width/2, self.rect.height/2)
            self.image.blit(self.current_image, image_rect)
            self.text_surface = self.font.render(self.text, True, self.text_colour)
        else:
            self.text_surface = self.font.render(self.text, True, self.text_colour, self.background_colour)
        self.image.blit(self.text_surface, self.aligned_text_rect)

    def check_pressed_and_reset(self):
        if self.pressed:
            self.pressed = False
            return True
        else:
            return False

    def disable(self):
        self.is_enabled = False
        self.text_colour = self.colours['disabled_text']
        self.background_colour = self.colours['disabled_bg']
        self.current_image = self.disabled_image

    def enable(self):
        self.is_enabled = True
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.current_image = self.normal_image

    def set_active(self):
        self.text_colour = self.colours['active_text']
        self.background_colour = self.colours['active_bg']
        self.redraw()

    def set_inactive(self):
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.redraw()

    def select(self):
        self.is_selected = True
        self.text_colour = self.colours['selected_text']
        self.background_colour = self.colours['selected_bg']
        self.current_image = self.selected_image
        self.redraw()

    def unselect(self):
        self.is_selected = False
        self.text_colour = self.colours['normal_text']
        self.background_colour = self.colours['normal_bg']
        self.current_image = self.normal_image
        self.redraw()

    def set_text(self, text):
        self.text = text
        self.redraw()

    def set_hold_range(self, xy_range):
        self.hold_range = xy_range

    def in_hold_range(self, position):
        """
        Imagines a potentially larger rectangle around our button in which range we still grip hold of our
        button when moving the mouse. Makes it easier to use scrollbars.
        :param position:
        :return :
        """
        if self.rect.collidepoint(position[0], position[1]):
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
