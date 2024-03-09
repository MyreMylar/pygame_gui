from abc import ABCMeta, abstractmethod
from pygame import DIRECTION_LTR
from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface


class IUIFontDictionaryInterface(metaclass=ABCMeta):
    """
    A metaclass that defines the interface that a font dictionary uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """

    @abstractmethod
    def find_font(self, font_size: int, font_name: str,
                  bold: bool = False, italic: bool = False,
                  antialiased: bool = True,
                  script: str = 'Latn',
                  direction: int = DIRECTION_LTR) -> IGUIFontInterface:
        """
        Find a loaded font from the font dictionary. Will load a font if it does not already exist,
        and we have paths to the needed files, however it will issue a warning after doing so
        because dynamic file loading is normally a bad idea as you will get frame rate hitches
        while the running program waits for the font to load.

        Instead, it's best to preload all your needed files at another time in your program when
        you have more control over the user experience.

        :param font_size: The size of the font to find.
        :param font_name: The name of the font to find.
        :param bold: Whether the font is bold or not.
        :param italic: Whether the font is italic or not.
        :param antialiased: Whether the font is antialiased or not.
        :param script: The ISO 15924 script code used for text shaping as a string.
        :param direction: the direction of text e.g. left to right or right to left. An integer.

        :return IGUIFontInterface: Returns either the font we asked for, or the default font.

        """

    @abstractmethod
    def get_default_font(self) -> IGUIFontInterface:
        """
        Grab the default font.

        :return: The default font.

        """

    @abstractmethod
    def create_font_id(self, font_size: int, font_name: str, bold: bool, italic: bool,
                       antialiased: bool = True) -> str:
        """
        Create an id for a particularly styled and sized font from those characteristics.

        :param font_size: The size of the font.
        :param font_name: The name of the font.
        :param bold: Whether the font is bold styled or not.
        :param italic: Whether the font is italic styled or not.
        :param antialiased: Whether the font is antialiased or not.

        :return str: The finished font id.

        """

    @abstractmethod
    def preload_font(self, font_size: int, font_name: str,
                     bold: bool = False, italic: bool = False,
                     force_immediate_load: bool = False,
                     antialiased: bool = True,
                     script: str = 'Latn',
                     direction: int = DIRECTION_LTR):
        """
        Lets us load a font at a particular size and style before we use it. While you can get
        away with relying on dynamic font loading during development, it is better to eventually
        preload all your font data at a controlled time, which is where this method comes in.

        :param font_size: The size of the font to load.
        :param font_name: The name of the font to load.
        :param bold: Whether the font is bold styled or not.
        :param italic: Whether the font is italic styled or not.
        :param force_immediate_load: bypasses any asynchronous threaded loading setup to immediately
                                     load the font on the main thread.
        :param antialiased: Whether the font is antialiased or not.
        :param script: The ISO 15924 script code used for text shaping as a string.
        :param direction: the direction of text e.g. left to right or right to left. An integer.

        """

    @abstractmethod
    def add_font_path(self, font_name: str, font_path: str, bold_path: str = None,
                      italic_path: str = None, bold_italic_path: str = None):
        """
        Adds paths to different font files for a font name.

        :param font_name: The name to assign to these font files.
        :param font_path: The path to the font's file with no particular style.
        :param bold_path: The path to the font's file with a bold style.
        :param italic_path: The path to the font's file with an italic style.
        :param bold_italic_path: The path to the font's file with a bold and an italic style.

        """

    @abstractmethod
    def print_unused_loaded_fonts(self):
        """
        Can be called to check if the UI is loading any fonts that we haven't used by the point
        this function is called. If a font is truly unused then we can remove it from our loading
        and potentially speed up the overall loading of the program.

        This is not a foolproof check because this function could easily be called before we have
        explored all the code paths in a project that may use fonts.
        """

    @abstractmethod
    def convert_html_to_point_size(self, html_size: float) -> int:
        """
        Takes in an HTML style font size and converts it into a point font size.

        :param html_size: Size in HTML style.

        :return int: A 'point' font size.

        """

    @abstractmethod
    def check_font_preloaded(self, font_id: str) -> bool:
        """
        Check if a font is already preloaded or not.

        :param font_id: The ID of the font to check for

        :return: True or False.

        """

    @abstractmethod
    def ensure_debug_font_loaded(self):
        """
        Ensure the font we use for debugging purposes is loaded. Generally called after we start
        a debugging mode.

        """

    def set_locale(self, new_locale: str):
        """
        This may change the default font.

        :param new_locale: The new locale to set, a two-letter country code ISO 639-1
        """
