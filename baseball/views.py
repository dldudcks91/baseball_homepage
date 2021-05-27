
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
    
    context = {'game_date_set':game_date_set,'is_end':is_end, 'data_length':data_length}
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
            
            TGI = TodayTeamGameInfo
            GI = TodayGameInfo
            
        else:
            
            TGI = TeamGameInfo
            GI = GameInfo
            
        
        game_date_set = GI.objects.filter(game_idx__contains = str(date))
        today_game_idx = game_date_set.values("game_idx")
        
        team_game_set = TGI.objects.filter(game_idx__in = today_game_idx).order_by('game_idx','home_away')
        today_game_set = team_game_set[today_game_num_idx_min:today_game_num_idx_max]
        
        
        
        year = int(str(date)[:4])
        
        home_team_num = today_game_set[1].team_num
        away_team_num = today_game_set[0].team_num
        
        home_name = game_date_set[today_game_num-1].home_name
        away_name = game_date_set[today_game_num-1].away_name
        
        home_game_num = today_game_set[1].game_num
        away_game_num = today_game_set[0].game_num
              
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
        home_rp_5 = list()
        home_rp_20 = list()
        
        away_run_5 = list()
        away_run_20 = list()
        away_rp_5 = list()
        away_rp_20 = list()
        for run in home_team_dic:
        
            home_run_5.append([run['game_num'],run['run_5']])
            home_run_20.append([run['game_num'],run['run_20']])
            home_rp_5.append([run['game_num'],run['rp_fip_5']])
            home_rp_20.append([run['game_num'],run['rp_fip_20']])
        for run in away_team_dic:
            away_run_5.append([run['game_num'],run['run_5']])
            away_run_20.append([run['game_num'],run['run_20']])
            away_rp_5.append([run['game_num'],run['rp_fip_5']])
            away_rp_20.append([run['game_num'],run['rp_fip_20']])
        
        '''
        end_idx = today_game_set[1].team_game_idx
        start_idx = end_idx[:6] + '001'
        data_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = start_idx, team_game_idx__lt = end_idx)
        rp_set = PitcherRecord.objects.filter(team_game_idx__gte = start_idx, team_game_idx__lt = end_idx).exclude(po=1)
        data_q= data_set.values()
        park_factor_total = {'잠실': 0.854,'사직': 1.099,'광주':1.003, '대구': 1.153, '대전': 0.977,'문학':1.046,'고척':0.931,'창원':1.051,'수원':1.032}
        
        
        
        for i, data in enumerate(data_set):
            pass
            
            team_game_idx = data.team_game_idx
            
            stadium = data.game_idx.stadium
            data.stadium = stadium
            park_factor = park_factor_total.get(stadium)
            
            if park_factor ==None: park_factor = 0
            run = data.scorerecord.r
            
            rp_fip = sum(rp_set.filter(team_game_idx = team_game_idx).values_list('fip',flat=True))
            rp_inn = sum(rp_set.filter(team_game_idx = team_game_idx).values_list('inn',flat=True))
        '''
        
        
        
        
        
        
        
        result_data = {'year':year, 'home_name': home_name, 'away_name':away_name, 'home_run_dist': home_run_dist, 'away_run_dist': away_run_dist, 
                       'home_run_5':home_run_5, 'home_run_20':home_run_20,'away_run_5':away_run_5, 'away_run_20':away_run_20,
                       'home_rp_5':home_rp_5, 'home_rp_20':home_rp_20,'away_rp_5':away_rp_5,'away_rp_20':away_rp_20}
        
        
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
        
        
        
        '''
        def get_sp(start_idx,end_idx,sp_name):
            
            data_set = PitcherRecord.objects.filter(team_game_idx__gte = start_idx, team_game_idx__lt= end_idx, name = sp_name, po = 1)
            
            team_game_idx = data_set.values('team_game_idx')
            rp_set = PitcherRecord.objects.filter(team_game_idx__in=team_game_idx).exclude(po=1)
            sp_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__in= team_game_idx).prefetch_related('pitcherrecord')
            
            
            if sp_set.exists():
                count = sp_set.count()
                fip = 0
                er = 0
                run = 0
                rp_fip = 0
                rp_inn = 0
                qs_count = 0
                for i, sp in enumerate(sp_set):
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
                    
                    if (new_inn >= 6) & (new_er <= 3):
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
                if rp_inn == 0:
                    rp_fip = 0
                    
                    
                if inn == 0:
                    fip = 99
                    era = 99
                else:
                    fip = round(fip / inn  +3.2, 2)
                    era = round(er / inn * 9, 2)
                    inn = round(inn / count,1)
                    
                rp = rp_fip / rp_inn + 3.2
                qs = qs_count / count * 10
                run = round(run / count, 2)
                
                
                
                
                
            else:
                count = 0
                inn = 0
                fip = 0
                era= 0
                run = 0
                rp = 0
                qs = 0
                
            
            return [count, inn, fip, era, run, rp, qs]
        hsp = get_sp(home_start_idx, home_game_idx, home_sp)
        asp = get_sp(away_start_idx, away_game_idx, away_sp)
        '''
        hsp = [1,1,1,1,1,1,1]
        asp = [2,2,2,2,2,2,2]
        
        
        
        
                
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
    today_game_idx = game_date_set.values("game_idx")
    
    
    team_game_set = TGI.objects.filter(game_idx__in = today_game_idx).order_by('game_idx','home_away')
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
    
    
    
    
    
    
    def get_recent_sp(game_idx, sp_name, year):
        start_idx = game_idx[:6] + '001'
        sp_set = PitcherRecord.objects.select_related('team_game_idx').filter(team_game_idx__gte= start_idx, team_game_idx__lt = game_idx, name = sp_name ,po = 1).all()
        
        if sp_set.exists():
            
            sp_count= sp_set.count()
            if sp_count >= 3:
                sp_count -= 3
            else:
                sp_count = 0
            recent_set = sp_set[sp_count:]
            
            
            
            for i, recent in enumerate(recent_set):
                
                
                
                game_idx = recent.team_game_idx.game_idx
                foe_num = recent.team_game_idx.foe_num
                recent.date = str(game_idx)[21:25]
                foe_name = TeamInfo.objects.filter(year = year, team_num = foe_num)[0].team_name
                recent.foe_name = foe_name 
                
                recent.foe_url = "/static/images/emblem/emblem_" + foe_name + ".png"
                inn = float(recent.inn)
                inn_round = round(inn)
                inn_point = (inn%1)/3
                inn = inn_round + inn_point
                recent.ip = round(inn,1)
                
            
        else:
            recent_set = sp_set
        
        return recent_set
    
    
    home_sp_set = get_recent_sp(home_game_idx, home_sp, year)
    away_sp_set = get_recent_sp(away_game_idx, away_sp, year)
    
    
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
        
        recent_set = TeamGameInfo.objects.select_related('game_idx','scorerecord').filter(team_game_idx__gte = start_idx, team_game_idx__lt = game_idx)
        
        
        range_idx = recent_set.values('game_idx')
        foe_set = TeamGameInfo.objects.select_related('scorerecord').filter(game_idx__in=range_idx).exclude(team_num= team_num)
        
        
        
        
        for i, recent in enumerate(recent_set):
            recent.stadium = recent.game_idx.stadium 
            recent.date = recent.game_idx.game_idx[4:8]
            
            
            home_name = recent.game_idx.home_name
            away_name = recent.game_idx.away_name
            recent.home_name = home_name
            recent.away_name = away_name
            recent.home_url = "/static/images/emblem/emblem_" + home_name + ".png"
            recent.away_url = "/static/images/emblem/emblem_" + away_name + ".png"
            
            team_run = recent.scorerecord.r 
            foe_run = foe_set[i].scorerecord.r
            
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
    
    
    
    
    
    context ={'date':date,'today_game_num':today_game_num,'stadium':stadium, 'home_dic':home_dic,'away_dic':away_dic, 'home_set': home_set, 'away_set':away_set, 'home_sp_set':home_sp_set,'away_sp_set':away_sp_set}
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

