class TextEffect:
    """
    Base class for text effects
    """
    def __init__(self):
        self._text_changed = False

    def update(self, time_delta: float):
        """
        Stub for overriding.

        :param time_delta: time in seconds since last frame.
        """

    # pylint: disable=unused-argument
    def get_final_alpha(self) -> int:
        """
        The alpha value to draw the text box with. By default, it is 255.

        :return: The default alpha value for a text box.
        """
        return 255

    def apply_effect(self):
        """
        Apply the effect to the text
        """

    @property
    def text_changed(self):
        return self._text_changed

    @text_changed.setter
    def text_changed(self, value: bool):
        self._text_changed = value

    def has_text_changed(self) -> bool:
        """
        Test if we should redraw the text.

        :return: True if we should redraw, False otherwise.
        """
        if self.text_changed:
            self.text_changed = False
            return True
        else:
            return False
