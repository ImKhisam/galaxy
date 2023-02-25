import os
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import FileResponse, Http404


class BB(TemplateView):
    template_name = "content_for_evrbd/BB.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'BB'
        return context


def pdf_view(request):
    module_dir = os.path.dirname(__file__)
    filepath = os.path.join(module_dir, 'media/2015.pdf')

    try:
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()