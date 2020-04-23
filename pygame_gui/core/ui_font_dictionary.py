import os
import io
import base64
import warnings

from typing import Dict

import pygame

from pygame_gui.core.interfaces.font_dictionary_interface import IUIFontDictionaryInterface
from pygame_gui.core.utility import create_resource_path

# Only import the 'stringified' data if we can't find the actual default font file
# This is need for a working PyInstaller build
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
FONT_PATH = os.path.normpath(os.path.join(ROOT_PATH, 'data/FiraCode-Regular.ttf'))
if not os.path.exists(FONT_PATH):
    from pygame_gui.core._string_data import FiraCode_Regular, FiraCode_Bold
    from pygame_gui.core._string_data import FiraMono_BoldItalic, FiraMono_RegularItalic


class UIFontDictionary(IUIFontDictionaryInterface):
    """
    The font dictionary is used to store all the fonts that have been loaded into the UI system.
    """
    _html_font_sizes = {
        1: 8,
        1.5: 9,
        2: 10,
        2.5: 11,
        3: 12,
        3.5: 13,
        4: 14,
        4.5: 16,
        5: 18,
        5.5: 20,
        6: 24,
        6.5: 32,
        7: 48
    }

    _html_font_sizes_reverse_lookup = {
        8: 1,
        9: 1.5,
        10: 2,
        11: 2.5,
        12: 3,
        13: 3.5,
        14: 4,
        16: 4.5,
        18: 5,
        20: 5.5,
        24: 6,
        32: 6.5,
        48: 7
    }

    def __init__(self):
        self.default_font_size = 14
        self.default_font_name = "fira_code"
        self.default_font_style = "regular"
        self.default_font_id = (self.default_font_name + '_' + self.default_font_style
                                + '_' + str(self.default_font_size))

        self.debug_font_size = 8

        self.loaded_fonts = None
        self.known_font_paths = None
        module_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        default_font_file_path = os.path.normpath(os.path.join(module_root_path,
                                                               'data/FiraCode-Regular.ttf'))
        self._load_default_font(default_font_file_path, module_root_path)

        self.used_font_ids = [self.default_font_id]

    def _load_default_font(self, default_font_file_path: str, module_root_path: str):
        """
        Load the default font.

        :param default_font_file_path: path to the font.
        :param module_root_path: root path to the module.

        """
        # Only use the 'stringified' data if we can't find the actual default font file
        # This is need for a working PyInstaller build
        if os.path.exists(default_font_file_path):
            self.loaded_fonts = {self.default_font_id: pygame.font.Font(default_font_file_path,
                                                                        self.default_font_size)}
            regular_path = os.path.abspath(os.path.join(module_root_path,
                                                        'data/FiraCode-Regular.ttf'))
            bold_path = os.path.abspath(os.path.join(module_root_path,
                                                     'data/FiraCode-Bold.ttf'))
            italic_path = os.path.abspath(os.path.join(module_root_path,
                                                       'data/FiraMono-RegularItalic.ttf'))
            bold_italic_path = os.path.abspath(os.path.join(module_root_path,
                                                            'data/FiraMono-BoldItalic.ttf'))
            self.known_font_paths = {'fira_code': [regular_path,
                                                   bold_path,
                                                   italic_path,
                                                   bold_italic_path]}
        else:
            fira_code_regular_file_object = io.BytesIO(base64.standard_b64decode(FiraCode_Regular))
            self.loaded_fonts = {self.default_font_id:
                                 pygame.font.Font(fira_code_regular_file_object,
                                                  self.default_font_size)}

            self.known_font_paths = {'fira_code': [FiraCode_Regular,
                                                   FiraCode_Bold,
                                                   FiraMono_RegularItalic,
                                                   FiraMono_BoldItalic]}

    def find_font(self, font_size: int, font_name: str,
                  bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """
        Find a loaded font from the font dictionary. Will load a font if it does not already exist
        and we have paths to the needed files, however it will issue a warning after doing so
        because dynamic file loading is normally a bad idea as you will get frame rate hitches
        while the running program waits for the font to load.

        Instead it's best to preload all your needed files at another time in your program when
        you have more control over the user experience.

        :param font_size: The size of the font to find.
        :param font_name: The name of the font to find.
        :param bold: Whether the font is bold or not.
        :param italic: Whether the font is italic or not.

        :return pygame.font.Font: Returns either the font we asked for, or the default font.

        """
        font_id = self.create_font_id(font_size, font_name, bold, italic)

        if font_id not in self.used_font_ids:
            self.used_font_ids.append(font_id)  # record font usage for optimisation purposes

        if self.check_font_preloaded(font_id):  # font already loaded
            return self.loaded_fonts[font_id]
        elif font_name in self.known_font_paths:
            # we know paths to this font, just haven't loaded current size/style
            style_string = "regular"
            if bold and italic:
                style_string = "bold_italic"
            elif bold:
                style_string = "bold"
            elif italic:
                style_string = "italic"

            warning_string = ('Finding font with id: ' +
                              font_id +
                              " that is not already loaded.\n"
                              "Preload this font with {'name': "
                              "'" + font_name + "',"
                              " 'point_size': " + str(font_size) + ","
                              " 'style': '" + style_string + "'}")
            warnings.warn(warning_string, UserWarning)
            self.preload_font(font_size, font_name, bold, italic)
            return self.loaded_fonts[font_id]
        else:
            return self.loaded_fonts[self.default_font_id]

    def get_default_font(self) -> pygame.font.Font:
        """
        Grab the default font.

        :return: The default font.

        """
        return self.find_font(self.default_font_size, self.default_font_name)

    def create_font_id(self, font_size: int, font_name: str, bold: bool, italic: bool) -> str:
        """
        Create an id for a particularly styled and sized font from those characteristics.

        :param font_size: The size of the font.
        :param font_name: The name of the font.
        :param bold: Whether the font is bold styled or not.
        :param italic: Whether the font is italic styled or not.

        :return str: The finished font id.

        """
        if font_size <= 0:
            font_size = self.default_font_size
            warnings.warn("Font size less than or equal to 0", UserWarning)
        if bold and italic:
            font_style_string = "bold_italic"
        elif bold:
            font_style_string = "bold"
        elif italic:
            font_style_string = "italic"
        else:
            font_style_string = "regular"
        return font_name + "_" + font_style_string + "_" + str(font_size)

    def preload_font(self, font_size: int, font_name: str,
                     bold: bool = False, italic: bool = False):
        """
        Lets us load a font at a particular size and style before we use it. While you can get
        away with relying on dynamic font loading during development, it is better to eventually
        pre-load all your font data at a controlled time, which is where this method comes in.

        :param font_size: The size of the font to load.
        :param font_name: The name of the font to load.
        :param bold: Whether the font is bold styled or not.
        :param italic: Whether the font is italic styled or not.

        """
        font_id = self.create_font_id(font_size, font_name, bold, italic)
        if font_id in self.loaded_fonts:    # font already loaded
            warnings.warn('Trying to pre-load font id: ' +
                          font_id +
                          ' that is already loaded', UserWarning)
        elif font_name in self.known_font_paths:
            # we know paths to this font, just haven't loaded current size/style
            regular_path = self.known_font_paths[font_name][0]
            bold_path = self.known_font_paths[font_name][1]
            italic_path = self.known_font_paths[font_name][2]
            bold_italic_path = self.known_font_paths[font_name][3]
            if bold and italic:
                self._load_single_font_style(bold_italic_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': True,
                                                         'italic': True})

            elif bold:
                self._load_single_font_style(bold_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': True,
                                                         'italic': False})
            elif italic:
                self._load_single_font_style(italic_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': False,
                                                         'italic': True})
            else:
                self._load_single_font_style(regular_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': False,
                                                         'italic': False})
        else:
            warnings.warn('Trying to pre-load font id:' + font_id + ' with no paths set')

    def _load_single_font_style(self,
                                font_path: str,
                                font_id: str,
                                font_size: int,
                                font_style: Dict[str, bool]):
        """
        Load a single font file with a given style.

        :param font_path: Path to the font file.
        :param font_id: id for the font in the loaded fonts dictionary.
        :param font_size: pygame font size.
        :param font_style: style dictionary (italic, bold, both or neither)

        """
        try:
            if isinstance(font_path, bytes):
                file_loc = io.BytesIO(base64.standard_b64decode(font_path))
            else:
                file_loc = create_resource_path(font_path)
            new_font = pygame.font.Font(file_loc, font_size)
        except (FileNotFoundError, OSError):
            warnings.warn("Failed to load font at path: " + font_path)
        else:
            new_font.set_bold(font_style['bold'])
            new_font.set_italic(font_style['italic'])
            self.loaded_fonts[font_id] = new_font

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
        if font_name not in self.known_font_paths:
            if bold_path is None:
                bold_path = font_path
            if italic_path is None:
                italic_path = font_path
            if bold_italic_path is None:
                bold_italic_path = font_path
            self.known_font_paths[font_name] = [os.path.abspath(font_path),
                                                os.path.abspath(bold_path),
                                                os.path.abspath(italic_path),
                                                os.path.abspath(bold_italic_path)]

    def print_unused_loaded_fonts(self):
        """
        Can be called to check if the UI is loading any fonts that we haven't used by the point
        this function is called. If a font is truly unused then we can remove it from our loading
        and potentially speed up the overall loading of the program.

        This is not a foolproof check because this function could easily be called before we have
        explored all the code paths in a project that may use fonts.
        """
        unused_font_ids = [key for key in self.loaded_fonts if key not in self.used_font_ids]
        if unused_font_ids:
            print('Unused font ids:')
            for font_id in unused_font_ids:
                point_size = int(font_id.split('_')[-1])
                html_size = UIFontDictionary._html_font_sizes_reverse_lookup[point_size]
                print(font_id + '(HTML size: ' + str(html_size) + ')')

    def convert_html_to_point_size(self, html_size: float) -> int:
        """
        Takes in a HTML style font size and converts it into a point font size.

        :param html_size: Size in HTML style.

        :return int: A 'point' font size we can use with pygame.font

        """
        if html_size in UIFontDictionary._html_font_sizes:
            return UIFontDictionary._html_font_sizes[html_size]
        else:
            return self.default_font_size

    def check_font_preloaded(self, font_id: str) -> bool:
        """
        Check if a font is already preloaded or not.

        :param font_id: The ID of the font to check for

        :return: True or False.

        """
        return font_id in self.loaded_fonts

    def ensure_debug_font_loaded(self):
        """
        Ensure the font we use for debugging purposes is loaded. Generally called after we start
        a debugging mode.

        """
        if not self.check_font_preloaded(self.default_font_name + '_'
                                         + self.default_font_style +
                                         '_' + str(self.debug_font_size)):
            self.preload_font(self.debug_font_size, self.default_font_name)
