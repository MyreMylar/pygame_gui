import random
from typing import Dict, Any, Optional, List

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

    def __init__(
        self,
        text_owner: IUITextOwnerInterface,
        params: Optional[Dict[str, Any]] = None,
        text_sub_chunks: List[TextLineChunkFTFont] | None = None,
        effect_id_tag: str | None = None,
    ):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunks = text_sub_chunks
        self.effect_id_tag = effect_id_tag
        self.text_sub_chunk_lengths = None
        self.text_sub_chunk_progress = None
        if self.text_sub_chunks is not None:
            self.text_sub_chunk_lengths = []
            self.text_sub_chunk_progress = []
            for chunk in self.text_sub_chunks:
                self.text_sub_chunk_lengths.append(
                    self.text_owner.get_text_letter_count(chunk)
                )
                self.text_sub_chunk_progress.append(0)

        self.effect_letter_count = 0
        if self.text_sub_chunks is None:
            self.effect_letter_count = self.text_owner.get_text_letter_count(None)
        else:
            for chunk in self.text_sub_chunks:
                self.effect_letter_count += self.text_owner.get_text_letter_count(chunk)

        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_average_deviation = 0.0
        self.time_per_letter_acc = 0.0
        if self.text_sub_chunks is not None:
            for chunk in self.text_sub_chunks:
                self.text_owner.clear_text_surface(chunk)
        else:
            self.text_owner.clear_text_surface(None)

        if self.text_sub_chunks is not None:
            for chunk in self.text_sub_chunks:
                self.text_owner.update_text_end_position(self.text_progress, chunk)
        else:
            self.text_owner.update_text_end_position(self.text_progress, None)

        self._load_params(params)

        self.current_time_per_letter = max(
            0.00001,
            min(
                random.gauss(self.time_per_letter, self.time_average_deviation / 3),
                self.time_per_letter + self.time_average_deviation,
            ),
            self.time_per_letter - self.time_average_deviation,
        )

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if "time_per_letter" in params:
                self.time_per_letter = float(params["time_per_letter"])
            if "time_per_letter_deviation" in params:
                self.time_average_deviation = float(params["time_per_letter_deviation"])

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update. Adds a new
        letter to the progress every self.time_per_letter seconds.

        :param time_delta: time in seconds since last frame.
        """

        if self.text_progress < self.effect_letter_count:
            self.time_per_letter_acc += time_delta
            if self.time_per_letter_acc >= self.current_time_per_letter:
                self.time_per_letter_acc -= self.current_time_per_letter
                self.text_progress += 1
                self.text_changed = True
                self.current_time_per_letter = max(
                    0.00001,
                    min(
                        random.gauss(
                            self.time_per_letter, self.time_average_deviation / 3
                        ),
                        self.time_per_letter + self.time_average_deviation,
                    ),
                    self.time_per_letter - self.time_average_deviation,
                )
            if (
                self.text_sub_chunk_lengths is not None
                and self.text_sub_chunk_progress is not None
            ):
                progress_decrement = self.text_progress
                for index, chunk_length in enumerate(self.text_sub_chunk_lengths):
                    chunk_progress = min(progress_decrement, chunk_length)
                    progress_decrement -= chunk_progress
                    self.text_sub_chunk_progress[index] = chunk_progress

        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunks)

            event_data = {
                "ui_element": self.text_owner,
                "ui_object_id": self.text_owner.get_object_id(),
                "effect": TEXT_EFFECT_TYPING_APPEAR,
            }
            if self.effect_id_tag is not None:
                event_data["effect_tag_id"] = self.effect_id_tag
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        if (
            self.text_sub_chunks is not None
            and self.text_sub_chunk_progress is not None
        ):
            for index, chunk in enumerate(self.text_sub_chunks):
                self.text_owner.update_text_end_position(
                    self.text_sub_chunk_progress[index], chunk
                )
        else:
            self.text_owner.update_text_end_position(self.text_progress, None)
