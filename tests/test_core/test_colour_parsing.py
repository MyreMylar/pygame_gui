import pytest
import pygame
from pygame_gui.core.colour_parser import parse_color_or_gradient, is_valid_color_string, is_valid_gradient_string


class TestColourParsing:
    def test_rgb(self, _init_pygame):
        assert parse_color_or_gradient("rgb(20, 30, 50)") == pygame.Color(20, 30, 50)

    def test_rgb_out_of_range(self, _init_pygame):
        assert is_valid_color_string("rgb(-20, 30, 50") is False

    def test_cmy_int(self, _init_pygame):
        assert is_valid_color_string("cmy(20, 0.5, 0.3)") is False

    def test_degree_string_unit(self, _init_pygame):
        assert is_valid_color_string("hsl(30deg, 0.5, 0.5)") is True

    def test_percentage_and_float(self, _init_pygame):
        assert is_valid_color_string("cmy(20%, 0.20, 40%)") is True

    def test_rgb_above_range(self, _init_pygame):
        assert is_valid_color_string("rgb(260, 200, 150)") is False

    def test_hex_shorthand(self, _init_pygame):
        assert is_valid_color_string("#fa2") is True

    def test_hex_shorthand_alpha(self, _init_pygame):
        assert is_valid_color_string("#fa2f") is True

    def test_hex_alpha(self, _init_pygame):
        assert is_valid_color_string("#ff2389ad") is True

    def test_hex_capitalized(self, _init_pygame):
        assert is_valid_color_string("#FA3CB4") is True

    def test_hex_digit_out_of_range(self, _init_pygame):
        assert is_valid_color_string("#FG2R40") is False

    def test_double_gradient(self, _init_pygame):
        assert is_valid_gradient_string("#446A3B,#23AC67,30") is True

    def test_gradient_degree_unit(self, _init_pygame):
        assert is_valid_gradient_string("#446A3B,#23AC67,30deg") is True

    def test_gradient_rgb_hex(self, _init_pygame):
        assert is_valid_gradient_string("rgb(30, 40, 100),#23AC67,30deg") is True

    def test_rgb_double_comma(self, _init_pygame):
        assert is_valid_color_string("rgb(30, 40,, 100)") is False

    def test_rgb_double_parentheses(self, _init_pygame):
        assert is_valid_color_string("rgb(30, 40,, 100))") is False

    def test_rgb_capitalized(self, _init_pygame):
        assert is_valid_color_string("RGB(30, 40, 100)") is True

    def test_cmy_capitalized(self, _init_pygame):
        assert is_valid_color_string("CMY(0.30, 0.40, 0.100)") is True

    def test_hsl_capitalized(self, _init_pygame):
        assert is_valid_color_string("HSL(30deg, 0.40, 0.100)") is True

    def test_float_without_leading_zeros(self, _init_pygame):
        assert is_valid_color_string("cmy(.30, .40, .100)") is True

    def test_triple_gradient(self, _init_pygame):
        assert is_valid_gradient_string("rgb(20, 30, 40),cmy(0.2, 0.5, 0.7),hsl(40deg, 50%, 70%),30deg") is True

    def test_quadruple_gradient(self, _init_pygame):
        assert is_valid_gradient_string("rgb(20, 30, 40),cmy(0.2, 0.5, 0.7),hsl(40deg, 50%, 70%),#32FC95,30deg") is False

    def test_no_color_gradient(self, _init_pygame):
        assert is_valid_gradient_string(",30deg") is False

    def test_reverse_order_gradient(self, _init_pygame):
        assert is_valid_gradient_string("30deg,#222,#888") is False

    def test_misspelled_degree_unit(self, _init_pygame):
        assert is_valid_color_string("hsl(30deb, 0.2, 0.4)") is False

    def test_nested_color(self, _init_pygame):
        assert is_valid_color_string("rgb(rgb(0, 5, 3), 11, 22)") is False

    def test_double_opening_parentheses(self, _init_pygame):
        assert is_valid_color_string("rgb((0, 30, 50)") is False

    def test_leading_comma_in_parentheses(self, _init_pygame):
        assert is_valid_color_string("cmy(,0.3, 0.4, 0.5)") is False

    def test_trailing_comma_in_parentheses(self, _init_pygame):
        assert is_valid_color_string("hsl(40, 0.5, 0.6,)") is False

    def test_trailing_gradient_comma(self, _init_pygame):
        assert is_valid_color_string("#222,#ccc,45deg,") is False

    def test_hex_shorthand_alpha_parsing(self, _init_pygame):
        assert (parse_color_or_gradient("#ffff") == pygame.Color(255, 255, 255, 255)) is True

    def test_hex_shorthand_parsing(self, _init_pygame):
        assert (parse_color_or_gradient("#fff") == pygame.Color(255, 255, 255)) is True

    def test_rgba_validity(self, _init_pygame):
        assert is_valid_color_string("rgba(0, 20, 40, 30)") is True

    def test_rgb_too_many_components(self, _init_pygame):
        assert is_valid_color_string("rgb(0, 30, 50, 70)") is False

    def test_rgb_too_little_components(self, _init_pygame):
        assert is_valid_color_string("rgb(0, 30)") is False
    



if __name__ == "__main__":
    pytest.main()