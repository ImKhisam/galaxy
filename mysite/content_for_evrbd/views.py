from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import FileResponse, Http404
from django.conf import settings

from .models import *


#class BB_years(ListView):
#    model = BrittishBulldog
#    template_name = "content_for_evrbd/BB_years.html"
#    context_object_name = 'years'
#
#    def get_context_data(self, *, object_list=None, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['title'] = 'BB'
#        return context
#
#    def get_queryset(self):
#        #print(BrittishBulldog.objects.values('year').distinct('year'))
#        #BrittishBulldog.objects.values('year').distinct('year')   # return <QuerySet [{'year': '2021-2022'}, {'year': '2022-2023'}]>
#        return BrittishBulldog.objects.distinct('year')


#class BB_year(ListView):
#    model = BrittishBulldog
#    template_name = "content_for_evrbd/BB_year.html"
#    context_object_name = 'classes'
#
#    def get_context_data(self, *, object_list=None, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['title'] = 'BB_' + self.kwargs['bb_slug']
#        return context
#
#    def get_queryset(self):
#        return BrittishBulldog.objects.filter(year=self.kwargs['bb_slug'])


#class Show_doc(DetailView):
#    model = BrittishBulldog
#    template_name = "content_for_evrbd/show_doc.html"
#    #slug_url_kwarg = 'bb_slug'
#    pk_url_kwarg = 'classes_id'
#    context_object_name = 'file'
#
#    def get_context_data(self, *, object_list=None, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['title'] = '_'.join(('BB', context['file'].year, context['file'].classes)) # 'BB', context['file'].year, context['file'].classes
#        return context


class BB(ListView):
    model = BritishBulldog
    template_name = 'content_for_evrbd/BB.html'
    context_object_name = 'bb_tasks'

    def get_queryset(self):
        content_dict = {year_obj: {x: BritishBulldog.objects.get(year=year_obj.year, classes=x)
                                   if BritishBulldog.objects.filter(year=year_obj.year, classes=x).exists()
                                   else ' '
                                   for x in ['1-2', '3-4', '5-6', '7-8', '9-11', 'Answers']}
                        for year_obj in BritishBulldog.objects.order_by('-year').distinct('year')}

        return content_dict

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'BB Archive'
        return context


class Olymp(ListView):
    model = OlympWay
    template_name = 'content_for_evrbd/olymp.html'
    context_object_name = 'olymp_tasks'

    def get_queryset(self):
        from django.db.models.functions import Cast
        from django.db.models import Value, CharField, IntegerField
        content_dict = {}

        #for item in OlympWay.objects.order_by('-year').distinct('year'):
        #    menu_dict[item] = {key: {value: {item for item in OlympWay.objects.filter(id=key.id)}
        #                             for value in OlympWay.objects.filter(year=item.year, stage=key.stage)}
        #                       for key in OlympWay.objects.filter(year=item.year).order_by('-stage').distinct('stage')}

        for item in OlympWay.objects.order_by('-year').distinct('year'):
            content_dict[item] = {key: OlympWay.objects.filter(year=item.year, stage=key.stage).order_by('order')
                               for key in OlympWay.objects.filter(year=item.year).order_by('-stage').distinct('stage')}

        return content_dict

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Olymp Archive'
        return context


def showdoc(request, classes_id, source, doc_type):
    media = settings.MEDIA_ROOT                                     # importing from settings
    model = OlympWay if source == 'Olymp' else BritishBulldog
    obj = get_object_or_404(model, id=classes_id)          # get path from db

    if source == 'BB':
        filepath = os.path.join(media, str(obj.content))                # uniting path
    elif source == 'Olymp':
        filepath = os.path.join(media, str(obj.task))  # uniting path
        if doc_type == 'answer':
            filepath = os.path.join(media, str(obj.answer))
        elif doc_type == 'script':
            filepath = os.path.join(media, str(obj.script))

    try:
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


# todo add LoginRequiredMixin
class Playaudio(DetailView):
    template_name = 'content_for_evrbd/play_audio.html'
    context_object_name = 'file'

    def get_object(self, queryset=None):
        classes_id = self.kwargs.get('classes_id')
        source = self.kwargs.get('source')
        if source == 'BB':
            self.model = BritishBulldog
        elif source == 'Olymp':
            self.model = OlympWay
        else:
            raise Http404("Invalid source")

        try:
            obj = self.model.objects.get(pk=classes_id)
        except self.model.DoesNotExist:
            raise Http404("Object does not exist")

        return obj

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['title'] = '_'.join(('BB', context['file'].year, context['file'].classes)) # 'BB', context['file'].year, context['file'].classes
        context['title'] = 'Play audio'
        return context


def play_video(request):
    videos = Video.objects.all()
    context = {
        'title': 'Videos',
        'videos': videos,
        'fl': Video.objects.count()
    }
    return render(request, 'content_for_evrbd/play_video.html', context=context)


def cross_choice(request):
    context = {
        'title': 'Crosswords',
    }
    return render(request, 'content_for_evrbd/crossword_choice.html', context=context)


def cross(request, cross_num):
    crossword_template = "".join(('content_for_evrbd/crossword_', str(cross_num), '.html'))
    return render(request, crossword_template)


def quizpreview(request):
    return render(request, 'content_for_evrbd/quiz_preview.html')   # delete?


class QuizPreview(ListView):
    paginate_by = 5
    model = Quizzes
    template_name = 'content_for_evrbd/quiz_preview.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quizzes.objects.all()


class ShowQuiz(DetailView):
    model = Quizzes
    template_name = 'content_for_evrbd/show_quiz.html'
    pk_url_kwarg = 'quiz_id'
    context_object_name = 'quiz'

