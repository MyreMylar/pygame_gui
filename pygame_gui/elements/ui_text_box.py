import pygame
import warnings
import html.parser
from typing import Union, List

from .. import ui_manager
from ..core import ui_container
from ..core.ui_element import UIElement
from ..elements.ui_vertical_scroll_bar import UIVerticalScrollBar


class TextBoxEffect:
    def __init__(self, all_characters):
        self.all_characters = all_characters

    def should_full_redraw(self):
        return False

    def should_redraw_from_chunks(self):
        return False

    def update(self, time_delta):
        pass

    def get_end_text_pos(self):
        return len(self.all_characters)

    def get_final_alpha(self):
        return 255


class TypingAppearEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_per_letter_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.text_progress < len(self.all_characters):
            if self.time_per_letter_acc < self.time_per_letter:
                self.time_per_letter_acc += time_delta
            else:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.time_to_redraw = True

    def should_full_redraw(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_end_text_pos(self):
        return self.text_progress


class FadeInEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.alpha_value < 255:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value > 255:
                    self.alpha_value = 255
                self.time_to_redraw = True

    def should_redraw_from_chunks(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self):
        return self.alpha_value


class FadeOutEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.alpha_value = 255
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.alpha_value > 0:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = 255 - int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value < 0:
                    self.alpha_value = 0
                self.time_to_redraw = True

    def should_redraw_from_chunks(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self):
        return self.alpha_value


class CharStyle:
    def __init__(self, char_style=None):
        if char_style is not None:
            self.bold = char_style.bold
            self.italic = char_style.italic
            self.underline = char_style.underline
        else:
            self.bold = False
            self.italic = False
            self.underline = False

    def __eq__(self, other):
        return self.bold == other.bold and self.italic == other.italic and self.underline == other.underline


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
    :param containing_rect: The 'visible area' rectangle, positioned relative to it's container.
    :param manager: The UIManager that manages this element.
    :param wrap_to_height: False by default, if set to True the box will increase in height to match the text within.
    :param layer_starting_height: Sets the height, above it's container, to start placing the text box at.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """

    class TextStyleData:

        default_style = {
            'font_name': 'fira_code',
            'font_size': 14
        }

        def __init__(self, theme, element_ids, object_id):
            super().__init__()

            self.ui_theme = theme
            self.len_text = 0
            self.element_stack = []
            self.style_stack = []
            self.current_style = {}
            self.next_style = {}
            self.text_data = ""

            self.indexed_styles = {}

            self.char_style = CharStyle()

            font_info = self.ui_theme.get_font_info(object_id, element_ids)

            self.default_font_name = font_info['name']
            self.default_font_size = int(font_info['size'])
            self.default_style['font_name'] = self.default_font_name
            self.default_style['font_size'] = self.default_font_size

            self.default_font_color = self.ui_theme.get_colour(object_id, element_ids, 'normal_text')
            self.default_bg_color = self.ui_theme.get_colour(object_id, element_ids, 'dark_bg')
            self.font_name = self.default_font_name
            self.font_size = self.default_font_size
            self.font_color = self.default_font_color
            self.bg_color = self.default_bg_color

            self.is_link = False
            self.link_href = ''

            self.push_style('default_style', self.default_style)

        def push_style(self, key, styles):
            old_styles = {}
            for name in styles.keys():
                old_styles[name] = self.current_style.get(name)
            self.style_stack.append((key, old_styles))
            self.current_style.update(styles)
            self.next_style.update(styles)

        def pop_style(self, key):
            # Don't do anything if key is not in stack
            for match, _ in self.style_stack:
                if key == match:
                    break
            else:
                return

            # Remove all innermost elements until key is closed.
            while True:
                match, old_styles = self.style_stack.pop()
                self.next_style.update(old_styles)
                self.current_style.update(old_styles)
                if match == key:
                    break

        def add_text(self, text):
            self.add_indexed_style(len(self.text_data))
            self.text_data = self.text_data[:self.len_text] + text + self.text_data[self.len_text:]
            self.len_text += len(text)

        def add_indexed_style(self, index):
            if 'bold' in self.current_style.keys():
                self.char_style.bold = self.current_style['bold']
                if self.char_style.bold is None:
                    self.char_style.bold = False
            else:
                self.char_style.bold = False
            if 'italic' in self.current_style.keys():
                self.char_style.italic = self.current_style['italic']
                if self.char_style.italic is None:
                    self.char_style.italic = False
            else:
                self.char_style.italic = False
            if 'underline' in self.current_style.keys():
                self.char_style.underline = self.current_style['underline']
                if self.char_style.underline is None:
                    self.char_style.underline = False
            else:
                self.char_style.underline = False
            if 'font_name' in self.current_style.keys():
                self.font_name = self.current_style['font_name']
                if self.font_name is None:
                    self.font_name = self.default_font_name
            else:
                self.font_name = self.default_font_name
            if 'font_size' in self.current_style.keys():
                self.font_size = self.current_style['font_size']
                if self.font_size is None:
                    self.font_size = self.default_font_size
            else:
                self.font_size = self.default_font_size
            if 'font_color' in self.current_style.keys():
                self.font_color = self.current_style['font_color']
                if self.font_color is None:
                    self.font_color = self.default_font_color
            else:
                self.font_color = self.default_font_color
            if 'bg_color' in self.current_style.keys():
                self.bg_color = self.current_style['bg_color']
                if self.bg_color is None:
                    self.bg_color = self.default_bg_color
            else:
                self.bg_color = self.default_bg_color

            if 'link' in self.current_style.keys():
                self.is_link = self.current_style['link']
                if self.is_link is None:
                    self.is_link = False
            else:
                self.is_link = False

            if 'link_href' in self.current_style.keys():
                self.link_href = self.current_style['link_href']
                if self.link_href is None:
                    self.link_href = ''
            else:
                self.link_href = ''

            self.indexed_styles[index] = TextLineContext(self.font_size,
                                                         self.font_name,
                                                         CharStyle(self.char_style),
                                                         self.font_color,
                                                         self.bg_color,
                                                         self.is_link,
                                                         self.link_href)

    class TextHTMLParser(TextStyleData, html.parser.HTMLParser):

        font_sizes = {
            1: 8,
            1.5: 9,
            2: 10,
            2.5: 11,
            3: 12,
            3.5: 13,
            4: 14,
            4.5: 16,
            5: 18,
            5.5: 20,
            6: 24,
            6.5: 32,
            7: 48
        }

        def __init__(self, ui_theme, element_ids, object_id):
            super().__init__(ui_theme, element_ids, object_id)
            self.ui_theme = ui_theme
            self.element_ids = element_ids
            self.object_id = object_id

        def handle_starttag(self, tag, attrs):
            element = tag.lower()

            self.element_stack.append(element)

            attributes = {}
            for key, value in attrs:
                attributes[key.lower()] = value

            style = {}
            if element in ('b', 'strong'):
                style['bold'] = True
            elif element == 'a':
                style['link'] = True
                if 'href' in attributes:
                    style["link_href"] = attributes['href']
            elif element in ('i', 'em', 'var'):
                style['italic'] = True
            elif element == 'u':
                style['underline'] = True
            elif element == 'font':
                if 'face' in attributes:
                    font_name = attributes['face']  # .split(',')
                    style["font_name"] = font_name
                if 'size' in attributes:
                    font_size = self.font_sizes[float(attributes['size'])]
                    style["font_size"] = font_size
                if 'color' in attributes:
                    if attributes['color'][0] == '#':
                        style["font_color"] = pygame.color.Color(attributes['color'])
                    else:
                        style["font_color"] = self.ui_theme.get_colour(self.object_id,
                                                                       self.element_ids, attributes['color'])

            elif element == 'body':
                if 'bgcolor' in attributes:
                    style["bg_color"] = pygame.color.Color(attributes['bgcolor'])
            elif element == 'br':
                self.add_text('\n')  # u'\u2028'
            else:
                warning_text = 'Unsupported HTML Tag <' + element + '>. Check documentation' \
                                                                    ' for full range of supported tags.'
                warnings.warn(warning_text, UserWarning)

            self.push_style(element, style)

        def handle_endtag(self, tag):
            element = tag.lower()

            if element not in self.element_stack:
                return

            self.pop_style(element)

            while self.element_stack.pop() != element:
                pass

        def handle_data(self, data):
            self.add_text(data)

        def error(self, message):
            pass

    def __init__(self, html_text: str,
                 containing_rect: pygame.Rect,
                 manager: ui_manager.UIManager,
                 wrap_to_height: bool = False,
                 layer_starting_height: int = 1,
                 container: ui_container.UIContainer = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='text_box')
        super().__init__(containing_rect, manager, container,
                         starting_height=layer_starting_height,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids
                         )
        self.html_text = html_text
        self.font_dict = self.ui_theme.get_font_dictionary()

        self.active_text_effect = None
        self.scroll_bar = None
        self.scroll_bar_width = 20
        self.bg_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'dark_bg')
        self.border_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'normal_border')

        self.link_normal_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'link_text')
        self.link_hover_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'link_hover')
        self.link_selected_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'link_selected')

        link_normal_underline_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids,
                                                                   'link_normal_underline')
        if link_normal_underline_string is not None:
            self.link_normal_underline = bool(int(link_normal_underline_string))
        else:
            self.link_normal_underline = False

        link_hover_underline_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids,
                                                                  'link_hover_underline')
        if link_hover_underline_string is not None:
            self.link_hover_underline = bool(int(link_hover_underline_string))
        else:
            self.link_hover_underline = True

        self.link_style = {'link_text': self.link_normal_colour,
                           'link_hover': self.link_hover_colour,
                           'link_selected': self.link_selected_colour,
                           'link_normal_underline': self.link_normal_underline,
                           'link_hover_underline': self.link_hover_underline}

        self.formatted_text_block = None  # TextLine()
        # if we pass in a rect, text will be wrapped to the rect width (and warn if longer than the height?)
        self.rect = pygame.Rect((self.ui_container.rect.x + containing_rect.x,
                                 self.ui_container.rect.y + containing_rect.y),
                                containing_rect.size)

        padding_str = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'padding')
        if padding_str is None:
            self.padding = (10, 10)
        else:
            padding_list = padding_str.split(',')
            self.padding = (int(padding_list[0]), int(padding_list[1]))

        self.border_width = 0
        border_width_str = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'border_width')
        if border_width_str is not None:
            self.border_width = int(border_width_str)

        self.shadow_width = 0
        shadow_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shadow_width')
        if shadow_width_string is not None:
            self.shadow_width = int(shadow_width_string)

        self.wrap_to_height = wrap_to_height

        self.link_hover_chunks = []  # container for any link chunks we have

        text_wrap_rect = [self.rect[0] + self.padding[0] + self.border_width + self.shadow_width,
                          self.rect[1] + self.padding[1] + self.border_width + self.shadow_width,
                          self.rect[2] - (self.padding[0] * 2) - (self.border_width * 2) - (self.shadow_width * 2),
                          self.rect[3] - (self.padding[1] * 2) - (self.border_width * 2) - (self.shadow_width * 2)]
        ''' The text_wrap_area is the part of the text box that we try to keep the text inside of so that none 
        of it overlaps. Essentially we start with the containing box, subtract the border,  then subtract the 
        padding, then if necessary subtract the width of the scroll bar'''

        self.text_wrap_rect = text_wrap_rect
        if self.rect[3] == -1:
            self.text_wrap_rect[3] = -1

        self.parse_html_into_style_data()  # This gives us the height of the text at the 'width' of the text_wrap_area
        if self.formatted_text_block is not None:
            if self.wrap_to_height or self.rect[3] == -1:
                final_text_area_size = self.formatted_text_block.final_dimensions
                self.rect.size = [(final_text_area_size[0] + (self.padding[0] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2)),
                                  (final_text_area_size[1] + (self.padding[1] * 2) +
                                   (self.border_width * 2) + (self.shadow_width * 2))]

            elif self.formatted_text_block.final_dimensions[1] > self.text_wrap_rect[3]:
                # We need a scrollbar because our text is longer than the space we have to display it.
                # this also means we need to parse the text again.
                text_rect_width = (self.rect[2] - (self.padding[0] * 2)
                                   - (self.border_width * 2) - (self.shadow_width * 2) - self.scroll_bar_width)
                self.text_wrap_rect = [self.rect[0] + self.padding[0] + self.border_width + self.shadow_width,
                                       self.rect[1] + self.padding[1] + self.border_width + self.shadow_width,
                                       text_rect_width,
                                       (self.rect[3] - (self.padding[1] * 2) -
                                        (self.border_width * 2) - (self.shadow_width * 2))]
                self.parse_html_into_style_data()
                percentage_visible = self.text_wrap_rect[3] / self.formatted_text_block.final_dimensions[1]
                scroll_bar_position = (self.relative_rect.right - self.border_width -
                                       - self.shadow_width - self.scroll_bar_width,
                                       self.relative_rect.top + self.border_width + self.shadow_width)
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

        # This section creates the border by blitting a smaller surface over the top of one containing the border
        # to make the final background surface - this would be the point to add transparency I guess
        if self.shadow_width > 0:
            self.background_surf = self.ui_manager.get_shadow(self.rect.size)
        else:
            self.background_surf = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        border_rect = pygame.Rect((self.shadow_width, self.shadow_width),
                                  (self.rect.width - (2 * self.shadow_width),
                                   self.rect.height - (2 * self.shadow_width)))
        if self.border_width > 0:
            self.background_surf.fill(self.border_colour,
                                      border_rect)

        relative_background_rect = pygame.Rect((self.border_width + self.shadow_width,
                                                self.border_width + self.shadow_width),
                                               (border_rect.width - (2 * self.border_width),
                                                border_rect.height - (2 * self.border_width)))

        # background_rect = pygame.Rect((relative_background_rect.x + relative_rect.x,
        #                                relative_background_rect.y + relative_rect.y),
        #                               relative_background_rect.size)
        self.background_surf.fill(self.bg_colour,
                                  relative_background_rect)

        if self.scroll_bar is not None:
            height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
        else:
            height_adjustment = 0

        drawable_area = pygame.Rect((0, height_adjustment), (self.text_wrap_rect[2], self.text_wrap_rect[3]))
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.fill(pygame.Color(0, 0, 0, 0))
        self.image.blit(self.background_surf, (0, 0))
        self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                 self.shadow_width,
                                                                 self.padding[1] + self.border_width +
                                                                 self.shadow_width),
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
                    self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
                    self.image.fill(pygame.Color(0, 0, 0, 0))
                    self.image.blit(self.background_surf, (0, 0))
                    self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                             self.shadow_width,
                                                                             self.padding[1] + self.border_width +
                                                                             self.shadow_width),
                                    drawable_area)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            should_redraw_from_chunks = False

            if self.scroll_bar is not None:
                height_adjustment = self.scroll_bar.start_percentage * self.formatted_text_block.final_dimensions[1]
            else:
                height_adjustment = 0
            base_x = self.rect[0] + self.padding[0] + self.border_width + self.shadow_width
            base_y = self.rect[1] + self.padding[1] + self.border_width + self.shadow_width - height_adjustment

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

    def parse_html_into_style_data(self):
        """
        Parses HTML styled string text into a format more useful for styling pygame.font rendered text.
        """
        parser = UITextBox.TextHTMLParser(self.ui_theme, self.element_ids, self.object_ids)
        parser.push_style('body', {"bg_color": self.bg_colour})
        parser.feed(self.html_text)

        self.formatted_text_block = TextBlock(parser.text_data,
                                              self.text_wrap_rect,
                                              parser.indexed_styles,
                                              self.font_dict,
                                              self.link_style,
                                              self.bg_colour,
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
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.fill(pygame.Color(0, 0, 0, 0))
        self.image.blit(self.background_surf, (0, 0))
        self.image.blit(self.formatted_text_block.block_sprite, (self.padding[0] + self.border_width +
                                                                 self.shadow_width,
                                                                 self.padding[1] + self.border_width +
                                                                 self.shadow_width),
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
        fundamental fashion and need to reposition them (say, if some of them have gotten wider after being bolded).

        NOTE: This doesn't reparse the text of our box. If you need to do that, just create a new text box.

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
                    base_x = self.rect[0] + self.padding[0] + self.border_width + self.shadow_width
                    base_y = self.rect[1] + self.padding[1] + self.border_width + self.shadow_width - height_adjustment
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
                base_x = self.rect[0] + self.padding[0] + self.border_width + self.shadow_width
                base_y = self.rect[1] + self.padding[1] + self.border_width + self.shadow_width - height_adjustment
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
                                                                        {'user_type': 'ui_text_box_link_clicked',
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
        - 'fade in' - The text will fade in from the background colour (Only supported on Pygame 2)
        - 'fade out' - The text will fade out to the background colour (only supported on Pygame 2)

        :param effect_name: The name fo the t to set. If set to None instead it will cancel any active effect.
        """
        if effect_name is None:
            self.active_text_effect = None
        elif type(effect_name) is str:
            if effect_name == 'typing_appear':
                effect = TypingAppearEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.full_redraw()
            elif effect_name == 'fade_in':
                effect = FadeInEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.redraw_from_chunks()
            elif effect_name == 'fade_out':
                effect = FadeOutEffect(self.formatted_text_block.characters)
                self.active_text_effect = effect
                self.redraw_from_chunks()
            else:
                warnings.warn('Unsupported effect name: ' + effect_name + ' for text box')


class StyledChunk:
    def __init__(self, font_size, font_name, chunk, style,
                 color, bg_color, is_link, link_href, link_style, position, font_dictionary):
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

        if self.style.underline or (self.is_hovered and self.link_hover_underline) or\
                (self.link_normal_underline and not self.is_hovered):
            self.font.set_underline(True)

        if len(self.chunk) > 0:
            if self.bg_color.a != 255:
                self.rendered_chunk = self.font.render(self.chunk, True, self.color)
            else:
                self.rendered_chunk = self.font.render(self.chunk, True, self.color, self.bg_color)
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
            if self.bg_color.a != 255:
                self.rendered_chunk = self.font.render(self.chunk, True, self.color)
            else:
                self.rendered_chunk = self.font.render(self.chunk, True, self.color, self.bg_color)
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


class TextLineContext:
    """
    A class that covers all the states of the text 'options' so we know what
    to apply when rendering a letter.
    """
    def __init__(self, font_size, font_name, style, color, bg_color, is_link, link_href):
        self.font_size = font_size
        self.font_name = font_name
        self.style = style
        self.color = color
        self.bg_color = bg_color
        self.is_link = is_link
        self.link_href = link_href

    def __eq__(self, other):
        font_size_eq = self.font_size == other.font_size
        font_name_eq = self.font_name == other.font_name
        font_style_eq = self.style == other.style
        font_color_eq = self.color == other.color
        font_bg_color_eq = self.bg_color == other.bg_color
        link_eq = self.is_link == other.is_link
        link_href_eq = self.link_href == other.link_href
        if font_size_eq and font_name_eq and font_style_eq and\
                font_color_eq and font_bg_color_eq and link_eq and link_href_eq:
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


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
                    if word_split_point == 0 and len(line) == 1 and chunk_length > self.width:
                        # our chunk is one long word, so split the word instead of hunting for
                        # a word split point
                        if split_point > 0:
                            chunk_1 = [chunk_to_split[0][:split_point-1] + '-', chunk_to_split[1]]
                            chunk_2 = ["-" + chunk_to_split[0][split_point-1:].lstrip(' '), chunk_to_split[1]]

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

                        lines_of_chunks.insert(line_index+1, new_line)
                line_index += 1

        surface = None
        surface_width = self.width
        surface_height = self.height
        if self.height != -1 and self.width != -1:
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        position = [0.0, 0.0]
        line_height_acc = 0
        max_line_length = 0
        for line in lines_of_chunks:
            line_chunks = []
            max_line_char_height = 0
            max_line_ascent = 0.0
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
                                        position,
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

            position[0] = 0.0
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

            surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

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

        self.block_sprite = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
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
