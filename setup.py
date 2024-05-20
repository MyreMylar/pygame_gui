from setuptools import setup


setup(
      name='pygame_gui',
      version='0.6.10',
      description='A GUI module for pygame Community Edition',
      long_description="Helps create GUIs for games made using pygame Community Edition. "
                       "Features HTML-style text formatting, localization,"
                       "theme files to control the look and a system to manage"
                       " multiple windows of GUI stuff.",
      keywords=["pygame", "gui", "ui"],
      url='https://github.com/MyreMylar/pygame_gui',
      download_url='https://github.com/MyreMylar/pygame_gui/archive/v_0610.tar.gz',
      author='Dan Lawrence',
      author_email='danintheshed@gmail.com',
      license='MIT',
      packages=['pygame_gui',
                'pygame_gui.__pyinstaller',
                'pygame_gui.core',
                'pygame_gui.core.interfaces',
                'pygame_gui.core.drawable_shapes',
                'pygame_gui.core.text',
                'pygame_gui.core.text.text_effects',
                'pygame_gui.elements',
                'pygame_gui.windows',
                'pygame_gui.data',
                'pygame_gui.data.translations'],
      zip_safe=False,
      python_requires='>=3.8',
      setup_requires=[],
      install_requires=['pygame-ce>=2.4.0',
                        'python-i18n>=0.3.9',
                        'importlib_resources>1.3; python_version < "3.9"'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
      ],
      )
