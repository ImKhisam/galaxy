from django import template
#from content_for_evrbd.models import BritishBulldog

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

    for item in Tests.objects.filter(type=type_of_exam).order_by('part').distinct('part'):
        menu_dict[item] = Tests.objects.filter(type=type_of_exam, part=item.part).order_by('test_num')

    return {"menu_dict": menu_dict}


@register.filter                        # отображение баллов в результатах
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='multiply')       # нумерация результатов исходя из страницы
def multiply(value, arg):
    return value * arg

