from django import template
#from content_for_evrbd.models import BritishBulldog

from django.utils import timezone
from ..models import *


register = template.Library()

@register.inclusion_tag('galaxy/olymp_drop_menu.html')
def drop_menu_olymp():
    menu_dict = {}

    for item in OlympWay.objects.order_by('-year').distinct('year'):

        menu_dict[item] = {key: {value: {item for item in OlympWay.objects.filter(id=key.id)}
                                 for value in OlympWay.objects.filter(year=item.year, stage=key.stage)}
                           for key in OlympWay.objects.filter(year=item.year).order_by('-stage').distinct('stage')}

    return {"menu_dict": menu_dict}


@register.inclusion_tag('galaxy/test_drop_menu.html')
def drop_menu_test(type_of_exam):
    menu_dict = {}

    for item in Tests.objects.filter(type=type_of_exam, is_assessment=False).order_by('part').distinct('part'):
        menu_dict[item] = Tests.objects.filter(type=type_of_exam, part=item.part, is_assessment=False)\
                                        .order_by('test_num')

    return {"menu_dict": menu_dict}


@register.inclusion_tag('galaxy/tag_assessment.html')
def assessment():
    today = timezone.now().date()
    #assessment_list = Tests.objects.filter(date_of_assessment=today)

    return {"today": today}


@register.filter                        # отображение баллов в результатах(show_results.html)
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter                        # used in show_color_result
def is_list(variable):
    return isinstance(variable, list)


@register.filter(name='multiply')       # нумерация результатов исходя из страницы
def multiply(value, arg):
    return value * arg


@register.filter(name='divide_integral')       # конвертация секунд в минуты
def divide_integral(value, arg):
    return value // arg


@register.filter(name='modulus')       # конвертация секунд в минуты
def modulus(value, arg):
    return value % arg


@register.filter(name='adding')
def adding(value, arg):
    return value + arg