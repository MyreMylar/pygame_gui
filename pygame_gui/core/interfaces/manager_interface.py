from abc import ABCMeta, abstractmethod
from typing import Tuple, List, Union, Dict, Set, Optional

import pygame

from pygame_gui.core.interfaces.appearance_theme_interface import IUIAppearanceThemeInterface
from pygame_gui.core.interfaces.element_interface import IUIElementInterface
from pygame_gui.core.interfaces.container_interface import IUIContainerInterface
from pygame_gui.core.interfaces.window_stack_interface import IUIWindowStackInterface
from pygame_gui.core.interfaces.tool_tip_interface import IUITooltipInterface


class IUIManagerInterface(metaclass=ABCMeta):
    """
    A meta class that defines the interface that a UI Manager uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """

    @abstractmethod
    def get_double_click_time(self) -> float:
        """
        Returns time between clicks that counts as a double click.

        :return: A float, time measured in seconds.
        """

    @abstractmethod
    def get_root_container(self) -> IUIContainerInterface:
        """
        Returns the 'root' container. The one all UI elements are placed in by default if they are
        not placed anywhere else, fills the whole OS/pygame window.

        :return: A container.
        """

    @abstractmethod
    def get_theme(self) -> IUIAppearanceThemeInterface:
        """
        Gets the theme so the data in it can be accessed.

        :return: The theme data used by this UIManager
        """

    @abstractmethod
    def get_sprite_group(self) -> pygame.sprite.LayeredDirty:
        """
        Gets the sprite group used by the entire UI to keep it in the correct order for drawing and
        processing input.

        :return: The UI's sprite group.
        """

    @abstractmethod
    def get_window_stack(self) -> IUIWindowStackInterface:
        """
        The UIWindowStack organises any windows in the UI Manager so that they are correctly sorted
        and move windows we interact with to the top of the stack.

        :return: The stack of windows.
        """

    @abstractmethod
    def get_shadow(self, size: Tuple[int, int], shadow_width: int = 2,
                   shape: str = 'rectangle', corner_radius: int = 2) -> pygame.surface.Surface:
        """
        Returns a 'shadow' surface scaled to the requested size.

        :param size: The size of the object we are shadowing + it's shadow.
        :param shadow_width: The width of the shadowed edge.
        :param shape: The shape of the requested shadow.
        :param corner_radius: The radius of the shadow corners if this is a rectangular shadow.

        :return: A shadow as a pygame Surface.

        """

    @abstractmethod
    def set_window_resolution(self, window_resolution: Tuple[int, int]):
        """
        Sets the window resolution.

        :param window_resolution: the resolution to set.
        """

    @abstractmethod
    def clear_and_reset(self):
        """
        Clear the whole UI.
        """

    @abstractmethod
    def process_events(self, event: pygame.event.Event):
        """
        This is the top level method through which all input to UI elements is processed and
        reacted to.

        :param event:  pygame.event.Event - the event to process.
        """

    @abstractmethod
    def update(self, time_delta: float):
        """
        Update the UIManager.

        :param time_delta: The time passed since the last call to update, in seconds.
        """

    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get the position of the mouse in the UI.
        """

    @abstractmethod
    def calculate_scaled_mouse_position(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """
        Scaling an input mouse position by a scale factor.
        """

    @abstractmethod
    def draw_ui(self, window_surface: pygame.surface.Surface):
        """
        Draws the UI.

        :param window_surface: The screen or window surface on which we are going to draw all of
         our UI Elements.

        """

    @abstractmethod
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

    @abstractmethod
    def preload_fonts(self, font_list: List[Dict[str, Union[str, int, float]]]):
        """
        Pre-loads a list of fonts.

        :param font_list: A list of font descriptions in dictionary format as described above.

        """

    @abstractmethod
    def print_unused_fonts(self):
        """
        Prints a list of fonts that have been loaded but are not being used.

        """

    @abstractmethod
    def get_focus_set(self) -> Set[IUIElementInterface]:
        """
        Gets the focused set.

        :return: The set of elements that currently have interactive focus.
                 If None, nothing is currently focused.
        """

    @abstractmethod
    def set_focus_set(self, focus: Union[IUIElementInterface, Set[IUIElementInterface]]):
        """
        Set a set of element as the focused set.

        :param focus: The set of element to focus on.
        """

    @abstractmethod
    def set_visual_debug_mode(self, is_active: bool):
        """
        Loops through all our UIElements to turn visual debug mode on or off. Also calls
        print_layer_debug()

        :param is_active: True to activate visual debug and False to turn it off.
        """

    @abstractmethod
    def print_layer_debug(self):
        """
        Print some formatted information on the current state of the UI Layers.

        Handy for debugging layer problems.
        """

    @abstractmethod
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

    @abstractmethod
    def get_universal_empty_surface(self) -> pygame.surface.Surface:
        """
        Sometimes we want to hide sprites or just have sprites with no visual component, when we
        do we can just use this empty surface to save having lots of empty surfaces all over memory.

        :return: An empty, and therefore invisible pygame.surface.Surface

        """

    @abstractmethod
    def create_tool_tip(self,
                        text: str,
                        position: Tuple[int, int],
                        hover_distance: Tuple[int, int],
                        *,
                        text_kwargs: Optional[Dict[str, str]] = None) -> IUITooltipInterface:
        """
        Creates a tool tip ands returns it.

        :param text: The tool tips text, can utilise the HTML subset used in all UITextBoxes.
        :param position: The screen position to create the tool tip for.
        :param hover_distance: The distance we should hover away from our target position.
        :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                            useful when you have multiple translations that need variables inserted
                            in the middle.

        :return: A tool tip placed somewhere on the screen.

        """

    @abstractmethod
    def set_locale(self, locale: str):
        """
        Set a locale language code to use in the UIManager

        :param locale: A two letter ISO 639-1 code for a supported language.

        TODO: Make this raise an exception for an unsupported language?
        """

    @abstractmethod
    def get_locale(self) -> str:
        """
        Get the locale language code being used in the UIManager

        :return: A two letter ISO 639-1 code for the current locale.
        """

    @abstractmethod
    def set_text_input_hovered(self, hovering_text_input: bool):
        """
        Set to true when hovering an area text can be input into.

        Currently switches the cursor to the I-Beam cursor.

        :param hovering_text_input: set to True to toggle the I-Beam cursor
        """

    @abstractmethod
    def get_hovering_any_element(self) -> bool:
        """
        True if any UI element (other than the root container) is hovered by the mouse.

        Combined with 'get_focus_set()' and the return value from process_events(), it should make
        it easier to switch input events between the UI and other parts of an application.
        """
