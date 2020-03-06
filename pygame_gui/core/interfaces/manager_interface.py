from abc import ABCMeta
from typing import Tuple, List, Union, Dict

import pygame


class IUIManagerInterface:
    """
    A meta class that defines the interface that a UI Manager uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the actual manager class later
    on and have it make use of the classes that use the interface.
    """
    __metaclass__ = ABCMeta

    def get_double_click_time(self) -> float:
        pass

    def get_root_container(self):
        pass

    def get_theme(self):
        pass

    def get_sprite_group(self) -> pygame.sprite.LayeredUpdates:
        pass

    def get_window_stack(self):
        pass

    def get_shadow(self, size: Tuple[int, int], shadow_width: int = 2,
                   shape: str = 'rectangle', corner_radius: int = 2) -> pygame.Surface:
        pass

    def set_window_resolution(self, window_resolution: Tuple[int, int]):
        pass

    def clear_and_reset(self):
        pass

    def process_events(self, event: pygame.event.Event):
        pass

    def update(self, time_delta: float):
        pass

    def update_mouse_position(self):
        pass

    def get_mouse_position(self) -> Tuple[int, int]:
        pass

    def draw_ui(self, window_surface: pygame.Surface):
        pass

    def add_font_paths(self, font_name: str, regular_path: str, bold_path: str = None,
                       italic_path: str = None, bold_italic_path: str = None):
        pass

    def preload_fonts(self, font_list: List[Dict[str, Union[str, int, float]]]):
        pass

    def print_unused_fonts(self):
        pass

    def unset_focus_element(self):
        pass

    def set_focus_element(self, ui_element):
        pass

    def clear_last_focused_from_vert_scrollbar(self, vert_scrollbar):
        pass

    def get_last_focused_vert_scrollbar(self):
        pass

    def set_visual_debug_mode(self, is_active: bool):
        pass

    def print_layer_debug(self):
        pass

    def load_default_cursors(self):
        pass

    def set_active_cursor(self, cursor: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, ...], Tuple[int, ...]]):
        pass

    def get_universal_empty_surface(self) -> pygame.Surface:
        pass

    def create_tool_tip(self, text: str, position: Tuple[int, int], hover_distance: Tuple[int, int]):
        pass
