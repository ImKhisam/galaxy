from django import template
#from content_for_evrbd.models import BritishBulldog

from ..models import *


register = template.Library()

@register.inclusion_tag('galaxy/olymp_drop_menu.html')
def drop_menu_olymp():
    menu_dict = {}
    files = {}

    for item in OlympWay.objects.order_by('-year').distinct('year'):

        menu_dict[item] = {key: {value: {item for item in OlympWay.objects.filter(id=key.id)}
                                 for value in OlympWay.objects.filter(year=item.year, stage=key.stage)}
                           for key in OlympWay.objects.filter(year=item.year).order_by('-stage').distinct('stage')}

    return {"menu_dict": menu_dict}
