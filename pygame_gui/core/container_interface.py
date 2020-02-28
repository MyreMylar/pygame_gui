from abc import ABCMeta


class IWindowInterface:
    __metaclass__ = ABCMeta

    def change_layer(self, layer):
        pass


class IContainerInterface:
    __metaclass__ = ABCMeta

    def get_container(self):
        pass
