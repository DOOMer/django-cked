Setup
=====

Installation
------------

::

    pip install django-cked

or

::

    pip install -e git+git://github.com/DOOMer/django-cked.git

Configuration
-------------

Add ``cked`` to your ``INSTALLED_APPS`` setting.

Then set ``ELFINDER_OPTIONS`` in your settings:

::

    ELFINDER_OPTIONS = {
        ## required options
        'root': os.path.join(PROJECT_ROOT, 'media', 'uploads'),
        'URL': '/media/uploads/',
    }

And add CKEd URL include to your project ``urls.py`` file:

::

    path('cked/', include('cked.urls')),

Settings
--------

-  **CKEDITOR\_OPTIONS**: CKEditor config. See
   http://docs.ckeditor.com/#!/guide/dev_configuration
-  **ELFINDER\_OPTIONS**: elFinder config. See
   https://github.com/Studio-42/elFinder/wiki/Client-configuration-options




