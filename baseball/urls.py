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
    
    
    path('game_info/preview/<int:date>/<int:today_game_num>', views.preview, name='preview'),
    path('game_info/lineup/<int:date>/<int:today_game_num>', views.lineup, name='lineup'),
    path('game_info/boxscore/<int:date>/<int:today_game_num>', views.boxscore, name='boxscore'),
    
    path('game_info/run_graph/<int:date>/<int:today_game_num>', views.RunGraphView.as_view(), name='run_graph'),
    path('game_info/compare_graph/<int:date>/<int:today_game_num>', views.CompareGraphView.as_view(), name='compare_graph'),]
        
    
