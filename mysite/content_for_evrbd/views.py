from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import FileResponse, Http404


from .models import *
from pathlib import Path
from django.conf import settings


class BB_years(ListView):
    model = BrittishBulldog
    template_name = "content_for_evrbd/BB_years.html"
    context_object_name = 'years'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'BB'
        return context

    def get_queryset(self):
        print(BrittishBulldog.objects.values('year').distinct('year'))
        #BrittishBulldog.objects.values('year').distinct('year')   # return <QuerySet [{'year': '2021-2022'}, {'year': '2022-2023'}]>
        return BrittishBulldog.objects.distinct('year')


class BB_year(ListView):
    model = BrittishBulldog
    template_name = "content_for_evrbd/BB_year.html"
    context_object_name = 'classes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'BB_' + self.kwargs['bb_slug']
        return context

    def get_queryset(self):
        return BrittishBulldog.objects.filter(year=self.kwargs['bb_slug'])


class Show_doc(DetailView):
    model = BrittishBulldog
    template_name = "content_for_evrbd/show_doc.html"
    #slug_url_kwarg = 'bb_slug'
    pk_url_kwarg = 'classes_id'
    context_object_name = 'file'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '_'.join(('BB', context['file'].year, context['file'].classes)) # 'BB', context['file'].year, context['file'].classes
        return context


def pdf_view(request, classes_id):
    media = settings.MEDIA_ROOT                                     # importing from settings
    object = get_object_or_404(BrittishBulldog, id=classes_id)      # get path from db
    filepath = os.path.join(media, str(object.content))             # uniting path

    try:
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()