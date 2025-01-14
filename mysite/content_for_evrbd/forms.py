from django import forms
from .models import *


class TutorialFileAddForm(forms.ModelForm):
    class Meta:
        model = TutorialFile
        fields = ['category', 'file']
