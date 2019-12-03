import pygame
import warnings
import math

from typing import Union, Tuple

import pygame_gui
from pygame_gui import ui_manager
from pygame_gui.core import ui_container
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar

from pygame_gui.elements.text.html_parser import TextHTMLParser
from pygame_gui.elements.text.text_effects import TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.ui_appearance_theme import ColourGradient


class UITextBox(UIElement):
    """
    A Text Box element lets us display word-wrapped, formatted text. If the text to display is longer than the height
    of the box given then the element will automatically create a vertical scroll bar so that all the text can be seen.

    Formatting the text is done via a subset of HTML tags. Currently supported tags are:

    - <b></b> or <strong></strong> - to encase bold styled text.
    - <i></i>, <em></em> or <var></var> - to encase italic styled text.
    - <u></u> - to encase underlined text.
    - <a href='id'></a> - to encase 'link' text that can be clicked on to generate events with the id given in href.
    - <body bgcolor='#FFFFFF'></body> - to change the background colour of encased text.
    - <br> - to start a new line.
    - <font face='verdana' color='#000000' size=3.5></font> - To set the font, colour and size of encased text.

    More may be added in the future if needed or frequently requested.

    NOTE: if dimensions of the initial containing rect are set to -1 the text box will match the final dimension to
    whatever the text rendering produces. This lets us make dynamically sized text boxes depending on their contents.


    :param html_text: The HTML formatted text to display in this text box.
    :param relative_rect: The 'visible area' rectangle, positioned relative to it's container.
    :param manager: The UIManager that manages this element.
    :param wrap_to_height: False by default, if set to True the box will increase in height to match the text within.
    :param layer_starting_height: Sets the height, above it's container, to start placing the text box at.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """

    def __init__(self, html_text: str,
                 relative_rect: pygame.Rect,
                 manager: ui_manager.UIManager,
                 wrap_to_height: bool = False,
                 layer_starting_height: int = 1,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='text_box')
        super().__init__(relative_rect, manager, container,
                         starting_height=layer_starting_height,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids
                         )
        self.html_text = html_text
        self.font_dict = self.ui_theme.get_font_dictionary()

        self.wrap_to_height = wrap_to_height
        self.link_hover_chunks = []  # container for any link chunks we have

        self.active_text_effect = None
        self.scroll_bar = None
        self.scroll_bar_width = 20

        self.border_width = None
        self.shadow_width = None
        self.padding = None
        self.background_colour = None
        self.border_colour = None

        self.link_normal_colour = None
        self.link_hover_colour = None
        self.link_selected_colour = None
        self.link_normal_underline = False
        self.link_hover_underline = True
        self.link_style = None

        self.rounded_corner_offset = None
        self.formatted_text_block = None  # TextLine()
        self.text_wrap_rect = None
        self.background_surf = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        self.rebuild_from_changed_theme_data()

    def rebuild(self):
        """
        Rebuild whatever needs building.

        """
        ''' The text_wrap_area is the part of the text box that we try to keep the text inside of so that none 
            of it overlaps. Essentially we start with the containing box, subtract the border,  then subtract 
            the padding, then if necessary subtract the width of the scroll bar'''
        self.rounded_corner_offset = int(self.shape_corner_radius - (math.sin(math.pi / 4) * self.shape_corner_radius))
        self.text_wrap_rect = [(self.rect[0] + self.padding[0] + self.border_width +
                                self.shadow_width + self.rounded_corner_offset),
                               (self.rect[1] + self.padding[1] + self.border_width +
                                self.shadow_width + self.rounded_corner_offset),
                               (self.rect[2] - (self.padding[0] * 2) - (self.border_width * 2) -
                                (self.shadow_width * 2) - (2 * self.rounded_corner_offset)),
                               (self.rect[3] - (self.padding[1] * 2) - (self.border_width * 2) -
                                (self.shadow_width * 2) - (2 * self.rounded_corner_offset))]
        if self.rect[3] == -1:
            self.text_wrap_rect[3] = -1

        self.parse_html_into_style_data()  # This gives us the height of the text at the 'width' of the text_wrap_area
        if self.formatted_text_block is not None:
            if self.wrap_to_height or self.rect[3] == -1:
                final_text_area_size = self.formatted_text_block.final_dimensions
                self.rect.size = [(final_text_area_size[0] + (self.padding[0] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2) +
                                   (2 * self.rounded_corner_offset)),
                                  (final_text_area_size[1] + (self.padding[1] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2) +
                                   (2 * self.rounded_corner_offset))]

            elif self.formatted_text_block.final_dimensions[1] > self.text_wrap_rect[3]:
                # We need a scrollbar because our text is longer than the space we have to display it.
                # this also means we need to parse the text again.
                text_rect_width = (self.rect[2] - (self.padding[0] * 2) - (self.border_width * 2) -
                                   (self.shadow_width * 2) - self.rounded_corner_offset - self.scroll_bar_width)
                self.text_wrap_rect = [(self.rect[0] + self.padding[0] + self.border_width +
                                        self.shadow_width + self.rounded_corner_offset),
                                       (self.rect[1] + self.padding[1] + self.border_width +
                                        self.shadow_width + self.rounded_corner_offset),
                                       text_rect_width,
                                       (self.rect[3] - (self.padding[1] * 2) - (self.border_width * 2) -
                                        (self.shadow_width * 2) - (2 * self.rounded_corner_offset))]
                self.parse_html_into_style_data()
                percentage_visible = self.text_wrap_rect[3] / self.formatted_text_block.final_dimensions[1]
                scroll_bar_position = (self.relative_rect.right - self.border_width -
                                       self.shadow_width - self.scroll_bar_width,
                                       self.relative_rect.top + self.border_width +
                                       self.shadow_width)

                if self.scroll_bar is not None:
                    self.scroll_bar.kill()
                self.scroll_bar = UIVerticalScrollBar(pygame.Rect(scroll_bar_position,
                                                                  (self.scroll_bar_width,
                                                                   self.rect.height - (2 * self.border_width) -
                                                                   (2 * self.shadow_width))),
                                                      percentage_visible,
                                                      self.ui_manager,
                                                      self.ui_container,
                                                      parent_element=self)
            else:
                self.rect.size = [self.rect[2], self.rect[3]]

        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.background_surf = self.drawable_shape.get_surface('normal')

        if self.scroll_bar is not None:
            height_adjustment = int(self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1])
        else:
            height_adjustment = 0

        drawable_area = pygame.Rect((0, height_adjustment), (self.text_wrap_rect[2], self.text_wrap_rect[3]))
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
        self.image.fill(pygame.Color(0, 0, 0, 0))
        self.image.blit(self.background_surf, (0, 0))
        self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                 self.shadow_width + self.rounded_corner_offset,
                                                                 self.padding[1] + self.border_width +
                                                                 self.shadow_width + self.rounded_corner_offset),
                        drawable_area)

        self.formatted_text_block.add_chunks_to_hover_group(self.link_hover_chunks)

    def update(self, time_delta: float):
        """
        Called once every update loop of the UI Manager. Used to react to scroll bar movement (if there is one),
        update the text effect (if there is one) and check if we are hovering over any text links (if there are any).

        :param time_delta: The time in seconds between calls to update. Useful for timing things.
        """
        if self.alive():
            if self.scroll_bar is not None:
                if self.scroll_bar.check_has_moved_recently():
                    height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
                    drawable_area = pygame.Rect((0, height_adjustment),
                                                (self.text_wrap_rect[2], self.text_wrap_rect[3]))
                    self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
                    self.image.fill(pygame.Color(0, 0, 0, 0))
                    self.image.blit(self.background_surf, (0, 0))
                    self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                             self.shadow_width +
                                                                             self.rounded_corner_offset,
                                                                             self.padding[1] + self.border_width +
                                                                             self.shadow_width +
                                                                             self.rounded_corner_offset),
                                    drawable_area)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            should_redraw_from_chunks = False

            if self.scroll_bar is not None:
                height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
            else:
                height_adjustment = 0
            base_x = int(self.rect[0] + self.padding[0] + self.border_width +
                      self.shadow_width + self.rounded_corner_offset)
            base_y = int(self.rect[1] + self.padding[1] + self.border_width +
                      self.shadow_width + self.rounded_corner_offset - height_adjustment)

            for chunk in self.link_hover_chunks:
                hovered_currently = False

                hover_rect = pygame.Rect((base_x + chunk.rect.x,
                                          base_y + chunk.rect.y),
                                         chunk.rect.size)
                if hover_rect.collidepoint(mouse_x, mouse_y):
                    if self.rect.collidepoint(mouse_x, mouse_y):
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
                if self.active_text_effect.should_full_redraw():
                    self.full_redraw()
                if self.active_text_effect.should_redraw_from_chunks():
                    self.redraw_from_chunks()

    def update_containing_rect_position(self):
        """
        Sets the final screen position of this element based on the position of it's container and it's relative
        position inside that container.
        """
        self.rect = pygame.Rect((self.ui_container.rect.x + self.relative_rect.x,
                                 self.ui_container.rect.y + self.relative_rect.y),
                                self.relative_rect.size)

        # for chunk in self.link_hover_chunks:
        #     chunk.rect = pygame.Rect((self.ui_container.rect.x + self.relative_rect.x + chunk.rect.x,
        #                               self.ui_container.rect.y + self.relative_rect.y + chunk.rect.y),
        #                              chunk.rect.size)

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_relative_position(position)

        if self.scroll_bar is not None:
            scroll_bar_position = (self.relative_rect.right - self.border_width -
                                   self.shadow_width - self.scroll_bar_width,
                                   self.relative_rect.top + self.border_width +
                                   self.shadow_width)
            self.scroll_bar.set_relative_position(scroll_bar_position)

    def set_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        super().set_position(position)

        if self.scroll_bar is not None:
            scroll_bar_position = (self.relative_rect.right - self.border_width -
                                   self.shadow_width - self.scroll_bar_width,
                                   self.relative_rect.top + self.border_width +
                                   self.shadow_width)
            self.scroll_bar.set_relative_position(scroll_bar_position)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        self.rect.width = dimensions[0]
        self.rect.height = dimensions[1]
        self.relative_rect.width = dimensions[0]
        self.relative_rect.height = dimensions[1]

        self.rebuild()

    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.font rendered text.
        """
        parser = TextHTMLParser(self.ui_theme, self.element_ids, self.object_ids)
        parser.push_style('body', {"bg_color": self.background_colour})
        parser.feed(self.html_text)

        self.formatted_text_block = TextBlock(parser.text_data,
                                              self.text_wrap_rect,
                                              parser.indexed_styles,
                                              self.font_dict,
                                              self.link_style,
                                              self.background_colour,
                                              self.wrap_to_height
                                              )

    def redraw_from_text_block(self):
        """
        Redraws the final parts of the text box element that don't include redrawing the actual text. Useful if we've
        just moved the position of the text (say, with a scroll bar) without actually changing the text itself.
        """
        if self.scroll_bar is not None:
            height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
        else:
            height_adjustment = 0

        drawable_area = pygame.Rect((0, height_adjustment), (self.text_wrap_rect[2], self.text_wrap_rect[3]))
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA, depth=32)
        self.image.fill(pygame.Color(0, 0, 0, 0))
        self.image.blit(self.background_surf, (0, 0))
        self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                 self.shadow_width + self.rounded_corner_offset,
                                                                 self.padding[1] + self.border_width +
                                                                 self.shadow_width + self.rounded_corner_offset),
                        drawable_area)

    def redraw_from_chunks(self):
        """
        Redraws from slightly earlier in the process than 'redraw_from_text_block'. Useful if we have redrawn
        individual chunks already (say, to change their style slightly after being hovered) and now want to update the
        text block with those changes without doing a full redraw.

        This won't work very well if redrawing a chunk changed it's dimensions.
        """
        self.formatted_text_block.redraw_from_chunks(self.active_text_effect)
        self.redraw_from_text_block()

    def full_redraw(self):
        """
        Trigger a full redraw of the entire text box. Useful if we have messed with the text chunks in a more
        fundamental fashion and need to reposition them (say, if some of them have gotten wider after being made bold).

        NOTE: This doesn't re-parse the text of our box. If you need to do that, just create a new text box.

        """
        self.formatted_text_block.redraw(self.active_text_effect)
        self.redraw_from_text_block()
        self.link_hover_chunks = []
        self.formatted_text_block.add_chunks_to_hover_group(self.link_hover_chunks)

    def select(self):
        """
        Called when we focus select the text box (usually by clicking on it). In this case we just pass the focus over
        to the box's scroll bar, if it has one, so that some input events will be directed that way.
        """
        if self.scroll_bar is not None:
            self.scroll_bar.select()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Deals with input events. In this case we just handle clicks on any links in the text.

        :param event: A pygame event to check for a reaction to.
        :return bool: Returns True if we made use of this event.
        """
        processed_event = False
        should_redraw_from_chunks = False
        should_full_redraw = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    processed_event = True
                    if self.scroll_bar is not None:
                        text_block_full_height = self.formatted_text_block.final_dimensions[1]
                        height_adjustment = self.scroll_bar.start_percentage * text_block_full_height
                    else:
                        height_adjustment = 0
                    base_x = (self.rect[0] + self.padding[0] + self.border_width +
                              self.shadow_width + self.rounded_corner_offset)
                    base_y = (self.rect[1] + self.padding[1] + self.border_width +
                              self.shadow_width + self.rounded_corner_offset - height_adjustment)
                    for chunk in self.link_hover_chunks:

                        hover_rect = pygame.Rect((base_x + chunk.rect.x,
                                                  base_y + chunk.rect.y),
                                                 chunk.rect.size)
                        if hover_rect.collidepoint(mouse_x, mouse_y):
                            processed_event = True
                            if not chunk.is_selected:
                                chunk.on_selected()
                                if chunk.metrics_changed_after_redraw:
                                    should_full_redraw = True
                                else:
                                    should_redraw_from_chunks = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.scroll_bar is not None:
                    height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
                else:
                    height_adjustment = 0
                base_x = (self.rect[0] + self.padding[0] + self.border_width +
                          self.shadow_width + self.rounded_corner_offset)
                base_y = (self.rect[1] + self.padding[1] + self.border_width +
                          self.shadow_width + self.rounded_corner_offset - height_adjustment)
                mouse_x, mouse_y = event.pos
                for chunk in self.link_hover_chunks:

                    hover_rect = pygame.Rect((base_x + chunk.rect.x,
                                              base_y + chunk.rect.y),
                                             chunk.rect.size)
                    if hover_rect.collidepoint(mouse_x, mouse_y):
                        if self.rect.collidepoint(mouse_x, mouse_y):
                            processed_event = True
                            if chunk.is_selected:
                                link_clicked_event = pygame.event.Event(pygame.USEREVENT,
                                                                        {'user_type':
                                                                         pygame_gui.UI_TEXT_BOX_LINK_CLICKED,
                                                                         'link_target': chunk.link_href,
                                                                         'ui_element': self,
                                                                         'ui_object_id': self.object_ids[-1]})
                                pygame.event.post(link_clicked_event)

                    if chunk.is_selected:
                        chunk.on_unselected()
                        if chunk.metrics_changed_after_redraw:
                            should_full_redraw = True
                        else:
                            should_redraw_from_chunks = True

        if should_redraw_from_chunks:
            self.redraw_from_chunks()

        if should_full_redraw:
            self.full_redraw()

        return processed_event

    def set_active_effect(self, effect_name: Union[str, None]):
        """
        Set an animation effect to run on the text box. The effect will start running immediately after this call.

        These effects are currently supported:

        - 'typing_appear' - Will look as if the text is being typed in.
        - 'fade_in' - The text will fade in from the background colour (Only supported on Pygame 2)
        - 'fade_out' - The text will fade out to the background colour (only supported on Pygame 2)

        :param effect_name: The name fo the t to set. If set to None instead it will cancel any active effect.
        """
        if effect_name is None:
            self.active_text_effect = None
        elif type(effect_name) is str:
            if effect_name == pygame_gui.TEXT_EFFECT_TYPING_APPEAR:
                effect = TypingAppearEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.full_redraw()
            elif effect_name == pygame_gui.TEXT_EFFECT_FADE_IN:
                effect = FadeInEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.redraw_from_chunks()
            elif effect_name == pygame_gui.TEXT_EFFECT_FADE_OUT:
                effect = FadeOutEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.redraw_from_chunks()
            else:
                warnings.warn('Unsupported effect name: ' + effect_name + ' for text box')

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for this element when
        the theme data has changed.
        """
        has_any_changed = False

        # misc parameters
        shape_type = 'rectangle'
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if shape_type_string is not None:
            if shape_type_string in ['rectangle', 'rounded_rectangle']:
                shape_type = shape_type_string
        if shape_type != self.shape_type:
            self.shape_type = shape_type
            has_any_changed = True

        corner_radius = 2
        shape_corner_radius_string = self.ui_theme.get_misc_data(self.object_ids,
                                                                 self.element_ids, 'shape_corner_radius')
        if shape_corner_radius_string is not None:
            try:
                corner_radius = int(shape_corner_radius_string)
            except ValueError:
                corner_radius = 2
        if corner_radius != self.shape_corner_radius:
            self.shape_corner_radius = corner_radius
            has_any_changed = True

        border_width = 0
        border_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_string is not None:
            try:
                border_width = int(border_width_string)
            except ValueError:
                border_width = 0

        if border_width != self.border_width:
            self.border_width = border_width
            has_any_changed = True

        shadow_width = 0
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            try:
                shadow_width = int(shadow_width_string)
            except ValueError:
                shadow_width = 0
        if shadow_width != self.shadow_width:
            self.shadow_width = shadow_width
            has_any_changed = True

        padding = (10, 10)
        padding_str = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'padding')
        if padding_str is not None:
            try:
                padding = (int(padding_str.split(',')[0]), int(padding_str.split(',')[1]))
            except ValueError:
                padding = (10, 10)
        if padding != self.padding:
            self.padding = padding
            has_any_changed = True

        # colour parameters
        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        # link styles
        link_normal_underline = True
        link_normal_underline_string = self.ui_theme.get_misc_data(self.object_ids,
                                                                   self.element_ids, 'link_normal_underline')
        if link_normal_underline_string is not None:
            try:
                link_normal_underline = bool(int(link_normal_underline_string))
            except ValueError:
                link_normal_underline = True
        if link_normal_underline != self.link_normal_underline:
            self.link_normal_underline = link_normal_underline

        link_hover_underline = True
        link_hover_underline_string = self.ui_theme.get_misc_data(self.object_ids,
                                                                  self.element_ids, 'link_hover_underline')
        if link_hover_underline_string is not None:
            try:
                link_hover_underline = bool(int(link_hover_underline_string))
            except ValueError:
                link_hover_underline = True
        if link_hover_underline != self.link_hover_underline:
            self.link_hover_underline = link_hover_underline

        link_normal_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'link_text')
        if link_normal_colour != self.link_normal_colour:
            self.link_normal_colour = link_normal_colour

        link_hover_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'link_hover')
        if link_hover_colour != self.link_hover_colour:
            self.link_hover_colour = link_hover_colour

        link_selected_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'link_selected')
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

        if has_any_changed:
            self.rebuild()


class StyledChunk:
    def __init__(self, font_size, font_name, chunk, style,
                 color, bg_color, is_link, link_href, link_style, position: Tuple[int, int], font_dictionary):
        self.style = style
        self.chunk = chunk
        self.font_size = font_size
        self.font_name = font_name
        self.is_link = is_link
        self.link_href = link_href
        self.link_style = link_style

        self.font = font_dictionary.find_font(font_size, font_name, self.style.bold, self.style.italic)

        if self.is_link:
            self.normal_colour = self.link_style['link_text']
            self.hover_colour = self.link_style['link_hover']
            self.selected_colour = self.link_style['link_selected']
            self.link_normal_underline = self.link_style['link_normal_underline']
            self.link_hover_underline = self.link_style['link_hover_underline']
        else:
            self.normal_colour = color
            self.hover_colour = None
            self.selected_colour = None
            self.link_normal_underline = False
            self.link_hover_underline = False

        self.color = self.normal_colour
        self.bg_color = bg_color
        self.position = position

        self.is_hovered = False
        self.is_selected = False

        if self.style.underline or (self.is_hovered and self.link_hover_underline) or \
                (self.link_normal_underline and not self.is_hovered):
            self.font.set_underline(True)

        if len(self.chunk) > 0:
            if type(self.bg_color) == ColourGradient or self.bg_color.a != 255:
                if type(self.color) != ColourGradient:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                    self.color.apply_gradient_to_surface(self.rendered_chunk)
            else:
                if type(self.color) != ColourGradient:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color, self.bg_color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                    self.color.apply_gradient_to_surface(self.rendered_chunk)
        else:
            self.rendered_chunk = pygame.Surface((0, 0))
        metrics = self.font.metrics(self.chunk)
        self.ascent = self.font.get_ascent()
        self.width = self.font.size(self.chunk)[0]
        self.height = self.font.size(self.chunk)[1]
        self.advance = 0
        for i in range(0, len(self.chunk)):
            if len(metrics[i]) == 5:
                self.advance += metrics[i][4]

        self.rect = pygame.Rect(self.position, (self.width, self.height))
        self.metrics_changed_after_redraw = False

        self.unset_underline_style()

    def unset_underline_style(self):
        self.font.set_underline(False)

    def redraw(self):
        if self.style.underline or (self.is_hovered and self.link_hover_underline) or \
                (self.link_normal_underline and not self.is_hovered):
            self.font.set_underline(True)

        if len(self.chunk) > 0:
            if type(self.bg_color) == ColourGradient or self.bg_color.a != 255:
                if type(self.color) != ColourGradient:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                    self.color.apply_gradient_to_surface(self.rendered_chunk)
            else:
                if type(self.color) != ColourGradient:
                    self.rendered_chunk = self.font.render(self.chunk, True, self.color, self.bg_color)
                else:
                    self.rendered_chunk = self.font.render(self.chunk, True, pygame.Color('#FFFFFFFF'))
                    self.color.apply_gradient_to_surface(self.rendered_chunk)
        else:
            self.rendered_chunk = pygame.Surface((0, 0))

        self.font.set_underline(False)

        new_metrics = self.font.metrics(self.chunk)
        new_ascent = self.font.get_ascent()
        new_width = self.font.size(self.chunk)[0]
        new_height = self.font.size(self.chunk)[1]
        new_advance = 0
        for i in range(0, len(self.chunk)):
            if len(new_metrics[i]) == 5:
                new_advance += new_metrics[i][4]

        if (new_ascent != self.ascent or new_width != self.width) or (
                new_height != self.height or new_advance != self.advance):
            self.metrics_changed_after_redraw = True
            self.ascent = new_ascent
            self.width = new_width
            self.height = new_height
            self.advance = new_advance
            self.rect = pygame.Rect(self.position, (self.width, self.height))
        else:
            self.metrics_changed_after_redraw = False

    def on_hovered(self):
        if not self.is_selected:
            self.color = self.hover_colour
            self.is_hovered = True
            self.redraw()

    def on_unhovered(self):
        if not self.is_selected:
            self.color = self.normal_colour
            self.is_hovered = False
            self.redraw()

    def on_selected(self):
        self.color = self.selected_colour
        self.is_selected = True
        self.redraw()

    def on_unselected(self):
        self.color = self.normal_colour
        self.is_selected = False
        self.redraw()


class TextBlock:
    class TextLine:
        def __init__(self):
            self.chunks = []
            self.max_line_char_height = 0
            self.max_line_ascent = 0

    def __init__(self, text, rect_or_pos, indexed_styles, font_dict, link_style, bg_colour, wrap_to_height=False):
        self.characters = text
        if len(rect_or_pos) == 2:
            self.position = rect_or_pos
            self.width = -1
            self.height = -1
        else:
            self.position = (rect_or_pos[0], rect_or_pos[1])
            self.width = rect_or_pos[2]
            if wrap_to_height:
                self.height = rect_or_pos[3]
            else:
                self.height = -1

        self.indexed_styles = indexed_styles
        self.block_sprite = None
        self.font_dict = font_dict

        self.final_dimensions = (rect_or_pos[2], rect_or_pos[3])

        self.link_style = link_style

        self.bg_colour = bg_colour

        self.lines = []
        self.redraw(None)

    def redraw(self, text_effect):
        """
        Takes our parsed text and the styles generated from that parsing and builds rendered 'chunks' out of them
        that are then blitted onto a final surface containing all our drawn text.
        """
        self.lines = []
        if text_effect:
            end_text_position = text_effect.get_end_text_pos()
        else:
            end_text_position = len(self.characters)

        lines_of_chunks = []
        chunk_line = []
        start_style_key = 0
        keys = [key for key in list(self.indexed_styles.keys()) if key <= end_text_position]
        keys.append(end_text_position)
        max_line_ascent = 0
        for end_style_key in keys:
            if end_style_key != 0:
                text = self.characters[start_style_key:end_style_key]
                chunk = [text, self.indexed_styles[start_style_key]]
                chunk_font = self.font_dict.find_font(chunk[1].font_size,
                                                      chunk[1].font_name,
                                                      chunk[1].style.bold,
                                                      chunk[1].style.italic)
                chunk_ascent = chunk_font.get_ascent()
                if chunk_ascent > max_line_ascent:
                    max_line_ascent = chunk_ascent
                if chunk[0] == '\n':
                    if len(chunk_line) == 0:
                        lines_of_chunks.append([max_line_ascent, [['', chunk[1]]]])
                    else:
                        lines_of_chunks.append([max_line_ascent, chunk_line])
                    chunk_line = []
                    max_line_ascent = 0
                else:
                    chunk_line.append(chunk)

            start_style_key = end_style_key

        if len(chunk_line) > 0:
            lines_of_chunks.append([max_line_ascent, chunk_line])


        if self.width != -1:
            line_index = 0
            while line_index < len(lines_of_chunks):
                line = lines_of_chunks[line_index][1]
                line_render_length = 0
                split_point = -1
                chunk_index = 0
                chunk_to_split_index = 0
                chunk_length = 0
                for chunk in line:
                    font = self.font_dict.find_font(chunk[1].font_size,
                                                    chunk[1].font_name,
                                                    chunk[1].style.bold,
                                                    chunk[1].style.italic)

                    metrics = font.metrics(chunk[0])
                    chunk_length = font.size(chunk[0])[0]
                    line_render_length += chunk_length
                    if line_render_length > self.width:
                        char_line_length = line_render_length - chunk_length
                        for i in range(0, len(metrics)):
                            advance = metrics[i][4]
                            char_line_length += advance
                            if char_line_length > self.width:
                                # splitting time
                                chunk_to_split_index = chunk_index
                                split_point = i
                                break
                    if split_point != -1:
                        break
                    chunk_index += 1

                if split_point != -1:
                    word_split_point = 0
                    chunk_to_split = line[chunk_to_split_index]
                    for i in range(split_point, 0, -1):
                        if chunk_to_split[0][i] == ' ':
                            word_split_point = i
                            break
                    if word_split_point == 0 and chunk_to_split_index == 0 and chunk_length > self.width:
                        # our chunk is one word, at the start of the line, and the split point is in it, so split the
                        # word instead of hunting for a word split point
                        if split_point > 1:
                            font = self.font_dict.find_font(chunk_to_split[1].font_size,
                                                            chunk_to_split[1].font_name,
                                                            chunk_to_split[1].style.bold,
                                                            chunk_to_split[1].style.italic)

                            chunk_1 = [chunk_to_split[0][:split_point - 1] + '-', chunk_to_split[1]]
                            chunk_2 = ["-" + chunk_to_split[0][split_point - 1:].lstrip(' '), chunk_to_split[1]]

                            chunk_2_font = self.font_dict.find_font(chunk_2[1].font_size,
                                                                    chunk_2[1].font_name,
                                                                    chunk_2[1].style.bold,
                                                                    chunk_2[1].style.italic)
                            chunk_2_ascent = chunk_2_font.get_ascent()

                            lines_of_chunks[line_index][1][chunk_to_split_index] = chunk_1
                            new_line = [chunk_2_ascent, [chunk_2]]

                            chunk_length_of_line = len(lines_of_chunks[line_index][1])
                            for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                                remaining_chunk = lines_of_chunks[line_index][1][remaining_chunk_index]
                                new_line[1].append(remaining_chunk)

                                remaining_chunk_font = self.font_dict.find_font(remaining_chunk[1].font_size,
                                                                                remaining_chunk[1].font_name,
                                                                                remaining_chunk[1].style.bold,
                                                                                remaining_chunk[1].style.italic)
                                remaining_chunk_ascent = remaining_chunk_font.get_ascent()
                                if remaining_chunk_ascent > new_line[0]:
                                    new_line[0] = remaining_chunk_ascent

                            for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                                lines_of_chunks[line_index][1].pop()

                            lines_of_chunks.insert(line_index + 1, new_line)

                        else:
                            warnings.warn('Unable to split word into chunks because text box is too narrow')

                    else:
                        chunk_1 = [chunk_to_split[0][:word_split_point], chunk_to_split[1]]
                        chunk_2 = [chunk_to_split[0][word_split_point:].lstrip(' '), chunk_to_split[1]]

                        chunk_2_font = self.font_dict.find_font(chunk_2[1].font_size,
                                                                chunk_2[1].font_name,
                                                                chunk_2[1].style.bold,
                                                                chunk_2[1].style.italic)
                        chunk_2_ascent = chunk_2_font.get_ascent()

                        lines_of_chunks[line_index][1][chunk_to_split_index] = chunk_1
                        new_line = [chunk_2_ascent, [chunk_2]]

                        chunk_length_of_line = len(lines_of_chunks[line_index][1])
                        for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                            remaining_chunk = lines_of_chunks[line_index][1][remaining_chunk_index]
                            new_line[1].append(remaining_chunk)

                            remaining_chunk_font = self.font_dict.find_font(remaining_chunk[1].font_size,
                                                                            remaining_chunk[1].font_name,
                                                                            remaining_chunk[1].style.bold,
                                                                            remaining_chunk[1].style.italic)
                            remaining_chunk_ascent = remaining_chunk_font.get_ascent()
                            if remaining_chunk_ascent > new_line[0]:
                                new_line[0] = remaining_chunk_ascent

                        for remaining_chunk_index in range(chunk_to_split_index + 1, chunk_length_of_line):
                            lines_of_chunks[line_index][1].pop()

                        lines_of_chunks.insert(line_index + 1, new_line)
                line_index += 1

        surface = None
        surface_width = self.width
        surface_height = self.height
        if self.height != -1 and self.width != -1:
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, depth=32)

        position = [0, 0]
        line_height_acc = 0
        max_line_length = 0
        for line in lines_of_chunks:
            line_chunks = []
            max_line_char_height = 0
            max_line_ascent = 0
            for chunk in line[1]:
                new_chunk = StyledChunk(chunk[1].font_size,
                                        chunk[1].font_name,
                                        chunk[0],
                                        chunk[1].style,
                                        chunk[1].color,
                                        chunk[1].bg_color,
                                        chunk[1].is_link,
                                        chunk[1].link_href,
                                        self.link_style,
                                        (position[0], position[1]),
                                        self.font_dict)
                position[0] += new_chunk.advance
                if new_chunk.height > max_line_char_height:
                    max_line_char_height = new_chunk.height
                if new_chunk.ascent > max_line_ascent:
                    max_line_ascent = new_chunk.ascent
                line_chunks.append(new_chunk)

                if surface is not None:
                    # need to adjust y start pos based on ascents
                    chunk_rect = new_chunk.rect
                    adjust = line[0] - new_chunk.ascent
                    chunk_rect.y += adjust
                    surface.blit(new_chunk.rendered_chunk, chunk_rect)

            text_line = TextBlock.TextLine()
            text_line.chunks = line_chunks
            text_line.max_line_ascent = max_line_ascent
            self.lines.append(text_line)

            position[0] = 0
            position[1] += max_line_char_height
            line_height_acc += max_line_char_height

        if surface is None:
            if self.width == -1:
                surface_width = max_line_length
            else:
                surface_width = self.width
            if self.height == -1:
                surface_height = line_height_acc
            else:
                surface_height = self.height

            surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA, depth=32)

            for line in self.lines:
                for chunk in line.chunks:
                    # need to adjust y start pos based on ascents
                    chunk_rect = chunk.rect
                    adjust = line.max_line_ascent - chunk.ascent
                    chunk_rect.y += adjust
                    surface.blit(chunk.rendered_chunk, chunk_rect)

        self.block_sprite = surface
        self.final_dimensions = [surface_width, surface_height]
        self.width = surface_width
        self.height = surface_height

    def redraw_from_chunks(self, text_effect):
        if text_effect:
            final_alpha = text_effect.get_final_alpha()
        else:
            final_alpha = 255

        self.block_sprite = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA, depth=32)

        if type(self.bg_colour) == ColourGradient:
            self.block_sprite.fill(pygame.Color("#FFFFFFFF"))
            self.bg_colour.apply_gradient_to_surface(self.block_sprite)
        else:
            self.block_sprite.fill(self.bg_colour)

        for text_line in self.lines:
            for chunk in text_line.chunks:
                if self.block_sprite is not None:
                    if final_alpha != 255:
                        self.block_sprite.blit(chunk.rendered_chunk, chunk.rect)
                    else:
                        self.block_sprite.blit(chunk.rendered_chunk, chunk.rect)
        self.block_sprite.set_alpha(final_alpha)

    def add_chunks_to_hover_group(self, hover_group):
        for line in self.lines:
            for chunk in line.chunks:
                if chunk.is_link:
                    hover_group.append(chunk)

    def draw(self, surface):
        surface.blit(self.block_sprite, self.position)
