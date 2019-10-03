import pygame


class ShadowGenerator:
    def __init__(self):
        self.created_shadows = {}

        self.create_new_shadow(200, 200)
        self.create_new_shadow(100, 100)
        self.create_new_shadow(50, 50)
        self.create_new_shadow(170, 50)

    def create_new_shadow(self, width, height):
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha_increment = 21
        shadow_color = pygame.Color(0, 0, 0, alpha_increment)
        shadow_surface.fill(shadow_color)

        shadow_width = width
        shadow_height = height

        pixel_array = pygame.PixelArray(shadow_surface)
        pixel_array[0, 0] = pygame.Color(0, 0, 0, 0)
        pixel_array[shadow_width - 1, 0] = pygame.Color(0, 0, 0, 0)
        pixel_array[0, shadow_height - 1] = pygame.Color(0, 0, 0, 0)
        pixel_array[shadow_width - 1, shadow_height - 1] = pygame.Color(0, 0, 0, 0)
        pixel_array.close()
        for i in range(0, 6):
            shadow_width -= 2
            shadow_height -= 2
            # alpha_increment_increment -= 6
            # alpha_increment += alpha_increment_increment
            # if alpha_increment < 0:
            #     alpha_increment = 3
            shadow_color.a = alpha_increment
            temp_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            temp_surface.fill(shadow_color)
            pixel_array = pygame.PixelArray(temp_surface)
            pixel_array[0, 0] = pygame.Color(0, 0, 0, 0)
            pixel_array[shadow_width-1, 0] = pygame.Color(0, 0, 0, 0)
            pixel_array[0, shadow_height-1] = pygame.Color(0, 0, 0, 0)
            pixel_array[shadow_width-1, shadow_height-1] = pygame.Color(0, 0, 0, 0)
            pixel_array.close()
            shadow_surface.blit(temp_surface, (i+1, i+1))

        self.created_shadows[str(width) + 'x' + str(height)] = shadow_surface

    def find_closest_shadow_scale_to_size(self, size):
        lowest_diff = 1000000000000
        closest_key = None
        for key in self.created_shadows.keys():
            dimension_strs = key.split('x')
            width = int(dimension_strs[0])
            height = int(dimension_strs[1])

            width_diff = abs(width - size[0])
            height_diff = abs(height - size[1])
            total_diff = width_diff + height_diff
            if total_diff < lowest_diff:
                lowest_diff = total_diff
                closest_key = key

        if closest_key is not None:
            return pygame.transform.smoothscale(self.created_shadows[closest_key], size)

        return None
