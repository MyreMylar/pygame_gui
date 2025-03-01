from operator import truth
from abc import abstractmethod
from collections.abc import Iterable


from pygame.sprite import LayeredUpdates


class GUISprite:
    """
    A sprite class specifically designed for the GUI. Very similar to pygame's
    DirtySprite but without the Dirty flag.
    """

    def __init__(self, *groups):
        # referred to as special_flags in the documentation of Surface.blit
        self._blendmode = 0
        self._visible = 1

        self._image = None
        self._rect = None

        self.blit_data = [self._image, self._rect, None, self._blendmode]

        # Default 0 unless initialized differently.
        self._layer = getattr(self, "_layer", 0)
        self.source_rect = None
        self.__g = {}  # The groups the sprite is in
        if groups:
            self.add(*groups)

    def add(self, *groups):
        """
        add the sprite to groups

        :param groups: sprite groups to add to.

        Any number of Group instances can be passed as arguments. The
        Sprite will be added to the Groups it is not already a member of.

        """
        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, "_spritegroup"):
                if not has(group):
                    group.add_internal(self)
                    self.add_internal(group)
            elif isinstance(group, Iterable):
                self.add(*group)
            else:
                raise TypeError(
                    "Expected group to be an iterable of groups, got non-iterable type"
                )

    def remove(self, *groups):
        """remove the sprite from groups

        :param groups: sprite groups to remove from.

        Any number of Group instances can be passed as arguments. The Sprite
        will be removed from the Groups it is currently a member of.

        """
        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, "_spritegroup"):
                if has(group):
                    group.remove_internal(self)
                    self.remove_internal(group)
            else:
                self.remove(*group)

    def add_internal(self, group):
        """
        For adding this sprite to a group internally.

        :param group: The group we are adding to.
        """
        self.__g[group] = 0

    def remove_internal(self, group):
        """
        For removing this sprite from a group internally.

        :param group: The group we are removing from.
        """
        del self.__g[group]

    def kill(self):
        """remove the Sprite from all Groups

        Sprite.kill(): return None

        The Sprite is removed from all the Groups that contain it. This won't
        change anything about the state of the Sprite. It is possible to
        continue to use the Sprite after this method has been called, including
        adding it to Groups.

        """
        for group in self.__g:
            group.remove_internal(self)
        self.__g.clear()

    def groups(self):
        """list of Groups that contain this Sprite

        Sprite.groups(): return group_list

        Returns a list of all the Groups that contain this Sprite.

        """
        return list(self.__g)

    def alive(self):
        """does the sprite belong to any groups

        Sprite.alive(): return bool

        Returns True when the Sprite belongs to one or more Groups.
        """
        return truth(self.__g)

    def _set_visible(self, val):
        """set the visible value (0 or 1)"""
        self._visible = val

    def _get_visible(self):
        """return the visible value of that sprite"""
        return self._visible

    @abstractmethod
    def update(self, time_delta: float):
        """
        A stub to override.

        :param time_delta: the time passed in seconds between calls to this function.
        """

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
            group.should_update_visibility = True

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

    def __repr__(self):
        return f"<{self.__class__.__name__} GUISprite(in {len(self.groups())} groups)>"

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
                group.should_update_visibility = True
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
    A sprite group specifically for the GUI. Similar to pygame's LayeredDirty group but with the
    dirty flag stuff removed for simplicity and speed.
    TODO: sever this entirely from LayeredUpdates at some point to fix the type hinting
    """

    def __init__(self, *sprites):
        """initialize group."""
        LayeredUpdates.__init__(self, *sprites)
        self._clip = None
        self.visible = []
        self.should_update_visibility = True

    def add_internal(self, sprite: GUISprite, layer=None):
        """Do not use this method directly.

        It is used by the group to add a sprite internally.

        """
        # check if all needed attributes are set
        if not hasattr(sprite, "visible"):
            raise AttributeError()
        if not hasattr(sprite, "blendmode"):
            raise AttributeError()
        if not isinstance(sprite, GUISprite):
            raise TypeError()

        LayeredUpdates.add_internal(self, sprite, layer)
        self.should_update_visibility = True

    def remove_internal(self, sprite):
        LayeredUpdates.remove_internal(self, sprite)
        self.should_update_visibility = True

    def change_layer(self, sprite: GUISprite, new_layer):
        LayeredUpdates.change_layer(self, sprite, new_layer)
        self.should_update_visibility = True

    def draw(self, surface):
        """draw all sprites in the right order onto the given surface"""
        surface.blits(self.visible)

    def update(self, *args, **kwargs) -> None:
        """

        :param args:
        :param kwargs:
        """
        super().update(*args, **kwargs)
        if self.should_update_visibility:
            self.should_update_visibility = False
            self.update_visibility()

    def update_visibility(self):
        """
        Update the list of what is currently visible.

        Called when we add or remove elements from the group or when an element is hidden or shown.
        """
        self.visible = [
            spr.blit_data
            for spr in self._spritelist
            if spr.image is not None and spr.visible
        ]
