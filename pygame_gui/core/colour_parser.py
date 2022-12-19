"""
pygame_gui.core.colour_parser.py
A Functional Based Module for the parsing of Colour Strings in pygame_gui

Use Notes:
    Mostly all that one will ever need is these 5 functions 
        - **parse_colour_or_gradient_string**: Attempt to parse a string that may be a colour or gradient into its respective value
        - **is_valid_colour_string**: Check if a string represents a valid pygame Color
        - **is_valid_gradient_string**: Check if a string represents a valid ColourGradient
        - **parse_colour_string**: Parse a string into a pygame Color
        - **parse_gradient_string**: Parse a string into a ColourGradient
        
    The documentation for what counts as a 'Valid' colour and gradient string can be found in the Theme Guide of the pygame_gui documentation at https://pygame-gui.readthedocs.io/en/v_065/theme_guide.html

Developer Notes:
    How it Works:
        This module works through pairs of validating and parsing functions at the value, colour, and gradient levels
        Hopefully everything should be generic enough that any new colour models or representations can be easily added without much bloat or *magic*

        Parsing A Colour:
            Simply, The parsing of a colour is done by simply checking if there is any valid function cashed in the _colourParsers dictionary, then calling the paired parsing function to get its value
            Therefore, this system is not concrete at all, and should be extremely extensible to add **any 2 functions that can validate and parse a developer-determined schema**

        Parsing A Gradient:
            As of now, the gradient parser is implemented in such a way where it assumes that all commas outside an enclosing glyph ( Any comma not inside of a (), [], or {} ) is a separator in a gradient list
            Generally, if creating new colour string schemas, this will break if there is a new colour which uses commas not enclosed in a glyph. This shouldn't be a problem right now, but it is worth noting as a warning in case of any additions to this parser
            TL,DR: Dev life will be easier if it is ensured that commas in colour schemas are inside of parentheses, brackets, or curly braces ( like "rgb(20, 20, 20)" )
"""

import pygame
from typing import Callable, Union, Iterable, TypeVar, TypedDict, Optional, List, Tuple, Set
import enum
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.utility import premul_col
from pygame_gui._constants import _namedColours


class NumParserType(enum.Enum):
    """Enum for the supported value types in colour strings"""
    INT = "INT"
    FLOAT = "FLOAT"
    PERCENTAGE = "PERCENTAGE"
    DEGREE = "DEGREE"
    U8 = "U8"


T = TypeVar("T")


def is_num_str(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False


def is_int_str(string: str) -> bool:
    return is_num_str(string) and "." not in string


def is_float_str(string: str):
    return is_num_str(string) and "." in string


def is_degree_string(strdata: str) -> bool:
    if len(strdata) > 0:
        if strdata.endswith("deg") and len(strdata) > 3:
            if not is_int_str(strdata[:-3]):
                pass
            else:
                degrees = int(strdata[:-3])
                return 0 <= degrees <= 360
        elif is_int_str(strdata):
            degrees = int(strdata)
            return 0 <= degrees <= 360
    return False


def parse_degree_string(strdata: str) -> int:
    if len(strdata) > 0:
        if strdata.endswith("deg"):
            return int(strdata[:-3])
        return int(strdata)


def is_percentage_string(strdata: str) -> bool:
    if len(strdata) > 0:
        if strdata[-1] == "%" and is_int_str(strdata[:-1]):
            return True

        if is_float_str(strdata):
            floatvalue = float(strdata)
            return 0 <= floatvalue <= 1
    return False


def parse_percentage_string(strdata: str) -> float:
    if is_float_str(strdata):
        return float(strdata)
    return float(strdata[:-1]) / 100


def is_u8_string(strdata: str) -> bool:
    return is_int_str(strdata) and 0 <= int(strdata) <= 255


def parse_u8_string(strdata: str) -> int:
    return int(strdata)


ColourValueValidator = Callable[[str], bool]
ColourValueParser = Callable[[str], T]


class ColourValueParserData(TypedDict):
    validator: ColourValueValidator
    parser: ColourValueParser


_valueParsers: dict[NumParserType, ColourValueParserData] = {
    NumParserType.PERCENTAGE: {"validator": is_percentage_string, "parser": parse_percentage_string},
    NumParserType.U8: {"validator": is_u8_string, "parser": parse_u8_string},
    NumParserType.DEGREE: {"validator": is_degree_string, "parser": parse_degree_string},
    NumParserType.FLOAT: {"validator": is_float_str, "parser": lambda string: float(string)},
    NumParserType.INT: {"validator": is_int_str, "parser": lambda string: int(string)}
}
""" A mapping for each NumParserType to its corresponding validator and parser for strings of that type's specification  """

_colourModelSchemas: dict[str, list[NumParserType]] = {
    "hsl": [NumParserType.DEGREE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
    "hsla": [NumParserType.DEGREE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
    "hsv": [NumParserType.DEGREE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
    "hsva": [NumParserType.DEGREE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
    "rgb": [NumParserType.U8, NumParserType.U8, NumParserType.U8],
    "rgba": [NumParserType.U8, NumParserType.U8, NumParserType.U8, NumParserType.U8],
    "cmy": [NumParserType.PERCENTAGE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
}
"""Mapping for each supported colour model to the values that they take in"""


def validate_colour_model(strdata: str, name: str, types: list[NumParserType]) -> bool:
    """Use a colour model's name and types (generally denoted by its name in the _colourModelSchemas dictionary) to validate its use
        Developer Notes:
            - This function depends on the validator of each value type being present in the _valueParsers dictionary
            - This function assumes that the colour model also takes up the form "name(value, value...)"
    
    :param strdata: the colour model string to validate
    :type strdata: str
    :param name: the name of the colour model
    :type name: str
    :param types: the types of the values in the colour model in order, used to validate each value individually
    :type types: list[NumParserType]
    :return: A boolean on whether the colour model could find a working validator
    :rtype: bool
    """

    if strdata.lower().startswith(f'{name}(') and strdata.endswith(")"):
        component_strings = [component.strip() for component in strdata[(len(name) + 1):-1].split(",")]
        if len(types) == len(component_strings):
            if all([valueParserType in _valueParsers for valueParserType in types]):
                return all(
                    [_valueParsers[types[i]]["validator"](component_strings[i]) for i in range(len(component_strings))])
    return False


def parse_colour_model(strdata: str, name: str, types: list[NumParserType]) -> list[T]:
    """Use a colour model's name and types (generally denoted by its name in the _colourModelSchemas dictionary) to return a tuple of its containing values
        Developer Notes:
            - This function depends on the parser of each value type being present in the _valueParsers dictionary
            - This function assumes that the strdata parameter has **already been validated** against the validate_colour_model function
            - This function assumes that the colour model also takes up the form "name(value, value...)"
    
    :param strdata: the colour model string to parse
    :type strdata: str
    :param name: the name of the colour model
    :type name: str
    :param types: the types of the values in the colour model in order, used to parse each value individually
    :type types: list[NumParserType]
    :return: A tuple containing all the parsed values in the colour model
    :rtype: tuple
    :raises ValueError: if the colour model does not meet the standard <name(value, ...)> schema
    :raises KeyError: if the colour model cannot find the parser for a given type or the given type is not defined to have a parser
    """

    if strdata.lower().startswith(f'{name}(') and strdata.endswith(")"):
        component_strings = [component.strip() for component in strdata[(len(name) + 1):-1].split(",")]
        return [_valueParsers[types[i]]["parser"](component_strings[i]) for i in range(len(component_strings))]
    raise ValueError(
        fr'Given string data {strdata} does not meet the generic colour model schema <name(value, value, ...)>, always validate the colour model string first before parsing')


def is_valid_hex_string(strdata: str) -> bool:
    """Validate Hex Color string in the format "#FFF", "#FFFF", "#FFFFFF", or "#FFFFFFFF" 
        Value Parameter Descriptions:
            F: any hexadecimal digit between 0 and F inclusive
        Examples:
            - "#A3F" (Shorthand)
            - "#98C4" (Shorthand with Alpha)
            - "#F3FAFF" (Full)
            - "#BD24A017" (Full with Alpha)
        
    :param strdata: the hex string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined hex schema
    :rtype: bool
    """

    hexdigits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    valid_lengths = [4, 5, 7, 9]
    if strdata.startswith("#"):
        if len(strdata) in valid_lengths:
            return all([ch.lower() in hexdigits for ch in strdata[1:]])
    return False


def expand_shorthand_hex(strdata: str) -> str:
    """Expand a Shorthand Hex Color
        Example:
            #FA2 -> #FFAA22

    :param strdata: the hex string to expand
    :type strdata: str
    :returns: An expanded hex string
    :rtype: str
    """

    return ("#" + "".join([ch * 2 for ch in strdata[1:]])).lower()


def parse_hex_string(strdata: str) -> pygame.Color:
    """Parse Hex Color string in the formats "#FFF", "#FFFF", "#FFFFFF", or "#FFFFFFFF" 
        Value Parameter Descriptions:
            - **F**: any hexadecimal digit between 0 and F inclusive
        Examples:
            - "#A3F" (Shorthand)
            - "#98C4" (Shorthand with Alpha)
            - "#F3FAFF" (Full)
            - "#BD24A017" (Full with Alpha)

    :param strdata: the hex string to parse
    :type strdata: str
    :returns: A pygame Color from the hex data parsed from strdata
    :rtype: pygame.Color
    """

    if len(strdata) in [4, 5]:
        return pygame.Color(expand_shorthand_hex(strdata))
    return pygame.Color(strdata.lower())


def is_valid_rgb_string(strdata: str):
    """Validate RGB Color string in the format "rgb(uint8, uint8, uint8)"
        Value Parameter Descriptions:
            - **uint8**: is an integer value bounded between 0 and 255
        Examples:
            - "rgb(20, 40, 80)"

    :param strdata: the rgb string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined rgb schema
    :rtype: bool
    """

    return validate_colour_model(strdata, "rgb", _colourModelSchemas["rgb"])


def parse_rgb_string(strdata: str) -> pygame.Color:
    """Parse RGB Color string in the format "rgb(uint8, uint8, uint8)" 
        Value Parameter Descriptions:
            - **uint8**: is an integer value bounded between 0 and 255
        Examples:
            - "rgb(20, 40, 80)"

    :param strdata: the rgb string to parse
    :type strdata: str
    :returns: A pygame Color from the data parsed from strdata
    :rtype: pygame.Color
    """

    return pygame.Color(*parse_colour_model(strdata, "rgb", _colourModelSchemas["rgb"]))


def is_valid_rgba_string(strdata: str) -> bool:
    """Validate RGBA Color string in the format "rgba(uint8, uint8, uint8, uint8)" 
        Value Parameter Descriptions:
            - **uint8**: is an integer value bounded between 0 and 255
        Examples:
            - "rgba(30, 241, 174, 232)"

    :param strdata: the rgba string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined rgba schema
    :rtype: bool
    """

    return validate_colour_model(strdata, "rgba", _colourModelSchemas["rgba"])


def parse_rgba_string(strdata: str) -> pygame.Color:
    """Parse RGBA Color string in the format "rgba(uint8, uint8, uint8, uint8)"
        Value Parameter Descriptions:
            - **uint8**: is an integer value bounded between 0 and 255
        Examples:
            - "rgba(30, 241, 174, 232)"

    :param strdata: the rgba string to parse
    :type strdata: str
    :returns: A pygame Color from the rgba data parsed from strdata
    :rtype: pygame.Color
    """

    return pygame.Color(*parse_colour_model(strdata, "rgba", _colourModelSchemas["rgba"]))


def is_valid_cmy_string(strdata: str) -> bool:
    """Validate CMY Color string in the format "cmy(percentage, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
        Examples:
            - "cmy(.4, .7, 80%)"

    :param strdata: the cmy string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined cmy schema
    :rtype: bool
    """

    return validate_colour_model(strdata, "cmy", _colourModelSchemas["cmy"])


def parse_cmy_string(strdata: str) -> pygame.Color:
    """Parse CMY Color string in the format "cmy(percentage, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
        Examples:
            - "cmy(.4, .7, 80%)"

    :param strdata: the cmy string to parse
    :type strdata: str
    :returns: A pygame Color from the cmy data parsed from strdata
    :rtype: pygame.Color
    """

    colour = pygame.Color(0, 0, 0)
    colour.cmy = parse_colour_model(strdata, "cmy", _colourModelSchemas["cmy"])
    return colour


def is_valid_hsl_string(strdata: str) -> bool:
    """Validate HSL Color string in the format "hsl(degree, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsl(30, 0.6, 0.7)"
            - "hsl(30deg, 40%, .5)"

    :param strdata: the hsl string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined hsl schema
    :rtype: bool
    """
    return validate_colour_model(strdata, "hsl", _colourModelSchemas["hsl"])


def parse_hsl_string(strdata: str) -> pygame.Color:
    """Parse HSL Color string in the format "hsl(degree, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsl(30, 0.6, 0.7)"
            - "hsl(30deg, 40%, .5)"


    :param strdata: the hsl string to parse
    :type strdata: str
    :returns: A pygame Color from the hsl data parsed from strdata
    :rtype: pygame.Color
    """

    colour = pygame.Color(0, 0, 0)
    hsl = parse_colour_model(strdata, "hsl", _colourModelSchemas["hsl"])
    colour.hsla = (hsl[0], int(hsl[1] * 100), int(hsl[2] * 100), 100)
    return colour


def is_valid_hsla_string(strdata: str) -> bool:
    """Validate HSLA Color string in the format "hsla(degree, percentage, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsla(30, 0.6, 0.7, 80%)"
            - "hsla(30deg, 40%, .5, 40%)"

    :param strdata: the hsla string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined hsla schema
    :rtype: bool
    """

    return validate_colour_model(strdata, "hsla", _colourModelSchemas["hsla"])


def parse_hsla_string(strdata: str) -> pygame.Color:
    """Parse HSLA Color string in the format "hsla(degree, percentage, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsla(30, 0.6, 0.7, 80%)"
            - "hsla(30deg, 40%, .5, 40%)"


    :param strdata: the hsla string to parse
    :type strdata: str
    :returns: A pygame Color from the hsla data parsed from strdata
    :rtype: pygame.Color
    """

    colour = pygame.Color(0, 0, 0)
    hsla = parse_colour_model(strdata, "hsla", _colourModelSchemas["hsla"])
    colour.hsla = (hsla[0], int(hsla[1] * 100), int(hsla[2] * 100), int(hsla[3] * 100))
    return colour


def is_valid_hsv_string(strdata: str) -> bool:
    """Validate HSLA Color string in the format "hsv(degree, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsv(50, 30%, .4)"
            - "hsv(60deg, 40%, 12%)"

    :param strdata: the hsv string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined hsv schema
    :rtype: bool
    """

    return validate_colour_model(strdata, "hsv", _colourModelSchemas["hsv"])


def parse_hsv_string(strdata: str) -> pygame.Color:
    """Parse HSV Color string in the format "hsv(degree, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsv(50, 30%, .4)"
            - "hsv(60deg, 40%, 12%)"


    :param strdata: the hsv string to parse
    :type strdata: str
    :returns: A pygame Color from the hsv data parsed from strdata
    :rtype: pygame.Color
    """

    colour = pygame.Color(0, 0, 0)
    hsv = parse_colour_model(strdata, "hsv", _colourModelSchemas["hsv"])
    colour.hsva = (hsv[0], int(hsv[1] * 100), int(hsv[2] * 100), 100)
    return colour


def parse_hsva_string(strdata: str) -> pygame.Color:
    """Parse HSVA Color string in the format "hsva(degree, percentage, percentage, percentage)"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsva(50, .3, 40%, .75)"
            - "hsva(60deg, 40%, 12%, .94)"


    :param strdata: the hsva string to parse
    :type strdata: str
    :returns: A pygame Color from the hsva data parsed from strdata
    :rtype: pygame.Color
    """

    colour = pygame.Color(0, 0, 0)
    hsva = parse_colour_model(strdata, "hsva", _colourModelSchemas["hsva"])
    colour.hsva = (hsva[0], int(hsva[1] * 100), int(hsva[2] * 100), int(hsva[3] * 100))
    return colour


def is_valid_hsva_string(strdata: str) -> bool:
    """Validate HSVA Color string in the format "*hsva(degree, percentage, percentage, percentage)*"
        Value Parameter Descriptions:
            - **percentage**: either an integer value from 0 to 100 with "%" appended at the end or a float value ranging from 0 to 1
            - **degree**: a value between 0 and 360 with the "deg" unit optionally appended to the end
        Examples:
            - "hsva(50, .3, 40%, .75)"
            - "hsva(60deg, 40%, 12%, .94)"


    :param strdata: the hsva string to validate
    :type strdata: str
    :returns: A boolean determining whether the string fits the determined hsva schema or not
    :rtype: bool
    """

    return validate_colour_model(strdata, "hsva", _colourModelSchemas["hsva"])


def is_valid_colour_name(strdata: str):
    """| Validate Colour name string to be recognizable by pygame_gui as a valid colour_name
    | As of the writing of these documentations, all colour names defined are from the CSS colours given by all major browsers, which can be found here: https://w3schools.sinsixx.com/css/css_colornames.asp.htm
    | All colour names are not case-sensitive, so RED, Red, and red all represent the same value
    
    :param strdata: the colour name to validate
    :type strdata: str
    :returns: A boolean determining whether strdata is recognized as a colour name and has a locatable colour value
    :rtype: bool
    """

    return strdata.lower() in _namedColours


def parse_colour_name(strdata: str) -> pygame.Color:
    """| Parse Colour name string into its corresponding colour value
    | As of the writing of these documentations, all colour names defined are from the CSS colours given by all major browsers, which can be found here: https://w3schools.sinsixx.com/css/css_colornames.asp.htm
    | All colour names are not case-sensitive, so RED, Red, and red all represent the same value

    :param strdata: The colour name to parse
    :type strdata: str
    :returns: A pygame Color from the colour name given by strdata
    :rtype: pygame.Color
    :raises KeyError: If the colour corresponding to the strdata passed in could not be found ( always call is_valid_colour_name first to check )
    """

    return pygame.Color(_namedColours[strdata.lower()])


ColourStringValidator = Callable[[str], bool]
ColourStringParser = Callable[[str], pygame.Color]
_colourParsers: list[tuple[ColourStringValidator, ColourStringParser]] = [
    (is_valid_colour_name, parse_colour_name),
    (is_valid_hex_string, parse_hex_string),
    (is_valid_rgb_string, parse_rgb_string),
    (is_valid_hsl_string, parse_hsl_string),
    (is_valid_cmy_string, parse_cmy_string),
    (is_valid_rgba_string, parse_rgba_string),
    (is_valid_hsla_string, parse_hsla_string),
    (is_valid_hsv_string, parse_hsv_string),
    (is_valid_hsva_string, parse_hsva_string)]
"""The list of validator and parser function pairs that will be used by is_valid_colour_string and parse_colour_string
The functions have no requirement other than the validator confirming a schema and the parser returning a pygame.Color value from the string data if it is valid
Note that if new validator and parsing formulas are added, these validators should not overlap if it can be helped, as there's no way to determine whether one colour could be more "valid" than another in that case
"""


def is_valid_colour_string(strdata: str) -> bool:
    """Validate a colour string using the available colour string validator and parsers in pygame_gui
    
    :param strdata: the colour string data to validate
    :return: A boolean on whether any valid parser could be found for the string data
    :rtype: bool
    """

    return any([validator(strdata) for validator, _ in _colourParsers])


def parse_colour_string(strdata: str) -> Optional[pygame.Color]:
    """ Parse a Color String
        Developer Notes:
            - This function uses the implemented colour parsing and colour validating functions available through _colourParsers in order to determine a proper colour data
            - Additionally, named colour strings are taken into account firstly when determining the data of the colour
            - Note that this function returns the first valid occurance that they find
    
    :param strdata: The string to parse into a Colour
    :type strdata: str 
    :return: A Pygame Color Object from the colour data parsed from strdata or None if the strdata is an invalid colour string
    :rtype: pygame.Color or None
    """

    for validator, parser in _colourParsers:
        if validator(strdata):
            return parser(strdata)
    return None


def valid_enclosing_glyphs(strdata: str) -> bool:
    """Find if each opening parenthesis in a string has a valid closing parenthesis and vice versa
        Developer Notes:
            - Used to determine which top level commas should be used to separate gradients
            - Used with the assumption that colour values themselves do not have glyphs that are left opened
    
    :param strdata: the string to check
    :type strdata: str
    :returns: A boolean determining whether each opening parenthesis has a closing parenthesis and each closing parenthesis has an open parenthesis
    :rtype: bool
    """

    glyphs: dict[str, str] = {
        ")": "(",
        "]": "[",
        "}": "{"
    }

    opening_stack: list[str] = []
    for ch in strdata:
        if ch in glyphs.values():
            opening_stack.append(ch)
        elif ch in glyphs:
            if len(opening_stack) > 0:
                if opening_stack[-1] == glyphs[ch]:
                    opening_stack.pop()
                    continue
            return False
    return len(opening_stack) == 0


def get_commas_outside_enclosing_glyphs(strdata: str) -> list[int]:
    """In the colour_parser module, This function is used to determine where to split gradient strings in order to get the full list of colours and the final degrees
        Developer Notes: 
            - Used to determine which top level commas should be used to separate gradients
            - Used with the assumption that colour values themselves do not have glyphs that are left opened
            - Used with the assumption that top level commas used to separate gradients are not within any sort of enclosing glyph
            - An **enclosing glyph** is like a parentheses, bracket, curly brace, or something of the sort

    :param strdata: the string to check
    :type strdata: str
    :returns: A list of the indices of the commas determined to be outside any enclosing parentheses
    :rtype: list[int]
    """

    glyphs: dict[str, str] = {
        ")": "(",
        "]": "[",
        "}": "{"
    }

    opening_stack = []
    comma_indices_outside_parentheses: list[int] = []

    for i in range(len(strdata)):
        ch = strdata[i]
        if ch == "," and len(opening_stack) == 0:
            comma_indices_outside_parentheses.append(i)
        if ch in glyphs.values():
            opening_stack.append(ch)
        elif ch in glyphs:
            if len(opening_stack) > 0:
                if opening_stack[-1] == glyphs[ch]:
                    opening_stack.pop()
                    continue
            return comma_indices_outside_parentheses
    return comma_indices_outside_parentheses


def may_be_gradient_string(strdata: str) -> bool:
    """Determine if a string should even be considered for validation as a gradient
        Developer Notes:
            - Determines this by determining if there are 2 or 3 commas outside any enclosing glyph and if the enclosing glyphs in the colour string are validly closed and opened.

    :param strdata: the possible gradient string to check
    :type strdata: str

    :returns: If the gradient string passes the starting check 
    :rtype: bool
    """

    return "," in strdata and valid_enclosing_glyphs(strdata) and len(get_commas_outside_enclosing_glyphs(strdata)) in [
        2, 3]


def split_string_at_indices(strdata: str, indices: Union[List[int], Set[int], Tuple[int]]) -> list[str]:
    """Works similarly to the built-in string split function, where the split data is discarded from the resultant array
        Developer Notes:
            - Used in colour_parser module to split gradient strings into their respective colour and angle components

    :param strdata: the string to split
    :type strdata: str
    :param indices: the indices to split the string at
    :type indices: Iterable[int]
    :return: A list of the split strings after cutting at the specified indices given by the 'indices' parameter
    :rtype: list[str]
    """

    splits = []
    last = 0
    for i in range(len(indices)):
        splits.append(strdata[last: indices[i]])
        last = indices[i] + 1
        if last >= len(strdata):
            return splits
    splits.append(strdata[last:])
    return splits


def is_valid_gradient_string(strdata: str) -> bool:
    """Validate a gradient string
        A gradient string should consist of a 3 or 4 length comma separated list, with the first values being any valid colour strings and the last value representing a degree angle for the direction of the gradient
        Examples:
            - "red,blue,40deg"
            - "#f23,rgb(30, 70, 230),hsv(50, 70%, 90%),50"

    :param strdata: the gradient string to validate
    :type strdata: str
    :returns: A boolean indicating whether the gradient string is valid or not
    :rtype: bool
    """

    if may_be_gradient_string(strdata):
        gradient_data = [dataComponent.strip() for dataComponent in
                         split_string_at_indices(strdata, get_commas_outside_enclosing_glyphs(strdata))]
        if is_degree_string(gradient_data[-1]):
            colour_strings = gradient_data[:-1]
            return all([is_valid_colour_string(colour) for colour in colour_strings])
    return False


def parse_gradient_string(strdata: str) -> Optional[ColourGradient]:
    """Parse a gradient string
        A gradient string should consist of a 3 or 4 length comma separated list, with the first values being any valid colour strings and the last value representing a degree angle for the direction of the gradient
        Examples:
            - "red,blue,40deg"
            - "#f23,rgb(30, 70, 230),hsv(50, 70%, 90%),50"

    :param strdata: the gradient string to validate
    :type strdata: str
    :returns: A ColourGradient object if strdata is a valid gradient string, otherwise None
    :rtype: bool or None
    """

    if is_valid_gradient_string(strdata):
        gradient_data = [dataComponent.strip() for dataComponent in
                         split_string_at_indices(strdata, get_commas_outside_enclosing_glyphs(strdata))]
        gradient_direction = parse_degree_string(gradient_data[-1])
        colours = [premul_col(parse_colour_string(colour)) for colour in gradient_data[:-1]]
        return ColourGradient(gradient_direction, *colours)
    return None


def parse_colour_or_gradient_string(strdata: str) -> Optional[Union[pygame.Color, ColourGradient]]:
    """| Parse a colour or gradient string into a pygame Color or a ColourGradient Object
    |
    | The documentation for what counts as a 'Valid' colour and gradient string, including the supported colour formats by pygame_gui, can be found in the Theme Guide of the pygame_gui documentation at https://pygame-gui.readthedocs.io/en/v_065/theme_guide.html

    :param strdata: the string data to parse into a colour or gradient
    :type strdata: str
    :return: The colour or gradient generated from the string data, or none
    :rtype: pygame.Color, ColourGradient, or None
    """

    if is_valid_gradient_string(strdata):
        return parse_gradient_string(strdata)
    elif is_valid_colour_string(strdata):
        return premul_col(parse_colour_string(strdata))
    return None
