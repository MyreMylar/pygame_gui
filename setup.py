from setuptools import setup
from stringify import stringify_py

# will only run when calling: python setup.py install and not when running: pip install . -U
# that is actually the behaviour we want.
stringify_py(source_path='pygame_gui/data', destination_file='pygame_gui/core/_string_data.py')


setup(name='pygame_gui',
      version='0.4.0',
      description='A GUI module for pygame 2',
      long_description="Helps create GUIs for games made using pygame 2. Features HTML-style text formatting, "
                       "theme files to control the look and a system to manage multiple windows of GUI stuff.",
      keywords=["pygame", "gui", "ui"],
      url='https://github.com/MyreMylar/pygame_gui',
      download_url='https://github.com/MyreMylar/pygame_gui/archive/v_040.tar.gz',
      author='Dan Lawrence',
      author_email='danintheshed@gmail.com',
      license='MIT',
      packages=['pygame_gui', 'pygame_gui.core', 'pygame_gui.elements',
                'pygame_gui.elements.text', 'pygame_gui.windows'],
      zip_safe=False,
      python_requires='>=3.5',
      setup_requires=['stringify'],
      install_requires=['pygame>=1.9.3'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      )
