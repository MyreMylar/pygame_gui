import os
import sys
from typing import Union
from pathlib import Path


def _create_resource_path(relative_path: Union[str, Path]):
    """
    Get absolute path to resource, works for dev and for PyInstaller's 'onefile' mode

    :param relative_path: A relative path to a file of some kind.

    """

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS  # type: ignore # pylint: disable=no-member,protected-access
        else:
            base_path = os.path.abspath(".")
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class PackageResource:
    """
    A data class to handle input for importlib.resources as single parameter.

    :param package: The python package our resource is located in (e.g. 'pygame_gui.data')
    :param resource: The name of the resource (e.g. 'default_theme.json')
    """

    def __init__(self, package: str, resource: str):
        self.package = package
        self.resource = resource

    def __repr__(self):
        return f"{self.package}.{self.resource}"

    def to_path(self) -> str:
        """
        If we don't have any importlib module to use, we can try to turn the resource into a file
        path.

        :return: A string path.
        """
        root_path = ""
        relative_path = self.package.replace(".", "/") + "/" + self.resource
        if self.package.find("pygame_gui") == 0:
            # This is default data from pygame_gui so relative to pygame_gui rather than app
            root_path = os.path.abspath(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
        return _create_resource_path(os.path.join(root_path, relative_path))
