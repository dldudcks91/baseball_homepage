# ---------------------------------------- [edit] ---------------------------------------- #
from django.urls import path

from . import views



app_name = 'baseball'


# ---------------------------------------------------------------------------------------- #
urlpatterns = [
    # ---------------------------------------- [edit] ---------------------------------------- #
    path('', views.index, name='index'),
    path('team_info/', views.team_info, name='team_info'),
    path('team_info/<int:year>', views.team_info_year, name='team_info_year'),
    
    path('game_info/', views.game_info, name='game_info'),
    path('game_info/<int:date>', views.game_info_date, name='game_info_date'),
    
    path('game_info/team_game_info/<int:date>/<int:game_num>', views.team_game_info, name='team_game_info'),]
        
    
