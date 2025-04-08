import warnings
import html.parser
from collections import deque
from typing import List, Dict, Any, Tuple, Deque
from pathlib import Path

# noinspection PyPackageRequirements
from _markupbase import ParserBase

import pygame

from pygame_gui.core.interfaces import (
    IUIAppearanceThemeInterface,
    IColourGradientInterface,
)

from pygame_gui.core.text.text_layout_rect import TextLayoutRect
from pygame_gui.core.text.line_break_layout_rect import LineBreakLayoutRect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont
from pygame_gui.core.text.hyperlink_text_chunk import HyperlinkTextChunk
from pygame_gui.core.text.text_layout_rect import TextFloatPosition, Padding
from pygame_gui.core.text.image_layout_rect import ImageLayoutRect


class HTMLParser(html.parser.HTMLParser):
    """
    Parses a subset of HTML styled text to make it usable as text in pygame GUI. There are
    lots of text markup languages and this would be the class to swap in and out if you
    wanted to support them (Though this might need some refactoring to have a generic
    markup parser base class).

    :param ui_theme: The UI theme we are using - for colour and fonts.
    :param combined_ids: The IDs for the UI element this parser instance belongs to.
    :param line_spacing: The line spacing we use when the text is on multiple lines -
                         defaults to 1.2.
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
        7: 48,
    }

    def __init__(
        self,
        ui_theme: IUIAppearanceThemeInterface,
        combined_ids: List[str],
        link_style: Dict[str, Any],
        line_spacing: float = 1.0,
        text_direction: int = pygame.DIRECTION_LTR,
    ):
        super().__init__()
        ParserBase.__init__(self)
        self.ui_theme = ui_theme
        self.combined_ids = combined_ids
        self.line_spacing = line_spacing

        self.link_style = link_style
        self.element_stack: List[str] = []

        self.style_stack: List[Tuple[str, Dict[str, Any]]] = []
        self.current_style: Dict[str, Any] = {}

        font_info = self.ui_theme.get_font_info(combined_ids)

        self.default_style = {
            "font_name": font_info["name"],
            "font_size": int(font_info["size"]),
            "font_colour": self.ui_theme.get_colour_or_gradient(
                "normal_text", combined_ids
            ),
            "bg_colour": pygame.Color("#00000000"),
            "shadow_data": None,
            "bold": False,
            "italic": False,
            "underline": False,
            "link": False,
            "link_href": "",
            "effect_id": None,
            "antialiased": True,
            "script": "Latn",
            "direction": text_direction,
        }

        # this is the style used before any html is loaded
        self.push_style("default_style", self.default_style)

        self.layout_rect_queue: Deque[TextLayoutRect] = deque([])

        self.in_paragraph_block = False

    def empty_layout_queue(self):
        """
        Clear out the layout queue.
        """
        self.layout_rect_queue.clear()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]):
        """
        Process an HTML 'start tag' (e.g. 'b' - tags are stripped of their angle brackets)
        where we have a start and an end tag enclosing a range of text this is the first
        one of those and controls where we add the 'styling' thing to our styling stack.

        Eventually we will want to expand this to handle tags like <img>.

        :param tag: The tag itself
        :param attrs: Attributes of the tag.
        """
        element = tag.lower()

        if element not in ("img", "br"):
            # don't add self-closing tags to the element stack
            self.element_stack.append(element)

        attributes: Dict[str, str | None] = {key.lower(): value for key, value in attrs}
        style: Dict[str, Any] = {}
        if element in {"b", "strong"}:
            style["bold"] = True
        elif element in {"i", "em", "var"}:
            style["italic"] = True
        elif element == "u":
            style["underline"] = True
        elif element == "a":
            style["link"] = True
            if "href" in attributes:
                style["link_href"] = attributes["href"]
        elif element == "effect":
            HTMLParser._handle_effect_tag(attributes, style)
        elif element == "shadow":
            self._handle_shadow_tag(attributes, style)
        elif element == "font":
            self._handle_font_tag(attributes, style)
        elif element == "body":
            self._handle_body_tag(attributes, style)
        elif element == "br":
            self._handle_line_break()
        elif element == "p":
            self._handle_p_tag()
        elif element == "img":
            self._handle_img_tag(attributes)
        else:
            warning_text = (
                f"Unsupported HTML Tag <{element}" + ">. Check documentation"
                " for full range of supported tags."
            )
            warnings.warn(warning_text, UserWarning)

        self.push_style(element, style)

    @classmethod
    def _handle_effect_tag(cls, attributes, style):
        if "id" in attributes:
            style["effect_id"] = str(attributes["id"])

    def _handle_shadow_tag(self, attributes, style):
        shadow_size = 0
        shadow_offset = [0, 0]
        shadow_colour: pygame.Color | IColourGradientInterface = pygame.Color(
            50, 50, 50
        )
        if "size" in attributes and (
            attributes["size"] is not None and len(attributes["size"]) > 0
        ):
            try:
                shadow_size = int(attributes["size"])
            except (ValueError, AttributeError):
                shadow_size = 0

        if "offset" in attributes and (
            attributes["offset"] is not None and len(attributes["offset"]) > 0
        ):
            try:
                offset_str = attributes["offset"].split(",")
                if len(offset_str) == 2:
                    shadow_offset[0] = int(offset_str[0])
                    shadow_offset[1] = int(offset_str[1])
            except (ValueError, AttributeError):
                shadow_offset = [0, 0]
        if "color" in attributes:
            try:
                if self._is_legal_hex_colour(attributes["color"]):
                    shadow_colour = pygame.color.Color(attributes["color"])
                elif attributes["color"] is not None and len(attributes["color"]) > 0:
                    shadow_colour = self.ui_theme.get_colour_or_gradient(
                        attributes["color"], self.combined_ids
                    )
            except (ValueError, AttributeError):
                shadow_colour = pygame.Color(50, 50, 50)

        style["shadow_data"] = (
            shadow_size,
            shadow_offset[0],
            shadow_offset[1],
            shadow_colour,
            False,
        )

    def _handle_font_tag(self, attributes, style):
        if "face" in attributes and attributes["face"] is not None:
            font_name = attributes["face"] if len(attributes["face"]) > 0 else None
            style["font_name"] = font_name
        if "pixel_size" in attributes:
            if (
                attributes["pixel_size"] is not None
                and len(attributes["pixel_size"]) > 0
            ):
                try:
                    font_size = int(attributes["pixel_size"])
                except (ValueError, AttributeError):
                    font_size = self.default_style["font_size"]
            else:
                font_size = self.default_style["font_size"]
            style["font_size"] = font_size
        elif "size" in attributes:
            if attributes["size"] is not None and len(attributes["size"]) > 0:
                try:
                    if float(attributes["size"]) in self.font_sizes:
                        font_size = self.font_sizes[float(attributes["size"])]
                    else:
                        warnings.warn(
                            "Size of: "
                            + str(float(attributes["size"]))
                            + " - is not a supported html style size."
                            " Try .5 increments between 1 & 7 or use 'pixel_size' instead to "
                            "set the font size directly",
                            category=UserWarning,
                        )
                        font_size = self.default_style["font_size"]
                except (ValueError, AttributeError):
                    font_size = self.default_style["font_size"]
            else:
                font_size = self.default_style["font_size"]
            style["font_size"] = font_size
        if "color" in attributes:
            style["font_colour"] = self.default_style["font_colour"]
            try:
                if self._is_legal_hex_colour(attributes["color"]):
                    style["font_colour"] = pygame.color.Color(attributes["color"])
                elif attributes["color"] is not None and len(attributes["color"]) > 0:
                    style["font_colour"] = self.ui_theme.get_colour_or_gradient(
                        attributes["color"], self.combined_ids
                    )
            except (ValueError, AttributeError):
                style["font_colour"] = self.default_style["font_colour"]

    def _handle_body_tag(self, attributes, style):
        if "bgcolor" in attributes:
            if attributes["bgcolor"] is not None and len(attributes["bgcolor"]) > 0:
                try:
                    if self._is_legal_hex_colour(attributes["bgcolor"]):
                        style["bg_colour"] = pygame.color.Color(attributes["bgcolor"])
                    else:
                        style["bg_colour"] = self.ui_theme.get_colour_or_gradient(
                            attributes["bgcolor"], self.combined_ids
                        )
                except (ValueError, AttributeError):
                    style["bg_colour"] = pygame.Color("#00000000")
            else:
                style["bg_colour"] = pygame.Color("#00000000")

    def _handle_line_break(self):
        current_font = self.ui_theme.get_font_dictionary().find_font(
            font_name=self.current_style["font_name"],
            font_size=self.current_style["font_size"],
            bold=self.current_style["bold"],
            italic=self.current_style["italic"],
            antialiased=self.current_style["antialiased"],
            script=self.current_style["script"],
            direction=self.current_style["direction"],
        )
        dimensions = (
            4,
            int(round(self.current_style["font_size"] * self.line_spacing)),
        )
        chunk = self.create_styled_text_chunk("")
        self.layout_rect_queue.append(
            LineBreakLayoutRect(dimensions=dimensions, font=current_font)
        )
        self.layout_rect_queue.append(chunk)

    def _handle_p_tag(self):
        if self.in_paragraph_block:
            self._handle_line_break()
        self.in_paragraph_block = True

    def _handle_img_tag(self, attributes):
        image_path = Path("")
        image_float = TextFloatPosition.NONE
        padding_top = 0
        padding_right = 0
        padding_bottom = 0
        padding_left = 0
        if "src" in attributes:
            image_path = Path(attributes["src"])
        if "float" in attributes:
            if attributes["float"] == "left":
                image_float = TextFloatPosition.LEFT
            elif attributes["float"] == "right":
                image_float = TextFloatPosition.RIGHT
            else:
                image_float = TextFloatPosition.NONE
        if "padding" in attributes and isinstance(attributes["padding"], str):
            paddings: List[str] = attributes["padding"].split(" ")
            for index, padding in enumerate(paddings):
                paddings[index] = padding.strip("px")
            if len(paddings) == 4:
                padding_top = int(paddings[0])
                padding_right = int(paddings[1])
                padding_bottom = int(paddings[2])
                padding_left = int(paddings[3])
            elif len(paddings) == 3:
                padding_top = int(paddings[0])
                padding_right = int(paddings[1])
                padding_left = int(paddings[1])
                padding_bottom = int(paddings[2])
            elif len(paddings) == 2:
                padding_top = int(paddings[0])
                padding_right = int(paddings[1])
                padding_left = int(paddings[1])
                padding_bottom = int(paddings[0])
            elif len(paddings) == 1:
                padding_top = int(paddings[0])
                padding_right = int(paddings[0])
                padding_left = int(paddings[0])
                padding_bottom = int(paddings[0])
            else:
                padding_top = 0
                padding_right = 0
                padding_left = 0
                padding_bottom = 0
        all_paddings = Padding(padding_top, padding_right, padding_bottom, padding_left)
        self.layout_rect_queue.append(
            ImageLayoutRect(image_path, image_float, all_paddings)
        )

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

        if element == "p":
            self.in_paragraph_block = False
            self._handle_line_break()

        result = None
        while result != element:
            result = self.element_stack.pop()

    def handle_data(self, data: str):
        """
        Handles parsed HTML that is not a tag of any kind, ordinary text basically.

        :param data: Some string data.
        """
        self._add_text(data)

    def error(self, message):
        """
        Feeds any parsing errors up the chain to the warning system.

        :param message: The message to warn about.
        """
        warnings.warn(message, UserWarning)

    def push_style(self, key: str, styles: Dict[str, Any]):
        """
        Add a new styling element onto the style stack. These are single styles generally (i.e. a
        font size change, or a bolding of text) rather than a load of different styles all at once.
        The eventual style of a character/bit of text is built up by evaluating all styling
        elements currently on the stack when we parse that bit of text.

        Styles on top of the stack will be evaluated last, so they can overwrite elements earlier
        in the stack (i.e. a later 'font_size' of 5 will overwrite an earlier 'font_size' of 3).

        :param key: Name for this styling element so, we can identify when to remove it
        :param styles: The styling dictionary that contains the actual styling.

        """
        old_styles = {name: self.current_style.get(name) for name in styles}
        self.style_stack.append((key, old_styles))
        self.current_style.update(styles)

    def pop_style(self, key: str):
        """
        Remove a styling element/dictionary from the stack by its identifying key name.

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
            self.current_style.update(old_styles)
            if match == key:
                break

    def _add_text(self, text: str):
        """
        Add another bit of text using the current style, and index the text's style appropriately.

        :param text:
        """
        chunk = self.create_styled_text_chunk(text)
        self.layout_rect_queue.append(chunk)

    def create_styled_text_chunk(self, text: str):
        """
        Create a styled text chunk from the input text string and the current style.

        :param text: The text to style up into a chunk.
        :return: A text 'chunk' all in the same style.
        """
        chunk_font = self.ui_theme.get_font_dictionary().find_font(
            font_name=self.current_style["font_name"],
            font_size=self.current_style["font_size"],
            bold=self.current_style["bold"],
            italic=self.current_style["italic"],
            antialiased=self.current_style["antialiased"],
            script=self.current_style["script"],
            direction=self.current_style["direction"],
        )

        if self.current_style["link"]:
            should_underline = (
                self.current_style["underline"]
                or self.link_style["link_normal_underline"]
            )

            return HyperlinkTextChunk(
                self.current_style["link_href"],
                text,
                chunk_font,
                should_underline,
                colour=self.link_style["link_text"],
                bg_colour=self.current_style["bg_colour"],
                hover_colour=self.link_style["link_hover"],
                active_colour=self.link_style["link_selected"],
                hover_underline=self.link_style["link_hover_underline"],
                text_shadow_data=self.current_style["shadow_data"],
                effect_id=self.current_style["effect_id"],
            )
        else:
            using_default_text_colour = (
                self.current_style["font_colour"] == self.default_style["font_colour"]
            )

            return TextLineChunkFTFont(
                text,
                chunk_font,
                self.current_style["underline"],
                colour=self.current_style["font_colour"],
                using_default_text_colour=using_default_text_colour,
                bg_colour=self.current_style["bg_colour"],
                text_shadow_data=self.current_style["shadow_data"],
                effect_id=self.current_style["effect_id"],
            )

    @staticmethod
    def _is_legal_hex_colour(col):
        if col is not None and len(col) > 0 and col[0] == "#" and len(col) in {7, 9}:
            for col_index in range(1, len(col)):
                col_letter = col[col_index]
                if col_letter not in [
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "a",
                    "A",
                    "b",
                    "B",
                    "c",
                    "C",
                    "d",
                    "D",
                    "e",
                    "E",
                    "f",
                    "F",
                ]:
                    return False
            return True
        return False
