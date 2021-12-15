
from django.urls import path
from . import views

urlpatterns = [
    path('elfinder/', views.elfinder, name='cked_elfinder'),
    path('elfinder/connector/', views.elfinder_connector, name='cked_elfinder_connector')
]
