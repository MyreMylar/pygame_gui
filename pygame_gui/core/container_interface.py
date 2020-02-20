from abc import ABCMeta


class IContainerInterface:
    __metaclass__ = ABCMeta

    def get_container(self):
        pass
