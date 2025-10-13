from django.shortcuts import render
from .models import Market, MarketHour, MarketDay, MarketInfo, MADays, MA60Minutes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import DateTimeField, ExpressionWrapper, IntegerField
from django.db.models import Sum, F, Count, Max, Min
from django.db.models.functions import TruncHour, ExtractHour, Floor, TruncDate
from django.db.models.expressions import F
from django.db import connection
from collections import defaultdict
from datetime import datetime, timedelta, timezone
# Create your views here.
def index(request):
    context = {'index': 'Hello'}
    return render(request,'bithumb/index.html',context)
def trade_list(request):
    context = {'index': 'Hello'}
    return render(request,'bithumb/trade_list.html',context)
def trade_info(request):

    market_info_list = MarketInfo.objects.all().order_by('symbol')
    market_supply_list = MarketSupply.objects.all().order_by('symbol')
    market_list = [
        {
            'market': item.market[4:],
            'korean_name':item.korean_name,
            'english_name':item.english_name,
            'issue_month': item.issue_month,
            'listing_month': item.listing_month,

            'capitalization':next((d.capitalization for d in market_supply_list if d.symbol == item.symbol), None),
            'max_supply':next((d.max_supply for d in market_supply_list if d.symbol == item.symbol), None),
            'now_supply':next((d.now_supply for d in market_supply_list if d.symbol == item.symbol), None),
            'chain': item.chain,
            'category': item.category,
            'focus': item.focus,
            'country': item.country,
            'description': item.description
            


            

        }
        for item in market_info_list
        ]
    context = {'trade_info_data': market_list}

    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_info.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    return render(request,'bithumb/trade_info.html',context)

def get_current_time(current_time: datetime, modify_seconds: int) -> str:   
    '''
    현재시간을 10초 단위로 맞춰서 변화해주는 함수
    '''
    # 10초 단위로 내림
    rounded_seconds = (current_time.second // 10) * 10
    
    # 기본 시간 설정 (초만 변경)
    base_time = current_time.replace(
        second=rounded_seconds, 
        microsecond=0
    )
    
    # 양수/음수에 따라 시간 조정
    if modify_seconds < 0:
        adjusted_time = base_time - timedelta(seconds=abs(modify_seconds))
    else:
        adjusted_time = base_time + timedelta(seconds=abs(modify_seconds))
    
    return adjusted_time


def trade_day(request):
    
    
    TEST_SECONDS= 0
    #current_time = datetime(2025, 2, 11, 23, 14, 41, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_SECONDS)
    current_time = datetime.now(tz = timezone.utc)
    #current_time = datetime(2025, 2, 12, 8, 1, 33, tzinfo = timezone.utc)
    last_time = get_current_time(current_time, -(10 + TEST_SECONDS))
    last_1_time = get_current_time(current_time, -(10 + 60 + TEST_SECONDS))
    last_5_time = get_current_time(current_time, -(10 + 300 + TEST_SECONDS))
    last_10_time = get_current_time(current_time, -(10 + 600 + TEST_SECONDS))
    last_30_time = get_current_time(current_time, -(10 + 1800 + TEST_SECONDS))
    last_60_time = get_current_time(current_time, -(10 + 3600 + TEST_SECONDS))
    last_240_time = get_current_time(current_time, -(10 + 14400 + TEST_SECONDS))
    last_1440_time = get_current_time(current_time, -(10 + 86400 +TEST_SECONDS))
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0),0)
    
    #시점데이터
    last_data = Market.objects.filter(log_dt = last_time)
    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)

    

    
    #고점데이터
    today_high_low_data = Market.objects.filter(log_dt__gte= utc_00_time).values('market').annotate(max_price = Max('price'), min_price = Min('price'))
    
    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    # last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    
    
    last_hour = (last_time.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    last_day = (last_time- timedelta(days=1)).date()
    
    ma_60_data = MA60Minutes.objects.filter(log_dt = last_hour).order_by('market')
    ma_day_data = MADays.objects.filter(date = last_day).order_by('market')

    print(last_hour, last_day)
    print(last_data, ma_60_data, ma_day_data)


    market_info_list = MarketInfo.objects.all().order_by('market')
    
    market_list = [
        {
            'market': item.market[4:],
            # 'korean_name':item.korean_name,
            # 'english_name':item.english_name,
            # 'issue_month': item.issue_month,
            # 'listing_month': item.listing_month,

            # 'capitalization':next((d.capitalization for d in market_supply_list if d.symbol == item.symbol), None),
            # 'max_supply':next((d.max_supply for d in market_supply_list if d.symbol == item.symbol), None),
            # 'now_supply':next((d.now_supply for d in market_supply_list if d.symbol == item.symbol), None),


            # 'kimchi_premium': next((d.price_foreign for d in last_data if d.market == item.market), None),

            'price_last': next((d.price for d in last_data if d.market == item.market), None),
            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            

            'price_today_high': next((d['max_price'] for d in today_high_low_data if d['market'] == item.market), None),
            'price_today_low': next((d['min_price'] for d in today_high_low_data if d['market'] == item.market), None),
            
            'ma_60_10': next((d.ma_10 for d in ma_60_data if d.market == item.market), None),
            'ma_60_20': next((d.ma_20 for d in ma_60_data if d.market == item.market), None),
            'ma_60_34': next((d.ma_34 for d in ma_60_data if d.market == item.market), None),
            'ma_60_50': next((d.ma_50 for d in ma_60_data if d.market == item.market), None),
            'ma_60_100': next((d.ma_100 for d in ma_60_data if d.market == item.market), None),
            'ma_60_200': next((d.ma_200 for d in ma_60_data if d.market == item.market), None),
            'ma_60_400': next((d.ma_400 for d in ma_60_data if d.market == item.market), None),
            'ma_60_800': next((d.ma_800 for d in ma_60_data if d.market == item.market), None),

            'ma_day_10': next((d.ma_10 for d in ma_day_data if d.market == item.market), None),
            'ma_day_20': next((d.ma_20 for d in ma_day_data if d.market == item.market), None),
            'ma_day_34': next((d.ma_34 for d in ma_day_data if d.market == item.market), None),
            'ma_day_50': next((d.ma_50 for d in ma_day_data if d.market == item.market), None),
            'ma_day_100': next((d.ma_100 for d in ma_day_data if d.market == item.market), None),
            'ma_day_200': next((d.ma_200 for d in ma_day_data if d.market == item.market), None),
            
            
            

            # 'amount_1m': next((d['total_amount'] for d in last_1_sum_data if d['market'] == item.market), None),
            # 'amount_5m': next((d['total_amount'] for d in last_5_sum_data if d['market'] == item.market), None),
            # 'amount_10m': next((d['total_amount'] for d in last_10_sum_data if d['market'] == item.market), None),
            # 'amount_60m': next((d['total_amount'] for d in last_60_sum_data if d['market'] == item.market), None),
            # 'amount_1440m': next((d['total_amount'] for d in last_1440_sum_data if d['market'] == item.market), None),
            # 'amount_today': next((d['total_amount'] for d in last_today_sum_data if d['market'] == item.market), None),

            # 'count_1m': next((d['cnt'] for d in last_1_sum_data if d['market'] == item.market), None),
            # 'count_5m': next((d['cnt'] for d in last_5_sum_data if d['market'] == item.market), None),
            # 'count_10m': next((d['cnt'] for d in last_10_sum_data if d['market'] == item.market), None),
            # 'count_60m': next((d['cnt'] for d in last_60_sum_data if d['market'] == item.market), None),
            # 'count_1440m': next((d['cnt'] for d in last_1440_sum_data if d['market'] == item.market), None),
            # 'count_today': next((d['cnt'] for d in last_today_sum_data if d['market'] == item.market), None),

        }
        for item in market_info_list
        ]

    print(market_list[0])
    context = {'trade_day_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_day.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'bithumb/trade_day.html', context)



def trade_swing(request):
   
    
    TEST_HOURS= 0
    #current_time = datetime(2025, 2, 12, 8, 1, 33, tzinfo = timezone.utc)
    #current_time = datetime(2025, 2, 7, 2, 56, 3, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_SECONDS)
    current_time = datetime.now(tz = timezone.utc)
    current_hour = current_time.replace(minute =0, second= 0)
    
    last_time = get_current_time(current_time, -(10 + TEST_HOURS))
    last_day_time = get_current_time(current_hour, -((24 * 1) + TEST_HOURS)*3600)
    last_3days_time = get_current_time(current_hour, -((24 * 3) + TEST_HOURS)*3600)
    last_week_time = get_current_time(current_hour, -((24 * 7) + TEST_HOURS)*3600)
    last_month_time = get_current_time(current_hour, -((24 * 28) + TEST_HOURS)*3600)
    
    
    #시점데이터
    last_1_data = Market.objects.filter(log_dt = last_time)
    last_day_data = MarketHour.objects.filter(log_dt = last_day_time)
    last_3days_data = MarketHour.objects.filter(log_dt = last_3days_time)
    last_week_data = MarketHour.objects.filter(log_dt = last_week_time)
    last_month_data = MarketHour.objects.filter(log_dt = last_month_time)

    #고점데이터
    high_low_data = MarketHour.objects.filter(log_dt__gte= last_month_time, low_price__gt = 0).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))
    
    #거래량,거래대금
    
    last_day_sum_data = MarketHour.objects.filter(log_dt__gte= last_day_time).values('market').annotate(total_amount = Sum('amount'), cnt = Count('amount'))
    last_3days_sum_data = MarketHour.objects.filter(log_dt__gte= last_3days_time).values('market').annotate(total_amount = Sum('amount'), cnt = Count('amount'))
    last_week_sum_data = MarketHour.objects.filter(log_dt__gte= last_week_time).values('market').annotate(total_amount = Sum('amount'), cnt = Count('amount'))
    last_month_sum_data = MarketHour.objects.filter(log_dt__gte= last_month_time).values('market').annotate(total_amount = Sum('amount'), cnt = Count('amount'))
    market_info_list = MarketInfo.objects.all().order_by('symbol')
    market_supply_list = MarketSupply.objects.all().order_by('symbol')
    
    #rsi 구하기
    RSI_PERIOD = 15

    #rsi 4시간봉
    rsi_240_time_list = [get_current_time(current_hour, -(i * 60 * 4)) for i in range(RSI_PERIOD)]
    rsi_240_data = MarketHour.objects.filter(log_dt__in=rsi_240_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_240_results = get_rsi_results_swing(rsi_240_data)

    
    
    

    #rsi 1일봉
    rsi_day_time_list = [get_current_time(current_hour, -(i * 60 * 24)) for i in range(RSI_PERIOD)]
    rsi_day_data = MarketHour.objects.filter(log_dt__in=rsi_day_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_day_results = get_rsi_results_swing(rsi_day_data)
    
    
    #rsi 3일봉
    rsi_3days_time_list = [get_current_time(current_hour, -(i * 60 * 72)) for i in range(RSI_PERIOD)]
    rsi_3days_data = MarketHour.objects.filter(log_dt__in=rsi_3days_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_3days_results = get_rsi_results_swing(rsi_3days_data)


    market_list = [
        {
            'market': item.market[4:],
            'korean_name':item.korean_name,
            'english_name':item.english_name,
            'issue_month': item.issue_month,
            'listing_month': item.listing_month,

            'capitalization':next((d.capitalization for d in market_supply_list if d.symbol == item.symbol), None),
            'max_supply':next((d.max_supply for d in market_supply_list if d.symbol == item.symbol), None),
            'now_supply':next((d.now_supply for d in market_supply_list if d.symbol == item.symbol), None),


            'kimchi_premium':next((round(((d.price/d.price_foreign)-1)*100,2) if (d.price !=None) & (d.price_foreign != None) else 0 for d in last_1_data if d.market == item.market), None),

            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_day': next((d.trade_price for d in last_day_data if d.market == item.market), None),
            'price_3days': next((d.trade_price for d in last_3days_data if d.market == item.market), None),
            'price_week': next((d.trade_price for d in last_week_data if d.market == item.market), None),
            'price_month': next((d.trade_price for d in last_month_data if d.market == item.market), None),
            'price_high': next((d['max_price'] for d in high_low_data if d['market'] == item.market), None),
            'price_low': next((d['min_price'] for d in high_low_data if d['market'] == item.market), None),
            
            
            'amount_day': next((d['total_amount'] for d in last_day_sum_data if d['market'] == item.market), None),
            'amount_3days': next((d['total_amount'] for d in last_3days_sum_data if d['market'] == item.market), None),
            'amount_week': next((d['total_amount'] for d in last_week_sum_data if d['market'] == item.market), None),
            'amount_month': next((d['total_amount'] for d in last_month_sum_data if d['market'] == item.market), None),

            
            'count_day': next((d['cnt'] for d in last_day_sum_data if d['market'] == item.market), None),
            'count_3days': next((d['cnt'] for d in last_3days_sum_data if d['market'] == item.market), None),
            'count_week': next((d['cnt'] for d in last_week_sum_data if d['market'] == item.market), None),
            'count_month': next((d['cnt'] for d in last_month_sum_data if d['market'] == item.market), None),
            
            'rsi_240m': rsi_240_results[item.market] if rsi_240_results.get(item.market) != None else 0,
            'rsi_day': rsi_day_results[item.market] if rsi_day_results.get(item.market) != None else 0,
            'rsi_3days': rsi_3days_results[item.market] if rsi_3days_results.get(item.market) != None else 0

        }
        for item in market_info_list
        ]

    #print(market_list)
    context = {'trade_swing_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_swing.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'bithumb/trade_swing.html', context)


@csrf_exempt
def trade_timetable(request):

    HOURS_LEN = 12
    TEST_HOURS= 0
    #current_time = datetime(2025, 1, 23, 17, 0, 3, tzinfo = timezone.utc)
    current_time = datetime.now(tz = timezone.utc).replace(minute= 0, second = 0)

    current_hour = current_time.replace(minute =0, second= 0)
    last_1_time = get_current_time(current_time, -(1+TEST_HOURS))
    #시점데이터
    last_1_data = Market.objects.filter(log_dt = last_1_time)


    parameter_hour = int(request.POST.get('hours', 0))
    group_interval = parameter_hour
    hours_gap = parameter_hour * HOURS_LEN
    min_hour = current_hour - timedelta(hours = hours_gap)
    

    

    with connection.cursor() as cursor:
        sql = """
            WITH RAW_DATA as (
            SELECT 
                market,
                log_dt,
                (ROW_NUMBER() OVER (PARTITION BY market ORDER BY log_dt desc) -1) DIV %s AS row_num ,
                amount
            FROM bithumb.tb_market_hour
            
            )
            SELECT market, 
                row_num,
                
                SUM(amount) as total_amount
            FROM RAW_data
            
            WHERE log_dt >= %s
            GROUP BY market, row_num
            ORDER BY market, row_num
            
            """
        cursor.execute(sql, [parameter_hour, min_hour])
        hour_data = cursor.fetchall()


    market_info_list = MarketInfo.objects.all().order_by('symbol')

    market_list = [
        {
            'market': item.market[4:],
            'korean_name':item.korean_name,
            'price_1m': next((d.price for d in last_1_data if (d.market == item.market)), None),

            'd0': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 0)), None),
            'd1': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 1)), None),
            'd2': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 2)), None),
            'd3': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 3)), None),
            'd4': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 4)), None),
            'd5': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 5)), None),
            'd6': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 6)), None),
            'd7': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 7)), None),
            'd8': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 8)), None),
            'd9': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 9)), None),
            'd10': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 10)), None),
            'd11': next((d[2] for d in hour_data if (d[0] == item.market) & (d[1] == 11)), None),
            


            

            
            

        }
        for item in market_info_list
        ]
    context = {'trade_timetable_data': market_list
        # time trading 관련 데이터
    }
    
    
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_timetable.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
            })
            
        return render(request, 'bithumb/trade_timetable.html', context)
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    