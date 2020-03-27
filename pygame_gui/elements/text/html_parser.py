import warnings
import html.parser
from typing import Union, List, Dict, Any

import pygame

from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme


class CharStyle:
    """
    Encapsulates the three classic styling options for a character; bold, italic and underlined.

    :param char_style: An optional CharStyle to copy this character style from.
    """
    def __init__(self, char_style: Union['CharStyle', None] = None):
        if char_style is not None:
            self.bold = char_style.bold
            self.italic = char_style.italic
            self.underline = char_style.underline
        else:
            self.bold = False
            self.italic = False
            self.underline = False

    def __eq__(self, other: 'CharStyle'):
        """
        Test if this character style is the same as a another.

        :param other: The other to test against.
        """
        return (self.bold == other.bold and
                self.italic == other.italic and
                self.underline == other.underline)


class TextLineContext:
    """
    A class that covers all the states of the text 'options' so we know what to apply when
    rendering a letter.

    :param font_size: The size of the font in pixels.
    :param font_name: The name of the font to use.
    :param style: The style of the letter (some combination of bold, italic & underlined)
    :param colour: The colour or gradient to render the text with.
    :param bg_colour: The colour or gradient to render the background of the text with.
    :param is_link: True if it is a hyperlink.
    :param link_href: The destination of the hyperlink if we have one.
    """
    def __init__(self,
                 font_size: int,
                 font_name: str,
                 style: CharStyle,
                 colour: Union[pygame.Color, ColourGradient],
                 bg_colour: Union[pygame.Color, ColourGradient],
                 is_link: bool,
                 link_href: str):

        self.font_size = font_size
        self.font_name = font_name
        self.style = style
        self.colour = colour
        self.bg_colour = bg_colour
        self.is_link = is_link
        self.link_href = link_href

    def __eq__(self, other: 'TextLineContext'):
        """
        Test if this text context is the same as a another.

        :param other: The other to test against.
        """
        font_size_eq = self.font_size == other.font_size
        font_name_eq = self.font_name == other.font_name
        font_style_eq = self.style == other.style
        font_colour_eq = self.colour == other.colour
        font_bg_colour_eq = self.bg_colour == other.bg_colour
        link_eq = self.is_link == other.is_link
        link_href_eq = self.link_href == other.link_href

        font_name_size_style_equal = (font_size_eq and font_name_eq and font_style_eq)
        font_colours_equal = (font_colour_eq and font_bg_colour_eq)
        if font_name_size_style_equal and font_colours_equal and link_eq and link_href_eq:
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other: 'TextLineContext'):
        """
        Test if this text context is not the same as a another.

        :param other: The other to test against.
        """
        return not self.__eq__(other)


class TextStyleData:
    """
    A group of styles organised so that we can easily access them when stepping through our text
    character by character o we always know what style goes with what text. Also stores the text
    that goes along with the styles.

    There are three main things going on in this class and the Parse one below:

    1. Parsing the html tags into 'styles' which don't have an associated object but maybe should
       (StyleTag?).
    2. Storing the style tags into a stack as we also step through the regular text.
    3. Each time we change the style tags in some way we take the current state of the style stack,
       and the current progress through the regular text and store the style under an index for the
       current text position.

    :param theme:
    :param element_ids:
    :param object_id:
    """

    default_style = {
        'font_name': 'fira_code',
        'font_size': 14,
        'font_colour': pygame.Color(255, 255, 255, 255),
        'bg_colour': pygame.Color(0, 0, 0, 0)
    }

    def __init__(self,
                 theme: UIAppearanceTheme,
                 element_ids: List[str],
                 object_id: List[Union[str, None]]):

        self.ui_theme = theme
        self.len_text = 0

        self.style_stack = []
        self.current_style = {}
        # self.next_style = {}
        self.text_data = ""

        self.indexed_styles = {}

        self.char_style = CharStyle()

        font_info = self.ui_theme.get_font_info(object_id, element_ids)

        self.default_style['font_name'] = font_info['name']
        self.default_style['font_size'] = int(font_info['size'])

        self.default_style['font_colour'] = self.ui_theme.get_colour_or_gradient(object_id,
                                                                                 element_ids,
                                                                                 'normal_text')
        self.default_style['bg_colour'] = self.ui_theme.get_colour_or_gradient(object_id,
                                                                               element_ids,
                                                                               'dark_bg')
        self.font_name = self.default_style['font_name']
        self.font_size = self.default_style['font_size']
        self.font_colour = self.default_style['font_colour']
        self.bg_colour = self.default_style['bg_colour']

        self.is_link = False
        self.link_href = ''

        self.push_style('default_style', self.default_style)

    def push_style(self, key: str, styles: Dict[str, Any]):
        """
        Add a new styling element onto the style stack. These are single styles generally (i.e. a
        font size change, or a bolding of text) rather than a load of different styles all at once.
        The eventual style of a character/bit of text is built up by evaluating all styling
        elements currently on the stack when we parse that bit of text.

        Styles on top of the stack will be evaluated last so they can overwrite elements earlier
        in the stack (i.e. a later 'font_size' of 5 wil overwrite an earlier 'font_size' of 3).

        :param key: Name for this styling element so we can identify when to remove it when the
        styling block is closed
        :param styles: The styling dictionary that contains the actual styling.
        """
        old_styles = {name: self.current_style.get(name) for name in styles}
        self.style_stack.append((key, old_styles))
        self.current_style.update(styles)
        # self.next_style.update(styles)

    def pop_style(self, key: str):
        """
        Remove a styling element/dictionary from the stack by it's identifying key name.

        :param key: The identifier.
        """
        # Don't do anything if key is not in stack
        for match, _ in self.style_stack:
            if key == match:
                break
        else:
            return

        # Remove all innermost elements until key is closed.
        while True:
            match, old_styles = self.style_stack.pop()
            # self.next_style.update(old_styles)
            self.current_style.update(old_styles)
            if match == key:
                break

    def add_text(self, text: str):
        """
        Add another bit of text using the current style, and index the text's style appropriately.

        :param text:
        """
        self.add_indexed_style(len(self.text_data))
        self.text_data = self.text_data[:self.len_text] + text + self.text_data[self.len_text:]
        self.len_text += len(text)

    def add_indexed_style(self, index: int):
        """
        Styles indexed by their starting position in the text.

        :param index: The index to use.
        """
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

        self._set_style_attribute('font_name')
        self._set_style_attribute('font_size')
        self._set_style_attribute('font_colour')
        self._set_style_attribute('bg_colour')

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
                                                     self.font_colour,
                                                     self.bg_colour,
                                                     self.is_link,
                                                     self.link_href)

    def _set_style_attribute(self, attribute: str):
        """
        Set a style attribute for this font style.

        :param attribute: Name of the attribute to set.
        """
        if attribute in self.current_style:
            setattr(self, attribute, self.current_style[attribute])
            if getattr(self, attribute) is None:
                setattr(self, attribute, self.default_style[attribute])
        else:
            setattr(self, attribute, self.default_style[attribute])


class TextHTMLParser(TextStyleData, html.parser.HTMLParser):
    """
    Parse a subset of HTML tags into styling data for our text.

    :param ui_theme: The UI theming data.
    :param element_ids: The element IDs used to look up theming data.
    :param object_id: The object IDs used to look up theming data.
    """
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

    def __init__(self,
                 ui_theme: UIAppearanceTheme,
                 element_ids: List[str],
                 object_id: List[Union[str, None]]):

        TextStyleData.__init__(self, ui_theme, element_ids, object_id)
        html.parser.HTMLParser.__init__(self)

        self.ui_theme = ui_theme
        self.element_ids = element_ids
        self.object_id = object_id

        self.element_stack = []

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        """
        Process an HTML 'start tag' (e.g. <b>) where we have a start and an end tag enclosing a
        range of text this is the first one of those and controls where we add the 'styling' thing
        to our styling stack.

        Eventually we will want to expand this to handle tags like <img>.

        :param tag: The tag itself
        :param attrs: Attributes of the tag.
        """
        element = tag.lower()

        self.element_stack.append(element)

        attributes = {key.lower(): value for key, value in attrs}
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
                font_name = attributes['face'] if len(attributes['face']) > 0 else None
                style["font_name"] = font_name
            if 'size' in attributes:
                if len(attributes['size']) > 0:
                    font_size = self.font_sizes[float(attributes['size'])]
                else:
                    font_size = None
                style["font_size"] = font_size
            if 'color' in attributes:
                if attributes['color'][0] == '#':
                    style["font_colour"] = pygame.color.Color(attributes['color'])
                else:
                    style["font_colour"] = self.ui_theme.get_colour_or_gradient(self.object_id,
                                                                                self.element_ids,
                                                                                attributes['color'])
        elif element == 'body':
            if 'bgcolor' in attributes:
                if len(attributes['bgcolor']) > 0:
                    if ',' in attributes['bgcolor']:
                        col_id = attributes['bgcolor']
                        style["bg_colour"] = self.ui_theme.get_colour_or_gradient(self.object_id,
                                                                                  self.element_ids,
                                                                                  col_id)
                    else:
                        style["bg_colour"] = pygame.color.Color(attributes['bgcolor'])
                else:
                    style["bg_colour"] = None

        elif element == 'br':
            self.add_text('\n')  # u'\u2028'
        else:
            warning_text = 'Unsupported HTML Tag <' + element + '>. Check documentation' \
                                                                ' for full range of supported tags.'
            warnings.warn(warning_text, UserWarning)

        self.push_style(element, style)

    def handle_endtag(self, tag: str):
        """
        Handles encountering an HTML end tag. Usually this will involve us popping a style off our
        stack of styles.

        :param tag: The end tag to handle.
        """
        element = tag.lower()

        if element not in self.element_stack:
            return

        self.pop_style(element)

        result = None
        while result != element:
            result = self.element_stack.pop()

    def handle_data(self, data: str):
        """
        Handles parsed HTML that is not a tag of any kind, ordinary text basically.

        :param data: Some string data.
        """
        self.add_text(data)

    def error(self, message):
        """
        Feeds any parsing errors up the chain to the warning system.

        :param message: The message to warn about.
        """
        warnings.warn(message, UserWarning)
