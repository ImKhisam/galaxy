from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from galaxy.utils import TeacherUserMixin, teacher_check
from .forms import TutorialFileAddForm
from .models import *


class BB(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
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


class Olymp(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
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
            content_dict[item] = {key: OlympWay.objects.filter(year=item.year, stage=key.stage).order_by('classes_order')
                               for key in OlympWay.objects.filter(year=item.year).order_by('stage_order').distinct('stage_order')}

        return content_dict

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Olymp Archive'
        return context


@login_required(login_url='/login/')
def publications(request):
    context = {
        'title': 'Publications',
    }
    return render(request, 'content_for_evrbd/publications.html', context=context)


class Publications(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = TutorialFile
    template_name = 'content_for_evrbd/publications.html'
    context_object_name = 'files'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Publications'
        context['current_category'] = 'Articles'
        return context

    def get_queryset(self):
        return TutorialFile.objects.filter(category='Articles')


#@user_passes_test(teacher_check, login_url='home')
def filter_publications(request):
    data = dict()
    # Get parameters from AJAX request
    filter_flag = request.GET.get('filter_flag')

    files = TutorialFile.objects.filter(category=filter_flag)

    context = dict()
    context['files'] = files
    context['current_category'] = filter_flag
    data['my_content'] = render_to_string('content_for_evrbd/render_publications_table.html',
                                          context, request=request)

    return JsonResponse(data)


class AddTutorialFileView(LoginRequiredMixin, TeacherUserMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'

    def get(self, request, *args, **kwargs):
        # Get the category from the query parameter
        selected_category = request.GET.get('category', None)

        # Initialize the form with the selected category if provided
        initial_data = {'category': selected_category} if selected_category else {}
        file_form = TutorialFileAddForm(initial=initial_data)

        context = {
            'file_form': file_form,
        }
        return render(request, 'content_for_evrbd/add_tutorial_file.html', context)

    def post(self, request, *args, **kwargs):
        file_form = TutorialFileAddForm(request.POST, request.FILES)
        if file_form.is_valid():
            file_obj = file_form.save(commit=False)
            file_obj.title = file_obj.file.name
            file_obj.save()  # Save the file

            return redirect('publications')

        context = {
            'file_form': file_form,
        }
        return render(request, 'content_for_evrbd/add_tutorial_file.html', context)


def download_file(request, pk):
    try:
        file_obj = TutorialFile.objects.get(pk=pk)
        return FileResponse(file_obj.file.open(), as_attachment=True, filename=file_obj.file.name.split('/')[-1])
    except TutorialFile.DoesNotExist:
        raise Http404("File does not exist")


@user_passes_test(teacher_check, login_url='home')
def delete_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        file_obj = get_object_or_404(TutorialFile, id=file_id)
        file_obj.delete()
        return JsonResponse({'message': 'Test deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='/login/')
def master_yls(request):
    context = {
        'title': 'Master Your Language Skills',
    }
    return render(request, 'content_for_evrbd/master_yls.html', context=context)


@login_required(login_url='/login/')
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


class Playaudio(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
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


@login_required(login_url='/login/')
def watch_and_learn(request):
    videos = Video.objects.all()
    context = {
        'title': 'Videos',
        'videos': videos,
        'fl': Video.objects.count()
    }
    return render(request, 'content_for_evrbd/watch_and_learn.html', context=context)


@login_required(login_url='/login/')
def cross_choice(request):
    context = {
        'title': 'Crosswords',
    }
    return render(request, 'content_for_evrbd/crossword_choice.html', context=context)


@login_required(login_url='/login/')
def cross(request, cross_num):
    crossword_template = "".join(('content_for_evrbd/crossword_', str(cross_num), '.html'))
    return render(request, crossword_template)


@login_required(login_url='/login/')
def quizpreview(request):
    return render(request, 'content_for_evrbd/quiz_preview.html')   # delete?


class QuizPreview(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    paginate_by = 5
    model = Quizzes
    template_name = 'content_for_evrbd/quiz_preview.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quizzes.objects.all()


class ShowQuiz(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Quizzes
    template_name = 'content_for_evrbd/show_quiz.html'
    pk_url_kwarg = 'quiz_id'
    context_object_name = 'quiz'

