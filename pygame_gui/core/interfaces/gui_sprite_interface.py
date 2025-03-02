from abc import ABCMeta, abstractmethod


class IGUISpriteInterface(metaclass=ABCMeta):
    """
    A sprite Interface class specifically designed for the GUI. Very similar to pygame's
    DirtySprite but without the Dirty flag.
    """

    @abstractmethod
    def add(self, *groups):
        """
        add the sprite to groups

        :param groups: sprite groups to add this sprite to.

        Any number of Group instances can be passed as arguments. The
        Sprite will be added to the Groups it is not already a member of.

        """

    @abstractmethod
    def remove(self, *groups):
        """
        remove the sprite from groups

        :param groups: sprite groups to remove this sprite from.

        Any number of Group instances can be passed as arguments. The Sprite
        will be removed from the Groups it is currently a member of.

        """

    @abstractmethod
    def add_internal(self, group):
        """
        For adding this sprite to a group internally.

        :param group: The group we are adding to.
        """

    @abstractmethod
    def remove_internal(self, group):
        """
        For removing this sprite from a group internally.

        :param group: The group we are removing from.
        """

    @abstractmethod
    def kill(self):
        """remove the Sprite from all Groups

        Sprite.kill(): return None

        The Sprite is removed from all the Groups that contain it. This won't
        change anything about the state of the Sprite. It is possible to
        continue to use the Sprite after this method has been called, including
        adding it to Groups.

        """

    @abstractmethod
    def groups(self):
        """list of Groups that contain this Sprite

        Sprite.groups(): return group_list

        Returns a list of all the Groups that contain this Sprite.

        """

    @abstractmethod
    def alive(self):
        """does the sprite belong to any groups

        Sprite.alive(): return bool

        Returns True when the Sprite belongs to one or more Groups.
        """

    @abstractmethod
    def _set_visible(self, val: int):
        """
        Set the visible value (0 or 1)

        :param val: set the visibility state 1 is visible, 0 is invisible
        """

    @abstractmethod
    def _get_visible(self):
        """return the visible value of that sprite"""

    @abstractmethod
    def update(self, time_delta: float):
        """
        A stub to override.

        :param time_delta: the time passed in seconds between calls to this function.
        """

    @property
    @abstractmethod
    def visible(self):
        """
        You can make this sprite disappear without removing it from the group
        assign 0 for invisible and 1 for visible
        """

    @visible.setter
    @abstractmethod
    def visible(self, value):
        """
        :param value:
        """

    @property
    @abstractmethod
    def layer(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """

    @layer.setter
    @abstractmethod
    def layer(self, value):
        """
        :param value:
        """

    @property
    @abstractmethod
    def image(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """

    @image.setter
    @abstractmethod
    def image(self, value):
        """

        :param value:
        :return:
        """

    @property
    @abstractmethod
    def rect(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """

    @rect.setter
    @abstractmethod
    def rect(self, value):
        """
        :param value:
        """

    @property
    @abstractmethod
    def blendmode(self):
        """
        Layer property can only be set before the sprite is added to a group,
        after that it is read only and a sprite's layer in a group should be
        set via the group's change_layer() method.

        Overwrites dynamic property from sprite class for speed.
        """

    @blendmode.setter
    @abstractmethod
    def blendmode(self, value):
        """
        :param value:
        """
