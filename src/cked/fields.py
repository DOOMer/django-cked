
from django.db import models
from django import forms

from .widgets import CKEditorWidget


class RichTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RichTextFormField,
        }
        defaults.update(kwargs)
        return super(RichTextField, self).formfield(**defaults)


class RichTextFormField(forms.fields.Field):
    def __init__(self, *args, **kwargs):
        del(kwargs['max_length']) # Fiz bug Exception Value: __init__() got an unexpected keyword argument 'max_length'
        kwargs.update({'widget': CKEditorWidget()})
        super(RichTextFormField, self).__init__(*args, **kwargs)

