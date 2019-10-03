import os
import pygame
import warnings


class UIFontDictionary:
    html_font_sizes = {
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

    html_font_sizes_reverse_lookup = {
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

        module_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.loaded_fonts = {'fira_code_regular_14':
                             pygame.font.Font(os.path.join(module_root_path, 'data/FiraCode-Regular.ttf'),
                                              self.default_font_size)}
        self.known_font_paths = {'fira_code': [os.path.normpath(os.path.join(module_root_path,
                                                                             'data/FiraCode-Regular.ttf')),
                                               os.path.normpath(os.path.join(module_root_path,
                                                                             'data/FiraCode-Bold.ttf')),
                                               os.path.normpath(os.path.join(module_root_path,
                                                                             'data/FiraMono-RegularItalic.ttf')),
                                               os.path.normpath(os.path.join(module_root_path,
                                                                             'data/FiraMono-BoldItalic.ttf'))]}

        self.used_font_ids = ['fira_code_regular_14']

    def find_font(self, font_size, font_name, bold=False, italic=False):
        font_id = self.create_font_id(font_size, font_name, bold, italic)

        if font_id not in self.used_font_ids:
            self.used_font_ids.append(font_id)  # record font usage for optimisation purposes

        if font_id in self.loaded_fonts:  # font already loaded
            return self.loaded_fonts[font_id]
        elif font_name in self.known_font_paths:  # we know paths to this font, just haven't loaded current size/style
            warnings.warn('Finding font with id: ' + font_id + ' that is not already loaded', UserWarning)
            self.preload_font(font_size, font_name, bold, italic)
            return self.loaded_fonts[font_id]
        else:
            return self.loaded_fonts["default_font_regular_12"]

    @staticmethod
    def create_font_id(font_size, font_name, bold, italic):
        if bold and italic:
            font_style_string = "bold_italic"
        elif bold and not italic:
            font_style_string = "bold"
        elif not bold and italic:
            font_style_string = "italic"
        else:
            font_style_string = "regular"
        font_id = font_name + "_" + font_style_string + "_" + str(font_size)
        return font_id

    def preload_font(self, font_size, font_name, bold=False, italic=False):
        font_id = self.create_font_id(font_size, font_name, bold, italic)
        if font_id in self.loaded_fonts:  # font already loaded
            warnings.warn('Trying to pre-load font id: ' + font_id + ' that is already loaded', UserWarning)
        elif font_name in self.known_font_paths:  # we know paths to this font, just haven't loaded current size/style
            if bold and italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][3], font_size)
                new_font.set_bold(True)
                new_font.set_italic(True)
                self.loaded_fonts[font_id] = new_font
            elif bold and not italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][1], font_size)
                new_font.set_bold(True)
                self.loaded_fonts[font_id] = new_font
            elif not bold and italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][2], font_size)
                new_font.set_italic(True)
                self.loaded_fonts[font_id] = new_font
            else:
                self.loaded_fonts[font_id] = pygame.font.Font(self.known_font_paths[font_name][0], font_size)
        else:
            raise UserWarning('Trying to pre-load font id:' + font_id + 'with no paths set')

    def add_font_path(self, font_name, font_path, bold_path=None, italic_path=None, bold_italic_path=None):
        if font_name not in self.known_font_paths:
            if bold_path is None:
                bold_path = font_path
            if italic_path is None:
                italic_path = font_path
            if bold_italic_path is None:
                bold_italic_path = font_path
            self.known_font_paths[font_name] = [font_path, bold_path, italic_path, bold_italic_path]

    def print_unused_loaded_fonts(self):

        unused_font_ids = []
        for key in self.loaded_fonts.keys():
            if key not in self.used_font_ids:
                unused_font_ids.append(key)

        if len(unused_font_ids) > 0:
            print('Unused font ids:')
            for font_id in unused_font_ids:
                html_size = UIFontDictionary.html_font_sizes_reverse_lookup[int(font_id.split('_')[-1])]
                print(font_id + '(HTML size: ' + str(html_size) + ')')
