from django import template



from ..models import *


register = template.Library()

@register.inclusion_tag('content_for_evrbd/bb_drop_menu.html')
def drop_menu_bb():
    menu_dict = {}

    for item in BritishBulldog.objects.order_by('-year').distinct('year'):
        menu_dict[item] = BritishBulldog.objects.filter(year=item.year) # 2 запроса!!!!!!!!!!!

    return {"menu_dict": menu_dict}
