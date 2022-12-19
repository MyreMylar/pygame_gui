import pytest

from pygame_gui import UITextEffectType
from pygame_gui.core.colour_parser import is_valid_colour_string
from pygame_gui._constants import _namedColours


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
        """The only real requirement for a colour name is that it is not case sensitive.
        As convention, the colour name should always be stored as a lower cased string, so that any colour name compared to the string can simply be lowered with .lower() for checking validity
        """
        errorMessages: list[str] = []
        for colourName, colourValue in _namedColours.items():
            if not colourName == colourName.lower():
                errorMessages.append(f'Found Invalid Colour Name: {colourName} (must be lowercased)')
            if not is_valid_colour_string(colourValue):
                errorMessages.append(f'Found Invalid Colour Name Pair: {colourName}, {colourValue}')

        if len(errorMessages) > 0:
            pytest.fail("\n".join(errorMessages))
        assert len(errorMessages) == 0
            

