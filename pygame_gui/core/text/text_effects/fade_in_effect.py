from typing import Dict, Any, Optional

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_FADE_IN
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class FadeInEffect(TextEffect):
    """
    A fade in effect for the text box. Allows us to fade the text, though this class just takes
    care of fading up an alpha value over time.

    """

    def __init__(
        self,
        text_owner: IUITextOwnerInterface,
        params: Optional[Dict[str, Any]] = None,
        text_sub_chunk: Optional[TextLineChunkFTFont] = None,
    ):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.text_owner.set_text_alpha(0, self.text_sub_chunk)
        self._load_params(params)
        self.finished = False

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None and "time_per_alpha_change" in params:
            self.time_per_alpha_change = float(params["time_per_alpha_change"])

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.alpha_value < 255:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = int(
                self.time_per_alpha_change_acc / self.time_per_alpha_change
            )

            if alpha_progress != self.alpha_value:
                self.alpha_value = min(alpha_progress, 255)
                self.text_changed = True
        elif not self.finished:
            self.finished = True
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {
                "ui_element": self.text_owner,
                "ui_object_id": self.text_owner.get_object_id(),
                "effect": TEXT_EFFECT_FADE_IN,
            }
            if self.text_sub_chunk is not None:
                event_data["effect_tag_id"] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def get_final_alpha(self) -> int:
        """
        Returns the current alpha value of the fade.

        :return: The alpha value, between 0 and 255
        """
        return self.alpha_value

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        self.text_owner.set_text_alpha(self.alpha_value, self.text_sub_chunk)
