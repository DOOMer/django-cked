
# This file is generated automatically.
# !!! DO NOT MODIFY !!!.
# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cked', 'cked.elf']

package_data = \
{'': ['*'],
 'cked': ['static/cked/ckeditor/*',
          'static/cked/ckeditor/adapters/*',
          'static/cked/ckeditor/lang/*',
          'static/cked/ckeditor/plugins/*',
          'static/cked/ckeditor/plugins/a11yhelp/dialogs/*',
          'static/cked/ckeditor/plugins/a11yhelp/dialogs/lang/*',
          'static/cked/ckeditor/plugins/about/dialogs/*',
          'static/cked/ckeditor/plugins/about/dialogs/hidpi/*',
          'static/cked/ckeditor/plugins/clipboard/dialogs/*',
          'static/cked/ckeditor/plugins/colordialog/dialogs/*',
          'static/cked/ckeditor/plugins/copyformatting/cursors/*',
          'static/cked/ckeditor/plugins/copyformatting/styles/*',
          'static/cked/ckeditor/plugins/dialog/*',
          'static/cked/ckeditor/plugins/dialog/styles/*',
          'static/cked/ckeditor/plugins/div/dialogs/*',
          'static/cked/ckeditor/plugins/find/dialogs/*',
          'static/cked/ckeditor/plugins/flash/dialogs/*',
          'static/cked/ckeditor/plugins/flash/images/*',
          'static/cked/ckeditor/plugins/forms/dialogs/*',
          'static/cked/ckeditor/plugins/forms/images/*',
          'static/cked/ckeditor/plugins/iframe/dialogs/*',
          'static/cked/ckeditor/plugins/iframe/images/*',
          'static/cked/ckeditor/plugins/image/dialogs/*',
          'static/cked/ckeditor/plugins/image/images/*',
          'static/cked/ckeditor/plugins/link/dialogs/*',
          'static/cked/ckeditor/plugins/link/images/*',
          'static/cked/ckeditor/plugins/link/images/hidpi/*',
          'static/cked/ckeditor/plugins/liststyle/dialogs/*',
          'static/cked/ckeditor/plugins/magicline/images/*',
          'static/cked/ckeditor/plugins/magicline/images/hidpi/*',
          'static/cked/ckeditor/plugins/pagebreak/images/*',
          'static/cked/ckeditor/plugins/pastefromgdocs/filter/*',
          'static/cked/ckeditor/plugins/pastefromlibreoffice/filter/*',
          'static/cked/ckeditor/plugins/pastefromword/filter/*',
          'static/cked/ckeditor/plugins/pastetools/filter/*',
          'static/cked/ckeditor/plugins/preview/*',
          'static/cked/ckeditor/plugins/preview/images/*',
          'static/cked/ckeditor/plugins/preview/styles/*',
          'static/cked/ckeditor/plugins/scayt/*',
          'static/cked/ckeditor/plugins/scayt/dialogs/*',
          'static/cked/ckeditor/plugins/scayt/skins/moono-lisa/*',
          'static/cked/ckeditor/plugins/showblocks/images/*',
          'static/cked/ckeditor/plugins/smiley/dialogs/*',
          'static/cked/ckeditor/plugins/smiley/images/*',
          'static/cked/ckeditor/plugins/specialchar/dialogs/*',
          'static/cked/ckeditor/plugins/specialchar/dialogs/lang/*',
          'static/cked/ckeditor/plugins/table/dialogs/*',
          'static/cked/ckeditor/plugins/tableselection/styles/*',
          'static/cked/ckeditor/plugins/tabletools/dialogs/*',
          'static/cked/ckeditor/plugins/templates/dialogs/*',
          'static/cked/ckeditor/plugins/templates/templates/*',
          'static/cked/ckeditor/plugins/templates/templates/images/*',
          'static/cked/ckeditor/plugins/widget/images/*',
          'static/cked/ckeditor/plugins/wsc/*',
          'static/cked/ckeditor/plugins/wsc/dialogs/*',
          'static/cked/ckeditor/plugins/wsc/icons/*',
          'static/cked/ckeditor/plugins/wsc/icons/hidpi/*',
          'static/cked/ckeditor/plugins/wsc/lang/*',
          'static/cked/ckeditor/plugins/wsc/skins/moono-lisa/*',
          'static/cked/ckeditor/samples/*',
          'static/cked/ckeditor/samples/css/*',
          'static/cked/ckeditor/samples/img/*',
          'static/cked/ckeditor/samples/js/*',
          'static/cked/ckeditor/samples/old/*',
          'static/cked/ckeditor/samples/old/assets/*',
          'static/cked/ckeditor/samples/old/assets/inlineall/*',
          'static/cked/ckeditor/samples/old/assets/outputxhtml/*',
          'static/cked/ckeditor/samples/old/assets/uilanguages/*',
          'static/cked/ckeditor/samples/old/dialog/*',
          'static/cked/ckeditor/samples/old/dialog/assets/*',
          'static/cked/ckeditor/samples/old/enterkey/*',
          'static/cked/ckeditor/samples/old/htmlwriter/*',
          'static/cked/ckeditor/samples/old/htmlwriter/assets/outputforflash/*',
          'static/cked/ckeditor/samples/old/magicline/*',
          'static/cked/ckeditor/samples/old/toolbar/*',
          'static/cked/ckeditor/samples/old/wysiwygarea/*',
          'static/cked/ckeditor/samples/toolbarconfigurator/*',
          'static/cked/ckeditor/samples/toolbarconfigurator/css/*',
          'static/cked/ckeditor/samples/toolbarconfigurator/font/*',
          'static/cked/ckeditor/samples/toolbarconfigurator/js/*',
          'static/cked/ckeditor/skins/moono-lisa/*',
          'static/cked/ckeditor/skins/moono-lisa/images/*',
          'static/cked/ckeditor/skins/moono-lisa/images/hidpi/*',
          'static/cked/ckeditor/vendor/*',
          'static/cked/elfinder/*',
          'static/cked/elfinder/css/*',
          'static/cked/elfinder/files/*',
          'static/cked/elfinder/img/*',
          'static/cked/elfinder/js/*',
          'static/cked/elfinder/js/i18n/*',
          'static/cked/elfinder/js/i18n/help/*',
          'static/cked/elfinder/js/proxy/*',
          'static/cked/elfinder/js/worker/*',
          'static/cked/elfinder/sounds/*',
          'templates/cked/*']}

install_requires = \
['django>=2.2']

setup_kwargs = {
    'name': 'django-cked',
    'version': '0.1.4',
    'description': 'CKEditor and elFinder integration for Django Framework.',
    'long_description': 'Django CKEd\n===========\n\n**CKEditor and elFinder integration for Django Framework.**\n\nProvides a ``RichTextField`` and ``CKEditorWidget`` with upload and browse support.\n\n.. figure:: docs/_static/img/ckeditor.jpg\n      :align: center\n      :alt: CKEditor widget\n\n      CKEditor widget\n\n.. figure:: docs/_static/img/elfinder.jpg\n      :align: center\n      :alt: elFinder widget\n\n      elFinder widget\n\n\nInstallation and configuration\n------------------------------\n\nSee `setup part`_ in documentation.\n\n.. _setup part: docs/setup.rst\n\nUsage\n-----\n\nSee `usage part`_ in documentation.\n\n.. _usage part: docs/usage.rst\n\nAuthors\n-------\n\nSee `authors link`_ in documentation.\n\n.. _authors link: AUTHORS.rst\n\n\nLicense\n-------\n\nLicensed under BSD license. See `license link`_ in documentation.\n\n.. _license link: LICENSE.rst\n\n\n',
    'author': 'Artem Galichkin',
    'author_email': 'doomer3d@gmail.com',
    'maintainer': 'Artem Galichkin',
    'maintainer_email': 'doomer3d@gmail.com',
    'url': 'https://github.com/DOOMer/django-cked',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
