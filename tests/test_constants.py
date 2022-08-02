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
