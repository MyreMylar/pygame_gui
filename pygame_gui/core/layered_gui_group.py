from pygame.sprite import LayeredUpdates, Sprite


class GUISprite(Sprite):
    """

    """

    def __init__(self, *groups):

        # referred to as special_flags in the documentation of Surface.blit
        self._blendmode = 0
        self._visible = 1

        self._image = None
        self._rect = None

        self.blit_data = [self._image, self._rect, None, self._blendmode]

        # Default 0 unless initialized differently.
        self._layer = getattr(self, '_layer', 0)
        self.source_rect = None
        Sprite.__init__(self, *groups)

    def _set_visible(self, val):
        """set the visible value (0 or 1) """
        self._visible = val

    def _get_visible(self):
        """return the visible value of that sprite"""
        return self._visible

    @property
    def visible(self):
        """
        You can make this sprite disappear without removing it from the group
        assign 0 for invisible and 1 for visible
        """
        return self._get_visible()

    @visible.setter
    def visible(self, value):
        self._set_visible(value)
        for group in self.groups():
            group.update_visibility()

    @property
    def layer(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """
        return self._layer

    @layer.setter
    def layer(self, value):
        if not self.alive():
            self._layer = value
        # else:
        #     raise AttributeError("Can't set layer directly after "
        #                          "adding to group. Use "
        #                          "group.change_layer(sprite, new_layer) "
        #                          "instead.")

    def __repr__(self):
        return "<%s GUISprite(in %d groups)>" % \
            (self.__class__.__name__, len(self.groups()))

    @property
    def image(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """
        return self._image

    @image.setter
    def image(self, value):
        if self._image is None:
            self._image = value
            self.blit_data[0] = self._image
            for group in self.groups():
                group.update_visibility()
        else:
            self._image = value
            self.blit_data[0] = self._image

    @property
    def rect(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.blit_data[1] = self._rect

    @property
    def blendmode(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """
        return self._blendmode

    @blendmode.setter
    def blendmode(self, value):
        self._blendmode = value
        self.blit_data[3] = self._blendmode


class LayeredGUIGroup(LayeredUpdates):
    """

    """
    def __init__(self, *sprites):
        """initialize group.

        """
        LayeredUpdates.__init__(self, *sprites)
        self._clip = None
        self.visible = []

    def add_internal(self, sprite, layer=None):
        """Do not use this method directly.

        It is used by the group to add a sprite internally.

        """
        # check if all needed attributes are set
        if not hasattr(sprite, 'visible'):
            raise AttributeError()
        if not hasattr(sprite, 'blendmode'):
            raise AttributeError()
        if not isinstance(sprite, GUISprite):
            raise TypeError()

        LayeredUpdates.add_internal(self, sprite, layer)
        self.update_visibility()

    def remove_internal(self, sprite):
        LayeredUpdates.remove_internal(self, sprite)
        self.update_visibility()

    def draw(self, surface):
        """draw all sprites in the right order onto the given surface

        """
        surface.blits(self.visible)

    def update_visibility(self):
        self.visible = [spr.blit_data
                        for spr in self._spritelist
                        if spr.image is not None and spr.visible]
