import pygame
import json
import os

from ..core.ui_font_dictionary import UIFontDictionary


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
                             'link_text': pygame.Color('#c5cbFF'),
                             'link_hover': pygame.Color('#a5abDF'),
                             'link_selected': pygame.Color('#DFabDF'),
                             'text_shadow': pygame.Color('#777777'),
                             'border': pygame.Color('#DDDDDD'),
                             'filled_bar': pygame.Color("#f4251b"),
                             'unfilled_bar': pygame.Color("#CCCCCC")}

        # colours for specific elements stored by element id then colour id
        self.ui_element_colours = {}

        # font dictionary that stores loaded fonts
        self.font_dictionary = UIFontDictionary()

        # the font to use if no other font is specified
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
        self.ui_element_font_infos = {}
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

    def get_font_dictionary(self):
        """
        Lets us grab the Font dictionary, which is created by the theme object, so we can access it directly.

        :return UIFontDictionary:
        """
        return self.font_dictionary

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

        for element_key in self.ui_element_font_infos.keys():
            font_info = self.ui_element_font_infos[element_key]

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
            self.ui_element_image_surfaces[element_key] = {}
            for path_key in image_paths_dict:
                path = image_paths_dict[path_key]['path']
                if path in self.loaded_image_files:
                    image = self.loaded_image_files[path]
                else:
                    image = pygame.image.load(path).convert_alpha()
                    self.loaded_image_files[path] = image

                if 'sub_surface_rect' in image_paths_dict[path_key]:
                    surface = image.subsurface(image_paths_dict[path_key]['sub_surface_rect'])
                else:
                    surface = image
                self.ui_element_image_surfaces[element_key][path_key] = surface

    def get_image(self, object_id, element_ids, image_id):
        """
        Will return None if no image is specified. There are UI elements that have an optional image display.

        :param image_id: The id identifying the particular image spot in the UI we are looking for an image to add to.
        :param object_id: An ID for the particular instance of this element being created.
        :param element_ids: A list of IDs for all elements of this particular type in the theme.
        :return None or pygame.Surface:
        """

        if object_id is not None:
            if object_id in self.ui_element_image_surfaces:
                if image_id in self.ui_element_image_surfaces[object_id]:
                    return self.ui_element_image_surfaces[object_id][image_id]

        # then check for an element specific colour
        for element_id in element_ids:
            if element_id in self.ui_element_image_surfaces:
                if image_id in self.ui_element_image_surfaces[element_id]:
                    return self.ui_element_image_surfaces[element_id][image_id]

        return None

    def get_font(self, object_id, element_ids):
        """
        Uses some data about a UIElement to get a font object.

        :param object_id: An ID for the particular instance of this element being created.
        :param element_ids: A list of IDs for all elements of this particular type in the theme.
        :return pygame.font.Font: A pygame font object.
        """
        # set the default font as the final fall back
        font = self.font_dictionary.find_font(self.base_font_info['size'],
                                              self.base_font_info['name'],
                                              self.base_font_info['bold'],
                                              self.base_font_info['italic'])

        # first check for a unique font for this specific object
        if object_id is not None and object_id in self.ui_element_fonts:
            font = self.ui_element_fonts[object_id]
        else:
            # then fall back on a font for this element type
            for element_id in element_ids:
                if element_id in self.ui_element_fonts:
                    font = self.ui_element_fonts[element_id]
                    break

        return font

    def get_misc_data(self, object_id, element_ids, misc_data_id):
        """
        Uses data about a UI element and a specific ID to try and find a piece of miscellaneous theming data.

        :param object_id: An ID for the particular instance of this element being created.
        :param element_ids: A list of IDs for all elements of this particular type in the theme.
        :param misc_data_id: The id for the specific piece of miscellaneous data we are looking for.
        :return None or str: Returns a string if we find the data, otherwise returns None.
        """
        if object_id is not None:
            if object_id in self.ui_element_misc_data:
                if misc_data_id in self.ui_element_misc_data[object_id]:
                    return self.ui_element_misc_data[object_id][misc_data_id]

        # then check for an element specific colour
        for element_id in element_ids:
            if element_id in self.ui_element_misc_data:
                if misc_data_id in self.ui_element_misc_data[element_id]:
                    return self.ui_element_misc_data[element_id][misc_data_id]

        return None

    def get_colour(self, object_id, element_ids, colour_id):
        """
        Uses data about a UI element and a specific ID to find a colour from our theme.

        :param object_id: An ID for the particular instance of this element being created.
        :param element_ids: A list of IDs for all elements of this particular type in the theme.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color: A pygame colour.
        """
        # first check for a unique theming for this specific object
        if object_id is not None:
            if object_id in self.ui_element_colours:
                if colour_id in self.ui_element_colours[object_id]:
                    return self.ui_element_colours[object_id][colour_id]

        # then check for an element specific colour
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

    def load_theme(self, file_path: str):
        """
        Loads a theme file, and currently, all associated data like fonts and images required by the theme.

        :param file_path: The path to the theme we want to load.

        """
        with open(os.path.abspath(file_path), 'r') as theme_file:
            theme_dict = json.load(theme_file)

            for element_name in theme_dict.keys():
                if element_name == 'defaults':
                    for data_type in theme_dict[element_name]:
                        if data_type == 'colours':
                            colours_dict = theme_dict[element_name][data_type]
                            for colour_key in colours_dict:
                                self.base_colours[colour_key] = pygame.Color(colours_dict[colour_key])

                else:

                    for data_type in theme_dict[element_name]:
                        if data_type == 'font':
                            font_dict = theme_dict[element_name][data_type]
                            self.ui_element_font_infos[element_name] = {}
                            self.ui_element_font_infos[element_name]['name'] = font_dict['name']
                            self.ui_element_font_infos[element_name]['size'] = int(font_dict['size'])
                            if 'bold' in font_dict:
                                self.ui_element_font_infos[element_name]['bold'] = bool(int(font_dict['bold']))
                            else:
                                self.ui_element_font_infos[element_name]['bold'] = False
                            if 'italic' in font_dict:
                                self.ui_element_font_infos[element_name]['italic'] = bool(int(font_dict['italic']))
                            else:
                                self.ui_element_font_infos[element_name]['italic'] = False

                            if 'regular_path' in font_dict:
                                self.ui_element_font_infos[element_name]['regular_path'] = font_dict['regular_path']
                            if 'bold_path' in font_dict:
                                self.ui_element_font_infos[element_name]['bold_path'] = font_dict['bold_path']
                            if 'italic_path' in font_dict:
                                self.ui_element_font_infos[element_name]['italic_path'] = font_dict['italic_path']
                            if 'bold_italic_path' in font_dict:
                                self.ui_element_font_infos[element_name]['bold_italic_path'] = font_dict['bold_italic_path']

                        if data_type == 'colours':
                            self.ui_element_colours[element_name] = {}
                            colours_dict = theme_dict[element_name][data_type]
                            for colour_key in colours_dict:
                                self.ui_element_colours[element_name][colour_key] = pygame.Color(colours_dict[colour_key])

                        elif data_type == 'images':
                            self.ui_element_image_paths[element_name] = {}
                            images_dict = theme_dict[element_name][data_type]
                            for image_key in images_dict:
                                self.ui_element_image_paths[element_name][image_key] = {}
                                self.ui_element_image_paths[element_name][image_key]['path'] = str(images_dict[image_key]['path'])
                                if 'sub_surface_rect' in images_dict[image_key]:
                                    rect_list = str(images_dict[image_key]['sub_surface_rect']).strip().split(',')
                                    x = int(rect_list[0].strip())
                                    y = int(rect_list[1].strip())
                                    w = int(rect_list[2].strip())
                                    h = int(rect_list[3].strip())
                                    rect = pygame.Rect((x, y), (w, h))
                                    self.ui_element_image_paths[element_name][image_key]['sub_surface_rect'] = rect

                        elif data_type == 'misc':
                            self.ui_element_misc_data[element_name] = {}
                            misc_dict = theme_dict[element_name][data_type]
                            for misc_data_key in misc_dict:
                                self.ui_element_misc_data[element_name][misc_data_key] = str(misc_dict[misc_data_key])

        # TODO: these should be triggered at an appropriate time in our project when lots of files are being loaded
        self.load_fonts()
        self.load_images()
