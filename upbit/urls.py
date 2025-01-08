# ---------------------------------------- [edit] ---------------------------------------- #
from django.urls import path, include

from . import views




app_name = 'upbit'


# ---------------------------------------------------------------------------------------- #
urlpatterns = [
    # ---------------------------------------- [edit] ---------------------------------------- #
    path('', views.index, name='index'),
    path('market_data/', views.market_data, name='market_data'),
    path('get_market_data/', views.get_market_data, name='get_market_data'),
    ]
        







