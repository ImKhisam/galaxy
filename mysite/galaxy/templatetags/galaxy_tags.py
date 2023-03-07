from django import template

#from content_for_evrbd.models import BrittishBulldog

from ..models import *


register = template.Library()

@register.inclusion_tag('galaxy/drop_menu.html')
def drop_menu(fl):
    menu_dict = {}
    if fl == 'BB':
        for item in BritishBulldog.objects.distinct('year'):
            menu_dict[item] = BritishBulldog.objects.filter(year=item.year) # 2 запроса!!!!!!!!!!!

    return {"menu_dict": menu_dict}