import pytest

from pygame_gui import UITextEffectType


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
