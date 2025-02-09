
# 장고 패키지
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import AuthUser, TeamInfo, GameInfo, TeamGameInfo, ScoreRecord, BatterRecord, PitcherRecord, TodayGameInfo, TodayTeamGameInfo, TodayLineUp, TodayToTo, RunGraphData, UpdateTime, Post
# 데이터용 패키지
from django.db.models import Q
# 그래프용 패키지
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import View
#제네릭 뷰
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


import json
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
    
def team_info_year(request, year):
    '''
    연도별 team_info 데이터 불러오는 view
    '''
    team_year_set = TeamInfo.objects.filter(year__contains = year)
    rank = 1
    last_win_rate = 0
    max_predicted_win = 0
    for i,team_year in enumerate(team_year_set):
        
        win_rate = team_year.win_rate
        if win_rate != last_win_rate:
            rank = i+1
        team_year.rank = rank
        last_win_rate = win_rate

        matched_count = team_year.win + team_year.draw + team_year.lose
        last_count = 144 - matched_count
        predicted_win = team_year.win + last_count * 0.5
        max_predicted_win = max(max_predicted_win, predicted_win)
        team_year.predicted_win = predicted_win
    
    for i,team_year in enumerate(team_year_set):
        difference_1st = max_predicted_win - team_year.predicted_win
        team_year.difference_1st = difference_1st


    context = {'team_year_set':team_year_set,'year':year}
    return render(request,'baseball/team_info_year.html',context)


def game_info(request):
    local_time = time.localtime()
    year = str(local_time[0])
    month = str(local_time[1]).zfill(2)
    day = str(local_time[2]).zfill(2)
    today = f'{year}-{month}-{day}'
    
    try:
        TGI = TodayGameInfo.objects.all()
        last_date = TGI[0].game_idx[:8]
    except:
        GI = GameInfo.objects.all()
        last_date = GI.last().game_idx[:8]
    last_date = last_date[:4]+"-" + last_date[4:6] + "-" +last_date[6:8]
    
    UDT = UpdateTime.objects.all().order_by('-date','-craw_time')
    date = UDT[0].date#list(game_date_dic.values('etc')[0].values())[0]
    craw_time = UDT[0].craw_time
    context = {'today':today,'date':date, 'craw_time':craw_time,'last_date': last_date}
    
    
    return render(request,'baseball/game_info.html',context)
    
def game_info_date(request,date):
    '''
    특정날짜에 진행되는 경기들의 데이터를 가져옴
    
    '''
    game_date_set = GameInfo.objects.filter(game_idx__contains = str(date)).values()
    game_date_idx = game_date_set.values('game_idx')
    
    team_game_dic = TeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
    team_game_idx = team_game_dic.values("team_game_idx","home_away")
    is_end = True
    
    
    if game_date_set.exists():
        pass
    else:
        game_date_set = TodayGameInfo.objects.filter(game_idx__contains = str(date)).values()
        game_date_idx = game_date_set.values('game_idx')
        team_game_dic = TodayTeamGameInfo.objects.filter(game_idx__in = game_date_idx).values()
        team_game_idx = team_game_dic.values("team_game_idx","home_away")
        is_end = False
        
    
    for game_num_idx, game_date in enumerate(game_date_set):
        
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
        
        
        print(home_idx, away_idx)
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
    
    data_length = game_date_set.count()
    #print(game_date_set)
    context = {'game_date_set':game_date_set,'is_end':is_end, 'data_length':data_length}
    return render(request,'baseball/game_info_date.html',context)



class RunGraphView(APIView):
    
    def __init__(self):

        self.year = int 

        self.home_name = str
        self.away_name = str

        self.home_set = None
        self.away_set = None

        
    def set_data(self, request, date, today_game_num, team_or_foe = 'team'):
        today_game_num_idx_min = (2*today_game_num)-2
        today_game_num_idx_max = (2*today_game_num)
        
        if TodayGameInfo.objects.filter(game_idx__contains = str(date)).exists():
            
            TGI = TodayTeamGameInfo
            GI = TodayGameInfo
            
        else:
            
            TGI = TeamGameInfo
            GI = GameInfo
            
        
        game_date_set = GI.objects.filter(game_idx__contains = str(date))
        today_game_idx = game_date_set.values("game_idx")
        
        team_game_set = TGI.objects.filter(game_idx__in = today_game_idx)
        today_game_set = team_game_set[today_game_num_idx_min:today_game_num_idx_max]
        

        year = int(str(date)[:4])
        self.year = year

        home_team_num = today_game_set[1].team_num
        away_team_num = today_game_set[0].team_num
        
        self.home_name = game_date_set[today_game_num-1].home_name
        self.away_name = game_date_set[today_game_num-1].away_name
        

        home_game_num = today_game_set[1].game_num
        away_game_num = today_game_set[0].game_num
        if team_or_foe == 'team':
            self.home_set = TeamGameInfo.objects.select_related('scorerecord').filter(year = year, team_num= home_team_num)
            self.away_set = TeamGameInfo.objects.select_related('scorerecord').filter(year = year, team_num= away_team_num)
        
        else:
            self.home_set = TeamGameInfo.objects.select_related('scorerecord').filter(year = year, foe_num= home_team_num)
            self.away_set = TeamGameInfo.objects.select_related('scorerecord').filter(year = year, foe_num= away_team_num)
            
    def get_run_dist(self, score_set):
            run_list = [0 for i in range(16)]
            length= score_set.count()
            
            for score in score_set:
                run = round(score.scorerecord.r)
                
                if run >=15:
                    run_list[-1]+=1
                else:
                    run_list[run]+=1
                    
            
            result_list= list()
            count = 0
            run_sum = 0
            for run in run_list:
                
                run_sum+=run
                count+=1
                if count == 2:
                    if length == 0:
                        result_list.append(0)
                    else:
                        result_list.append(run_sum / length*100)
                    count = 0
                    run_sum = 0 
                
            return result_list

    def get_run_range(self, score_set, game_range):
            length = score_set.count()
            score_list = list()
            temp_score_list = list()
            range_score = 0
            for i,score in enumerate(score_set):
                now_score = score.scorerecord.r
                temp_score_list.append(now_score)
                range_score+= now_score
                if i >= game_range:
                    range_score-= temp_score_list[i - game_range]
                devide = game_range if i >= game_range else i + 1 
                score_list.append(round(range_score / devide,3))
            
            return score_list

    

    def get(self,request,date,today_game_num):
        
        self.set_data(request, date, today_game_num)

        year = self.year
        home_name = self.home_name
        away_name = self.away_name

        home_set = self.home_set
        away_set = self.away_set
     
        home_dic = dict()
        home_dic['dist'] = self.get_run_dist(home_set)
        home_dic['range_run'] = self.get_run_range(home_set, 5)
        home_dic['name'] = home_name

        away_dic = dict()
        away_dic['dist'] = self.get_run_dist(away_set)
        away_dic['range_run'] = self.get_run_range(away_set, 5)
        away_dic['name'] = away_name
        
        
        result_data = {'year':year, 'home_dic':home_dic,'away_dic':away_dic}
        
        
        return Response(result_data)
    
    
    def post(self,request,date,today_game_num):
        
        
        
        
        game_range = int(eval(request.body)['game_range'])
        team_or_foe = str(eval(request.body)['team_or_foe'])
        
        self.set_data(request, date, today_game_num, team_or_foe)

        year = self.year
        home_name = self.home_name
        away_name = self.away_name

        home_set = self.home_set
        away_set = self.away_set
     
        home_dic = dict()
        home_dic['dist'] = self.get_run_dist(home_set)
        home_dic['range_run'] = self.get_run_range(home_set, game_range)
        home_dic['name'] = home_name

        away_dic = dict()
        away_dic['dist'] = self.get_run_dist(away_set)
        away_dic['range_run'] = self.get_run_range(away_set, game_range)
        away_dic['name'] = away_name
        

        result_data = {'year':year, 'home_dic':home_dic,'away_dic':away_dic, 'game_range': game_range}

        return Response(result_data)




class SpGraphView(APIView):
    
    def get(self,request,date,today_game_num):
        
        today_game_num_idx_min = (2*today_game_num)-2
        today_game_num_idx_max = (2*today_game_num)
        
        if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
            
            TGI = TodayTeamGameInfo
            GI = TodayGameInfo
            is_end = False
        else:
            
            TGI = TeamGameInfo
            GI = GameInfo
            is_end = True
        
        game_date_set = GI.objects.filter(game_idx__contains = str(date))
        today_game_idx = game_date_set.values("game_idx")
        
        team_game_set = TGI.objects.filter(game_idx__in = today_game_idx)#.order_by('game_idx','home_away')
        today_game_set = team_game_set[today_game_num_idx_min:today_game_num_idx_max]
        
        
        
        
        year = int(str(date)[:4])
        park_factor_total = {'잠실': 0.854,'사직': 1.099,'광주':1.003, '대구': 1.153, '대전': 0.977,'문학':1.046,'고척':0.931,'창원':1.051,'수원':1.032}
        home_dic = dict()
        away_dic = dict()
        
        home_name = game_date_set[today_game_num-1].home_name
        away_name = game_date_set[today_game_num-1].away_name
        
        home_dic['name'] = home_name
        away_dic['name'] = away_name
        
        
        home_game_idx = today_game_set[1].team_game_idx
        away_game_idx = today_game_set[0].team_game_idx
    
        
        if is_end:
            home_sp = PitcherRecord.objects.filter(team_game_idx = home_game_idx)[0].name
            away_sp = PitcherRecord.objects.filter(team_game_idx = away_game_idx)[0].name
        else:
            home_sp = TodayLineUp.objects.filter(team_game_idx=home_game_idx)[0].name
            away_sp = TodayLineUp.objects.filter(team_game_idx=away_game_idx)[0].name
        
        home_dic['sp'] = home_sp
        away_dic['sp'] = away_sp
        
        home_start_idx = home_game_idx[:6] + '001'
        away_start_idx = away_game_idx[:6] + '001'
        
        
        
        
        def get_sp(start_idx,end_idx,sp_name):
            
            data_set = PitcherRecord.objects.filter(team_game_idx__gte = start_idx, team_game_idx__lt= end_idx, name = sp_name, po = 1)
            
            team_game_idx_values = data_set.values('team_game_idx')
            rp_set = PitcherRecord.objects.filter(team_game_idx__in=team_game_idx_values).exclude(po=1)
            sp_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__in= team_game_idx_values).prefetch_related('pitcherrecord').all()
            sp_list = list(sp_set)
            
            count = 0
            inn = 0
            fip = 0
            era = 0
            run = 0
            rp =0

            rp_fip = 0
            rp_inn = 0
            qs_count = 0
            er = 0
            if sp_list:
                count = len(sp_list) # sp_set.count()
                
                for sp in sp_list:
                    
                    team_game_idx = sp.team_game_idx #sp['team_game_idx_id']
                    #game_idx = TeamGameInfo.objects.filter(team_game_idx = team_game_idx).values()[0]['game_idx_id']
                    stadium = sp.game_idx.stadium#GameInfo.objects.filter(game_idx = game_idx).values()[0]['stadium']
                    
                    park_factor = park_factor_total.get(stadium)
                    if park_factor ==None: park_factor = 1
                    
                    new_fip = int(sp.pitcherrecord.fip)/park_factor          #int(sp['fip']) / park_factor
                    new_er = int(sp.pitcherrecord.er)/park_factor
                    new_inn = int(sp.pitcherrecord.inn)
                    fip += new_fip
                    er += new_er
                    
                    if (new_inn >= 6) & (sp.pitcherrecord.er <= 3):
                        qs_count+=1
                    
                    
                    new_run = int(sp.scorerecord.r)/park_factor #int(ScoreRecord.objects.filter(team_game_idx = team_game_idx).values()[0]['r']) / park_factor
                    run += new_run
                    
                    new_rp  = rp_set.filter(team_game_idx = team_game_idx)
                    new_rp_fip = sum(new_rp.values_list('fip',flat=True)) #sum(PitcherRecord.objects.filter(team_game_idx = team_game_idx).values_list('fip',flat=True)[1:])
                    new_rp_inn = sum(new_rp.values_list('inn',flat=True)) #sum(PitcherRecord.objects.filter(team_game_idx = team_game_idx).values_list('inn',flat=True)[1:])
                      
                    rp_fip += new_rp_fip
                    rp_inn += new_rp_inn
                
                inn= sum(data_set.values_list('inn',flat=True))
                
                er = sum(data_set.values_list('er',flat=True))
                
                    
                    
                if inn == 0:
                    fip = 99
                    era = 99
                else:
                    fip = round(fip / inn  +3.2, 2)
                    era = round(er / inn * 9, 2)
                    inn = round(inn / count,1)
                    
                if rp_inn == 0:
                    rp = 0
                else:
                    rp = (rp_fip / rp_inn) + 3.2
                qs_count = (qs_count / count) * 10
                run = round(run / count, 2)
                
                
                
                
                
            
                
            
            return [count, inn, fip, era, run, rp, qs_count]
        hsp = get_sp(home_start_idx, home_game_idx, home_sp)
        asp = get_sp(away_start_idx, away_game_idx, away_sp)
        
        
        
        
        
                
        home_dic['count'] = hsp[0]
        home_dic['inn'] = hsp[1]
        home_dic['fip'] = hsp[2]
        home_dic['era'] = hsp[3]
        home_dic['run'] = hsp[4]
        home_dic['rp'] = hsp[5]
        home_dic['qs'] = hsp[6]
        
        away_dic['count'] = asp[0]
        away_dic['inn'] = asp[1]
        away_dic['fip'] = asp[2]
        away_dic['era'] = asp[3]
        away_dic['run'] = asp[4]
        away_dic['rp'] = asp[5]
        away_dic['qs'] = asp[6]
        
      
                
            
        
        
        
        result_data = {'year':year, 'home_dic':home_dic,'away_dic':away_dic}

        return Response(result_data)
    


def preview(request,date,today_game_num):
    
    
    today_game_num_idx_min = (2*today_game_num)-2
    today_game_num_idx_max = (2*today_game_num)
    
    if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
        
        TGI = TodayTeamGameInfo
        GI = TodayGameInfo
        is_end = False
    else:
        
        TGI = TeamGameInfo
        GI = GameInfo
        is_end = True
    
    game_date_set = GI.objects.filter(game_idx__contains = str(date))
    today_game_idx_values = game_date_set.values("game_idx")
    
    
    team_game_set = TGI.objects.filter(game_idx__in = today_game_idx_values)
    today_game_set= team_game_set[today_game_num_idx_min:today_game_num_idx_max]

    
    home_dic = dict()
    away_dic = dict()
    
    year = str(date)[:4]
    stadium = game_date_set[today_game_num-1].stadium
    
    away_team_num = today_game_set[0].team_num
    home_team_num = today_game_set[1].team_num
    
    
    
    
    home_name = game_date_set[today_game_num-1].home_name
    away_name = game_date_set[today_game_num-1].away_name
    
    home_dic['name'] = home_name    
    away_dic['name'] = away_name
    
    
    away_game_idx = today_game_set[0].team_game_idx
    home_game_idx = today_game_set[1].team_game_idx

    
    home_dic['url'] = "/static/images/emblem_back/emblem_" + home_name + ".png"
    away_dic['url'] = "/static/images/emblem_back/emblem_" + away_name + ".png"
    
    home_dic['emb_url'] = "/static/images/emblem/emblem_" + home_name + ".png"
    away_dic['emb_url'] = "/static/images/emblem/emblem_" + away_name + ".png"

    
    home_start_game_idx = home_game_idx[:6] + '001'
    away_start_game_idx = away_game_idx[:6] + '001'

    home_pitcher_data = PitcherRecord.objects.select_related('team_game_idx').filter(team_game_idx__gte = home_start_game_idx)
    away_pitcher_data = PitcherRecord.objects.select_related('team_game_idx').filter(team_game_idx__gte = away_start_game_idx)

    if is_end:
        #home_pitcher_data = PitcherRecord.objects.filter(team_game_idx = home_game_idx)
        #away_pitcher_data = PitcherRecord.objects.filter(team_game_idx = away_game_idx)
        home_sp_name = home_pitcher_data.filter(team_game_idx = home_game_idx)[0].name
        away_sp_name = away_pitcher_data.filter(team_game_idx = away_game_idx)[0].name
    else:
        home_sp_name = TodayLineUp.objects.filter(team_game_idx=home_game_idx)[0].name
        away_sp_name = TodayLineUp.objects.filter(team_game_idx=away_game_idx)[0].name


    home_dic['sp'] = home_sp_name
    away_dic['sp'] = away_sp_name
        
    def get_recent_sp(sp_set, team_game_idx, sp_name, year, recent_count):
        team_name_dic = {2017:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2018:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2019:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2020:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2021:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2022:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2023:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2024:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         }
        
                         
        
        sp_set = sp_set.filter(team_game_idx__lt = team_game_idx, name = sp_name ,po = 1).all()
        
        if sp_set.exists():
            
            sp_count= sp_set.count()
            if sp_count >= recent_count:
                sp_count -= recent_count
            else:
                sp_count = 0
            recent_set = sp_set[sp_count:]
            
            
            
            for recent in recent_set:
                
                
                
                game_idx = recent.team_game_idx.game_idx
                foe_num = recent.team_game_idx.foe_num
                recent.date = str(game_idx)[21:25]
                foe_name = team_name_dic[int(year)][foe_num]
                recent.foe_name = foe_name 
                
                recent.foe_url = "/static/images/emblem/emblem_" + foe_name + ".png"
                inn = float(recent.inn)
                inn_round = inn//1
                inn_point = (inn%1)/3
                inn = inn_round + inn_point
                recent.ip = round(inn,1)
                
            
        else:
            recent_set = sp_set
        
        return recent_set
    
    
    home_sp_set = get_recent_sp( home_pitcher_data , home_game_idx, home_sp_name, year,3)
    away_sp_set = get_recent_sp( away_pitcher_data , away_game_idx, away_sp_name, year,3)
    
    
    home_game_num = int(today_game_set[1].game_num)
    away_game_num = int(today_game_set[0].game_num)
    

    
    #스코어 데이터 불러오기
    home_score_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = home_start_game_idx, team_game_idx__lt = home_game_idx)
    away_score_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = away_start_game_idx, team_game_idx__lt = away_game_idx)


    home_score_list = list(home_score_set)
    away_score_list = list(away_score_set)


    #상대팀 스코어 데이터 불러오기
    home_game_idx_list = [score.game_idx for score in home_score_list]
    away_game_idx_list = [score.game_idx for score in away_score_list]

    home_foe_score_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=home_game_idx_list)
    away_foe_score_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=away_game_idx_list)

    home_foe_score_list = list(home_foe_score_set)
    home_foe_score_list = [score for score in home_foe_score_list if score.team_num !=home_team_num]

    away_foe_score_list = list(away_foe_score_set)
    away_foe_score_list = [score for score in away_foe_score_list if score.team_num !=away_team_num]


    #최신값으로 변경
    recent_range = 7
    
    home_recent_game_num = 1 if home_game_num <= recent_range else home_game_num - recent_range
    away_recent_game_num = 1 if away_game_num <= recent_range else away_game_num - recent_range

    home_recent_score_list = home_score_list[home_recent_game_num-1:]
    away_recent_score_list = away_score_list[away_recent_game_num-1:]

    home_recent_foe_score_list = home_foe_score_list[home_recent_game_num-1:]
    away_recent_foe_score_list = away_foe_score_list[away_recent_game_num-1:]
    
    def get_recent(recent_list, recent_foe_list, game_num,game_idx,team_num):
        
        #range_idx_list = [recent.game_idx for recent in recent_list]
        #range_idx = recent_set.values('game_idx')
        #foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx_list).exclude(team_num= team_num)
        #foe_list = list(foe_set)
        
        
        
        
        for recent, foe in zip(recent_list, recent_foe_list):
            recent.stadium = recent.game_idx.stadium 
            recent.date = recent.game_idx.game_idx[4:8]
            
            
            home_name = recent.game_idx.home_name
            away_name = recent.game_idx.away_name
            recent.home_name = home_name
            recent.away_name = away_name
            recent.home_url = "/static/images/emblem/emblem_" + home_name + ".png"
            recent.away_url = "/static/images/emblem/emblem_" + away_name + ".png"
            
            team_run = recent.scorerecord.r 
            foe_run = foe.scorerecord.r
            
            if team_run > foe_run:
                result = '승'
            elif team_run == foe_run:
                result = '무'
            else:
                result= '패'
            recent.result = result
            
            if str(recent.home_away) =='home':

                recent.home_run = team_run
                recent.away_run = foe_run
                
                
            else:
                recent.home_run = foe_run
                recent.away_run = team_run
                
        return recent_list
    
    home_set = get_recent(home_recent_score_list, home_recent_foe_score_list, home_game_num, home_game_idx, home_team_num)
    away_set = get_recent(away_recent_score_list, away_recent_foe_score_list, away_game_num, away_game_idx, away_team_num)
    
    def get_relative(score_list, score_foe_list, game_idx, team_num, foe_num):
        
        
        #team_set = score_set.filter(foe_num = foe_num)
        #range_idx = team_set.values('game_idx')

        #range_idx_list = [score.game_idx for score in score_list if score.foe_num == foe_num]
        #foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx_list).exclude(team_num= team_num)

        foe_list = [score for score in score_foe_list if score.team_num == foe_num]
        win = 0
        lose = 0
        draw = 0
        for team, foe in zip(score_list, foe_list):
            tr = team.scorerecord.r
            fr = foe.scorerecord.r
            if tr > fr: win+=1
            elif tr <fr: lose+=1
            else: draw+=1

        if (win+lose) == 0:
            win_rate = 0
            win_rate = '{:,.3f}'.format(win_rate)
            home_rate = f'{win_rate}({win}-{draw}-{lose})'
            away_rate = f'{win_rate}({win}-{draw}-{lose})'
        else:
            win_rate = np.round(win/(win+lose),3)
            away_win_rate = 1-win_rate

            win_rate = '{:,.3f}'.format(win_rate)

            away_win_rate = '{:,.3f}'.format(away_win_rate)
            home_rate =  f'{win_rate}({win}-{draw}-{lose})'
            away_rate = f'{away_win_rate}({lose}-{draw}-{win})'
        return [home_rate, away_rate]
    
    rela = get_relative(home_score_list, home_foe_score_list, home_game_idx, home_team_num, away_team_num)
    home_dic['rela'] = rela[0]
    away_dic['rela'] = rela[1]
    


    def get_home_away(score_list, score_foe_list, game_idx,team_num,home_away):
        
        
        
        
        #team_set = score_set.filter(home_away = home_away)
        
        #range_idx = team_set.values('game_idx')
        #foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx).exclude(team_num= team_num)

        team_list = [score for score in score_list if score.home_away == home_away]
        foe_list = [score for score in score_foe_list if score.home_away == home_away]
        win = 0
        lose = 0
        draw = 0
        
        for team,foe in zip(team_list,foe_list):
            tr = team.scorerecord.r
            fr = foe.scorerecord.r
            if tr > fr: win+=1
            elif tr <fr: lose+=1
            else: draw+=1

        if (win+lose) == 0:
            win_rate = 0
        else:
            win_rate = np.round(win/(win+lose),3)

        result = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
        return result
    
    home_dic['home_away'] = get_home_away(home_score_list, home_foe_score_list, home_game_idx,home_team_num,'home')
    away_dic['home_away'] = get_home_away(away_score_list, away_foe_score_list, away_game_idx,away_team_num,'away')
    

    team_set = TeamInfo.objects.filter(year = year)
    def get_win_rate(team_set, team_num):
        team_set = team_set.filter(team_num = team_num)[0]
        win = team_set.win
        lose = team_set.lose
        draw = team_set.draw
        win_rate = team_set.win_rate
        result = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
        return result
    home_dic['win_rate'] = get_win_rate(team_set, home_team_num)
    away_dic['win_rate'] = get_win_rate(team_set, away_team_num)
    
    def get_rank(team_set, team_num):
        
        rank = 1
        last_win_rate = 0
        for i,team_year in enumerate(team_set):
            
            win_rate = team_year.win_rate
            if win_rate != last_win_rate:
                rank = i+1
                
            last_win_rate = win_rate
            
            if team_year.team_num == team_num:
                break
        return rank
    
    home_dic['rank'] = get_rank(team_set, home_team_num)
    away_dic['rank'] = get_rank(team_set, away_team_num)
    
    '''
    time = game_date_set[today_game_num-1].end
    
    def get_toto(date,time,away_name,home_name):
        if time =="경기종료":
            toto_set = TodayToTo.objects.filter(date = date, away_name = away_name, home_name = home_name)
        else:
            toto_set = TodayToTo.objects.filter(date = date, time = time, away_name = away_name, home_name = home_name)
        return toto_set.values()
    
    toto_set = get_toto(date,time,away_name,home_name).order_by('craw_time')
    '''
    
    def get_toto(date,away_name,home_name):
        
        toto_set = TodayToTo.objects.filter(date = date, away_name = away_name, home_name = home_name)
        return toto_set.values()
    
    toto_set = get_toto(date,away_name,home_name).order_by('craw_time')
    toto_list = [toto for toto in toto_set.values()]
    
    
    context ={'date':date,'today_game_num':today_game_num,'stadium':stadium, 'is_end':is_end, 'home_dic':home_dic,'away_dic':away_dic, 'home_set': home_set, 'away_set':away_set, 'home_sp_set':home_sp_set,'away_sp_set':away_sp_set,'toto_list':toto_list}
    return render(request,'baseball/preview.html',context)

def preview_old(request,date,today_game_num):
    
    
    today_game_num_idx_min = (2*today_game_num)-2
    today_game_num_idx_max = (2*today_game_num)
    
    if TodayGameInfo.objects.filter(game_idx__contains = str(date)).values():
        
        TGI = TodayTeamGameInfo
        GI = TodayGameInfo
        is_end = False
    else:
        
        TGI = TeamGameInfo
        GI = GameInfo
        is_end = True
    
    game_date_set = GI.objects.filter(game_idx__contains = str(date))
    today_game_idx = game_date_set.values("game_idx")
    
    
    team_game_set = TGI.objects.filter(game_idx__in = today_game_idx)
    today_game_set= team_game_set[today_game_num_idx_min:today_game_num_idx_max]
    
    
   
    
    
    home_dic = dict()
    away_dic = dict()
    
    year = str(date)[:4]
    stadium = game_date_set[today_game_num-1].stadium
    
    away_team_num = today_game_set[0].team_num
    home_team_num = today_game_set[1].team_num
    
    
    
    
    home_name = game_date_set[today_game_num-1].home_name
    away_name = game_date_set[today_game_num-1].away_name
    
    home_dic['name'] = home_name    
    away_dic['name'] = away_name
    
    
    away_game_idx = today_game_set[0].team_game_idx
    home_game_idx = today_game_set[1].team_game_idx
    
    
    
    
    
    home_dic['url'] = "/static/images/emblem_back/emblem_" + home_name + ".png"
    away_dic['url'] = "/static/images/emblem_back/emblem_" + away_name + ".png"
    
    home_dic['emb_url'] = "/static/images/emblem/emblem_" + home_name + ".png"
    away_dic['emb_url'] = "/static/images/emblem/emblem_" + away_name + ".png"

    
    if is_end:
        home_sp = PitcherRecord.objects.filter(team_game_idx = home_game_idx)[0].name
        away_sp = PitcherRecord.objects.filter(team_game_idx = away_game_idx)[0].name
    else:
        home_sp = TodayLineUp.objects.filter(team_game_idx=home_game_idx)[0].name
        away_sp = TodayLineUp.objects.filter(team_game_idx=away_game_idx)[0].name
    
    home_dic['sp'] = home_sp
    away_dic['sp'] = away_sp
    
    
    
    
    
    
    def get_recent_sp(game_idx, sp_name, year, recent_count):
        team_name_dic = {2017:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2018:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2019:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2020:[0, 'LG','롯데','KIA','삼성','두산','한화','SK','키움','NC','KT'],
                         2021:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2022:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2023:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT'],
                         2024:[0, 'LG','롯데','KIA','삼성','두산','한화','SSG','키움','NC','KT']
                         }
        
                         
        start_idx = game_idx[:6] + '001'
        sp_set = PitcherRecord.objects.select_related('team_game_idx').filter(team_game_idx__gte= start_idx, team_game_idx__lt = game_idx, name = sp_name ,po = 1).all()
        sp_list = list(sp_set)
        
        if sp_list:
            
            #sp_count= sp_set.count()
            sp_count = len(sp_list)
            if sp_count >= recent_count:
                sp_count -= recent_count
            else:
                sp_count = 0
            #recent_set = sp_set[sp_count:]
            
            recent_list = sp_list[sp_count:]
            
            for recent in recent_list:
                
                
                
                game_idx = recent.team_game_idx.game_idx
                foe_num = recent.team_game_idx.foe_num
                recent.date = str(game_idx)[21:25]
                foe_name = team_name_dic[int(year)][foe_num]
                recent.foe_name = foe_name 
                
                recent.foe_url = "/static/images/emblem/emblem_" + foe_name + ".png"
                inn = float(recent.inn)
                inn_round = inn//1
                inn_point = (inn%1)/3
                inn = inn_round + inn_point
                recent.ip = round(inn,1)
                
            
        else:
            #recent_set = sp_set
            recent_list = sp_list
        
        return recent_list
    
    
    home_sp_set = get_recent_sp(home_game_idx, home_sp, year,3)
    away_sp_set = get_recent_sp(away_game_idx, away_sp, year,3)
    
    
    home_game_num = int(today_game_set[1].game_num)
    away_game_num = int(today_game_set[0].game_num)
    
    
    
    
    
    def get_recent(game_num,game_idx,team_num, recent_range):
        
        if game_num <= recent_range :
            start_num = 1
        else:
            start_num = game_num - recent_range
        
        
        game_num = str(game_num)
        start_num = str(start_num).zfill(3)
        start_idx = game_idx[:6] + start_num
        
        recent_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = start_idx, team_game_idx__lt = game_idx).all()
        
        
        range_idx = recent_set.values('game_idx')
        foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx).exclude(team_num= team_num).all()
        
        recent_list = list(recent_set)
        foe_list = foe_set
        
        
        
        for recent, foe in zip(recent_list, foe_list):
            recent.stadium = recent.game_idx.stadium 
            recent.date = recent.game_idx.game_idx[4:8]
            
            
            home_name = recent.game_idx.home_name
            away_name = recent.game_idx.away_name
            recent.home_name = home_name
            recent.away_name = away_name
            recent.home_url = "/static/images/emblem/emblem_" + home_name + ".png"
            recent.away_url = "/static/images/emblem/emblem_" + away_name + ".png"
            
            team_run = recent.scorerecord.r 
            foe_run = foe.scorerecord.r
            
            if team_run > foe_run:
                result = '승'
            elif team_run == foe_run:
                result = '무'
            else:
                result= '패'
            recent.result = result
            
            if str(recent.home_away) =='home':

                recent.home_run = team_run
                recent.away_run = foe_run
                
                
            else:
                recent.home_run = foe_run
                recent.away_run = team_run
                
        return recent_set
    
    home_set = get_recent(home_game_num,home_game_idx,home_team_num,7)
    away_set = get_recent(away_game_num,away_game_idx,away_team_num,7)
    
    def get_relative(game_idx,team_num,foe_num):
        
        start_idx = game_idx[:6] + '001'
        
        team_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = start_idx, team_game_idx__lt = game_idx, foe_num = foe_num)
        
        range_idx = team_set.values('game_idx')
        foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx).exclude(team_num= team_num)
        win = 0
        lose = 0
        draw = 0
        for team, foe in zip(team_set,foe_set):
            tr = team.scorerecord.r
            fr = foe.scorerecord.r
            if tr > fr: win+=1
            elif tr <fr: lose+=1
            else: draw+=1

        if (win+lose) == 0:
            win_rate = 0
            home_rate = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
            away_rate = '{:,.3f}'.format(round(win_rate,3)) + '(' + str(lose) + '-' + str(draw) + '-' + str(win) + ')'
        else:
            win_rate = np.round(win/(win+lose),3)
            home_rate = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
            away_rate = '{:,.3f}'.format(round(1-win_rate,3)) + '(' + str(lose) + '-' + str(draw) + '-' + str(win) + ')'
        return [home_rate, away_rate]
    
    rela = get_relative(home_game_idx,home_team_num,away_team_num)
    home_dic['rela'] = rela[0]
    away_dic['rela'] = rela[1]
    
    def get_home_away(game_idx,team_num,home_away):
        
        
        start_idx = game_idx[:6] + '001'
        
        team_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = start_idx, team_game_idx__lt = game_idx,home_away = home_away)
        
        range_idx = team_set.values('game_idx')
        foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx).exclude(team_num= team_num)
        win = 0
        lose = 0
        draw = 0
        for team,foe in zip(team_set,foe_set):
            tr = team.scorerecord.r
            fr = foe.scorerecord.r
            if tr > fr: win+=1
            elif tr <fr: lose+=1
            else: draw+=1

        if (win+lose) == 0:
            win_rate = 0
        else:
            win_rate = np.round(win/(win+lose),3)

        result = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
        return result
    
    home_dic['home_away'] = get_home_away(home_game_idx,home_team_num,'home')
    away_dic['home_away'] = get_home_away(away_game_idx,away_team_num,'away')
    
    def get_win_rate(team_num,year):
        team_set = TeamInfo.objects.filter(year = year, team_num = team_num)[0]
        win = team_set.win
        lose = team_set.lose
        draw = team_set.draw
        win_rate = team_set.win_rate
        result = '{:,.3f}'.format(win_rate) + '(' + str(win) + '-' + str(draw) + '-' + str(lose) + ')'
        return result
    home_dic['win_rate'] = get_win_rate(home_team_num,year)
    away_dic['win_rate'] = get_win_rate(away_team_num,year)
    
    def get_rank(team_num,year):
        team_year_set = TeamInfo.objects.filter(year = year)
        rank = 1
        last_win_rate = 0
        for i,team_year in enumerate(team_year_set):
            
            win_rate = team_year.win_rate
            if win_rate != last_win_rate:
                rank = i+1
                
            last_win_rate = win_rate
            
            if team_year.team_num == team_num:
                break
        return rank
    
    home_dic['rank'] = get_rank(home_team_num,year)
    away_dic['rank'] = get_rank(away_team_num,year)
    
    '''
    time = game_date_set[today_game_num-1].end
    
    def get_toto(date,time,away_name,home_name):
        if time =="경기종료":
            toto_set = TodayToTo.objects.filter(date = date, away_name = away_name, home_name = home_name)
        else:
            toto_set = TodayToTo.objects.filter(date = date, time = time, away_name = away_name, home_name = home_name)
        return toto_set.values()
    
    toto_set = get_toto(date,time,away_name,home_name).order_by('craw_time')
    '''
    
    def get_toto(date,away_name,home_name):
        
        toto_set = TodayToTo.objects.filter(date = date, away_name = away_name, home_name = home_name)
        return toto_set.values()
    
    toto_set = get_toto(date,away_name,home_name).order_by('craw_time')
    toto_list = [toto for toto in toto_set.values()]
    
    
    context ={'date':date,'today_game_num':today_game_num,'stadium':stadium, 'is_end':is_end, 'home_dic':home_dic,'away_dic':away_dic, 'home_set': home_set, 'away_set':away_set, 'home_sp_set':home_sp_set,'away_sp_set':away_sp_set,'toto_list':toto_list}
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









#게시판 제네릭뷰
class PostListView(ListView):
    model = Post
    template_name = 'baseball/board/list.html'
    context_object_name = 'posts'

    



class PostDetailView(DetailView):
    model = Post
    template_name = 'baseball/board/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        current_user = self.request.user
        
        if post.user_id_id == current_user.id:
            context['edit_button'] = True
        else:
            context['edit_button'] = False

        return context

class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    template_name = 'baseball/board/create.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('baseball:board')
    def form_valid(self, form):
        
        form.instance.user_id = self.request.user # 현재 로그인된 사용자 정보를 추가합니다
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    
    model = Post
    template_name = 'baseball/board/update.html'
    fields = ['title', 'content']

    
    
    def test_func(self):
        
        post = self.get_object()
        current_user = self.request.user
        
        #print(self.request.user.is_authenticated)
        print(f"Is user authenticated? {self.request.user.is_authenticated}")
        
        # 게시글의 소유자와 현재 사용자를 비교
        print(f"Current user ID: {current_user.id}, Post user ID: {post.user_id_id}")
        return current_user.id == post.user_id_id

    def get_success_url(self):
        
        return reverse_lazy('baseball:board')

#    success_url = reverse_lazy('baseball:board')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'baseball/board/delete.html'
    success_url = reverse_lazy('baseball:board')