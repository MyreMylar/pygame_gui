from typing import Dict, Any, Optional, List

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_EXPAND_CONTRACT
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class ExpandContractEffect(TextEffect):
    """
    Expands to a specified scale and then returns
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
        self.loop = True
        self.max_scale = 1.5
        self.time_to_complete_expand_contract = 2.0
        self.time_acc = 0.0
        self.current_scale = 1.0
        if self.text_sub_chunks is not None:
            for chunk in self.text_sub_chunks:
                self.text_owner.set_text_scale(self.current_scale, chunk)
        else:
            self.text_owner.set_text_scale(self.current_scale)
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
        if "max_scale" in params:
            self.max_scale = float(params["max_scale"])
        if "time_to_complete_expand_contract" in params:
            self.time_to_complete_expand_contract = float(
                params["time_to_complete_expand_contract"]
            )

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        self.time_acc += time_delta
        if self.time_acc < self.time_to_complete_expand_contract:
            scale_progress = self.time_acc / max(
                self.time_to_complete_expand_contract, 0.000001
            )
            if scale_progress < 0.5:
                current_scale = 1.0 + float(
                    ((scale_progress * 2) ** 2) * (self.max_scale - 1.0)
                )
            else:
                current_scale = 1.0 + float(
                    (((1 - scale_progress) * 2) ** 2) * (self.max_scale - 1.0)
                )

            if current_scale != self.current_scale:
                self.current_scale = max(current_scale, 1.0)
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunks)

            event_data = {
                "ui_element": self.text_owner,
                "ui_object_id": self.text_owner.get_object_id(),
                "effect": TEXT_EFFECT_EXPAND_CONTRACT,
            }
            if self.effect_id_tag is not None:
                event_data["effect_tag_id"] = self.effect_id_tag
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        if self.text_sub_chunks is not None:
            for chunk in self.text_sub_chunks:
                self.text_owner.set_text_scale(self.current_scale, chunk)
        else:
            self.text_owner.set_text_scale(self.current_scale)
