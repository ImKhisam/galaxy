
from .models import *

menu = [{'title': "Home", 'url_name': 'personal_acc'},
            #{'title': "PK", 'url_name': 'personal_acc'},
            {'title': "ОГЭ", 'url_name': 'oge'},
            {'title': "ЕГЭ", 'url_name': 'ege'},
            {'title': "Develop your skills", 'url_name': 'dev_skills'},
            {'title': "Подготовка к всероссийской олимпиаде", 'url_name': 'olymp'},
            {'title': "Brittish Bulldog", 'url_name': 'BB'},
            {'title': "Idioms & Collocations", 'url_name': 'idioms'},
            {'title': "Fun room", 'url_name': 'fun_room'}
        ]


class DataMixin:
    def check_access(self):
        return self.request.user.is_confirmed

    def get_user_context(self, **kwargs):
        context = kwargs
        user_menu = menu.copy()

        if self.request.user.is_authenticated and not self.request.user.is_confirmed:
            user_menu = [{'title': "Brittish Bulldog", 'url_name': 'BB'},
                            {'title': "Idioms & Collocations", 'url_name': 'idioms'},
                            {'title': "Fun room", 'url_name': 'fun_room'}
                        ]

        context['menu'] = user_menu
        return context



