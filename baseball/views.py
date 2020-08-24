

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import TeamInfo,GameInfo,TeamGameInfo,ScoreRecord,BatterRecord,PitcherRecord

# ---------------------------------------------------------------------------------------- #

def index(request):
    context = {'index': 'Hello'}
    return render(request,'baseball/index.html',context)
    
def team_info(request):
    '''
    team_list = TeamInfo.objects.all()
    context = {'team_list':team_list}
    '''
    return render(request,'baseball/team_info.html')
    
def team_info_year(request,year):
    team_year_list = TeamInfo.objects.filter(year__contains = year).values()
    context = {'team_year_list':team_year_list,'year':year}
    return render(request,'baseball/team_info_year.html',context)


def game_info(request):
    return render(request,'baseball/game_info.html')
    
def game_info_date(request,date):
    game_date_list = GameInfo.objects.filter(game_idx__contains = str(date)).values()
    

    for game_num_idx, game_date in enumerate(game_date_list):
        
        game_date['game_num_idx'] = game_num_idx+1
        game_date['away_url'] = "/static/images/emblem/emblem_" + game_date['away_name'] + ".png";
        game_date['home_url'] = "/static/images/emblem/emblem_" + game_date['home_name'] + ".png";
    
    
    context = {'game_date_list':game_date_list}
    return render(request,'baseball/game_info_date.html',context)

    
    

def team_game_info(request,date,game_num):
    
    
    game_num_idx_min = (2*game_num)-2
    game_num_idx_max = (2*game_num)
    

    game_date_list = GameInfo.objects.filter(game_idx__contains = str(date)).values()
    game_date_idx = game_date_list.values("game_idx")
    team_game_list = TeamGameInfo.objects.filter(game_idx__in=game_date_idx).values()
    
    
    
    team_game_idx = team_game_list.values("team_game_idx","home_away")[game_num_idx_min:game_num_idx_max]
    
    if team_game_idx[0]['home_away'] == 'home':
        home_idx = team_game_idx[0]['team_game_idx']
        away_idx = team_game_idx[1]['team_game_idx']
        
    else:
        home_idx = team_game_idx[1]['team_game_idx']
        away_idx = team_game_idx[0]['team_game_idx']
        
    team_name = game_date_list.values('away_name','home_name')[game_num-1]
    home_name = team_name['home_name']
    away_name = team_name['away_name']
    
    team_name = {'home':home_name,'away':away_name}

    home_score = ScoreRecord.objects.filter(team_game_idx = home_idx).values()
    away_score = ScoreRecord.objects.filter(team_game_idx = away_idx).values()
    

    home_batter = BatterRecord.objects.filter(team_game_idx = home_idx).values()
    away_batter = BatterRecord.objects.filter(team_game_idx = away_idx).values()
    
    home_pitcher = PitcherRecord.objects.filter(team_game_idx = home_idx).values()
    away_pitcher = PitcherRecord.objects.filter(team_game_idx = away_idx).values()
    
    
    
    context ={'home_score':home_score,'away_score':away_score,'home_batter':home_batter,'away_batter':away_batter,'team_name':team_name,
              'home_pitcher':home_pitcher, 'away_pitcher':away_pitcher}
    return render(request,'baseball/team_game_info.html',context)
    
