# ---------------------------------------- [edit] ---------------------------------------- #
from django.urls import path, include

from . import views




app_name = 'bithumb'


# ---------------------------------------------------------------------------------------- #
urlpatterns = [
    # ---------------------------------------- [edit] ---------------------------------------- #
    path('', views.index, name='index'),
    path('trade_list/', views.trade_list, name='trade_list'),
    path('trade_list/trade_bithumb/', views.trade_bithumb, name='trade_bithumb'),
    path('trade_list/trade_bitget/', views.trade_bitget, name='trade_bitget')
    ]
        







