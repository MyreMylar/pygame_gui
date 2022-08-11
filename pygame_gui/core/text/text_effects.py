import random
from typing import Dict, Any, Optional

import pygame

from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_TYPING_APPEAR
from pygame_gui._constants import TEXT_EFFECT_FADE_IN, TEXT_EFFECT_FADE_OUT
from pygame_gui._constants import TEXT_EFFECT_BOUNCE, TEXT_EFFECT_TILT
from pygame_gui._constants import TEXT_EFFECT_EXPAND_CONTRACT
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class TextEffect:
    """
    Base class for text effects
    """

    # pylint: disable=unused-argument,no-self-use
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
    # pylint: disable=unused-argument,no-self-use
    def get_final_alpha(self) -> int:
        """
        The alpha value to draw the text box with. By default it is 255.

        :return: The default alpha value for a text box.
        """
        return 255

    def apply_effect(self):
        """
        Apply the effect to the text
        """


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


class FadeInEffect(TextEffect):
    """
    A fade in effect for the text box. Allows us to fade the text, though this class just takes
    care of fading up an alpha value over time.

    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.text_changed = False
        self.text_owner.set_text_alpha(0, self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'time_per_alpha_change' in params:
                self.time_per_alpha_change = float(params['time_per_alpha_change'])

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
                self.text_changed = True
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_FADE_IN}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.text_changed:
            self.text_changed = False
            return True
        else:
            return False

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


class FadeOutEffect(TextEffect):
    """
    A fade out effect for the text box. Allows us to fade the text, though this class just takes
    care of fading out an alpha value over time.

    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.alpha_value = 255
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.text_changed = False
        self.text_owner.set_text_alpha(255, self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'time_per_alpha_change' in params:
                self.time_per_alpha_change = float(params['time_per_alpha_change'])

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
                self.text_changed = True

        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_FADE_OUT}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
        """
        if self.text_changed:
            self.text_changed = False
            return True
        else:
            return False

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


class BounceEffect(TextEffect):
    """
    A bounce effect
    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.loop = True
        self.bounce_max_height = 5
        self.time_to_complete_bounce = 0.5
        self.time_acc = 0.0
        self.bounce_height = 0
        self.text_changed = False
        self.text_owner.set_text_offset_pos((0, 0), self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'loop' in params:
                if isinstance(params['loop'], bool):
                    self.loop = params['loop']
                elif isinstance(params['loop'], str):
                    self.loop = bool(int(params['loop']))
                else:
                    self.loop = bool(params['loop'])
            if 'bounce_max_height' in params:
                self.bounce_max_height = int(params['bounce_max_height'])
            if 'time_to_complete_bounce' in params:
                self.time_to_complete_bounce = float(params['time_to_complete_bounce'])

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.time_acc < self.time_to_complete_bounce:
            self.time_acc += time_delta

            bounce_progress = self.time_acc / max(self.time_to_complete_bounce, 0.000001)
            if bounce_progress < 0.5:
                bounce_height = int(((bounce_progress * 2) ** 2) * self.bounce_max_height)
            else:
                bounce_height = int((((1-bounce_progress) * 2) ** 2) * self.bounce_max_height)

            if bounce_height != self.bounce_height:
                self.bounce_height = max(bounce_height, 0)
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_BOUNCE}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
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
        self.text_owner.set_text_offset_pos((0, -self.bounce_height),
                                            self.text_sub_chunk)


class TiltEffect(TextEffect):
    """
    Tilts to an angle and then returns
    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.loop = True
        self.max_rotation = 1080
        self.time_to_complete_rotation = 5.0
        self.time_acc = 0.0
        self.current_rotation = 0
        self.text_changed = False
        self.text_owner.set_text_rotation(self.current_rotation,
                                          self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'loop' in params:
                if isinstance(params['loop'], bool):
                    self.loop = params['loop']
                elif isinstance(params['loop'], str):
                    self.loop = bool(int(params['loop']))
                else:
                    self.loop = bool(params['loop'])
            if 'max_rotation' in params:
                self.max_rotation = int(params['max_rotation'])
            if 'time_to_complete_rotation' in params:
                self.time_to_complete_rotation = float(params['time_to_complete_rotation'])

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.time_acc < self.time_to_complete_rotation:
            self.time_acc += time_delta

            spin_progress = self.time_acc / max(self.time_to_complete_rotation, 0.000001)
            if spin_progress < 0.5:
                current_rotation = int(((spin_progress * 2) ** 2) * self.max_rotation)
            else:
                current_rotation = int((((1-spin_progress) * 2) ** 2) * self.max_rotation)

            if current_rotation != self.current_rotation:
                self.current_rotation = max(current_rotation, 0)
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_TILT}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
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
        self.text_owner.set_text_rotation(self.current_rotation,
                                          self.text_sub_chunk)


class ExpandContractEffect(TextEffect):
    """
    Expands to a specified scale and then returns
    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.loop = True
        self.max_scale = 1.5
        self.time_to_complete_expand_contract = 2.0
        self.time_acc = 0.0
        self.current_scale = 1.0
        self.text_changed = False
        self.text_owner.set_text_scale(self.current_scale, self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'loop' in params:
                if isinstance(params['loop'], bool):
                    self.loop = params['loop']
                elif isinstance(params['loop'], str):
                    self.loop = bool(int(params['loop']))
                else:
                    self.loop = bool(params['loop'])
            if 'max_scale' in params:
                self.max_scale = float(params['max_scale'])
            if 'time_to_complete_expand_contract' in params:
                self.time_to_complete_expand_contract = float(
                    params['time_to_complete_expand_contract'])

    def update(self, time_delta: float):
        """
        Updates the fade with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        if self.time_acc < self.time_to_complete_expand_contract:
            self.time_acc += time_delta

            scale_progress = self.time_acc / max(self.time_to_complete_expand_contract, 0.000001)
            if scale_progress < 0.5:
                current_scale = 1.0 + float(((scale_progress * 2) ** 2) * (self.max_scale - 1.0))
            else:
                current_scale = 1.0 + float((((1-scale_progress) * 2) ** 2)
                                            * (self.max_scale - 1.0))

            if current_scale != self.current_scale:
                self.current_scale = max(current_scale, 1.0)
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_EXPAND_CONTRACT}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the fade alpha has changed enough (i.e. by a whole int) to warrant us
        redrawing the text box with the new alpha value.

        :return: True if it is is time to redraw our text.
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
        self.text_owner.set_text_scale(self.current_scale, self.text_sub_chunk)
