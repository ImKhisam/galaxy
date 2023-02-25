from django.urls import path
from .views import *

urlpatterns = [
    path('BB/', pdf_view, name='BB'),
    ]