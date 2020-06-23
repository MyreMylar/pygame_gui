import pygame


def compare_surfaces(surf_a: pygame.Surface, surf_b: pygame.Surface):
    if surf_a.get_size() != surf_b.get_size():
        return False

    for x in range(surf_a.get_size()[0]):
        for y in range(surf_a.get_size()[1]):
            if surf_a.get_at((x, y)) != surf_b.get_at((x, y)):
                return False

    return True