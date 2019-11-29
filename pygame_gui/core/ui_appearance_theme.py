import pygame
import json
import os
import io
import base64
import warnings
from contextlib import contextmanager

from typing import Union

from pygame_gui.core.ui_font_dictionary import UIFontDictionary
from pygame_gui.core.ui_shadow import ShadowGenerator

# Only import the 'stringified' data if we can't find the actual default theme file
# This is need for working PyInstaller build
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
THEME_PATH = os.path.normpath(os.path.join(ROOT_PATH, 'data/default_theme.json'))
if not os.path.exists(THEME_PATH):
    from pygame_gui.core._string_data import default_theme

try:
    from os import PathLike  # for Python 3.6
except ImportError:
    PathLike = None


class UIAppearanceTheme:
    """
    The Appearance Theme class handles all the data that styles and generally dictates the appearance of UI elements
    across the whole UI.

    The styling is split into four general areas:

    - colours - spelled in the British English fashion with a 'u'.
    - font - specifying a font to use for a UIElement where that is a relevant consideration.
    - images - describing any images to be used in a UIElement.
    - misc - covering all other types of data and stored as strings.

    To change the theming for the UI you normally specify a theme file when creating the UIManager. For more
    information on theme files see the specific documentation elsewhere.
    """
    def __init__(self):

        # the base colours are the default colours all UI elements use if they
        # don't have a more specific colour defined for their element
        self.base_colours = {'normal_bg': pygame.Color('#25292e'),
                             'hovered_bg': pygame.Color('#35393e'),
                             'disabled_bg': pygame.Color('#25292e'),
                             'selected_bg': pygame.Color('#193754'),
                             'active_bg': pygame.Color('#193754'),
                             'dark_bg': pygame.Color('#15191e'),
                             'normal_text': pygame.Color('#c5cbd8'),
                             'hovered_text': pygame.Color('#FFFFFF'),
                             'selected_text': pygame.Color('#FFFFFF'),
                             'active_text': pygame.Color('#FFFFFF'),
                             'disabled_text': pygame.Color('#6d736f'),
                             'normal_border': pygame.Color('#DDDDDD'),
                             'hovered_border': pygame.Color('#EDEDED'),
                             'disabled_border': pygame.Color('#909090'),
                             'selected_border': pygame.Color('#294764'),
                             'active_border': pygame.Color('#294764'),
                             'link_text': pygame.Color('#c5cbFF'),
                             'link_hover': pygame.Color('#a5abDF'),
                             'link_selected': pygame.Color('#DFabDF'),
                             'text_shadow': pygame.Color('#777777'),
                             'filled_bar': pygame.Color("#f4251b"),
                             'unfilled_bar': pygame.Color("#CCCCCC")}

        # colours for specific elements stored by element id then colour id
        self.ui_element_colours = {}

        # font dictionary that stores loaded fonts
        self.font_dictionary = UIFontDictionary()

        # shadow generator
        self.shadow_generator = ShadowGenerator()

        # shape cache
        self.shape_cache = ShapeCache()

        # the font to use if no other font is specified
        # these hardcoded paths should be OK for PyInstaller right now because they will never actually used while
        # fira_code is the default pre-loaded font. May need to re-visit this later.
        module_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.base_font_info = {'name': 'fira_code',
                               'size': 14,
                               'bold': False,
                               'italic': False,
                               'regular_path': os.path.normpath(os.path.join(module_root_path,
                                                                             'data/FiraCode-Regular.ttf')),
                               'bold_path': os.path.normpath(os.path.join(module_root_path,
                                                                          'data/FiraCode-Bold.ttf')),
                               'italic_path': os.path.normpath(os.path.join(module_root_path,
                                                                            'data/FiraMono-RegularItalic.ttf')),
                               'bold_italic_path': os.path.normpath(os.path.join(module_root_path,
                                                                                 'data/FiraMono-BoldItalic.ttf'))}

        # fonts for specific elements stored by element id
        self.ui_element_fonts_info = {}
        self.ui_element_fonts = {}

        # stores any images specified in themes that need loading at the appropriate time
        self.ui_element_image_paths = {}
        self.ui_element_image_surfaces = {}
        self.loaded_image_files = {}  # just a dictionary of all images paths & image files loaded by the UI

        # stores everything that doesn't have a specific place elsewhere and doesn't need any time-consuming loading
        # all will be stored as strings and will have to do any further processing in their specific elements.
        # misc data that doesn't have a value defined in a theme will return None so elements should be prepared
        # to handle that with a default behaviour
        self.ui_element_misc_data = {}

        self._theme_file_last_modified = None
        self._theme_file_path = None

        # Only load  the 'stringified' data if we can't find the actual default theme file
        # This is need for PyInstaller build
        default_theme_file_path = os.path.normpath(os.path.join(module_root_path, 'data','default_theme.json'))
        if os.path.exists(default_theme_file_path):
            self.load_theme(default_theme_file_path)
        else:
            default_theme_file = io.BytesIO(base64.standard_b64decode(default_theme))
            self.load_theme(default_theme_file)

    def get_font_dictionary(self):
        """
        Lets us grab the Font dictionary, which is created by the theme object, so we can access it directly.

        :return UIFontDictionary:
        """
        return self.font_dictionary

    def check_need_to_reload(self):
        """
        Check if we need to reload our theme file because it's been modified. If so, trigger a reload and return True
        so that the UIManager can trigger elements to rebuild from the theme data.

        :return bool: True if we need to reload elements because the theme data has changed.
        """
        if self._theme_file_path is not None:
            try:
                stamp = os.stat(self._theme_file_path).st_mtime
            except FileNotFoundError:
                return False

            if stamp != self._theme_file_last_modified:
                self._theme_file_last_modified = stamp
                self.reload_theming()
                return True
            else:
                return False

    def update_shape_cache(self):
        self.shape_cache.update()

    def reload_theming(self):
        """
        We need to load our theme file see if anything expensive has changed, if so trigger it to reload/rebuild.

        """
        self.load_theme(self._theme_file_path)

    def load_fonts(self):
        """
        Loads all fonts specified in our loaded theme.

        """
        self.font_dictionary.add_font_path(self.base_font_info['name'],
                                           self.base_font_info['regular_path'],
                                           self.base_font_info['bold_path'],
                                           self.base_font_info['italic_path'],
                                           self.base_font_info['bold_italic_path'])

        font_id = self.font_dictionary.create_font_id(self.base_font_info['size'],
                                                      self.base_font_info['name'],
                                                      self.base_font_info['bold'],
                                                      self.base_font_info['italic'])

        if font_id not in self.font_dictionary.loaded_fonts:
            self.font_dictionary.preload_font(self.base_font_info['size'],
                                              self.base_font_info['name'],
                                              self.base_font_info['bold'],
                                              self.base_font_info['italic'])

        for element_key in self.ui_element_fonts_info.keys():
            font_info = self.ui_element_fonts_info[element_key]

            bold_path = None
            italic_path = None
            bold_italic_path = None
            if 'regular_path' in font_info:
                regular_path = font_info['regular_path']

                if 'bold_path' in font_info:
                    bold_path = font_info['bold_path']
                if 'italic_path' in font_info:
                    italic_path = font_info['italic_path']
                if 'bold_italic_path' in font_info:
                    bold_italic_path = font_info['bold_italic_path']

                self.font_dictionary.add_font_path(font_info['name'],
                                                   regular_path,
                                                   bold_path,
                                                   italic_path,
                                                   bold_italic_path)

            font_id = self.font_dictionary.create_font_id(font_info['size'],
                                                          font_info['name'],
                                                          font_info['bold'],
                                                          font_info['italic'])

            if font_id not in self.font_dictionary.loaded_fonts:
                self.font_dictionary.preload_font(font_info['size'],
                                                  font_info['name'],
                                                  font_info['bold'],
                                                  font_info['italic'])

            self.ui_element_fonts[element_key] = self.font_dictionary.find_font(font_info['size'],
                                                                                font_info['name'],
                                                                                font_info['bold'],
                                                                                font_info['italic'])

    def load_images(self):
        """
        Loads all images in our loaded theme.

        """
        for element_key in self.ui_element_image_paths.keys():
            image_paths_dict = self.ui_element_image_paths[element_key]
            if element_key not in self.ui_element_image_surfaces:
                self.ui_element_image_surfaces[element_key] = {}
            for path_key in image_paths_dict:
                if image_paths_dict[path_key]['changed']:
                    path = image_paths_dict[path_key]['path']
                    image = None
                    if path in self.loaded_image_files:
                        image = self.loaded_image_files[path]
                    else:
                        try:
                            image = pygame.image.load(os.path.normpath(path)).convert_alpha()
                            self.loaded_image_files[path] = image
                        except pygame.error:
                            warnings.warn('Unable to load image at path: ' + str(os.path.abspath(path)))

                    if image is not None:
                        if 'sub_surface_rect' in image_paths_dict[path_key]:
                            surface = image.subsurface(image_paths_dict[path_key]['sub_surface_rect'])
                        else:
                            surface = image
                        self.ui_element_image_surfaces[element_key][path_key] = surface

    def preload_shadow_edges(self):
        """
        Looks through the theming data for any shadow edge combos we haven't loaded yet and tries to pre-load them.
        This helps stop the UI from having to create the complicated parts of the shadows dynamically which can be
        noticeably slow (e.g. waiting a second for a window to appear).

        For this to work correctly the theme file shouldn't contain any 'invalid' data that is later clamped by the UI,
        Plus, it is helpful if any rounded rectangles that set a corner radius also set a shadow width at the same time.
        """
        for misc_id in self.ui_element_misc_data:

            shape = 'rectangle'
            shadow_width = 2
            shape_corner_radius = 2

            if 'shape' in self.ui_element_misc_data[misc_id]:
                shape = self.ui_element_misc_data[misc_id]['shape']

            if 'shadow_width' in self.ui_element_misc_data[misc_id]:
                try:
                    shadow_width = int(self.ui_element_misc_data[misc_id]['shadow_width'])
                except ValueError:
                    shadow_width = 2
                    warnings.warn(
                        "Invalid value: " + self.ui_element_misc_data[misc_id]['shadow_width'] +
                        " for shadow_width")

            if 'shape_corner_radius' in self.ui_element_misc_data[misc_id]:
                try:
                    shape_corner_radius = int(self.ui_element_misc_data[misc_id]['shape_corner_radius'])
                except ValueError:
                    shape_corner_radius = 2
                    warnings.warn(
                        "Invalid value: " + self.ui_element_misc_data[misc_id]['shape_corner_radius'] +
                        " for shape_corner_radius")

            # we can preload shadow edges if we are dealing with a rectangular shadow
            if (shape == 'rounded_rectangle' or shape == 'rectangle') and shadow_width > 0:
                if ('shadow_width' in self.ui_element_misc_data[misc_id] and
                        'shape_corner_radius' in self.ui_element_misc_data[misc_id]):
                    shadow_id = str(shadow_width) + 'x' + str(shape_corner_radius)
                    if shadow_id not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width, shape_corner_radius)
                elif ('shadow_width' in self.ui_element_misc_data[misc_id] and
                      'shape_corner_radius' not in self.ui_element_misc_data[misc_id]):
                    # have a shadow width but no idea on the corners, try most common -
                    shadow_id_1 = str(shadow_width) + 'x' + str(2)
                    if shadow_id_1 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width, 2)
                    shadow_id_2 = str(shadow_width) + 'x' + str(shadow_width)
                    if shadow_id_2 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width, shadow_width)
                elif ('shape_corner_radius' in self.ui_element_misc_data[misc_id] and
                      'shadow_width' not in self.ui_element_misc_data[misc_id]):
                    # have a corner radius but no idea on the shadow width, try most common -
                    shadow_id_1 = str(1) + 'x' + str(shape_corner_radius)
                    if shadow_id_1 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(1, shape_corner_radius)
                    shadow_id_2 = str(2) + 'x' + str(shape_corner_radius)
                    if shadow_id_2 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(2, shape_corner_radius)
                    shadow_id_3 = str(shape_corner_radius) + 'x' + str(shape_corner_radius)
                    if shadow_id_3 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shape_corner_radius, shape_corner_radius)

    def get_next_id_node(self, current_node, element_ids, object_ids, index, tree_size, combined_ids):
        if index < tree_size:
            if object_ids is not None:
                if index < len(object_ids):
                    object_id = object_ids[index]
                    if object_id is not None:
                        next_node = {'id': object_id, 'parent': current_node}
                        self.get_next_id_node(next_node, element_ids, object_ids, index + 1, tree_size, combined_ids)
            element_id = element_ids[index]
            next_node_2 = {'id': element_id, 'parent': current_node}
            self.get_next_id_node(next_node_2, element_ids, object_ids, index + 1, tree_size, combined_ids)
        else:
            # unwind
            gathered_ids = []
            unwind_node = current_node
            while unwind_node is not None:
                gathered_ids.append(unwind_node['id'])
                unwind_node = unwind_node['parent']
            gathered_ids.reverse()
            combined_id = gathered_ids[0]
            for index in range(1, len(gathered_ids)):
                combined_id += '.'
                combined_id += gathered_ids[index]
            combined_ids.append(combined_id)

    def build_all_combined_ids(self, element_ids, object_ids):
        """
        Construct a combined element id from the elements ids.

        :param element_ids: All the ids of elements this element is contained within.
        :param object_ids: All the ids of objects this element is contained within.
        :return: The combined id string in the database
        """
        combined_ids = []
        if object_ids is not None and element_ids is not None:
            if len(object_ids) != len(element_ids):
                raise ValueError("Object ID hierarchy is not equal in length to Element ID hierarchy"
                                 "Element IDs: " + str(element_ids) + "\n"
                                 "Object IDs: " + str(object_ids) + "\n")
            if len(element_ids) != 0:
                self.get_next_id_node(None, element_ids, object_ids, 0, len(element_ids), combined_ids)

        return combined_ids

    def get_image(self, object_ids, element_ids, image_id):
        """
        Will return None if no image is specified. There are UI elements that have an optional image display.

        :param image_id: The id identifying the particular image spot in the UI we are looking for an image to add to.
        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :return None or pygame.Surface:
        """

        combined_element_ids = self.build_all_combined_ids(element_ids, object_ids)

        # then check for an element specific data
        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_image_surfaces:
                if image_id in self.ui_element_image_surfaces[combined_element_id]:
                    return self.ui_element_image_surfaces[combined_element_id][image_id]

        return None

    def get_font_info(self, object_ids, element_ids):
        """
        Uses some data about a UIElement to get font data as dictionary

        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :return dictionary: Data about the font requested
        """
        font_info = self.base_font_info

        # Check for a unique theming for this specific object
        combined_element_ids = self.build_all_combined_ids(element_ids, object_ids)

        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_fonts_info:
                return self.ui_element_fonts_info[combined_element_id]

        return font_info

    def get_font(self, object_ids, element_ids):
        """
        Uses some data about a UIElement to get a font object.

        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :return pygame.font.Font: A pygame font object.
        """
        # set the default font as the final fall back
        font = self.font_dictionary.find_font(self.base_font_info['size'],
                                              self.base_font_info['name'],
                                              self.base_font_info['bold'],
                                              self.base_font_info['italic'])

        # Check for a unique theming for this specific object
        combined_element_ids = self.build_all_combined_ids(element_ids, object_ids)

        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_fonts:
                return self.ui_element_fonts[combined_element_id]

        return font

    def get_misc_data(self, object_ids, element_ids, misc_data_id):
        """
        Uses data about a UI element and a specific ID to try and find a piece of miscellaneous theming data.

        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :param misc_data_id: The id for the specific piece of miscellaneous data we are looking for.
        :return None or str: Returns a string if we find the data, otherwise returns None.
        """
        combined_element_ids = self.build_all_combined_ids(element_ids, object_ids)

        # then check for an element specific data
        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_misc_data:
                if misc_data_id in self.ui_element_misc_data[combined_element_id]:
                    return self.ui_element_misc_data[combined_element_id][misc_data_id]

        return None

    def get_colour(self, object_ids, element_ids, colour_id):
        """
        Uses data about a UI element and a specific ID to find a colour from our theme.

        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color: A pygame colour.
        """
        colour_or_gradient = self.get_colour_or_gradient(object_ids, element_ids, colour_id)
        if type(colour_or_gradient) == ColourGradient:
            gradient = colour_or_gradient
            colour = gradient.colour_1
        elif type(colour_or_gradient) == pygame.Color:
            colour = colour_or_gradient
        else:
            colour = pygame.Color('#000000')
        return colour

    def get_colour_or_gradient(self, object_ids, element_ids, colour_id):
        """
        Uses data about a UI element and a specific ID to find a colour, or a gradient, from our theme.
        Use this function if the UIElement can handle either type.

        :param object_ids: A list of custom IDs representing an element's location in a hierarchy.
        :param element_ids: A list of element IDs representing an element's location in a hierarchy.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color or ColourGradient: A colour or a gradient object.
        """
        # first check for a unique theming for this specific object
        combined_element_ids = self.build_all_combined_ids(element_ids, object_ids)

        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_colours:
                if colour_id in self.ui_element_colours[combined_element_id]:
                    return self.ui_element_colours[combined_element_id][colour_id]

        # if we don't have a specific colour for our individual element, try to inherit colours from higher
        # in the hierarchy
        if object_ids is not None:
            for object_id in object_ids:
                if object_id is not None:
                    if object_id in self.ui_element_colours:
                        if colour_id in self.ui_element_colours[object_id]:
                            return self.ui_element_colours[object_id][colour_id]

        if element_ids is not None:
            for element_id in element_ids:
                if element_id in self.ui_element_colours:
                    if colour_id in self.ui_element_colours[element_id]:
                        return self.ui_element_colours[element_id][colour_id]

        # then fall back on default colour with same id
        if colour_id in self.base_colours:
            return self.base_colours[colour_id]

        # if all else fails find a colour with the most similar id words
        colour_parts = colour_id.split('_')
        best_fit_key_count = 0
        best_fit_colour = self.base_colours['normal_bg']
        for key in self.base_colours.keys():
            key_words = key.split('_')
            count = sum(el in colour_parts for el in key_words)
            if count > best_fit_key_count:
                best_fit_key_count = count
                best_fit_colour = self.base_colours[key]
        return best_fit_colour

    @staticmethod
    @contextmanager
    def opened_w_error(filename, mode="r"):
        if type(filename) != io.BytesIO:
            try:
                f = open(filename, mode)
            except IOError as err:
                yield None, err
            else:
                try:
                    yield f, None
                finally:
                    f.close()
        else:
            f = filename
            try:
                yield f, None
            finally:
                f.close()

    def load_theme(self, file_path: Union[str, PathLike, io.BytesIO]):
        """
        Loads a theme file, and currently, all associated data like fonts and images required by the theme.

        :param file_path: The path to the theme we want to load.

        """
        if file_path is None:
            raise ValueError('Theme path cannot be None')

        if type(file_path) != io.BytesIO:
            self._theme_file_path = file_path
            self._theme_file_last_modified = os.stat(self._theme_file_path).st_mtime
            used_file_path = os.path.abspath(file_path)
        else:
            used_file_path = file_path

        with self.opened_w_error(used_file_path, 'r') as (theme_file, error):
            if error:
                warnings.warn("Failed to open theme file at path:" + str(file_path))
                load_success = False
            else:
                try:
                    load_success = True
                    theme_dict = json.load(theme_file)
                except json.decoder.JSONDecodeError:
                    warnings.warn("Failed to load current theme file, check syntax", UserWarning)
                    load_success = False

                if load_success:
                    for element_name in theme_dict.keys():
                        if element_name == 'defaults':
                            self.load_colour_defaults_from_theme(element_name, theme_dict)
                        else:
                            for data_type in theme_dict[element_name]:
                                if data_type == 'font':
                                    self.load_element_font_data_from_theme(data_type, element_name, theme_dict)

                                if data_type == 'colours':
                                    self.load_element_colour_data_from_theme(data_type, element_name, theme_dict)

                                elif data_type == 'images':
                                    self.load_element_image_data_from_theme(data_type, element_name, theme_dict)

                                elif data_type == 'misc':
                                    self.load_element_misc_data_from_theme(data_type, element_name, theme_dict)

        # TODO: these should be triggered at an appropriate time in our project when lots of files are being loaded
        if load_success:
            self.load_fonts()  # save to trigger load with the same data as it won't do anything
            self.load_images()
            self.preload_shadow_edges()

    def load_element_misc_data_from_theme(self, data_type, element_name, theme_dict):
        if element_name not in self.ui_element_misc_data:
            self.ui_element_misc_data[element_name] = {}
        misc_dict = theme_dict[element_name][data_type]
        for misc_data_key in misc_dict:
            self.ui_element_misc_data[element_name][misc_data_key] = str(misc_dict[misc_data_key])

    def load_element_image_data_from_theme(self, data_type, element_name, theme_dict):
        if element_name not in self.ui_element_image_paths:
            self.ui_element_image_paths[element_name] = {}
        images_dict = theme_dict[element_name][data_type]
        for image_key in images_dict:
            if image_key not in self.ui_element_image_paths[element_name]:
                self.ui_element_image_paths[element_name][image_key] = {}
                self.ui_element_image_paths[element_name][image_key]['changed'] = True
            else:
                self.ui_element_image_paths[element_name][image_key]['changed'] = False
            image_path = str(images_dict[image_key]['path'])
            if 'path' in self.ui_element_image_paths[element_name][image_key]:
                if image_path != self.ui_element_image_paths[element_name][image_key]['path']:
                    self.ui_element_image_paths[element_name][image_key]['changed'] = True
            self.ui_element_image_paths[element_name][image_key]['path'] = image_path
            if 'sub_surface_rect' in images_dict[image_key]:
                rect_list = str(images_dict[image_key]['sub_surface_rect']).strip().split(',')
                if len(rect_list) == 4:
                    try:
                        x = int(rect_list[0].strip())
                        y = int(rect_list[1].strip())
                        w = int(rect_list[2].strip())
                        h = int(rect_list[3].strip())
                        rect = pygame.Rect((x, y), (w, h))
                    except ValueError or TypeError:
                        rect = pygame.Rect((0, 0), (10, 10))
                        warnings.warn("Unable to create subsurface rectangle from string: "
                                      "" + images_dict[image_key]['sub_surface_rect'])

                    if 'sub_surface_rect' in self.ui_element_image_paths[element_name][image_key]:
                        if rect != self.ui_element_image_paths[element_name][image_key]['sub_surface_rect']:
                            self.ui_element_image_paths[element_name][image_key]['changed'] = True
                    self.ui_element_image_paths[element_name][image_key]['sub_surface_rect'] = rect

    def load_element_colour_data_from_theme(self, data_type, element_name, theme_dict):
        if element_name not in self.ui_element_colours:
            self.ui_element_colours[element_name] = {}
        colours_dict = theme_dict[element_name][data_type]
        for colour_key in colours_dict:
            self.ui_element_colours[element_name][colour_key] = self.load_colour_or_gradient_from_theme(colours_dict,
                                                                                                        colour_key)

    def load_element_font_data_from_theme(self, data_type, element_name, theme_dict):
        font_dict = theme_dict[element_name][data_type]
        if element_name not in self.ui_element_fonts_info:
            self.ui_element_fonts_info[element_name] = {}
        self.ui_element_fonts_info[element_name]['name'] = font_dict['name']
        try:
            self.ui_element_fonts_info[element_name]['size'] = int(font_dict['size'])
        except ValueError:
            self.ui_element_fonts_info[element_name]['size'] = self.font_dictionary.default_font_size
        if 'bold' in font_dict:
            try:
                self.ui_element_fonts_info[element_name]['bold'] = bool(int(font_dict['bold']))
            except ValueError:
                self.ui_element_fonts_info[element_name]['bold'] = False
        else:
            self.ui_element_fonts_info[element_name]['bold'] = False
        if 'italic' in font_dict:
            try:
                self.ui_element_fonts_info[element_name]['italic'] = bool(int(font_dict['italic']))
            except ValueError:
                self.ui_element_fonts_info[element_name]['italic'] = False
        else:
            self.ui_element_fonts_info[element_name]['italic'] = False
        if 'regular_path' in font_dict:
            self.ui_element_fonts_info[element_name]['regular_path'] = font_dict['regular_path']
        if 'bold_path' in font_dict:
            self.ui_element_fonts_info[element_name]['bold_path'] = font_dict['bold_path']
        if 'italic_path' in font_dict:
            self.ui_element_fonts_info[element_name]['italic_path'] = font_dict['italic_path']
        if 'bold_italic_path' in font_dict:
            bold_italic_path = font_dict['bold_italic_path']
            self.ui_element_fonts_info[element_name]['bold_italic_path'] = bold_italic_path

    def load_colour_defaults_from_theme(self, element_name, theme_dict):
        for data_type in theme_dict[element_name]:
            if data_type == 'colours':
                colours_dict = theme_dict[element_name][data_type]
                for colour_key in colours_dict:
                    self.base_colours[colour_key] = self.load_colour_or_gradient_from_theme(colours_dict, colour_key)

    @staticmethod
    def load_colour_or_gradient_from_theme(theme_colours_dictionary, colour_id):
        loaded_colour_or_gradient = None
        string_data = theme_colours_dictionary[colour_id]
        if ',' in string_data:
            # expecting some type of gradient description in string data
            string_data_list = string_data.split(',')
            gradient_direction = None
            try:
                gradient_direction = int(string_data_list[-1])
            except ValueError:
                warnings.warn("Invalid gradient: " + string_data + " for id:" + colour_id + " in theme file")

            if gradient_direction is not None and len(string_data_list) == 3:
                # two colour gradient
                try:
                    colour_1 = pygame.Color(string_data_list[0])
                    colour_2 = pygame.Color(string_data_list[1])
                    loaded_colour_or_gradient = ColourGradient(gradient_direction, colour_1, colour_2)
                except ValueError:
                    warnings.warn("Invalid gradient: " + string_data + " for id:" + colour_id + " in theme file")
            elif gradient_direction is not None and len(string_data_list) == 4:
                # three colour gradient
                try:
                    colour_1 = pygame.Color(string_data_list[0])
                    colour_2 = pygame.Color(string_data_list[1])
                    colour_3 = pygame.Color(string_data_list[2])
                    loaded_colour_or_gradient = ColourGradient(gradient_direction, colour_1, colour_2, colour_3)
                except ValueError:
                    warnings.warn("Invalid gradient: " + string_data + " for id:" + colour_id + " in theme file")
            else:
                warnings.warn("Invalid gradient: " + string_data + " for id:" + colour_id + " in theme file")
        else:
            # expecting a regular hex colour in string data
            try:
                loaded_colour_or_gradient = pygame.Color(string_data)
            except ValueError:
                warnings.warn("Colour hex code: " + string_data + " for id:" + colour_id + " invalid in theme file")

        if loaded_colour_or_gradient is None:
            # if the colour or gradient data is invalid, return a black default colour
            loaded_colour_or_gradient = pygame.Color("#000000")

        return loaded_colour_or_gradient


class ColourGradient:
    def __init__(self, angle_direction: int, colour_1: pygame.Color,
                 colour_2: pygame.Color, colour_3: Union[pygame.Color, None] = None):
        self.angle_direction = angle_direction
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.colour_3 = colour_3

        if self.colour_3 is None:
            pixel_width = 2
            colour_pixels_surf = pygame.Surface((pixel_width, 1), flags=pygame.SRCALPHA, depth=32)
            colour_pixels_surf.fill(self.colour_1, pygame.Rect((0, 0), (1, 1)))
            colour_pixels_surf.fill(self.colour_2, pygame.Rect((1, 0), (1, 1)))
        else:
            pixel_width = 3
            colour_pixels_surf = pygame.Surface((pixel_width, 1), flags=pygame.SRCALPHA, depth=32)
            colour_pixels_surf.fill(self.colour_1, pygame.Rect((0, 0), (1, 1)))
            colour_pixels_surf.fill(self.colour_2, pygame.Rect((1, 0), (1, 1)))
            colour_pixels_surf.fill(self.colour_3, pygame.Rect((2, 0), (1, 1)))

        self.gradient_surface = pygame.transform.rotozoom(colour_pixels_surf, 0, 30)

    def __eq__(self, other):
        if type(other) != ColourGradient:
            return False
        return (self.colour_1 == other.colour_1 and
                self.colour_2 == other.colour_2 and
                self.colour_3 == other.colour_3 and
                self.angle_direction == other.angle_direction)

    def __str__(self):
        result = (str(self.angle_direction) + '_' +
                  str(self.colour_1.r) + '_' + str(self.colour_1.g) + '_' +
                  str(self.colour_1.b) + '_' + str(self.colour_1.a) + '_' +
                  str(self.colour_2.r) + '_' + str(self.colour_2.g) + '_' +
                  str(self.colour_2.b) + '_' + str(self.colour_2.a))
        if self.colour_3 is not None:
            result += ('_' + str(self.colour_3.r) + '_' + str(self.colour_3.g) +
                       '_' + str(self.colour_3.b) + '_' + str(self.colour_3.a))

        return result

    def apply_gradient_to_surface(self, input_surface: pygame.Surface, rect=None):
        """
        Applies this gradient to a specified input surface using blending multiplication.
        As a result this method works best when the input surface is a mostly white, stencil shape type surface.

        :param input_surface:
        :param rect: The rectangle on the surface to apply the gradient to.
        """
        # scale the gradient up to the right size
        input_surface_size = input_surface.get_size()
        inverse_rotated_input = pygame.transform.rotate(input_surface, -self.angle_direction)
        gradient_size = inverse_rotated_input.get_rect().size
        gradient_surf = pygame.Surface(gradient_size, flags=pygame.SRCALPHA, depth=32)

        pygame.transform.scale(self.gradient_surface, gradient_size, gradient_surf)
        gradient_surf = pygame.transform.rotate(gradient_surf, self.angle_direction)

        if rect is not None:
            input_surface.set_clip(rect)
            input_surface.blit(gradient_surf, rect, special_flags=pygame.BLEND_RGBA_MULT)
            input_surface.set_clip(None)
        else:
            gradient_placement_rect = gradient_surf.get_rect()
            gradient_placement_rect.center = (int(input_surface_size[0] / 2), int(input_surface_size[1] / 2))

            input_surface.blit(gradient_surf, gradient_placement_rect, special_flags=pygame.BLEND_RGBA_MULT)


class ShapeCache:
    def __init__(self):
        self.cache_surface_size = (1024, 1024)
        self.cache_surfaces = []
        self.current_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
        self.current_surface.fill(pygame.Color('#00000000'))
        self.cache_surfaces.append(self.current_surface)

        self.free_space_rectangles = [pygame.Rect((0, 0), self.cache_surface_size)]

        self.cache_long_term_lookup = {}
        self.cache_short_term_lookup = {}

    def add_surface_to_cache(self, surface, string_id):
        self.cache_short_term_lookup[string_id] = surface.copy()

    def update(self):
        if any(self.cache_short_term_lookup):
            string_id, surface = self.cache_short_term_lookup.popitem()
            self.add_surface_to_long_term_cache(surface, string_id)

    def add_surface_to_long_term_cache(self, surface, string_id):
        surface_size = surface.get_size()
        if surface_size > self.cache_surface_size:
            warnings.warn('Unable to cache surfaces larger than ' + str(self.cache_surface_size))
            return None
        else:
            found_rectangle_to_split = None
            found_rectangle_cache = None

            while found_rectangle_cache is None:
                for free_rectangle in self.free_space_rectangles:
                    if found_rectangle_cache is None and (free_rectangle.width >= surface_size[0] and
                                                          free_rectangle.height >= surface_size[1]):
                        # we fits, so we sits
                        found_rectangle_to_split = free_rectangle
                        found_rectangle_cache = pygame.Rect(free_rectangle.topleft, surface_size)
                        self.current_surface.blit(surface, free_rectangle.topleft)
                        self.cache_long_term_lookup[string_id] = self.current_surface.subsurface(found_rectangle_cache)
                        break

                if found_rectangle_to_split is not None and found_rectangle_cache is not None:
                    self.split_rect(found_rectangle_to_split, found_rectangle_cache)
                    # check if our new cached rect overlaps any others
                    rects_to_split = []
                    for rect in self.free_space_rectangles:
                        if rect.colliderect(found_rectangle_cache):
                            rects_to_split.append(rect)

                    for split_rect in rects_to_split:
                        self.split_rect(split_rect, found_rectangle_cache)

                    # clean up rectangles entirely inside other rectangles
                    rects_to_remove = []
                    rectangles_to_check = [rectangle for rectangle in self.free_space_rectangles]
                    for free_rectangle in self.free_space_rectangles:
                        for check_rect in rectangles_to_check:
                            if free_rectangle != check_rect:
                                if check_rect.contains(free_rectangle):
                                    rects_to_remove.append(free_rectangle)
                    self.free_space_rectangles = [rect for rect in self.free_space_rectangles
                                                  if rect not in rects_to_remove]

                elif found_rectangle_to_split is None:
                    # create a new cache surface
                    self.current_surface = pygame.Surface(self.cache_surface_size, flags=pygame.SRCALPHA, depth=32)
                    self.current_surface.fill(pygame.Color('#00000000'))
                    self.cache_surfaces.append(self.current_surface)
                    self.free_space_rectangles = [pygame.Rect((0, 0), self.cache_surface_size)]

            return True

    def split_rect(self, found_rectangle_to_split, dividing_rect):
        self.free_space_rectangles.remove(found_rectangle_to_split)

        # create new rectangles
        if (found_rectangle_to_split.right - dividing_rect.right) > 0:
            rect_1 = pygame.Rect(dividing_rect.right,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.right - dividing_rect.right,
                                 found_rectangle_to_split.height)
            self.free_space_rectangles.append(rect_1)
        if (found_rectangle_to_split.bottom - dividing_rect.bottom) > 0:
            rect_2 = pygame.Rect(found_rectangle_to_split.left,
                                 dividing_rect.bottom,
                                 found_rectangle_to_split.width,
                                 found_rectangle_to_split.bottom - dividing_rect.bottom)
            self.free_space_rectangles.append(rect_2)
        if (dividing_rect.top - found_rectangle_to_split.top) > 0:
            rect_3 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 found_rectangle_to_split.width,
                                 dividing_rect.top - found_rectangle_to_split.top)
            self.free_space_rectangles.append(rect_3)
        if (dividing_rect.left - found_rectangle_to_split.left) > 0:
            rect_4 = pygame.Rect(found_rectangle_to_split.left,
                                 found_rectangle_to_split.top,
                                 dividing_rect.left - found_rectangle_to_split.left,
                                 found_rectangle_to_split.height)
            self.free_space_rectangles.append(rect_4)

    def find_surface_in_cache(self, lookup_id):
        # check short term
        if lookup_id in self.cache_short_term_lookup:
            return self.cache_short_term_lookup[lookup_id]
        # check long term
        if lookup_id in self.cache_long_term_lookup:
            return self.cache_long_term_lookup[lookup_id]
        else:
            return None

    @staticmethod
    def build_cache_id(shape, size, shadow_width, border_width, border_colour, bg_colour, corner_radius=None):

        id_string = (shape + '_' + str(size[0]) + '_' + str(size[1]) + '_' +
                     str(shadow_width) + '_' + str(border_width))

        if corner_radius is not None:
            id_string += '_' + str(corner_radius)

        if type(border_colour) == ColourGradient:
            id_string += '_' + str(border_colour)
        else:
            id_string += ('_' + str(border_colour.r) + '_' + str(border_colour.g) +
                          '_' + str(border_colour.b) + '_' + str(border_colour.a))

        if type(bg_colour) == ColourGradient:
            id_string += '_' + str(bg_colour)
        else:
            id_string += ('_' + str(bg_colour.r) + '_' + str(bg_colour.g) +
                          '_' + str(bg_colour.b) + '_' + str(bg_colour.a))

        return id_string
