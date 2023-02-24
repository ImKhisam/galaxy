from django.shortcuts import render
from django.views.generic import TemplateView


class BB(TemplateView):
    template_name = "content_for_evrbd/BB.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'BB'
        return context
