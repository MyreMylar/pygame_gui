.. _localization:

Localization
============

Localization is the process of adapting your application for different languages & cultures. Pygame GUI provides some
support for localizing your GUI, though no 'one size fits all' localization effort is going to be perfect, hopefully
it will serve as a starting point for some users.

Underlying localization package
-------------------------------

Pygame GUI uses `python-i18n <https://github.com/danhper/python-i18n>`_ for it's localization backend, if you plan to
make a lot of use out of the localization features in Pygame GUI you should check out the documentation for python-i18n
as well. They cover more of the pluralization options than I get to in this brief guide.

Basics of switching locale
--------------------------

To start with, locales in Pygame GUI are specified via the
`IS0 639-1 two letter language codes <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_. These are just a
convenient, standardised way to refer to different languages.

You can set a starting locale for the GUI by passing one of these codes to the UIManager for your application like so:

.. code-block:: python
   :linenos:

   manager = UIManager((800, 600), starting_language='ja')

Which would start the GUI in Japanese.

You can also switch the language of the GUI while it is running by calling `set_locale()` on the manager like so:

.. code-block:: python
   :linenos:

   manager.set_locale('fr')

Which would switch the language to French, and make any other adaptions that might be needed for French speaking
countries.

Default supported languages
---------------------------

Right now the list of languages support by default by Pygame GUI elements and windows is:

 - Arabic
 - German
 - English
 - Spanish
 - French
 - Georgian
 - Hebrew
 - Indonesian
 - Italian
 - Japanese
 - Korean
 - Polish
 - Portuguese
 - Russian
 - Ukrainian
 - Vietnamese
 - Simplified Chinese

Though many of the translations may be imperfect as they were largely not handled by native speakers (yet). If you
would like to improve an existing translation or add a new one the current default translations are
`stored here <https://github.com/MyreMylar/pygame_gui/tree/main/pygame_gui/data/translations/>`_ and should give you
a good place to start. Pull requests, or simple issue reports of translation issues are very welcome.

Providing custom translation files to the GUI
---------------------------------------------

What if you have your own text in your application that you want to translate into a few different languages? For that
you can supply your own json translation file directories to the UI Manager. The files should be in the same format as
the default translation files above. Here is a quick example of one from the examples:

.. code-block:: json
   :caption: examples.fr.json
   :linenos:

   {
     "fr": {
       "holmes_text_test": "<p>&nbsp;&nbsp;&nbsp;Ce matin-là, M. Sherlock Holmes qui, sauf les cas assez fréquents où il passait les nuits, se levait tard, était assis devant la table de la salle à manger. Je me tenais près de la cheminée, examinant la canne que notre visiteur de la veille avait oubliée. C’était un joli bâton, solide, terminé par une boule — ce qu’on est convenu d'appeler « une permission de minuit ». Immédiatement au-dessous de la pomme, un cercle d’or, large de deux centimètres, portait l’inscription et la date suivantes : « À M. James Mortimer, ses amis du C. C. H. — 1884 ». Cette canne, digne, grave, rassurante, ressemblait à celles dont se servent les médecins « vieux jeu ».</p>",
       "hello_world_message_text": "Bonjour le monde"
     }
   }

Once you have your strings translated into the languages you want to support, you pass the directory they are in to the
UIManager like so:

.. code-block:: python
   :linenos:

   manager = UIManager((800, 600),
                       starting_language='en',
                       translation_directory_paths=['data/translations'])

Then for the strings in your GUI, you use the 'namespace' from the filenames ('examples' in the json file above),
followed by the keys for each string separated with a full stop. Like so:

.. code-block:: python
   :linenos:

   text_box = UITextBox(
           html_text="examples.holmes_text_test",
           relative_rect=pygame.Rect(300, 100, 400, 200),
           manager=manager)

To see a more complete example of the current localization setup see the translation_test script in the
`examples project <https://github.com/MyreMylar/pygame_gui_examples>`_ on GitHub.

Providing custom fonts per locale
---------------------------------

If you make use of custom fonts in your application, and also want to support localizations to languages that may not
have their characters present in your initial custom font - you will be pleased to find out that you can specify a
different custom font for a particular locale.

The setup in the theme file looks like this:

.. code-block:: json
   :caption: translations_theme.json
   :linenos:
   :emphasize-lines: 16

   {
      "label":
      {
         "font":
         [
            {
                "name": "montserrat",
                "size": "12",
                "bold": "0",
                "italic": "0",
                "regular_resource": {"package": "data.fonts",
                                     "resource": "Montserrat-Regular.ttf"}
            },
            {
                "name": "kosugimaru",
                "locale": "ja",
                "size": "12",
                "bold": "0",
                "italic": "0",
                "regular_resource": {"package": "data.fonts",
                                     "resource": "KosugiMaru-Regular.ttf"}
            }
         ]
      }
   }

Note that the font block now contains the square brackets for a list/array and the addition of a "locale" entry on the
second font to designate it to be used instead by the japanese language.

As always, please let us know how you get on with localization using the library. It is a new feature for the library
and undoubtedly has lots of bugs and areas that have yet to be considered.