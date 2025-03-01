from typing import Dict, Any, Optional

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_TILT
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class TiltEffect(TextEffect):
    """
    Tilts to an angle and then returns
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
        self.max_rotation = 1080
        self.time_to_complete_rotation = 5.0
        self.time_acc = 0.0
        self.current_rotation = 0
        self.text_changed = False
        self.text_owner.set_text_rotation(self.current_rotation, self.text_sub_chunk)
        self._load_params(params)

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
        if "max_rotation" in params:
            self.max_rotation = int(params["max_rotation"])
        if "time_to_complete_rotation" in params:
            self.time_to_complete_rotation = float(params["time_to_complete_rotation"])

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        self.time_acc += time_delta
        if self.time_acc < self.time_to_complete_rotation:
            spin_progress = self.time_acc / max(
                self.time_to_complete_rotation, 0.000001
            )
            if spin_progress < 0.5:
                current_rotation = int(((spin_progress * 2) ** 2) * self.max_rotation)
            else:
                current_rotation = int(
                    (((1 - spin_progress) * 2) ** 2) * self.max_rotation
                )

            if current_rotation != self.current_rotation:
                self.current_rotation = max(current_rotation, 0)
                self.text_changed = True
        elif self.loop:
            self.time_acc -= self.time_to_complete_rotation
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {
                "ui_element": self.text_owner,
                "ui_object_id": self.text_owner.get_object_id(),
                "effect": TEXT_EFFECT_TILT,
            }
            if self.text_sub_chunk is not None:
                event_data["effect_tag_id"] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the effect has changed enough to warrant us redrawing the text.

        :return: True if it is time to redraw our text.
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
        self.text_owner.set_text_rotation(self.current_rotation, self.text_sub_chunk)
