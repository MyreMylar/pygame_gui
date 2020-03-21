class TextBoxEffect:
    """
    Base class for text box effects

    :param all_characters: All the character sin the text box.
    """
    def __init__(self, all_characters: str):
        self.all_characters = all_characters

    def should_full_redraw(self) -> bool:
        """
        Stub that returns False

        :return: False
        """
        return False

    def should_redraw_from_chunks(self) -> bool:
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
        pass

    def get_end_text_pos(self) -> int:
        """
        Returns the position to draw the text up to (e.g 1 would draw only the first character).
        By default it is the whole text.

        :return: length of self.all_characters.
        """
        return len(self.all_characters)

    def get_final_alpha(self) -> int:
        """
        The alpha value to draw the text box with. By default it is 255.

        :return: The default alpha value for a text box.
        """
        return 255


class TypingAppearEffect(TextBoxEffect):
    """
    Does that 'typewriter' effect where the text in a box appears one character at a time as if
    they were being typed by an invisible hand.

    :param all_characters: All the character sin the text box.
    """
    def __init__(self, all_characters: str):
        super().__init__(all_characters)
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_per_letter_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update. Adds a new
        letter to the progress every self.time_per_letter seconds.

        :param time_delta: time in seconds since last frame.
        """
        if self.text_progress < len(self.all_characters):
            if self.time_per_letter_acc < self.time_per_letter:
                self.time_per_letter_acc += time_delta
            else:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.time_to_redraw = True

    def should_full_redraw(self) -> bool:
        """
        Test if we should redraw the whole text box.

        TODO: Once text box is refactored change this.
              So we only redraw the new bits of added text and the last two lines
              (current and previous)

        :return: True if we should redraw, False otherwise.
        """
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_end_text_pos(self) -> int:
        """
        Returns the position to draw the text up to (e.g 1 would draw only the first character).

        :return: progress through the typing effect.
        """
        return self.text_progress


# TODO: Should we merge these two effects into one with a direction parameter?
class FadeInEffect(TextBoxEffect):
    """
    A fade in effect for the text box. Allows us to fade the text, though this class just takes
    care of fading up an alpha value over time.

    :param all_characters: The text characters in the text box. Useful to know for some effects.
    """
    def __init__(self, all_characters: str):
        super().__init__(all_characters)
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.alpha_value < 255:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value > 255:
                    self.alpha_value = 255
                self.time_to_redraw = True

    def should_redraw_from_chunks(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self) -> int:
        """
        Returns the current alpha value of the fade.

        :return: The alpha value, between 0 and 255
        """
        return self.alpha_value


class FadeOutEffect(TextBoxEffect):
    """
    A fade out effect for the text box. Allows us to fade the text, though this class just takes
    care of fading out an alpha value over time.

    :param all_characters: The text characters in the text box. Useful to know for some effects.
    """
    def __init__(self, all_characters: str):

        super().__init__(all_characters)
        self.alpha_value = 255
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.alpha_value > 0:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = 255 - int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value < 0:
                    self.alpha_value = 0
                self.time_to_redraw = True

    def should_redraw_from_chunks(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self) -> int:
        """
        Returns the current alpha value of the fade.

        :return: The alpha value, between 0 and 255
        """
        return self.alpha_value
