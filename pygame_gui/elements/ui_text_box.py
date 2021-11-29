import warnings
import math

from typing import Union, Tuple, Dict

import pygame

from pygame_gui.core import ObjectID
from pygame_gui._constants import UI_TEXT_BOX_LINK_CLICKED, OldType
from pygame_gui._constants import TEXT_EFFECT_TYPING_APPEAR
from pygame_gui._constants import TEXT_EFFECT_FADE_IN, TEXT_EFFECT_FADE_OUT

from pygame_gui.core.utility import translate
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.utility import basic_blit

from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar

from pygame_gui.core.text.html_parser import HTMLParser
from pygame_gui.core.text.text_box_layout import TextBoxLayout
from pygame_gui.core.text.text_effects import TypingAppearEffect, FadeInEffect, FadeOutEffect


class UITextBox(UIElement):
    """
    A Text Box element lets us display word-wrapped, formatted text. If the text to display is
    longer than the height of the box given then the element will automatically create a vertical
    scroll bar so that all the text can be seen.

    Formatting the text is done via a subset of HTML tags. Currently supported tags are:

    - <b></b> or <strong></strong> - to encase bold styled text.
    - <i></i>, <em></em> or <var></var> - to encase italic styled text.
    - <u></u> - to encase underlined text.
    - <a href='id'></a> - to encase 'link' text that can be clicked on to generate events with the
                          id given in href.
    - <body bgcolor='#FFFFFF'></body> - to change the background colour of encased text.
    - <br> - to start a new line.
    - <font face='verdana' color='#000000' size=3.5></font> - To set the font, colour and size of
                                                              encased text.

    More may be added in the future if needed or frequently requested.

    NOTE: if dimensions of the initial containing rect are set to -1 the text box will match the
    final dimension to whatever the text rendering produces. This lets us make dynamically sized
    text boxes depending on their contents.


    :param html_text: The HTML formatted text to display in this text box.
    :param relative_rect: The 'visible area' rectangle, positioned relative to it's container.
    :param manager: The UIManager that manages this element.
    :param wrap_to_height: False by default, if set to True the box will increase in height to
                           match the text within.
    :param layer_starting_height: Sets the height, above it's container, to start placing the text
                                  box at.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(self,
                 html_text: str,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 wrap_to_height: bool = False,
                 layer_starting_height: int = 1,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager, container,
                         starting_height=layer_starting_height,
                         layer_thickness=2,
                         anchors=anchors,
                         visible=visible
                         )

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='text_box')

        self.html_text = html_text
        self.appended_text = ""
        self.font_dict = self.ui_theme.get_font_dictionary()

        self.wrap_to_height = wrap_to_height
        self.link_hover_chunks = []  # container for any link chunks we have

        self.active_text_effect = None
        self.scroll_bar = None
        self.scroll_bar_width = 20

        self.border_width = None
        self.shadow_width = None
        self.padding = (5, 5)
        self.background_colour = None
        self.border_colour = None

        self.link_normal_colour = None
        self.link_hover_colour = None
        self.link_selected_colour = None
        self.link_normal_underline = False
        self.link_hover_underline = True
        self.link_style = None

        self.rounded_corner_offset = None
        self.text_box_layout = None  # TextLine()
        self.text_wrap_rect = None
        self.background_surf = None

        self.drawable_shape = None
        self.shape = 'rectangle'
        self.shape_corner_radius = None

        self.text_horiz_alignment = 'default'
        self.text_vert_alignment = 'default'
        self.text_horiz_alignment_padding = 0
        self.text_vert_alignment_padding = 0

        self.should_trigger_full_rebuild = True
        self.time_until_full_rebuild_after_changing_size = 0.2
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

        self.parser = None

        self.rebuild_from_changed_theme_data()

    def kill(self):
        """
        Overrides the standard sprite kill method to also kill any scroll bars belonging to this
        text box.
        """
        if self.scroll_bar is not None:
            self.scroll_bar.kill()
        super().kill()

    def rebuild(self):
        """
        Rebuild whatever needs building.

        """
        if self.scroll_bar is not None:
            self.scroll_bar.kill()

        # The text_wrap_area is the part of the text box that we try to keep the text inside
        # of so that none  of it overlaps. Essentially we start with the containing box,
        # subtract the border, then subtract the padding, then if necessary subtract the width
        # of the scroll bar
        self.rounded_corner_offset = int(self.shape_corner_radius -
                                         (math.sin(math.pi / 4) *
                                          self.shape_corner_radius))
        self.text_wrap_rect = pygame.Rect((self.rect[0] +
                                           self.padding[0] +
                                           self.border_width +
                                           self.shadow_width +
                                           self.rounded_corner_offset),
                                          (self.rect[1] +
                                           self.padding[1] +
                                           self.border_width +
                                           self.shadow_width +
                                           self.rounded_corner_offset),
                                          max(1, (self.rect[2] -
                                                  (self.padding[0] * 2) -
                                                  (self.border_width * 2) -
                                                  (self.shadow_width * 2) -
                                                  (2 * self.rounded_corner_offset))),
                                          max(1, (self.rect[3] -
                                                  (self.padding[1] * 2) -
                                                  (self.border_width * 2) -
                                                  (self.shadow_width * 2) -
                                                  (2 * self.rounded_corner_offset))))
        if self.wrap_to_height or self.rect[3] == -1:
            self.text_wrap_rect[3] = -1
        if self.rect[2] == -1:
            self.text_wrap_rect[2] = -1

        drawable_area_size = (self.text_wrap_rect[2], self.text_wrap_rect[3])

        # This gives us the height of the text at the 'width' of the text_wrap_area
        self.parse_html_into_style_data()
        if self.text_box_layout is not None:
            if self.wrap_to_height or self.rect[3] == -1 or self.rect[2] == -1:
                final_text_area_size = self.text_box_layout.layout_rect.size
                new_dimensions = ((final_text_area_size[0] + (self.padding[0] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2) +
                                   (2 * self.rounded_corner_offset)),
                                  (final_text_area_size[1] + (self.padding[1] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2) +
                                   (2 * self.rounded_corner_offset)))
                self.set_dimensions(new_dimensions)

                # need to regen this because it was dynamically generated
                drawable_area_size = (max(1, (self.rect[2] -
                                              (self.padding[0] * 2) -
                                              (self.border_width * 2) -
                                              (self.shadow_width * 2) -
                                              (2 * self.rounded_corner_offset))),
                                      max(1, (self.rect[3] -
                                              (self.padding[1] * 2) -
                                              (self.border_width * 2) -
                                              (self.shadow_width * 2) -
                                              (2 * self.rounded_corner_offset))))

            elif self.text_box_layout.layout_rect.height > self.text_wrap_rect[3]:
                # We need a scrollbar because our text is longer than the space we
                # have to display it. This also means we need to parse the text again.
                text_rect_width = (self.rect[2] -
                                   (self.padding[0] * 2) -
                                   (self.border_width * 2) -
                                   (self.shadow_width * 2) -
                                   self.rounded_corner_offset - self.scroll_bar_width)
                self.text_wrap_rect = pygame.Rect((self.rect[0] + self.padding[0] +
                                                   self.border_width + self.shadow_width +
                                                   self.rounded_corner_offset),
                                                  (self.rect[1] + self.padding[1] +
                                                   self.border_width +
                                                   self.shadow_width +
                                                   self.rounded_corner_offset),
                                                  max(1, text_rect_width),
                                                  max(1, (self.rect[3] -
                                                          (self.padding[1] * 2) -
                                                          (self.border_width * 2) -
                                                          (self.shadow_width * 2) -
                                                          (2 * self.rounded_corner_offset))))
                self.parse_html_into_style_data()
                percentage_visible = (self.text_wrap_rect[3] /
                                      self.text_box_layout.layout_rect.height)
                scroll_bar_position = (self.relative_rect.right - self.border_width -
                                       self.shadow_width - self.scroll_bar_width,
                                       self.relative_rect.top + self.border_width +
                                       self.shadow_width)

                scroll_bar_rect = pygame.Rect(scroll_bar_position,
                                              (self.scroll_bar_width,
                                               self.rect.height -
                                               (2 * self.border_width) -
                                               (2 * self.shadow_width)))
                self.scroll_bar = UIVerticalScrollBar(scroll_bar_rect,
                                                      percentage_visible,
                                                      self.ui_manager,
                                                      self.ui_container,
                                                      parent_element=self,
                                                      visible=self.visible)
                self.join_focus_sets(self.scroll_bar)
            else:
                new_dimensions = (self.rect[2], self.rect[3])
                self.set_dimensions(new_dimensions)

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.background_surf = self.drawable_shape.get_fresh_surface()

        if self.scroll_bar is not None:
            height_adjustment = int(self.scroll_bar.start_percentage *
                                    self.text_box_layout.layout_rect.height)
        else:
            height_adjustment = 0

        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        drawable_area = pygame.Rect((0, height_adjustment),
                                    drawable_area_size)
        new_image = pygame.surface.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
        new_image.fill(pygame.Color(0, 0, 0, 0))
        basic_blit(new_image, self.background_surf, (0, 0))

        basic_blit(new_image, self.text_box_layout.finalised_surface,
                   (self.padding[0] + self.border_width +
                    self.shadow_width + self.rounded_corner_offset,
                    self.padding[1] + self.border_width +
                    self.shadow_width + self.rounded_corner_offset),
                   drawable_area)

        self.set_image(new_image)
        self.link_hover_chunks = []
        self.text_box_layout.add_chunks_to_hover_group(self.link_hover_chunks)

        self.should_trigger_full_rebuild = False
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def _align_all_text_rows(self):
        """
        Aligns the text drawing position correctly according to our theming options.

        """
        # Horizontal alignment
        if self.text_horiz_alignment != 'default':
            if self.text_horiz_alignment == 'center':
                self.text_box_layout.horiz_center_all_rows()
            elif self.text_horiz_alignment == 'left':
                self.text_box_layout.align_left_all_rows(self.text_horiz_alignment_padding)
            else:
                self.text_box_layout.align_right_all_rows(self.text_horiz_alignment_padding)

        # Vertical alignment
        if self.text_vert_alignment != 'default':
            if self.text_vert_alignment == 'center':
                self.text_box_layout.vert_center_all_rows()
            elif self.text_vert_alignment == 'top':
                self.text_box_layout.vert_align_top_all_rows(self.text_vert_alignment_padding)
            else:
                self.text_box_layout.vert_align_bottom_all_rows(self.text_vert_alignment_padding)

    def update(self, time_delta: float):
        """
        Called once every update loop of the UI Manager. Used to react to scroll bar movement
        (if there is one), update the text effect (if there is one) and check if we are hovering
        over any text links (if there are any).

        :param time_delta: The time in seconds between calls to update. Useful for timing things.

        """
        super().update(time_delta)
        if not self.alive():
            return
        if self.scroll_bar is not None and self.scroll_bar.check_has_moved_recently():
            height_adjustment = int(self.scroll_bar.start_percentage *
                                    self.text_box_layout.layout_rect.height)

            drawable_area_size = (max(1, (self.rect[2] -
                                          (self.padding[0] * 2) -
                                          (self.border_width * 2) -
                                          (self.shadow_width * 2) -
                                          (2 * self.rounded_corner_offset))),
                                  max(1, (self.rect[3] -
                                          (self.padding[1] * 2) -
                                          (self.border_width * 2) -
                                          (self.shadow_width * 2) -
                                          (2 * self.rounded_corner_offset))))
            drawable_area = pygame.Rect((0, height_adjustment),
                                        drawable_area_size)

            if self.rect.width <= 0 or self.rect.height <= 0:
                return

            new_image = pygame.surface.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
            new_image.fill(pygame.Color(0, 0, 0, 0))
            basic_blit(new_image, self.background_surf, (0, 0))
            basic_blit(new_image, self.text_box_layout.finalised_surface,
                       (self.padding[0] + self.border_width +
                        self.shadow_width +
                        self.rounded_corner_offset,
                        self.padding[1] + self.border_width +
                        self.shadow_width +
                        self.rounded_corner_offset),
                       drawable_area)
            self.set_image(new_image)

        mouse_x, mouse_y = self.ui_manager.get_mouse_position()
        should_redraw_from_chunks = False

        if self.scroll_bar is not None:
            height_adjustment = (self.scroll_bar.start_percentage *
                                 self.text_box_layout.layout_rect.height)
        else:
            height_adjustment = 0
        base_x = int(self.rect[0] + self.padding[0] + self.border_width +
                     self.shadow_width + self.rounded_corner_offset)
        base_y = int(self.rect[1] + self.padding[1] + self.border_width +
                     self.shadow_width + self.rounded_corner_offset - height_adjustment)

        for chunk in self.link_hover_chunks:
            hovered_currently = False

            hover_rect = pygame.Rect((base_x + chunk.x,
                                      base_y + chunk.y),
                                     chunk.size)
            if hover_rect.collidepoint(mouse_x, mouse_y) and self.rect.collidepoint(mouse_x,
                                                                                    mouse_y):
                hovered_currently = True
            if chunk.is_hovered and not hovered_currently:
                chunk.on_unhovered()
                should_redraw_from_chunks = True
            elif hovered_currently and not chunk.is_hovered:
                chunk.on_hovered()
                should_redraw_from_chunks = True

        if should_redraw_from_chunks:
            self.redraw_from_chunks()

        if self.active_text_effect is not None:
            self.active_text_effect.update(time_delta)
            if self.active_text_effect.has_text_block_changed():
                self.redraw_from_text_block()

        if self.should_trigger_full_rebuild and self.full_rebuild_countdown <= 0.0:
            self.rebuild()

        if self.full_rebuild_countdown > 0.0:
            self.full_rebuild_countdown -= time_delta

    def on_fresh_drawable_shape_ready(self):
        """
        Called by an element's drawable shape when it has a new image surface ready for use,
        normally after a rebuilding/redrawing of some kind.
        """
        self.background_surf = self.drawable_shape.get_fresh_surface()
        self.redraw_from_text_block()

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Sets the relative screen position of this text box, updating it's subordinate scroll bar at
        the same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)

        if self.scroll_bar is not None:
            scroll_bar_position = (self.relative_rect.right - self.border_width -
                                   self.shadow_width - self.scroll_bar_width,
                                   self.relative_rect.top + self.border_width +
                                   self.shadow_width)
            self.scroll_bar.set_relative_position(scroll_bar_position)

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this text box, updating it's subordinate scroll bar
        at the same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)

        if self.scroll_bar is not None:
            scroll_bar_position = (self.relative_rect.right - self.border_width -
                                   self.shadow_width - self.scroll_bar_width,
                                   self.relative_rect.top + self.border_width +
                                   self.shadow_width)
            self.scroll_bar.set_relative_position(scroll_bar_position)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Method to directly set the dimensions of a text box.

        :param dimensions: The new dimensions to set.

        """
        self.relative_rect.width = int(dimensions[0])
        self.relative_rect.height = int(dimensions[1])
        self.rect.size = self.relative_rect.size

        if dimensions[0] >= 0 and dimensions[1] >= 0:
            if self.relative_right_margin is not None:
                self.relative_right_margin = self.ui_container.rect.right - self.rect.right

            if self.relative_bottom_margin is not None:
                self.relative_bottom_margin = self.ui_container.rect.bottom - self.rect.bottom

            self._update_container_clip()

            # Quick and dirty temporary scaling to cut down on number of
            # full rebuilds triggered when rapid scaling
            if self.image is not None:
                if (self.full_rebuild_countdown > 0.0 and
                        (self.relative_rect.width > 0 and
                         self.relative_rect.height > 0)):
                    new_image = pygame.surface.Surface(self.relative_rect.size,
                                                       flags=pygame.SRCALPHA,
                                                       depth=32)
                    new_image.fill(pygame.Color('#00000000'))
                    basic_blit(new_image, self.image, (0, 0))
                    self.set_image(new_image)

                    if self.scroll_bar is not None:
                        self.scroll_bar.set_dimensions((self.scroll_bar.relative_rect.width,
                                                        self.relative_rect.height -
                                                        (2 * self.border_width) -
                                                        (2 * self.shadow_width)))
                        scroll_bar_position = (self.relative_rect.right - self.border_width -
                                               self.shadow_width - self.scroll_bar_width,
                                               self.relative_rect.top + self.border_width +
                                               self.shadow_width)
                        self.scroll_bar.set_relative_position(scroll_bar_position)

                self.should_trigger_full_rebuild = True
                self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.freetype
        rendered text.
        """

        # parser.push_style('body', {"bg_colour": self.background_colour})
        self.parser.feed(translate(self.html_text) + self.appended_text)

        self.text_box_layout = TextBoxLayout(self.parser.layout_rect_queue,
                                             pygame.Rect((0, 0), (self.text_wrap_rect[2],
                                                                  self.text_wrap_rect[3])),
                                             pygame.Rect((0, 0), (self.text_wrap_rect[2],
                                                                  self.text_wrap_rect[3])),
                                             line_spacing=1.25)
        self.parser.empty_layout_queue()
        if self.text_wrap_rect[3] == -1:
            self.text_box_layout.view_rect.height = self.text_box_layout.layout_rect.height

        self._align_all_text_rows()
        self.text_box_layout.finalise_to_new()

        # self.formatted_text_block = TextBlock(parser.text_data,
        #                                       self.text_wrap_rect,
        #                                       parser.indexed_styles,
        #                                       self.font_dict,
        #                                       self.link_style,
        #                                       self.background_colour,
        #                                       self.wrap_to_height
        #                                       )

    def redraw_from_text_block(self):
        """
        Redraws the final parts of the text box element that don't include redrawing the actual
        text. Useful if we've just moved the position of the text (say, with a scroll bar)
        without actually changing the text itself.
        """
        if self.rect.width <= 0 or self.rect.height <= 0:
            return
        if self.scroll_bar is not None:
            height_adjustment = int(self.scroll_bar.start_percentage *
                                    self.text_box_layout.layout_rect.height)
            percentage_visible = (self.text_wrap_rect[3] /
                                  self.text_box_layout.layout_rect.height)
            self.scroll_bar.set_visible_percentage(percentage_visible)
        else:
            height_adjustment = 0
        drawable_area_size = (max(1, (self.rect[2] -
                                      (self.padding[0] * 2) -
                                      (self.border_width * 2) -
                                      (self.shadow_width * 2) -
                                      (2 * self.rounded_corner_offset))),
                              max(1, (self.rect[3] -
                                      (self.padding[1] * 2) -
                                      (self.border_width * 2) -
                                      (self.shadow_width * 2) -
                                      (2 * self.rounded_corner_offset))))
        drawable_area = pygame.Rect((0, height_adjustment),
                                    drawable_area_size)
        new_image = pygame.surface.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
        new_image.fill(pygame.Color(0, 0, 0, 0))
        basic_blit(new_image, self.background_surf, (0, 0))
        basic_blit(new_image, self.text_box_layout.finalised_surface,
                   (self.padding[0] + self.border_width +
                    self.shadow_width + self.rounded_corner_offset,
                    self.padding[1] + self.border_width +
                    self.shadow_width + self.rounded_corner_offset),
                   drawable_area)
        self.set_image(new_image)

    def redraw_from_chunks(self):
        """
        Redraws from slightly earlier in the process than 'redraw_from_text_block'. Useful if we
        have redrawn individual chunks already (say, to change their style slightly after being
        hovered) and now want to update the text block with those changes without doing a
        full redraw.

        This won't work very well if redrawing a chunk changed it's dimensions.
        """
        self.text_box_layout.finalise_to_new()
        self.redraw_from_text_block()

    def full_redraw(self):
        """
        Trigger a full redraw of the entire text box. Useful if we have messed with the text
        chunks in a more fundamental fashion and need to reposition them (say, if some of them
        have gotten wider after being made bold).

        NOTE: This doesn't re-parse the text of our box. If you need to do that, just create a
        new text box.

        """
        self.text_box_layout.reprocess_layout_queue(pygame.Rect((0, 0),
                                                                (self.text_wrap_rect[2],
                                                                 self.text_wrap_rect[3])))
        self.text_box_layout.finalise_to_new()
        self.redraw_from_text_block()
        self.link_hover_chunks = []
        self.text_box_layout.add_chunks_to_hover_group(self.link_hover_chunks)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Deals with input events. In this case we just handle clicks on any links in the text.

        :param event: A pygame event to check for a reaction to.

        :return: Returns True if we consumed this event.

        """
        consumed_event = False
        should_redraw_from_chunks = False
        should_full_redraw = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                consumed_event = True

                if self.is_enabled:
                    if self.scroll_bar is not None:
                        text_block_full_height = self.text_box_layout.layout_rect.height
                        height_adjustment = (self.scroll_bar.start_percentage *
                                             text_block_full_height)
                    else:
                        height_adjustment = 0
                    base_x = int(self.rect[0] + self.padding[0] + self.border_width +
                                 self.shadow_width + self.rounded_corner_offset)
                    base_y = int(self.rect[1] + self.padding[1] + self.border_width +
                                 self.shadow_width + self.rounded_corner_offset - height_adjustment)
                    for chunk in self.link_hover_chunks:

                        hover_rect = pygame.Rect((base_x + chunk.x,
                                                  base_y + chunk.y),
                                                 chunk.size)
                        if hover_rect.collidepoint(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                            consumed_event = True
                            if not chunk.is_active:
                                chunk.set_active()
                                # if chunk.metrics_changed_after_redraw:
                                #     should_full_redraw = True
                                # else:
                                should_redraw_from_chunks = True

        if self.is_enabled and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.scroll_bar is not None:
                height_adjustment = (self.scroll_bar.start_percentage *
                                     self.text_box_layout.layout_rect.height)
            else:
                height_adjustment = 0
            base_x = int(self.rect[0] + self.padding[0] + self.border_width +
                         self.shadow_width + self.rounded_corner_offset)
            base_y = int(self.rect[1] + self.padding[1] + self.border_width +
                         self.shadow_width + self.rounded_corner_offset - height_adjustment)
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            for chunk in self.link_hover_chunks:

                hover_rect = pygame.Rect((base_x + chunk.x,
                                          base_y + chunk.y),
                                         chunk.size)
                if (hover_rect.collidepoint(scaled_mouse_pos[0], scaled_mouse_pos[1]) and
                        self.rect.collidepoint(scaled_mouse_pos[0], scaled_mouse_pos[1])):
                    consumed_event = True
                    if chunk.is_active:

                        # old event - to be removed in 0.8.0
                        event_data = {'user_type': OldType(UI_TEXT_BOX_LINK_CLICKED),
                                      'link_target': chunk.href,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                        # new event
                        event_data = {'link_target': chunk.href,
                                      'ui_element': self,
                                      'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(pygame.event.Event(UI_TEXT_BOX_LINK_CLICKED, event_data))

                if chunk.is_active:
                    chunk.set_inactive()
                    # if chunk.metrics_changed_after_redraw:
                    #     should_full_redraw = True
                    # else:
                    should_redraw_from_chunks = True

        if should_redraw_from_chunks:
            self.redraw_from_chunks()

        if should_full_redraw:
            self.full_redraw()

        return consumed_event

    def set_active_effect(self, effect_name: Union[str, None]):
        """
        Set an animation effect to run on the text box. The effect will start running immediately
        after this call.

        These effects are currently supported:

        - 'typing_appear' - Will look as if the text is being typed in.
        - 'fade_in' - The text will fade in from the background colour (Only supported on Pygame 2)
        - 'fade_out' - The text will fade out to the background colour (only supported on Pygame 2)

        :param effect_name: The name fo the t to set. If set to None instead it will cancel any
                            active effect.

        """
        if effect_name is None:
            self.active_text_effect = None
        elif isinstance(effect_name, str):
            if effect_name == TEXT_EFFECT_TYPING_APPEAR:
                effect = TypingAppearEffect(self.text_box_layout)
                self.active_text_effect = effect
            elif effect_name == TEXT_EFFECT_FADE_IN:
                effect = FadeInEffect(self.text_box_layout)
                self.active_text_effect = effect
            elif effect_name == TEXT_EFFECT_FADE_OUT:
                effect = FadeOutEffect(self.text_box_layout)
                self.active_text_effect = effect
            else:
                warnings.warn('Unsupported effect name: ' + effect_name + ' for text box')

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        # misc parameters
        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle']):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        def tuple_extract(str_data: str) -> Tuple[int, int]:
            return int(str_data.split(',')[0]), int(str_data.split(',')[1])

        if self._check_misc_theme_data_changed(attribute_name='padding',
                                               default_value=(5, 5),
                                               casting_func=tuple_extract):
            has_any_changed = True

        # colour parameters
        background_colour = self.ui_theme.get_colour_or_gradient('dark_bg',
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient('normal_border',
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        if self._check_text_alignment_theming():
            has_any_changed = True

        if self._check_link_style_changed():
            has_any_changed = True

        if has_any_changed:
            self.parser = HTMLParser(self.ui_theme, self.combined_element_ids,
                                     self.link_style, line_spacing=1.25)
            self.rebuild()

    def _check_text_alignment_theming(self) -> bool:
        """
        Checks for any changes in the theming data related to text alignment.

        :return: True if changes found.

        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment',
                                               default_value='left',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment',
                                               default_value='top',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        return has_any_changed

    def _check_link_style_changed(self) -> bool:
        """
        Checks for any changes in hyper link related styling in the theme data.

        :return: True if changes detected.

        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='link_normal_underline',
                                               default_value=True,
                                               casting_func=bool):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='link_hover_underline',
                                               default_value=True,
                                               casting_func=bool):
            has_any_changed = True

        link_normal_colour = self.ui_theme.get_colour_or_gradient('link_text',
                                                                  self.combined_element_ids)
        if link_normal_colour != self.link_normal_colour:
            self.link_normal_colour = link_normal_colour
        link_hover_colour = self.ui_theme.get_colour_or_gradient('link_hover',
                                                                 self.combined_element_ids)
        if link_hover_colour != self.link_hover_colour:
            self.link_hover_colour = link_hover_colour
        link_selected_colour = self.ui_theme.get_colour_or_gradient('link_selected',
                                                                    self.combined_element_ids)
        if link_selected_colour != self.link_selected_colour:
            self.link_selected_colour = link_selected_colour
        link_style = {'link_text': self.link_normal_colour,
                      'link_hover': self.link_hover_colour,
                      'link_selected': self.link_selected_colour,
                      'link_normal_underline': self.link_normal_underline,
                      'link_hover_underline': self.link_hover_underline}
        if link_style != self.link_style:
            self.link_style = link_style
            has_any_changed = True
        return has_any_changed

    def disable(self):
        """
        Disable the text box. Basically just disables the scroll bar if one exists.
        """
        if self.is_enabled:
            self.is_enabled = False
            if self.scroll_bar:
                self.scroll_bar.disable()

    def enable(self):
        """
        Enable the text box. Renables the scroll bar if one exists.
        """
        if not self.is_enabled:
            self.is_enabled = True
            if self.scroll_bar:
                self.scroll_bar.enable()

    def show(self):
        """
        In addition to the base UIElement.show() - call show() of scroll_bar if it exists.
        """
        super().show()

        if self.scroll_bar is not None:
            self.scroll_bar.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - call hide() of scroll_bar if it exists.
        """
        super().hide()

        if self.scroll_bar is not None:
            self.scroll_bar.hide()

    def append_html_text(self, new_html_str: str):
        """
        Adds a string, that is parsed for any HTML tags that pygame_gui supports, onto the bottom
        of the text box's current contents.

        This is useful for making things like logs.

        :param new_html_str: The, potentially HTML tag, containing string of text to append.
        """
        self.appended_text += new_html_str
        self.parser.feed(new_html_str)
        self.text_box_layout.append_layout_rects(self.parser.layout_rect_queue)
        self.parser.empty_layout_queue()

        if (self.scroll_bar is None and
                (self.text_box_layout.layout_rect.height > self.text_wrap_rect[3])):
            self.rebuild()
        else:
            if self.scroll_bar is not None:
                # set the scroll bar to the bottom
                percentage_visible = (self.text_wrap_rect[3] /
                                      self.text_box_layout.layout_rect.height)
                self.scroll_bar.start_percentage = 1.0 - percentage_visible
                self.scroll_bar.scroll_position = (self.scroll_bar.start_percentage *
                                                   self.scroll_bar.scrollable_height)
            self.redraw_from_text_block()

    def on_locale_changed(self):
        self.rebuild()