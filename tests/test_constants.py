import pytest

from pygame_gui import UITextEffectType
from pygame_gui.core.colour_parser import is_valid_colour_string
from pygame_gui._constants import __colourNames__


class TestConstants:
    """
    Testing the Constants
    """

    def test_ui_text_effect_type(self):
        text_effect_type = UITextEffectType("test")

        assert "basic " + text_effect_type == "basic test"
        assert text_effect_type + " this" == "test this"
        assert text_effect_type == "test"
        assert text_effect_type != 5

        with pytest.raises(AttributeError):
            5 + text_effect_type

        with pytest.raises(AttributeError):
            text_effect_type + 5
        
    def test_colours(self):
        invalidColoursFound: tuple[str, str] = {}
        for colourName, colourValue in __colourNames__.items():
            if not is_valid_colour_string(colourValue):
                invalidColoursFound[colourName] = colourValue

        if len(invalidColoursFound) > 0:
            pytest.fail(f'Found Invalid Colour Name Pairs: { invalidColoursFound  }')
        assert len(invalidColoursFound) == 0
            

