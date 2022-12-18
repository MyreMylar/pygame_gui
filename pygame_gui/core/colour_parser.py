import pygame
from typing import Callable, Union, Iterable, TypeVar, TypedDict, NamedTuple
import enum
import warnings
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.utility import premul_col
from pygame_gui._constants import __colourNames__

class NumParserType(enum.Flag):
    INT = "INT"
    FLOAT = "FLOAT"
    PERCENTAGE = "PERCENTAGE"
    DEGREE = "DEGREE"
    U8 = "U8"

T = TypeVar("T")

# Supported color strings: Hex, RGB, HSL

def is_num_str(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False

def is_int_str(string: str) -> bool:
    return is_num_str(string) and not "." in string

def is_float_str(string: str):
    return is_num_str(string) and "." in string

def is_degree_string(strdata: str) -> bool:
    if len(strdata) > 0:
        if strdata.endswith("deg") and len(strdata) > 3:
            if is_int_str(strdata[:-3]):
                degrees = int(strdata[:-3]) 
                return degrees >= 0 and degrees <= 360
        elif is_int_str(strdata):
            degrees = int(strdata)
            return degrees >= 0 and degrees <= 360
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
            return floatvalue >= 0 and floatvalue <= 1
    return False

def parse_percentage_string(strdata: str) -> float:
    if is_float_str(strdata):
        return float(strdata)
    return float(strdata[:-1]) / 100

def is_u8_string(strdata: str) -> bool:
    return is_int_str(strdata) and int(strdata) >= 0 and int(strdata) <= 255

def parse_u8_string(strdata: str) -> int:
    return int(strdata)

ColorValueValidator = Callable[[str], bool]
ColorValueParser = Callable[[str], T]
class ColorValueParserData(TypedDict):
    validator: ColorValueValidator
    parser: ColorValueParser

valueParsers: dict[NumParserType, ColorValueParserData] = {
    NumParserType.PERCENTAGE: { "validator": is_percentage_string, "parser": parse_percentage_string },
    NumParserType.U8: { "validator": is_u8_string, "parser": parse_u8_string },
    NumParserType.DEGREE: { "validator": is_degree_string, "parser": parse_degree_string },
    NumParserType.FLOAT: { "validator": is_float_str, "parser": lambda string: float(string) },
    NumParserType.INT: { "validator": is_int_str, "parser": lambda string: int(string) }
} 

colorModelSchemas: dict[str, list[NumParserType]] = {
    "hsl": [NumParserType.DEGREE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE],
    "rgb": [NumParserType.U8, NumParserType.U8, NumParserType.U8],
    "rgba": [NumParserType.U8, NumParserType.U8, NumParserType.U8, NumParserType.U8],
    "cmy": [NumParserType.PERCENTAGE, NumParserType.PERCENTAGE, NumParserType.PERCENTAGE]
}

def validate_color_model(strdata: str, name: str, types: list[NumParserType]) -> bool:
    if strdata.lower().startswith(f'{name}(') and strdata.endswith(")"):
        componentStrings = [ component.strip() for component in strdata[(len(name) + 1):-1].split(",") ]
        if len(types) == len(componentStrings):
            return all([ valueParsers[types[i]]["validator"](componentStrings[i]) for i in range(len(componentStrings)) ])
    return False

def parse_color_model(strdata: str, name: str, types: list[NumParserType]) -> tuple:
    if strdata.lower().startswith(f'{name}(') and strdata.endswith(")"):
        componentStrings = [ component.strip() for component in strdata[(len(name) + 1):-1].split(",") ]
        return [ valueParsers[types[i]]["parser"](componentStrings[i]) for i in range(len(componentStrings)) ]

def is_valid_hex_string(strdata: str) -> bool:
    hexdigits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    validLengths = [4, 5, 7, 9]
    if strdata.startswith("#"):
        if len(strdata) in validLengths:
            return all([ ch.lower() in hexdigits for ch in strdata[1:] ])
    return False

def is_valid_rgba_string(strdata: str) -> bool:
    return validate_color_model(strdata, "rgba", colorModelSchemas["rgba"])

def parse_rgba_string(strdata: str) -> pygame.Color:
    return pygame.Color(*parse_color_model(strdata, "rgba", colorModelSchemas["rgba"]))

def expand_shorthand_hex(strdata: str):
    return ("#" + "".join([ ch * 2 for ch in strdata[1:] ]) ).lower()

def parse_hex_string(strdata: str) -> pygame.Color:
    if len(strdata) == 4 or len(strdata) == 5:
        return pygame.Color(expand_shorthand_hex(strdata))
    return pygame.Color(strdata.lower())
    
def is_valid_cmy_string(strdata: str) -> bool:
    return validate_color_model(strdata, "cmy", colorModelSchemas["cmy"])

def parse_cmy_string(strdata: str) -> pygame.Color:
    color = pygame.Color(0, 0, 0)
    color.cmy = parse_color_model(strdata, "cmy", colorModelSchemas["cmy"]) 
    return color

def is_valid_hsl_string(strdata: str) -> bool:
    return validate_color_model(strdata, "hsl", colorModelSchemas["hsl"])

def parse_hsl_string(strdata: str) -> pygame.Color:
    color = pygame.Color(0, 0, 0)
    hsl = parse_color_model(strdata, "hsl", colorModelSchemas["hsl"]) 
    color.hsla = (hsl[0], int(hsl[1] * 100), int(hsl[2] * 100), 100)
    return color

def parse_rgb_string(strdata: str) -> pygame.Color:
    return pygame.Color(*parse_color_model(strdata, "rgb", colorModelSchemas["rgb"]))

def is_valid_rgb_string(strdata: str):
    return validate_color_model(strdata, "rgb", colorModelSchemas["rgb"])

ColorStringValidator = Callable[[str], bool]
ColorStringParser = Callable[[str], pygame.Color]
_colorParsers: list[tuple[ColorStringValidator, ColorStringParser]] = [
    (is_valid_hex_string, parse_hex_string),
    (is_valid_rgb_string, parse_rgb_string),
    (is_valid_hsl_string, parse_hsl_string),
    (is_valid_cmy_string, parse_cmy_string),
    (is_valid_rgba_string, parse_rgba_string) ]

def is_valid_color_string(strdata: str) -> bool:
    return strdata in __colourNames__ or any([ validator(strdata) for validator, _ in _colorParsers])

def parse_color_string(strdata: str) -> Union[pygame.Color, ColourGradient] | None:
    if strdata in __colourNames__:
        return pygame.Color(__colourNames__[strdata])
    for validator, parser in _colorParsers:
        if validator(strdata):
            return parser(strdata)
    return None

def has_unclosed_parentheses(strdata: str):
    unclosedParenteses = 0
    for ch in strdata:
        if ch == "(":
            unclosedParenteses += 1
        elif ch == ")":
            unclosedParenteses -= 1
        if unclosedParenteses < 0:
            return True
    return unclosedParenteses == 0

def may_be_gradient_string(strdata: str) -> bool:
    unclosedParentheses = 0
    commasOutsideParentheses = 0
    for ch in strdata:
        if ch == "," and unclosedParentheses == 0:
            commasOutsideParentheses += 1
        if ch == "(":
            unclosedParentheses += 1
        if ch == ")":
            unclosedParentheses -= 1
    return unclosedParentheses == 0 and commasOutsideParentheses > 0

def get_commas_outside_parentheses(strdata: str) -> list[int]:
    unclosedParentheses = 0
    commaIndicesOutsideParentheses = []
    for i in range(len(strdata)):
        ch = strdata[i]
        if ch == "," and unclosedParentheses == 0:
            commaIndicesOutsideParentheses.append(i)
        if ch == "(":
            unclosedParentheses += 1
        if ch == ")":
            unclosedParentheses -= 1
    return commaIndicesOutsideParentheses

def split_string_at_indices(strdata: str, indices: Iterable[int]) -> list[str]:
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
    validGradientLengths = [3, 4]
    if may_be_gradient_string(strdata):
        gradientData = split_string_at_indices(strdata, get_commas_outside_parentheses(strdata))
        if len(gradientData) in validGradientLengths:
            if is_degree_string(gradientData[-1]):
                    colorStrings = gradientData[:-1]
                    return all([  is_valid_color_string(color) for color in colorStrings ])
    return False

def parse_color_or_gradient(strdata: str) -> Union[pygame.Color, ColourGradient] | None:
    warningHeader: str = fr'Invalid gradient "{strdata}": '
    validGradientLengths = [3, 4]
    if may_be_gradient_string(strdata):
        gradientData = split_string_at_indices(strdata, get_commas_outside_parentheses(strdata))
        if len(gradientData) in validGradientLengths:
            if is_degree_string(gradientData[-1]):
                gradient_direction = parse_degree_string(gradientData[-1])
                colorStrings = gradientData[:-1]
                if all([  is_valid_color_string(color) for color in colorStrings ]):
                    colors = [ premul_col(parse_color_string(color)) for color in colorStrings ]
                    return ColourGradient(gradient_direction, *colors)
                else:
                    warnings.warn(fr'{warningHeader} Invalid colour strings {[ colorString for colorString in colorStrings if not is_valid_color_string(colorString) ] } in gradient definition')
            else:
                warnings.warn(fr'{warningHeader} Final argument of gradient must be an integer or a degree between the values of 0 and 360, was given a non degree value of {gradientData[-1]}')
        else:
            warnings.warn(fr'{warningHeader} Too many arguments given to gradient data, must be a comma separated list of either 2 or 3 colors with final value between 0 to 360 to declare the angle of the gradient')
    elif is_valid_color_string(strdata):
        return parse_color_string(strdata)
    else:
        warnings.warn(fr'{warningHeader} String data "{strdata}" could not be determined as a gradient string nor a color string')
    return None