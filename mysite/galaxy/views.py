from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView

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
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'galaxy/login.html'


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Registration')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):          # при успешном логине перенаправляет
        return reverse_lazy('personal_acc')


def logout_user(request):
    logout(request)             # станд функция выхода
    return redirect('home')

class Personal_Acc(DataMixin,TemplateView):
    #model = CustomUser
    template_name = "galaxy/personal_acc.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Personal Account')
        return dict(list(context.items()) + list(c_def.items()))


class Oge(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Oge')
        return dict(list(context.items()) + list(c_def.items()))


class Ege(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ege')
        return dict(list(context.items()) + list(c_def.items()))


class Dev_skills(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ege')
        return dict(list(context.items()) + list(c_def.items()))


class Olymp(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        if not self.check_access():
            return redirect('julik')

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ege')
        return dict(list(context.items()) + list(c_def.items()))


#class BB(DataMixin, TemplateView):
#    template_name = "galaxy/zaglushka.html"
#
#    def get_context_data(self, *, object_list=None, **kwargs):
#        context = super().get_context_data(**kwargs)
#        c_def = self.get_user_context(title='BB')
#        return dict(list(context.items()) + list(c_def.items()))


class Idioms(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='idioms')
        return dict(list(context.items()) + list(c_def.items()))


class Fun_room(DataMixin, TemplateView):
    template_name = "galaxy/zaglushka.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='fun_room')
        return dict(list(context.items()) + list(c_def.items()))

def julik(request):
    return render(request, 'galaxy/julik.html')