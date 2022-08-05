from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

from pygame_gui._constants import UITextEffectType

if TYPE_CHECKING:
    from pygame_gui.core.drawable_shapes.drawable_shape import TextLineChunkFTFont


class IUITextOwnerInterface(metaclass=ABCMeta):
    """
    A common interface for UIElements that own some text, to help make it easier to run text
    effects across multiple UIElements.
    """

    @abstractmethod
    def set_text_alpha(self, alpha: int, sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Set the global alpha value for the text

        :param alpha: the alpha to set.
        :param sub_chunk: An optional chunk so we only set the alpha for this chunk.
        """

    @abstractmethod
    def set_text_offset_pos(self, offset: Tuple[int, int],
                            sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Move the text around by this offset.

        :param offset: the offset to set
        :param sub_chunk: An optional chunk so we only set the offset for this chunk.
        :return:
        """

    @abstractmethod
    def set_text_rotation(self, rotation: int,
                          sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        rotate the text by this int in degrees

        :param rotation: the rotation to set
        :param sub_chunk:  An optional chunk so we only set the rotation for this chunk.
        :return:
        """

    @abstractmethod
    def set_text_scale(self, scale: float,  sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Scale the text by this float

        :param scale: the scale to set
        :param sub_chunk:  An optional chunk so we only set the rotation for this chunk.
        :return:
        """

    @abstractmethod
    def clear_text_surface(self, sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Clear the text surface

        :param sub_chunk: An optional chunk so we only clear the surface for this chunk.
        """

    @abstractmethod
    def get_text_letter_count(self, sub_chunk: Optional['TextLineChunkFTFont'] = None) -> int:
        """
        The amount of letters in the text

        :param sub_chunk: An optional chunk to restrict the count to only this chunk.

        :return: number of letters as an int
        """
    @abstractmethod
    def update_text_end_position(self, end_pos: int, sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        The position in the text to render up to.

        :param end_pos: The current end position as an int
        :param sub_chunk: An optional chunk to restrict the end_position to only this chunk.

        """

    @abstractmethod
    def set_active_effect(self, effect_type: Optional[UITextEffectType],
                          params: Optional[Dict[str, Any]] = None,
                          effect_tag: Optional[str] = None):
        """
        Set an animation effect to run on the text box. The effect will start running immediately
        after this call.

        These effects are currently supported:

        - TEXT_EFFECT_TYPING_APPEAR - Will look as if the text is being typed in.
        - TEXT_EFFECT_FADE_IN - The text will fade in from the background colour.
        - TEXT_EFFECT_FADE_OUT - The text will fade out to the background colour.

        :param effect_tag: if not None, only apply the effect to chunks with this tag.
        :param params: Any parameters for the effect you are setting,
                       if none are set defaults will be used.
        :param effect_type: The type of the effect to set. If set to None instead it will cancel any
                            active effect.

        """

    @abstractmethod
    def update_text_effect(self, time_delta: float):
        """
        Update any active text effect on the text owner

        :param time_delta: the time delta in seconds
        """

    @abstractmethod
    def get_object_id(self) -> str:
        """
        The UI object ID of this text owner for use in effect events.

        :return: the ID string
        """

    @abstractmethod
    def stop_finished_effect(self, sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Stops a finished effect. Will leave effected text in the state it was in when effect
        ended. Used when an effect reaches a natural end where we might want to keep it in
        the end of effect state (e.g. a fade out)

        :param sub_chunk: An optional chunk so we only clear the effect from this chunk.
        """

    @abstractmethod
    def clear_all_active_effects(self, sub_chunk: Optional['TextLineChunkFTFont'] = None):
        """
        Clears any active effects and redraws the text. A full reset, usually called before
        firing off a new effect if one is already in progress.

        :param sub_chunk: An optional chunk so we only clear the effect from this chunk.
        """
