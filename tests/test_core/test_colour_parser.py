import pytest
import pygame
from pygame_gui.core.colour_parser import parse_degree_string, is_u8_string, is_degree_string, is_percentage_string, parse_colour_or_gradient_string, is_valid_colour_string, is_valid_gradient_string


class TestColourParsing:
    def test_rgb(self, _init_pygame):
        assert parse_colour_or_gradient_string("rgb(20, 30, 50)") == pygame.Color(20, 30, 50)

    def test_rgb_out_of_range(self, _init_pygame):
        assert is_valid_colour_string("rgb(-20, 30, 50") is False

    def test_cmy_int(self, _init_pygame):
        assert is_valid_colour_string("cmy(20, 0.5, 0.3)") is False

    def test_degree_string_unit(self, _init_pygame):
        assert is_valid_colour_string("hsl(30deg, 0.5, 0.5)") is True

    def test_percentage_and_float(self, _init_pygame):
        assert is_valid_colour_string("cmy(20%, 0.20, 40%)") is True

    def test_rgb_above_range(self, _init_pygame):
        assert is_valid_colour_string("rgb(260, 200, 150)") is False

    def test_hex_shorthand(self, _init_pygame):
        assert is_valid_colour_string("#fa2") is True

    def test_hex_shorthand_alpha(self, _init_pygame):
        assert is_valid_colour_string("#fa2f") is True

    def test_hex_alpha(self, _init_pygame):
        assert is_valid_colour_string("#ff2389ad") is True

    def test_hex_capitalized(self, _init_pygame):
        assert is_valid_colour_string("#FA3CB4") is True

    def test_hex_digit_out_of_range(self, _init_pygame):
        assert is_valid_colour_string("#FG2R40") is False

    def test_double_gradient(self, _init_pygame):
        assert is_valid_gradient_string("#446A3B,#23AC67,30") is True

    def test_gradient_degree_unit(self, _init_pygame):
        assert is_valid_gradient_string("#446A3B,#23AC67,30deg") is True

    def test_gradient_rgb_hex(self, _init_pygame):
        assert is_valid_gradient_string("rgb(30, 40, 100),#23AC67,30deg") is True

    def test_rgb_double_comma(self, _init_pygame):
        assert is_valid_colour_string("rgb(30, 40,, 100)") is False

    def test_rgb_double_parentheses(self, _init_pygame):
        assert is_valid_colour_string("rgb(30, 40,, 100))") is False

    def test_rgb_capitalized(self, _init_pygame):
        assert is_valid_colour_string("RGB(30, 40, 100)") is True

    def test_cmy_capitalized(self, _init_pygame):
        assert is_valid_colour_string("CMY(0.30, 0.40, 0.100)") is True

    def test_hsl_capitalized(self, _init_pygame):
        assert is_valid_colour_string("HSL(30deg, 0.40, 0.100)") is True

    def test_float_without_leading_zeros(self, _init_pygame):
        assert is_valid_colour_string("cmy(.30, .40, .100)") is True

    def test_triple_gradient(self, _init_pygame):
        assert is_valid_gradient_string("rgb(20, 30, 40),cmy(0.2, 0.5, 0.7),hsl(40deg, 50%, 70%),30deg") is True

    def test_quadruple_gradient(self, _init_pygame):
        assert is_valid_gradient_string("rgb(20, 30, 40),cmy(0.2, 0.5, 0.7),hsl(40deg, 50%, 70%),#32FC95,30deg") is False

    def test_no_colour_gradient(self, _init_pygame):
        assert is_valid_gradient_string(",30deg") is False

    def test_reverse_order_gradient(self, _init_pygame):
        assert is_valid_gradient_string("30deg,#222,#888") is False

    def test_misspelled_degree_unit(self, _init_pygame):
        assert is_valid_colour_string("hsl(30deb, 0.2, 0.4)") is False

    def test_nested_colour(self, _init_pygame):
        assert is_valid_colour_string("rgb(rgb(0, 5, 3), 11, 22)") is False

    def test_double_opening_parentheses(self, _init_pygame):
        assert is_valid_colour_string("rgb((0, 30, 50)") is False

    def test_leading_comma_in_parentheses(self, _init_pygame):
        assert is_valid_colour_string("cmy(,0.3, 0.4, 0.5)") is False

    def test_trailing_comma_in_parentheses(self, _init_pygame):
        assert is_valid_colour_string("hsl(40, 0.5, 0.6,)") is False

    def test_trailing_gradient_comma(self, _init_pygame):
        assert is_valid_colour_string("#222,#ccc,45deg,") is False

    def test_hex_shorthand_alpha_parsing(self, _init_pygame):
        assert (parse_colour_or_gradient_string("#ffff") == pygame.Color(255, 255, 255, 255)) is True

    def test_hex_shorthand_parsing(self, _init_pygame):
        assert (parse_colour_or_gradient_string("#fff") == pygame.Color(255, 255, 255)) is True

    def test_rgba_validity(self, _init_pygame):
        assert is_valid_colour_string("rgba(0, 20, 40, 30)") is True

    def test_rgb_too_many_components(self, _init_pygame):
        assert is_valid_colour_string("rgb(0, 30, 50, 70)") is False

    def test_rgb_too_little_components(self, _init_pygame):
        assert is_valid_colour_string("rgb(0, 30)") is False

    def test_reversed_parentheses(self, _init_pygame):
        assert is_valid_colour_string("rgb)0, 40, 50(") is False

    def test_reversed_parentheses_gradient(self, _init_pygame):
        assert is_valid_gradient_string("rgb)0, 40, 50(,#fff,40") is False

    def test_hsv_string(self, _init_pygame):
        assert is_valid_colour_string("hsv(30deg, 0.4, 40%)") is True

    def test_hsva_string(self, _init_pygame):
        assert is_valid_colour_string("hsva(40, 40%, 20%, 70%)") is True

    def test_hsva_string(self, _init_pygame):
        assert is_valid_colour_string("hsla(160deg, 72%, 25%, 32%)") is True

    def test_space_separated(self, _init_pygame):
        assert is_valid_colour_string("rgb(20 20 20)") is False

    def test_space_and_comma_separated(self, _init_pygame):
        assert is_valid_colour_string("rgb(20, 20 20") is False

    def test_spaces_in_gradient(self, _init_pygame):
        assert is_valid_gradient_string("#f2f, hsv(30, 0.5, 0.8), 50deg") is True

    def test_whitespace_at_start(self, _init_pygame):
        assert is_valid_colour_string("   rgb(20, 50, 80)") is False

    def test_whitespace_at_end(self, _init_pygame):
        assert is_valid_colour_string("rgb(20, 50, 80)    ") is False

    def test_whitespace_on_ends(self, _init_pygame):
        assert is_valid_colour_string("   rgb(20, 50, 80)    ") is False

    def test_rgb_floats(self, _init_pygame):
        assert is_valid_colour_string("rgb(3.5, 70, 100)") is False

    def test_is_u8_above_range(self, _init_pygame):
        assert is_u8_string("257") is False

    def test_is_u8_below_range(self, _init_pygame):
        assert is_u8_string("-2") is False

    def test_is_u8_on_bounds(self, _init_pygame):
        assert is_u8_string("0") is True and is_u8_string("255") is True and is_u8_string("-1") is False and is_u8_string("257") is False

    def test_u8_float(self, _init_pygame):
        assert is_u8_string("4.3") is False

    def test_degree_on_bounds(self, _init_pygame):
        assert is_degree_string("0") is True and is_degree_string("360") is True and is_degree_string("-361") is False and is_degree_string("361") is False

    def test_degree_unit(self, _init_pygame):
        assert is_degree_string("40deg") is True
    
    def test_degree_only_unit(self, _init_pygame):
        assert is_degree_string("deg") is False
    
    def test_percentage_only_sign(self, _init_pygame):
        assert is_percentage_string("%") is False

    def test_percentage_float_and_sign(self, _init_pygame):
        assert is_percentage_string("37.5%") is False

    def test_degree_unit_optionality(self, _init_pygame):
        assert parse_degree_string("40") == parse_degree_string("40deg")

    def test_gradient_colour_names(self, _init_pygame):
        assert is_valid_gradient_string("red,blue,40") is True

    def test_gradient_colour_names_three(self, _init_pygame):
        assert is_valid_gradient_string("red,green,blue,60deg") is True



if __name__ == "__main__":
    pytest.console_main()