from setuptools import setup

setup(name='pygame_gui',
      version='0.0.1',
      description='A GUI module for pygame 2',
      long_description="Helps create GUIs for games made using pygame 2. Features HTML-style text formatting, "
                       "theme files to control the look and a system to manage multiple windows of GUI stuff.",
      keywords="pygame gui ui",
      url='https://github.com/MyreMylar/pygame_gui',
      author='Dan Lawrence',
      author_email='danintheshed@gmail.com',
      license='MIT',
      packages=['pygame_gui', 'pygame_gui.core', 'pygame_gui.elements', 'pygame_gui.windows'],
      zip_safe=False,
      install_requires=['pygame'],
      include_package_data=True)
