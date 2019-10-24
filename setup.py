from setuptools import setup

setup(name='pygame_gui',
      version='0.2.1',
      description='A GUI module for pygame 2',
      long_description="Helps create GUIs for games made using pygame 2. Features HTML-style text formatting, "
                       "theme files to control the look and a system to manage multiple windows of GUI stuff.",
      keywords=["pygame", "gui", "ui"],
      url='https://github.com/MyreMylar/pygame_gui',
      download_url='https://github.com/MyreMylar/pygame_gui/archive/v_021.tar.gz',
      author='Dan Lawrence',
      author_email='danintheshed@gmail.com',
      license='MIT',
      packages=['pygame_gui', 'pygame_gui.core', 'pygame_gui.elements', 'pygame_gui.windows'],
      zip_safe=False,
      install_requires=['pygame'],
      include_package_data=True,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
      ],
      )
