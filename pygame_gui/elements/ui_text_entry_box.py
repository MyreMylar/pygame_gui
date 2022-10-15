from typing import Union, Tuple, Dict, Optional, Any

from pygame import Rect
from pygame_gui.core import ObjectID
from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.elements.ui_text_box import UITextBox


class UITextEntryBox(UITextBox):
    def __init__(self,
                 relative_rect: Union[Rect, Tuple[int, int, int, int]],
                 initial_text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):
        super().__init__(initial_text,
                         relative_rect,
                         manager=manager,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)
