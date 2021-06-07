Usage
=====

Model field
~~~~~~~~~~~

::

    from django.db import models
    from cked.fields import RichTextField


    class Entry(models.Model):
        text = RichTextField()

Widget
~~~~~~

::

    from django import forms
    from cked.widgets import CKEditorWidget

    class MyForm(forms.Form):
        text = forms.CharField(widget=CKEditorWidget)

**NOTE**: If you are using custom forms, dont'r forget to include form
media to your template:

::

    {{ form.media }}
