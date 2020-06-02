import pygame


class UILayeredUpdates(pygame.sprite.LayeredUpdates):
    """Extends pygame.sprite.LayeredUpdates so that only UIElements with the is_visible flag set to True are drawn.
    """

    def shown_sprites(self):
        """returns an ordered list of sprites (first back, last top) that
        either have no is_visible attribute or it is set to True

        UILayeredUpdates.sprites(): return sprites

        """
        return [x for x in self.spritedict if (not hasattr(x, 'is_visible') or x.is_visible)]

    def draw(self, surface):
        """draw all the sprites that, either have no is_visible attribute or it is set to True,
        in the right order onto the passed surface

        UILayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.shown_sprites():
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect)
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty
