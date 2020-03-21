from abc import ABCMeta


class IWindowInterface:
    """
    A meta class that defines the interface that the window stack uses to interface with the
    UIWindow class.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual window class later on and have it make use of the window stack.
    """
    __metaclass__ = ABCMeta

    def change_layer(self, layer: int):
        pass
