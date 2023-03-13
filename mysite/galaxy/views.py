import os
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import FileResponse, Http404
from .utils import DataMixin
from .forms import *


class Index(DataMixin, TemplateView):
    template_name = "galaxy/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Main page')
        return dict(list(context.items()) + list(c_def.items()))


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'galaxy/register.html'
    success_url = reverse_lazy('personal_acc')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Registration')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()              # сохраняем форму в бд
        login(self.request, user)       # при успешной регистрации сразу логинит
        return redirect('personal_acc', acc_slug=self.request.user.slug)


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'galaxy/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Login')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):          # при успешном логине перенаправляет
        return reverse_lazy('personal_acc', kwargs={'acc_slug': self.request.user.slug})


def logout_user(request):
    logout(request)             # станд функция выхода
    return redirect('home')


class PersonalAcc(LoginRequiredMixin, DataMixin, DetailView):
    model = CustomUser
    template_name = "galaxy/personal_acc.html"
    slug_url_kwarg = 'acc_slug'
    # context_object_name = 'acc'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Personal Account')
        return dict(list(context.items()) + list(c_def.items()))


class Gse(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Oge')
        return dict(list(context.items()) + list(c_def.items()))


class Use(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ege')
        return dict(list(context.items()) + list(c_def.items()))


class ListeningTest(TemplateView):
    template_name = "galaxy/listening_test.html"


class DevSkills(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ege')
        return dict(list(context.items()) + list(c_def.items()))


def showdoc(request, classes_id, doc_type):
    media = settings.MEDIA_ROOT                                     # importing from settings
    obj = get_object_or_404(OlympWay, id=classes_id)                # get path from db
    filepath = os.path.join(media, str(obj.task))                   # uniting path
    if doc_type == 'answer':
        filepath = os.path.join(media, str(obj.answer))
    elif doc_type == 'script':
        filepath = os.path.join(media, str(obj.script))

    try:
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


class Playaudio(DetailView):
    model = OlympWay
    template_name = 'galaxy/play_audio.html'
    pk_url_kwarg = 'classes_id'
    context_object_name = 'file'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '_'.join(('Olymp', context['file'].year, context['file'].classes))
        return context


class Idioms(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='idioms')
        return dict(list(context.items()) + list(c_def.items()))


def julik(request):
    return render(request, 'galaxy/julik.html')


class Test(DataMixin, TemplateView):
    template_name = "galaxy/test.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='test')
        return dict(list(context.items()) + list(c_def.items()))
