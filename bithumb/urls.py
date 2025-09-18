# ---------------------------------------- [edit] ---------------------------------------- #
from django.urls import path, include

from . import views




app_name = 'bithumb'


# ---------------------------------------------------------------------------------------- #
urlpatterns = [
    # ---------------------------------------- [edit] ---------------------------------------- #
    path('', views.index, name='index'),
    path('trade_list/', views.trade_list, name='trade_list'),
    path('trade_list/trade_day/', views.trade_day, name='trade_day'),
    #path('get_market_data/', views.get_market_data, name='get_market_data'),
    ]
        







