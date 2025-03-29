import random
from typing import Dict, Any, Optional, List

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_SHAKE
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class ShakeEffect(TextEffect):
    """
    A shake effect
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
        self.loop = True
        self.frequency = 24
        self.duration = 1.2
        self.time_acc = 0.0
        self.amplitude = 4
        self.text_owner.set_text_offset_pos((0, 0), self.text_sub_chunk)
        self._load_params(params)

        sample_count = int(self.duration * self.frequency)

        self.x_samples: List[float] = []
        self.x_samples.extend(random.uniform(-1.0, 1.0) for _ in range(sample_count))
        self.y_samples: List[float] = []
        self.y_samples.extend(random.uniform(-1.0, 1.0) for _ in range(sample_count))
        self.shake = (0, 0)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is None:
            return
        if "loop" in params:
            if isinstance(params["loop"], bool):
                self.loop = params["loop"]
            elif isinstance(params["loop"], str):
                self.loop = bool(int(params["loop"]))
            else:
                self.loop = bool(params["loop"])
        if "frequency" in params:
            self.frequency = int(params["frequency"])
        if "amplitude" in params:
            self.amplitude = int(params["amplitude"])
        if "duration" in params:
            self.duration = float(params["duration"])

    def _decay(self, time_passed: float):
        return min(1.0, max((self.duration - time_passed) / self.duration, 0.0))

    def _x_noise(self, index):
        return 0 if index >= len(self.x_samples) else self.x_samples[index]

    def _y_noise(self, index):
        return 0 if index >= len(self.y_samples) else self.y_samples[index]

    def _x_amplitude(self, time_passed: float):
        s = time_passed * self.frequency
        s0 = int(s)
        s1 = s0 + 1

        k = 1.0 if self.loop else self._decay(time_passed)

        return (
            self._x_noise(s0) + (s - s0) * (self._x_noise(s1) - self._x_noise(s0))
        ) * k

    def _y_amplitude(self, time_passed: float):
        s = time_passed * self.frequency
        s0 = int(s)
        s1 = s0 + 1

        k = 1.0 if self.loop else self._decay(time_passed)

        return (
            self._y_noise(s0) + (s - s0) * (self._y_noise(s1) - self._y_noise(s0))
        ) * k

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        self.time_acc += time_delta
        if self.time_acc < self.duration:
            new_shake = (
                int(self._x_amplitude(self.time_acc) * self.amplitude),
                int(self._y_amplitude(self.time_acc) * self.amplitude),
            )
            if new_shake != self.shake:
                self.shake = new_shake
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {
                "ui_element": self.text_owner,
                "ui_object_id": self.text_owner.get_object_id(),
                "effect": TEXT_EFFECT_SHAKE,
            }
            if self.text_sub_chunk is not None:
                event_data["effect_tag_id"] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        self.text_owner.set_text_offset_pos(self.shake, self.text_sub_chunk)
