import random
from typing import Dict, Any, Optional

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_TYPING_APPEAR
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class TypingAppearEffect(TextEffect):
    """
    Does that 'typewriter' effect where the text in a box appears one character at a time as if
    they were being typed by an invisible hand.

    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_average_deviation = 0.0
        self.time_per_letter_acc = 0.0
        self.text_changed = False
        self.text_owner.clear_text_surface(self.text_sub_chunk)
        self.text_owner.update_text_end_position(self.text_progress, self.text_sub_chunk)

        self._load_params(params)

        self.current_time_per_letter = max(0.00001,
                                           random.gauss(self.time_per_letter,
                                                        self.time_average_deviation ** 0.5))

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'time_per_letter' in params:
                self.time_per_letter = float(params['time_per_letter'])
            if 'time_per_letter_deviation' in params:
                self.time_average_deviation = float(params['time_per_letter_deviation'])

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update. Adds a new
        letter to the progress every self.time_per_letter seconds.

        :param time_delta: time in seconds since last frame.
        """
        if self.text_progress < self.text_owner.get_text_letter_count(self.text_sub_chunk):
            self.time_per_letter_acc += time_delta
            if self.time_per_letter_acc >= self.current_time_per_letter:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.text_changed = True
                self.current_time_per_letter = max(
                    0.00001, random.gauss(self.time_per_letter, self.time_average_deviation ** 0.5))
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_TYPING_APPEAR}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

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

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        self.text_owner.update_text_end_position(self.text_progress, self.text_sub_chunk)
