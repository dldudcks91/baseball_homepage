
# 장고 패키지
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import TeamInfo,GameInfo,TeamGameInfo,ScoreRecord,BatterRecord,PitcherRecord,TodayGameInfo,TodayTeamGameInfo,TodayLineUp,RunGraphData
from django.db.models import Q
# 그래프용 패키지
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import View



# 데이터용 패키지
import time
import numpy as np
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
    local_time = time.localtime()
    year = str(local_time[0])
    month = str(local_time[1]).zfill(2)
    day = str(local_time[2]).zfill(2)
    today = year + "-" + month + "-" + day
    date = year+month+day
    game_date_dic = TodayGameInfo.objects.values()
    craw_time = list(game_date_dic.values('etc')[0].values())[0]
    
    context = {'today':today,'craw_time':craw_time}
    
    
    return render(request,'baseball/game_info.html',context)
    
def game_info_date(request,date):
    
    game_date_dic = GameInfo.objects.filter(game_idx__contains = str(date)).values()
    game_date_idx = game_date_dic.values('game_idx')
    team_game_dic = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
    team_game_idx = team_game_dic.values("team_game_idx","home_away")
    is_end = True
    if len(game_date_dic) == 0:
        game_date_dic = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
        game_date_idx = game_date_dic.values('game_idx')
        team_game_dic = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
        team_game_idx = team_game_dic.values("team_game_idx","home_away")
        is_end = False
        
        
    for game_num_idx, game_date in enumerate(game_date_dic):
        
        game_date['game_num_idx'] = game_num_idx+1
        game_date['away_url'] = "/static/images/emblem/emblem_" + game_date['away_name'] + ".png";
        game_date['home_url'] = "/static/images/emblem/emblem_" + game_date['home_name'] + ".png";
        
        game_idx = game_num_idx * 2
        if team_game_idx[game_idx]['home_away'] == 'home':
            home_idx = team_game_idx[game_idx]['team_game_idx']
            away_idx = team_game_idx[game_idx+1]['team_game_idx']

        else:
            home_idx = team_game_idx[game_idx+1]['team_game_idx']
            away_idx = team_game_idx[game_idx]['team_game_idx']
        
        if is_end:
            home_score_dic = ScoreRecord.objects.filter(team_game_idx = home_idx).values()
            away_score_dic = ScoreRecord.objects.filter(team_game_idx = away_idx).values()
            
            game_date['home_score'] = home_score_dic[0]['r']
            game_date['away_score'] = away_score_dic[0]['r']
    
            home_pitcher = PitcherRecord.objects.filter(team_game_idx = home_idx).values()[0]['name']
            away_pitcher = PitcherRecord.objects.filter(team_game_idx = away_idx).values()[0]['name']
    
            game_date['home_pitcher'] = home_pitcher
            game_date['away_pitcher'] = away_pitcher
        else:
            try:
                home_pitcher = TodayLineUp.objects.filter(team_game_idx = home_idx).values()[0]['name']
                away_pitcher = TodayLineUp.objects.filter(team_game_idx = away_idx).values()[0]['name']
                game_date['home_pitcher'] = home_pitcher
                game_date['away_pitcher'] = away_pitcher
            except:
                pass
            pass
    
    data_length = len(game_date_dic)
    
    context = {'game_date_dic':game_date_dic,'is_end':is_end, 'data_length':data_length}
    return render(request,'baseball/game_info_date.html',context)

def boxscore(request,date,today_game_num):
    
    today_game_num_idx_min = (2*today_game_num)-2
    today_game_num_idx_max = (2*today_game_num)
    
    game_date_dic = GameInfo.objects.filter(game_idx__contains = str(date)).values()
    game_date_idx = game_date_dic.values("game_idx")
    team_game_dic = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
    
    team_game_idx = team_game_dic.values("team_game_idx","home_away")[today_game_num_idx_min:today_game_num_idx_max]
    
    if team_game_idx[0]['home_away'] == 'home':
        home_idx = team_game_idx[0]['team_game_idx']
        away_idx = team_game_idx[1]['team_game_idx']
        
    else:
        home_idx = team_game_idx[1]['team_game_idx']
        away_idx = team_game_idx[0]['team_game_idx']
        
    team_name = game_date_dic.values('away_name','home_name')[today_game_num-1]
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
    return render(request,'baseball/boxscore.html',context)

class RunGraphView(APIView):
    
    def get(self,request,date,today_game_num):
        
        today_game_num_idx_min = (2*today_game_num)-2
        today_game_num_idx_max = (2*today_game_num)
        
        if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
            game_date_list = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
            game_date_idx = game_date_list.values("game_idx")
            
            
            team_game_list = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values().order_by('game_idx','team_game_idx')
            team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        else:
            game_date_list = GameInfo.objects.filter(game_idx__contains = str(date)).values()
            game_date_idx = game_date_list.values("game_idx")
            
            
            team_game_list = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values().order_by('game_idx','team_game_idx')
            team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        
        
        if team_game_idx[0]['home_away'] == 'home':
            i = 0 
            j = 1
            
        else:
            i = 1
            j = 0
        
        year = int(str(date)[:4])
        
        home_team_num = team_game_idx[i]['team_num']
        away_team_num = team_game_idx[j]['team_num']
        
        home_name = TeamInfo.objects.filter(year__contains = year, team_num = home_team_num).values('team_name')[0]['team_name']
        away_name = TeamInfo.objects.filter(year__contains = year, team_num = away_team_num).values('team_name')[0]['team_name']
        
        home_game_num = team_game_idx[i]['game_num']
        away_game_num = team_game_idx[j]['game_num']
              
        home_team_dic= RunGraphData.objects.filter(year = year , team_num = home_team_num, game_num__lt = home_game_num).values()
        away_team_dic = RunGraphData.objects.filter(year = year , team_num = away_team_num, game_num__lt = away_game_num).values()
        
        home_run_list = home_team_dic.values('run_1')
        away_run_list = away_team_dic.values('run_1')
        def get_run_list(run_list):
            r_list = [0 for i in range(16)]
            length= len(run_list)
            for r in run_list:
                r = round(r['run_1'])
                
                if r >=15:
                    r_list[-1]+=1
                else:
                    r_list[r]+=1
                    
            
            result_list= list()
            count = 0
            r_sum = 0
            for r in r_list:
                
                r_sum+=r
                count+=1
                if count == 2:                    
                    result_list.append(r_sum / length*100)
                    count = 0
                    r_sum = 0 
                
            return result_list
        
        home_run_dist= get_run_list(home_run_list)
        away_run_dist = list(-np.array(get_run_list(away_run_list)))
        
        home_run_5 = list()
        home_run_20 = list()
        
        away_run_5 = list()
        away_run_20 = list()
        
        for run in home_team_dic:
            
            home_run_5.append([run['game_num'],run['run_5']])
            home_run_20.append([run['game_num'],run['run_20']])
            
        for run in away_team_dic:
            away_run_5.append([run['game_num'],run['run_5']])
            away_run_20.append([run['game_num'],run['run_20']])
          
        
        result_data = {'year':year, 'home_name': home_name, 'away_name':away_name, 'home_run_dist': home_run_dist, 'away_run_dist': away_run_dist, 
                       'home_run_5':home_run_5, 'home_run_20':home_run_20,'away_run_5':away_run_5, 'away_run_20':away_run_20}
        
        
        return Response(result_data)

class CompareGraphView(APIView):
    
    def get(self,request,date,today_game_num):
        
        today_game_num_idx_min = (2*today_game_num)-2
        today_game_num_idx_max = (2*today_game_num)
        
        if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
            game_date_list = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
            game_date_idx = game_date_list.values("game_idx")
            
            
            team_game_list = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
            team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        else:
            game_date_list = GameInfo.objects.filter(game_idx__contains = str(date)).values()
            game_date_idx = game_date_list.values("game_idx")
            
            
            team_game_list = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
            team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        
        
        if team_game_idx[0]['home_away'] == 'home':
            i = 0 
            j = 1
            
        else:
            i = 1
            j = 0
        
        year = int(str(date)[:4])
        
        home_team_num = team_game_idx[i]['team_num']
        away_team_num = team_game_idx[j]['team_num']
        
        home_name = TeamInfo.objects.filter(year__contains = year, team_num = home_team_num).values('team_name')[0]['team_name']
        away_name = TeamInfo.objects.filter(year__contains = year, team_num = away_team_num).values('team_name')[0]['team_name']
        
        home_game_num = team_game_idx[i]['game_num']
        away_game_num = team_game_idx[j]['game_num']
            
        
        
          
        
        result_data = {'year':year, 'home_name': home_name, 'away_name':away_name}
                       
        
        
        return Response(result_data)

def preview(request,date,today_game_num):
    today_game_num_idx_min = (2*today_game_num)-2
    today_game_num_idx_max = (2*today_game_num)
    
    if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
        game_date_list = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
        game_date_idx = game_date_list.values("game_idx")
        
        
        team_game_list = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values().order_by('game_idx','team_game_idx')
        team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        is_end = False
    else:
        game_date_list = GameInfo.objects.filter(game_idx__contains = str(date)).values()
        game_date_idx = game_date_list.values("game_idx")
        
        
        team_game_list = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values().order_by('game_idx','team_game_idx')
        team_game_idx = team_game_list.values()[today_game_num_idx_min:today_game_num_idx_max]
        is_end = True
    
    if team_game_idx[0]['home_away'] == 'home':
        i = 0 
        j = 1
        
    else:
        i = 1
        j = 0
    
    
    
    
    home_dic = dict()
    away_dic = dict()
    
    year = int(str(date)[:4])
    home_team_num = team_game_idx[i]['team_num']
    away_team_num = team_game_idx[j]['team_num']
    
    
    home_dic['name'] = TeamInfo.objects.filter(year__contains = year, team_num = home_team_num).values('team_name')[0]['team_name']
    away_dic['name'] = TeamInfo.objects.filter(year__contains = year, team_num = away_team_num).values('team_name')[0]['team_name']
    
    
    home_idx = team_game_idx[i]['team_game_idx']
    away_idx = team_game_idx[j]['team_game_idx']
    
    if is_end:
        home_pitcher = PitcherRecord.objects.filter(team_game_idx = home_idx).values()[0]['name']
        away_pitcher = PitcherRecord.objects.filter(team_game_idx = away_idx).values()[0]['name']
    else:
        home_pitcher = TodayLineUp.objects.filter(team_game_idx=home_idx).values()[0]['name']
        away_pitcher = TodayLineUp.objects.filter(team_game_idx=away_idx).values()[0]['name']
    
    home_dic['sp'] = home_pitcher
    away_dic['sp'] = away_pitcher
    
    
    context ={'date':date,'today_game_num':today_game_num,'home_dic':home_dic,'away_dic':away_dic}
    return render(request,'baseball/preview.html',context)

def lineup(request,date,today_game_num):
    today_game_num_idx_min = (2*today_game_num)-2
    today_game_num_idx_max = (2*today_game_num)
    
    game_date_dic = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
    game_date_idx = game_date_dic.values("game_idx")
    team_game_dic = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
    
    team_game_idx = team_game_dic.values("team_game_idx","home_away")[today_game_num_idx_min:today_game_num_idx_max]
    
    if team_game_idx[0]['home_away'] == 'home':
        home_idx = team_game_idx[0]['team_game_idx']
        away_idx = team_game_idx[1]['team_game_idx']
        
    else:
        home_idx = team_game_idx[1]['team_game_idx']
        away_idx = team_game_idx[0]['team_game_idx']
        
    team_name = game_date_dic.values('away_name','home_name')[today_game_num-1]
    home_name = team_name['home_name']
    away_name = team_name['away_name']
    
    
    team_name = {'home':home_name,'away':away_name}
    team_name['away_url'] = "/static/images/emblem/emblem_" + away_name + ".png"
    team_name['home_url'] = "/static/images/emblem/emblem_" + home_name + ".png"
    
    home_lineup = TodayLineUp.objects.filter(team_game_idx = home_idx).values()
    away_lineup = TodayLineUp.objects.filter(team_game_idx = away_idx).values()
    
    
    
    context ={'team_name':team_name, 'home':home_lineup, 'away': away_lineup}
    
    
    return render(request,'baseball/lineup.html',context)