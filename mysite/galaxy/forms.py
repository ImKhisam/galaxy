from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import *
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(label='First name', widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label='Last name', widget=forms.TextInput(attrs={'class': 'form-input'}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Repeat pass', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('first_name', 'last_name', 'role', 'username', 'email', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class TestAddForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['type', 'part', 'test_info', 'time_limit', 'media']


class ChapterAddForm(forms.ModelForm):
    class Meta:
        model = Chapters
        fields = ['chapter_number', 'info', 'text_name', 'text', 'media']
        widgets = {
            'media': forms.ClearableFileInput(attrs={'multiple': True}),
        }


class QuestionAddForm(forms.ModelForm):
    class Meta:
        model: Questions
        fields = ['question_number', 'question_type', 'question', 'addition', 'points']


class AnswerAddForm(forms.ModelForm):
    class Meta:
        model: Answers
        fields = ['answer', 'is_true', 'addition', 'match']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answers
        fields = ['answer', 'is_true', 'addition', 'match']
        exclude = ('question_id',)


AnswerFormSet = inlineformset_factory(Questions, Answers, form=AnswerForm, extra=1, can_delete=False, fk_name='question_id', fields=('answer', 'is_true', 'addition', 'match'))

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['test_id', 'chapter_id', 'points', 'question', 'addition', 'question_number', 'question_type']


QuestionFormSet = inlineformset_factory(Tests, Questions, form=QuestionForm, extra=1, can_delete=False, fields=('chapter_id', 'points', 'question', 'addition', 'question_number', 'question_type'))