import os
import warnings

from typing import Dict, Union
from importlib.util import find_spec


import pygame

from pygame_gui.core.interfaces.font_dictionary_interface import IUIFontDictionaryInterface
from pygame_gui.core.resource_loaders import IResourceLoader
from pygame_gui.core.utility import PackageResource
from pygame_gui.core.utility import FontResource

# First try importlib
# Then importlib_resources
# If that fails fall back to __file__
# Finally fall back to stringified data
USE_IMPORT_LIB_RESOURCE = False
USE_FILE_PATH = False
USE_STRINGIFIED_DATA = False

RESOURCES_MODULE_SPEC = find_spec(name="importlib.resources")
if RESOURCES_MODULE_SPEC is None:
    RESOURCES_MODULE_SPEC = find_spec(name="importlib_resources")
    if RESOURCES_MODULE_SPEC is None:
        ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        FONT_PATH = os.path.normpath(os.path.join(ROOT_PATH, 'data/FiraCode-Regular.ttf'))
        if not os.path.exists(FONT_PATH):
            USE_STRINGIFIED_DATA = True
            from pygame_gui.core._string_data import FiraCode_Regular, FiraCode_Bold
            from pygame_gui.core._string_data import FiraMono_BoldItalic, FiraMono_RegularItalic
        else:
            USE_FILE_PATH = True
    else:
        USE_IMPORT_LIB_RESOURCE = True
else:
    USE_IMPORT_LIB_RESOURCE = True


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

    def __init__(self, resource_loader: IResourceLoader):
        # , use_threaded_loading: bool = False, loading_queue: ClosableQueue = None
        # self.use_threaded_loading = use_threaded_loading
        # self.loading_queue = loading_queue
        self._resource_loader = resource_loader

        self.default_font_size = 14
        self.default_font_name = "fira_code"
        self.default_font_style = "regular"
        self.default_font_id = (self.default_font_name + '_' + self.default_font_style
                                + '_' + str(self.default_font_size))

        self.default_font_info = {'name': self.default_font_name,
                                  'size': self.default_font_size,
                                  'bold': False,
                                  'italic': False}

        self.debug_font_size = 8

        self.loaded_fonts = {}  # type: Dict[str, FontResource]
        self.known_font_paths = {}

        self._load_default_font()

        self.used_font_ids = [self.default_font_id]

    def _load_default_font(self):
        """
        Load the default font.

        """
        default_font_res = FontResource(font_id=self.default_font_id,
                                        size=self.default_font_size,
                                        style={'bold': False, 'italic': False},
                                        location=PackageResource(package='pygame_gui.data',
                                                                 resource='FiraCode-Regular.ttf'))
        if not USE_STRINGIFIED_DATA:
            error = default_font_res.load()
            if error is not None:
                warnings.warn(str(error))
            self.loaded_fonts[self.default_font_id] = default_font_res

            self.known_font_paths['fira_code'] = [
                PackageResource(package='pygame_gui.data',
                                resource='FiraCode-Regular.ttf'),
                PackageResource(package='pygame_gui.data',
                                resource='FiraCode-Bold.ttf'),
                PackageResource(package='pygame_gui.data',
                                resource='FiraMono-RegularItalic.ttf'),
                PackageResource(package='pygame_gui.data',
                                resource='FiraMono-BoldItalic.ttf')]
        else:
            default_font_res.location = FiraCode_Regular
            error = default_font_res.load()
            if error is not None:
                warnings.warn(str(error))
            self.loaded_fonts[self.default_font_id] = default_font_res

            self.known_font_paths['fira_code'] = [FiraCode_Regular,
                                                  FiraCode_Bold,
                                                  FiraMono_RegularItalic,
                                                  FiraMono_BoldItalic]

    def find_font(self, font_size: int, font_name: str,
                  bold: bool = False, italic: bool = False) -> pygame.freetype.Font:
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

        :return pygame.freetype.Font: Returns either the font we asked for, or the default font.

        """
        return self.find_font_resource(font_size, font_name, bold, italic).loaded_font

    def find_font_resource(self, font_size: int, font_name: str,
                           bold: bool = False, italic: bool = False) -> FontResource:
        """
        Find a loaded font resource from the font dictionary. Will load a font if it does not
        already exist and we have paths to the needed files, however it will issue a warning
        after doing so because dynamic file loading is normally a bad idea as you will get frame
        rate hitches hile the running program waits for the font to load.

        Instead it's best to preload all your needed files at another time in your program when
        you have more control over the user experience.

        :param font_size: The size of the font to find.
        :param font_name: The name of the font to find.
        :param bold: Whether the font is bold or not.
        :param italic: Whether the font is italic or not.

        :return FontResource: Returns either the font resource we asked for, or the default font.

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
            self.preload_font(font_size, font_name, bold, italic, force_immediate_load=True)
            return self.loaded_fonts[font_id]
        else:
            return self.loaded_fonts[self.default_font_id]

    def get_default_font(self) -> pygame.freetype.Font:
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
                     bold: bool = False, italic: bool = False,
                     force_immediate_load: bool = False):
        """
        Lets us load a font at a particular size and style before we use it. While you can get
        away with relying on dynamic font loading during development, it is better to eventually
        pre-load all your font data at a controlled time, which is where this method comes in.

        :param font_size: The size of the font to load.
        :param font_name: The name of the font to load.
        :param bold: Whether the font is bold styled or not.
        :param italic: Whether the font is italic styled or not.
        :param force_immediate_load: resource loading setup to immediately
                                     load the font on the main thread.

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
                                                         'italic': True},
                                             force_immediate_load=force_immediate_load)

            elif bold:
                self._load_single_font_style(bold_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': True,
                                                         'italic': False},
                                             force_immediate_load=force_immediate_load)
            elif italic:
                self._load_single_font_style(italic_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': False,
                                                         'italic': True},
                                             force_immediate_load=force_immediate_load)
            else:
                self._load_single_font_style(regular_path,
                                             font_id,
                                             font_size,
                                             font_style={'bold': False,
                                                         'italic': False},
                                             force_immediate_load=force_immediate_load)
        else:
            warnings.warn('Trying to pre-load font id:' + font_id + ' with no paths set')

    def _load_single_font_style(self,
                                font_loc: Union[str, PackageResource, bytes],
                                font_id: str,
                                font_size: int,
                                font_style: Dict[str, bool],
                                force_immediate_load: bool = False):
        """
        Load a single font file with a given style.

        :param font_loc: Path to the font file.
        :param font_id: id for the font in the loaded fonts dictionary.
        :param font_size: pygame font size.
        :param font_style: style dictionary (italic, bold, both or neither)

        """
        resource = FontResource(font_id=font_id,
                                size=font_size,
                                style=font_style,
                                location=font_loc)
        if self._resource_loader.started() or force_immediate_load:
            error = resource.load()
            if error is not None:
                warnings.warn(str(error))

        else:
            self._resource_loader.add_resource(resource)

        self.loaded_fonts[font_id] = resource

    def add_font_path(self,
                      font_name: str,
                      font_path: Union[str, PackageResource],
                      bold_path: Union[str, PackageResource] = None,
                      italic_path: Union[str, PackageResource] = None,
                      bold_italic_path: Union[str, PackageResource] = None):
        """
        Adds paths to different font files for a font name.

        :param font_name: The name to assign to these font files.
        :param font_path: The path to the font's file with no particular style.
        :param bold_path: The path to the font's file with a bold style.
        :param italic_path: The path to the font's file with an italic style.
        :param bold_italic_path: The path to the font's file with a bold and an italic style.

        """
        if font_name in self.known_font_paths:
            return

        if isinstance(font_path, PackageResource):
            regular_font_loc = font_path
        else:
            regular_font_loc = os.path.abspath(font_path)

        style_locations = [bold_path, italic_path, bold_italic_path]
        for index, location in enumerate(style_locations):
            if location is None:
                style_locations[index] = regular_font_loc
            elif not isinstance(location, PackageResource):
                style_locations[index] = os.path.abspath(location)

            self.known_font_paths[font_name] = [regular_font_loc,
                                                style_locations[0],
                                                style_locations[1],
                                                style_locations[2]]

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

        :return int: A 'point' font size we can use with pygame.freetype

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
            self.preload_font(self.debug_font_size, self.default_font_name,
                              force_immediate_load=True)
