from django.urls import path
from solve.views import home, inp_data, result


app_name = 'solve'
urlpatterns = [
    path('', home, name='home'),
    path('inp_data/<int:count_var>/<int:count_cond>', inp_data, name='inp_data'),
    path('result', result, name='result')
]
