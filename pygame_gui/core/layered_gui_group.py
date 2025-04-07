from operator import truth
from abc import abstractmethod
from collections.abc import Iterable
from typing import Union, Optional, Dict, List


import pygame
from pygame.rect import Rect


class GUISprite:
    """
    A sprite class specifically designed for the GUI. Very similar to pygame's
    DirtySprite but without the Dirty flag.
    """

    def __init__(
        self,
        groups: Optional[Union[Iterable["LayeredGUIGroup"], "LayeredGUIGroup"]] = None,
    ):
        # referred to as special_flags in the documentation of Surface.blit
        self._blendmode = 0
        self._visible = 1

        self._image = None
        self._rect = None

        self.blit_data = [self._image, self._rect, None, self._blendmode]

        # Default 0 unless initialized differently.
        self._layer = getattr(self, "_layer", 0)
        self.source_rect = None
        self.__g: Dict["LayeredGUIGroup", int] = {}  # The groups the sprite is in
        if groups is not None:
            self.add(groups)

    def add(self, groups: Union[Iterable["LayeredGUIGroup"], "LayeredGUIGroup"]):
        """
        add the sprite to groups

        :param groups: sprite groups to add to.

        Any number of Group instances can be passed as arguments. The
        Sprite will be added to the Groups it is not already a member of.

        """
        has = self.__g.__contains__
        if isinstance(groups, Iterable):
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
        else:
            group = groups
            if hasattr(group, "_spritegroup"):
                if not has(group):
                    group.add_internal(self)
                    self.add_internal(group)
            elif isinstance(group, Iterable):
                self.add(group)

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


class LayeredGUIGroup:
    """
    A sprite group specifically for the GUI. Similar to pygame's LayeredDirty group but with the
    dirty flag stuff removed for simplicity and speed.
    """

    _spritegroup = True
    _init_rect = Rect(0, 0, 0, 0)

    def __init__(self, *sprites):
        """initialize group."""
        self._spritelayers = {}
        self._spritelist: List[GUISprite] = []
        self.spritedict = {}
        self.lostsprites = []
        self._default_layer = 0

        self.add(*sprites)
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

        self.spritedict[sprite] = self._init_rect

        if layer is None:
            try:
                layer = sprite.layer
            except AttributeError:
                layer = self._default_layer
                setattr(sprite, "_layer", layer)
        elif hasattr(sprite, "_layer"):
            setattr(sprite, "_layer", layer)

        sprites = self._spritelist  # speedup
        sprites_layers = self._spritelayers
        sprites_layers[sprite] = layer

        # add the sprite at the right position
        # bisect algorithmus
        leng = len(sprites)
        low = mid = 0
        high = leng - 1
        while low <= high:
            mid = low + (high - low) // 2
            if sprites_layers[sprites[mid]] <= layer:
                low = mid + 1
            else:
                high = mid - 1
        # linear search to find final position
        while mid < leng and sprites_layers[sprites[mid]] <= layer:
            mid += 1
        sprites.insert(mid, sprite)

        self.should_update_visibility = True

    def remove_internal(self, sprite: GUISprite):
        """

        :param sprite:
        :return:
        """
        self._spritelist.remove(sprite)
        # these dirty rects are suboptimal for one frame
        old_rect = self.spritedict[sprite]
        if old_rect is not self._init_rect:
            self.lostsprites.append(old_rect)  # dirty rect
        if hasattr(sprite, "rect"):
            self.lostsprites.append(sprite.rect)  # dirty rect

        del self.spritedict[sprite]
        del self._spritelayers[sprite]
        self.should_update_visibility = True

    def change_layer(self, sprite: GUISprite, new_layer: int):
        """
        Changes the layer of a sprite in the group.

        :param sprite: the sprite to change
        :param new_layer: the new layer to change to.
        """
        sprites = self._spritelist  # speedup
        sprites_layers = self._spritelayers  # speedup

        sprites.remove(sprite)
        sprites_layers.pop(sprite)

        # add the sprite at the right position
        # bisect algorithmus
        leng = len(sprites)
        low = mid = 0
        high = leng - 1
        while low <= high:
            mid = low + (high - low) // 2
            if sprites_layers[sprites[mid]] <= new_layer:
                low = mid + 1
            else:
                high = mid - 1
        # linear search to find final position
        while mid < leng and sprites_layers[sprites[mid]] <= new_layer:
            mid += 1
        sprites.insert(mid, sprite)
        if hasattr(sprite, "_layer"):
            setattr(sprite, "_layer", new_layer)

        # add layer info
        sprites_layers[sprite] = new_layer
        self.should_update_visibility = True

    def draw(self, surface: pygame.Surface):
        """draw all sprites in the right order onto the given surface"""
        surface.blits(self.visible)

    def update(self, *args, **kwargs) -> None:
        """
        Update all the sprites in the groups.

        :param args: the arguments to the sprite's update function.

        :param kwargs:
        """
        for sprite in self.sprites():
            sprite.update(*args, **kwargs)
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

    def sprites(self) -> List[GUISprite]:
        """return an ordered list of sprites (first back, last top)."""
        return self._spritelist.copy()

    def layers(self):
        """return a list of unique defined layers defined."""
        return sorted(set(self._spritelayers.values()))

    def get_sprites_from_layer(self, layer):
        """return all sprites from a layer ordered as they were added

        : return sprites

        Returns all sprites from a layer. The sprites are ordered in the
        sequence that they were added. (The sprites are not removed from the
        layer).

        """
        sprites: List[GUISprite] = []
        sprites_append = sprites.append
        sprite_layers = self._spritelayers
        for spr in self._spritelist:
            if sprite_layers[spr] == layer:
                sprites_append(spr)
            elif sprite_layers[spr] > layer:
                # break after because no other will
                # follow with same layer
                break
        return sprites

    def add(self, *sprites, **kwargs):
        """add a sprite or sequence of sprites to a group

        LayeredUpdates.add(*sprites, **kwargs): return None

        If the sprite you add has an attribute _layer, then that layer will be
        used. If **kwarg contains 'layer', then the passed sprites will be
        added to that layer (overriding the sprite._layer attribute). If
        neither the sprite nor **kwarg has a 'layer', then the default layer is
        used to add the sprites.

        """

        if not sprites:
            return
        layer = kwargs["layer"] if "layer" in kwargs else None
        for sprite in sprites:
            # It's possible that some sprite is also an iterator.
            # If this is the case, we should add the sprite itself,
            # and not the iterator object.
            if isinstance(sprite, GUISprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite, layer)
                    sprite.add_internal(self)
            else:
                try:
                    # See if sprite is an iterator, like a list or sprite
                    # group.
                    self.add(*sprite, **kwargs)
                except (TypeError, AttributeError):
                    # Not iterable. This is probably a sprite that is not an
                    # instance of the Sprite class or is not an instance of a
                    # subclass of the Sprite class. Alternately, it could be an
                    # old-style sprite group.
                    if hasattr(sprite, "_spritegroup"):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr, layer)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite, layer)
                        sprite.add_internal(self)

    def has_internal(self, sprite: GUISprite):
        """
        For checking if a sprite is in this group internally.

        :param sprite: The sprite we are checking.
        """
        return sprite in self.spritedict

    def get_top_layer(self):
        """
        return the top layer

        """
        return self._spritelayers[self._spritelist[-1]]
