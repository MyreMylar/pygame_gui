from abc import ABCMeta


class IContainerLikeInterface:
    """
        A meta class that defines the interface for containers used by elements.

        This interface lets us treat classes like UIWindows and UIPanels like containers for
        elements even though they actually pass this functionality off to the proper UIContainer
        class.
        """
    __metaclass__ = ABCMeta

    def get_container(self):
        """
        Gets an actual container from this container-like UI element.
        """
        pass
