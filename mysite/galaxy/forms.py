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
    role = forms.ChoiceField(label='Role', choices= ((None, 'Choose role'), ('Student', 'Student'), ('Teacher', 'Teacher')), widget=forms.Select(attrs={'class': 'form-choice'}))
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


class TaskCheckForm(forms.ModelForm):
    class Meta:
        model = TasksToCheck
        fields = ['points']




#class ChapterForm(ModelForm):
#    class Meta:
#        model = Chapters
#        fields = [
#            'test_id',
#            'chapter_number',
#        ]
#
#
##class BaseQuestionFormset(BaseInlineFormSet):
#
#    def add_fields(self, form, index):
#        super(BaseQuestionFormset, self).add_fields(form, index)
#        form.nested = AnswerFormset(
#            instance=form.instance,
#            data=form.data if form.is_bound else None,
#            files=form.files if form.is_bound else None)
#
#    def is_valid(self):
#        result = super(BaseQuestionFormset, self).is_valid()
#        print(result)
#        if self.is_bound:
#            for form in self.forms:
#                if hasattr(form, 'nested'):
#                    result = result and form.nested.is_valid()
#
#        return result
#
#    def save(self, commit=True):
#        for form in self.forms:
#            form.save(commit=commit)
#        result = super(BaseQuestionFormset, self).save(commit=commit)
#
#        for form in self.forms:
#            if hasattr(form, 'nested'):
#                if not self._should_delete_form(form):
#                    form.nested.save(commit=commit)
#
#        return result
#
#
#QuestionFormset = inlineformset_factory(
#    parent_model=Chapters, model=Questions, fields='__all__',
#    formset=BaseQuestionFormset, extra=1)
#
#AnswerFormset = inlineformset_factory(
#    parent_model=Questions, model=Answers,
#    fields='__all__', extra=1)
#
#QuestionForm = modelform_factory(Questions, fields=['question_number', 'question_type', 'question', 'addition', 'points'])
#AnswerForm = modelform_factory(Answers, fields=['answer', 'is_true', 'addition', 'match'])


