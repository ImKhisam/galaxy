from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth.models import User
from .models import *
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelform_factory
from django.forms import ModelForm, modelformset_factory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Login', widget=forms.TextInput(attrs={'class': 'auth_input', 'placeholder': 'Username'}))
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'auth_input', 'placeholder': 'Password'}))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label='First name', widget=forms.TextInput(attrs={'class': 'auth_input', 'placeholder': 'First name'}))
    last_name = forms.CharField(
        label='Last name', widget=forms.TextInput(attrs={'class': 'auth_input', 'placeholder': 'Last name'}))
    #role = forms.ChoiceField(label='Role', choices=
    #                         ((None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher')),
    #                         widget=forms.Select(attrs={'class': 'form-choice'}))
    username = forms.CharField(
        label='Username', widget=forms.TextInput(attrs={'class': 'auth_input', 'placeholder': 'Username'}))
    email = forms.EmailField(
        label='Email', widget=forms.EmailInput(attrs={'class': 'auth_input', 'placeholder': 'Email'}))
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'auth_input', 'placeholder': 'Password'}))
    password2 = forms.CharField(
        label='Repeat pass', widget=forms.PasswordInput(attrs={'class': 'auth_input', 'placeholder': 'Repeat Password'}))

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class NewPassSetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    new_password2 = forms.CharField(
        label='Password confirm', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat new password'}))


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class TestAddForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['type', 'part', 'media', 'is_assessment']


class ChapterAddForm(forms.ModelForm):
    class Meta:
        model = Chapters
        fields = ['chapter_number', 'info', 'text_name', 'text', 'media']
        widgets = {
            'chapter_number': forms.TextInput(attrs={'class': 'chapter-number-info-add'}),
            'info': forms.Textarea(attrs={'class': 'chapter-info-add', 'oninput': "auto_grow(this)"}),
            'text': forms.Textarea(attrs={'class': 'chapter-text-add', 'oninput': "auto_grow(this)"}),
            'text_name': forms.TextInput(attrs={'class': 'chapter-text-name-add', 'oninput': "this.size = this.value.length"}),
            'media': forms.ClearableFileInput(attrs={'multiple': True}),
        }


class TaskCheckForm(forms.ModelForm):       # выставление баллов?
    class Meta:
        model = TasksToCheck
        fields = ['points']


#class MinuteSecondField(forms.FloatField):
#    def to_python(self, value):
#        # Convert minutes to seconds
#        try:
#            return super().to_python(value) * 60
#        except forms.ValidationError:
#            raise forms.ValidationError("Enter a valid number.")


class QuestionAddForm(forms.ModelForm):
    #preparation_time = MinuteSecondField(label='Preparation Time(in minutes)', required=False)
    #time_limit = MinuteSecondField(label='Time limit(in minutes)', required=False)

    class Meta:
        model = Questions
        fields = ['question_type', 'question', 'media', 'picture', 'text_name',
                  'text', 'addition_before', 'addition_after', 'points',
                  'preparation_time', 'time_limit']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'question-add'}),
            'addition_before': forms.TextInput(attrs={'class': 'additions'}),
            'text': forms.Textarea(attrs={'class': 'question-add'})
        }
        labels = {
            'preparation_time': 'Preparation_time(in seconds)',
            'time_limit': 'Time_limit(in seconds)'
        }


class WritingQandAAddForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['question', 'media', 'points', 'time_limit',
                  'writing_fl', 'writing_from', 'writing_to', 'writing_subject',
                  'writing_letter', 'writing_after']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'question-add'}),
            'addition_before': forms.TextInput(attrs={'class': 'additions'})
        }


class SpeakingQandAAddForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['question', 'media', 'picture', 'text_name', 'text']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'question-add'}),
            'text': forms.Textarea(attrs={'class': 'question-add'})
        }


class AnswerAddForm(forms.ModelForm):
    class Meta:
        model = Answers
        fields = ['answer', 'is_true', 'addition', 'match']
        widgets = {
            'answer': forms.Textarea(attrs={'class': 'question-add'}),
            'addition': forms.Textarea(attrs={'class': 'question-add'})
        }


#class AssessmentAddForm(forms.ModelForm):
#    class Meta:
#        model = Tests
#        fields = ['date_of_assessment']
