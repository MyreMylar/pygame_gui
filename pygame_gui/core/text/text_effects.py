from typing import TYPE_CHECKING

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_TYPING_APPEAR
from pygame_gui._constants import TEXT_EFFECT_FADE_IN, TEXT_EFFECT_FADE_OUT

if TYPE_CHECKING:
    from pygame_gui.core.text.text_box_layout import TextBoxLayout
    from pygame_gui.elements.ui_text_box import UITextBox


class TextBoxEffect:
    """
    Base class for text box effects
    """

    # pylint: disable=unused-argument,no-self-use
    def has_text_block_changed(self) -> bool:
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
    # pylint: disable=unused-argument,no-self-use
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

    """
    def __init__(self, text_box: 'UITextBox'):
        super().__init__()
        self.text_box = text_box
        self.text_box_layout = text_box.text_box_layout
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_per_letter_acc = 0.0
        self.text_block_changed = False
        self.text_box_layout.set_alpha(255)
        self.text_box_layout.clear_final_surface()

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update. Adds a new
        letter to the progress every self.time_per_letter seconds.

        :param time_delta: time in seconds since last frame.
        """
        if self.text_progress < self.text_box_layout.letter_count:
            if self.time_per_letter_acc < self.time_per_letter:
                self.time_per_letter_acc += time_delta
            else:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.text_box_layout.update_text_with_new_text_end_pos(self.text_progress)
                self.text_block_changed = True
        else:
            # finished effect
            self.text_box.set_active_effect(None)

            event_data = {'ui_element': self.text_box,
                          'ui_object_id': self.text_box.most_specific_combined_id,
                          'effect': TEXT_EFFECT_TYPING_APPEAR}
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_block_changed(self) -> bool:
        """
        Test if we should redraw the whole text box.

        TODO: Once text box is refactored change this.
              So we only redraw the new bits of added text and the last two lines
              (current and previous)

        :return: True if we should redraw, False otherwise.
        """
        if self.text_block_changed:
            self.text_block_changed = False
            return True
        else:
            return False


class DropInAppearEffect(TextBoxEffect):
    """
    Letters appear to drop in one at a time from a void above the current line of text.

    """
    def __init__(self, text_box: 'TextBoxLayout'):
        super().__init__()
        self.text_box = text_box
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_per_letter_acc = 0.0
        self.text_block_changed = False
        self.text_box.set_alpha(255)
        self.text_box.clear_final_surface()
        self.letter_drop_speed = 0.1
        self.letter_drop_acc = 0.0

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update. Adds a new
        letter to the progress every self.time_per_letter seconds.

        :param time_delta: time in seconds since last frame.
        """
        if self.text_progress < self.text_box.letter_count:
            if self.time_per_letter_acc < self.time_per_letter:
                self.time_per_letter_acc += time_delta
            else:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.text_box.set_letter_active(self.text_progress, True)
                self.text_box.update_text_with_new_text_end_pos(self.text_progress)
                self.text_block_changed = True

        if self.letter_drop_acc >= self.letter_drop_speed:
            self.letter_drop_acc = 0.0
            self.text_box.update_active_letter_offsets((0, 1))
            # if letter has reached bottom make it inactive again
        else:
            self.letter_drop_acc += time_delta

    def has_text_block_changed(self) -> bool:
        """
        Test if we should redraw the whole text box.

        TODO: Once text box is refactored change this.
              So we only redraw the new bits of added text and the last two lines
              (current and previous)

        :return: True if we should redraw, False otherwise.
        """
        if self.text_block_changed:
            self.text_block_changed = False
            return True
        else:
            return False


# TODO: Should we merge these two effects into one with a direction parameter?
class FadeInEffect(TextBoxEffect):
    """
    A fade in effect for the text box. Allows us to fade the text, though this class just takes
    care of fading up an alpha value over time.

    """
    def __init__(self, text_box: 'UITextBox'):
        super().__init__()
        self.text_box = text_box
        self.text_box_layout = text_box.text_box_layout
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.text_block_changed = False
        self.text_box_layout.set_alpha(255)
        self.text_box_layout.set_alpha(0)

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.alpha_value < 255:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = min(alpha_progress, 255)
                self.text_box_layout.set_alpha(self.alpha_value)
                self.text_block_changed = True
        else:
            # finished effect
            self.text_box.set_active_effect(None)

            event_data = {'ui_element': self.text_box,
                          'ui_object_id': self.text_box.most_specific_combined_id,
                          'effect': TEXT_EFFECT_FADE_IN}
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_block_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.text_block_changed:
            self.text_block_changed = False
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
    def __init__(self, text_box: 'UITextBox'):
        super().__init__()
        self.text_box = text_box
        self.text_box_layout = text_box.text_box_layout
        self.alpha_value = 255
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.text_block_changed = False
        self.text_box_layout.set_alpha(255)

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.alpha_value > 0:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = 255 - int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = max(alpha_progress, 0)
                self.text_box_layout.set_alpha(self.alpha_value)
                self.text_block_changed = True

        else:
            # finished effect
            self.text_box.set_active_effect(None)

            event_data = {'ui_element': self.text_box,
                          'ui_object_id': self.text_box.most_specific_combined_id,
                          'effect': TEXT_EFFECT_FADE_OUT}
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_block_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.text_block_changed:
            self.text_block_changed = False
            return True
        else:
            return False

    def get_final_alpha(self) -> int:
        """
        Returns the current alpha value of the fade.

        :return: The alpha value, between 0 and 255
        """
        return self.alpha_value
