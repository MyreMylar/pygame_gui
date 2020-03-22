from abc import ABCMeta
from typing import Tuple, List, Union, Dict

import pygame


class IUIManagerInterface:
    """
    A meta class that defines the interface that a UI Manager uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """
    __metaclass__ = ABCMeta

    def get_double_click_time(self) -> float:
        """
        Returns time between clicks that counts as a double click.

        :return: A float, time measured in seconds.
        """

    def get_root_container(self):
        """
        Returns the 'root' container. The one all UI elements are placed in by default if they are
        not placed anywhere else, fills the whole OS/pygame window.

        :return: A container.
        """

    def get_theme(self):
        """
        Gets the theme so the data in it can be accessed.

        :return: The theme data used by this UIManager
        """

    def get_sprite_group(self) -> pygame.sprite.LayeredUpdates:
        """
        Gets the sprite group used by the entire UI to keep it in the correct order for drawing and
        processing input.

        :return: The UI's sprite group.
        """

    def get_window_stack(self):
        """
        The UIWindowStack organises any windows in the UI Manager so that they are correctly sorted
        and move windows we interact with to the top of the stack.

        :return: The stack of windows.
        """

    def get_shadow(self, size: Tuple[int, int], shadow_width: int = 2,
                   shape: str = 'rectangle', corner_radius: int = 2) -> pygame.Surface:
        """
        Returns a 'shadow' surface scaled to the requested size.

        :param size: The size of the object we are shadowing + it's shadow.
        :param shadow_width: The width of the shadowed edge.
        :param shape: The shape of the requested shadow.
        :param corner_radius: The radius of the shadow corners if this is a rectangular shadow.
        :return: A shadow as a pygame Surface.
        """

    def set_window_resolution(self, window_resolution: Tuple[int, int]):
        """
        Sets the window resolution.

        :param window_resolution: the resolution to set.
        """

    def clear_and_reset(self):
        """
        Clear the whole UI.
        """

    def process_events(self, event: pygame.event.Event):
        """
        This is the top level method through which all input to UI elements is processed and
        reacted to.

        :param event:  pygame.event.Event - the event to process.
        """

    def update(self, time_delta: float):
        """
        Update the UIManager.

        :param time_delta: The time passed since the last call to update, in seconds.
        """

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get the position of the mouse in the UI.
        """

    def draw_ui(self, window_surface: pygame.Surface):
        """
        Draws the UI.

        :param window_surface: The screen or window surface on which we are going to draw all of
         our UI Elements.

        """

    def add_font_paths(self, font_name: str, regular_path: str, bold_path: str = None,
                       italic_path: str = None, bold_italic_path: str = None):
        """
        Add file paths for custom fonts you want to use in the UI.

        :param font_name: The name of the font that will be used to reference it elsewhere in
        the GUI.
        :param regular_path: The path of the font file for this font with no styles applied.
        :param bold_path: The path of the font file for this font with just bold style applied.
        :param italic_path: The path of the font file for this font with just italic style applied.
        :param bold_italic_path: The path of the font file for this font with bold & italic style
        applied.

        """

    def preload_fonts(self, font_list: List[Dict[str, Union[str, int, float]]]):
        """
        Pre-loads a list of fonts.

        :param font_list: A list of font descriptions in dictionary format as described above.

        """

    def print_unused_fonts(self):
        """
        Prints a list of fonts that have been loaded but are not being used.

        """

    def unset_focus_element(self):
        """
        Clear the currently focused element.
        """

    def set_focus_element(self, ui_element):
        """
        Set an element as the focused element.

        :param ui_element: The element to focus on.
        """

    def clear_last_focused_from_vert_scrollbar(self, vert_scrollbar):
        """
        Clears the last scrollbar that we used. Right now this may also be one of the buttons of
        the scroll bar.

        :param vert_scrollbar: A scrollbar UIElement.
        """

    def get_last_focused_vert_scrollbar(self):
        """
        Gets the last scrollbar that we used. Right now this may also be one of the buttons of
        the scroll bar.

        :return: A UIElement.
        """

    def set_visual_debug_mode(self, is_active: bool):
        """
        Loops through all our UIElements to turn visual debug mode on or off. Also calls
        print_layer_debug()

        :param is_active: True to activate visual debug and False to turn it off.
        """

    def print_layer_debug(self):
        """
        Print some formatted information on the current state of the UI Layers.

        Handy for debugging layer problems.
        """

    def set_active_cursor(self, cursor: Tuple[Tuple[int, int],
                                              Tuple[int, int],
                                              Tuple[int, ...],
                                              Tuple[int, ...]]):
        """
        This is for users of the library to set the currently active cursor, it will be currently
        only be overriden by the resizing cursors.

        The expected input is in the same format as the standard pygame cursor module, except
        without expanding the initial Tuple. So, to call this function with the default pygame
        arrow cursor you would do:

           manager.set_active_cursor(pygame.cursors.arrow)

        """

    def get_universal_empty_surface(self) -> pygame.Surface:
        """
        Sometimes we want to hide sprites or just have sprites with no visual component, when we
        do we can just use this empty surface to save having lots of empty surfaces all over memory.

        :return: An empty, and therefore invisible pygame.Surface
        """

    def create_tool_tip(self,
                        text: str,
                        position: Tuple[int, int],
                        hover_distance: Tuple[int, int]):
        """
        Creates a tool tip ands returns it.

        :param text: The tool tips text, can utilise the HTML subset used in all UITextBoxes.
        :param position: The screen position to create the tool tip for.
        :param hover_distance: The distance we should hover away from our target position.

        :return: A tool tip placed somewhere on the screen.
        """
