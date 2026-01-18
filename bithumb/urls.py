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
    path('trade_list/trade_bitget/', views.trade_bitget, name='trade_bitget'),
    path('trade_list/user-memos/', views.get_user_memos, name='get_user_memos'),
    path('trade_list/user-memos/update', views.update_user_memo, name='update_user_memo')

    ]
        







