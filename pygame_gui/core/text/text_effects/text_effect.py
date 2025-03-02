class TextEffect:
    """
    Base class for text effects
    """

    # pylint: disable=unused-argument
    def has_text_changed(self) -> bool:
        """
        Stub that returns False

        :return: False
        """
        return False

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
