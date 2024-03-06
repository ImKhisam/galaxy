from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth.models import User
from .models import *
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelform_factory
from django.forms import ModelForm, modelformset_factory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model


User = get_user_model()


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Login', widget=forms.TextInput(attrs={'class': 'auth_input', 'placeholder': 'Username or Email'}))
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'auth_input', 'placeholder': 'Password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                ogg = User.objects.get(email=username)
                if ogg:
                    self.user_cache = authenticate(username=ogg.username,
                                                   password=password)
            else:
                self.user_cache = authenticate(username=username,
                                               password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


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
        fields = ['chapter_number', 'text_name', 'text', 'media']
        widgets = {
            'chapter_number': forms.TextInput(attrs={'class': 'chapter-number-info-add'}),
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
                  'text', 'addition_before', 'addition_after']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'question-add'}),
            'addition_before': forms.TextInput(attrs={'class': 'additions'}),
            'text': forms.Textarea(attrs={'class': 'question-add'})
        }


class WritingQandAAddForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['question', 'picture', 'writing_fl', 'writing_from', 'writing_to',
                  'writing_subject', 'writing_letter', 'writing_after']
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
