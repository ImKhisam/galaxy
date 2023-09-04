from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import *
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelform_factory
from django.forms import ModelForm, modelformset_factory


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label='First name', widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label='Last name', widget=forms.TextInput(attrs={'class': 'form-input'}))
    role = forms.ChoiceField(label='Role', choices=
                             ((None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher')),
                             widget=forms.Select(attrs={'class': 'form-choice'}))
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


class QuestionAddForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['chapter_id', 'question_number', 'question', 'question_type',
                  'addition_before', 'addition_after', 'points', 'time_limit']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'question-add'}),
        }

    def __init__(self, test_id,  *args, **kwargs):
        super(QuestionAddForm, self).__init__(*args, **kwargs)
        self.fields['chapter_id'] = \
            forms.ModelChoiceField(queryset=Chapters.objects.filter(test_id=test_id).order_by('chapter_number'))


class AnswerAddForm(forms.ModelForm):
    answer = forms.CharField(label='Answer', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Answers
        fields = ['answer', 'is_true', 'addition', 'match']


#class AssessmentAddForm(forms.ModelForm):
#    class Meta:
#        model = Tests
#        fields = ['date_of_assessment']
