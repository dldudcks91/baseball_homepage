from django.shortcuts import render
from .models import Market, MarketHour, MarketInfo, MarketSupply
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
    return render(request,'upbit/index.html',context)
def trade_list(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/trade_list.html',context)

def get_current_time(current_time: datetime, modify_minutes: int) -> str:   
        '''
        현재시간 포맷에맞춰서 변화해주는 함수
        '''
        rounded_minutes = (current_time.minute)
        if modify_minutes < 0:
            rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) - timedelta(minutes = abs(modify_minutes))
        else:
            rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) + timedelta(minutes = abs(modify_minutes))
        
        return rounded_time

def trade_day(request):
    
    
    TEST_MINUTES= 0
    #current_time = datetime(2025, 1, 18, 14, 35, 0, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_MINUTES)
    current_time = datetime.now(tz = timezone.utc)
    last_1_time = get_current_time(current_time, -(1+TEST_MINUTES))
    last_3_time = get_current_time(current_time, -(3+TEST_MINUTES))
    last_5_time = get_current_time(current_time, -(5+TEST_MINUTES))
    last_10_time = get_current_time(current_time, -(10+TEST_MINUTES))
    last_30_time = get_current_time(current_time, -(30+TEST_MINUTES))
    last_60_time = get_current_time(current_time, -(60+TEST_MINUTES))
    last_240_time = get_current_time(current_time, -(240+TEST_MINUTES))
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0) - timedelta(hours=9),0)
    
    #시점데이터
    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)

    def calculate_rsi(price_list, period=14):
        if len(price_list) != 14:
            return None

        price_changes = [price_list[i] - price_list[i-1] for i in range(1, len(price_list))]
        gains = [change for change in price_changes if change > 0]
        losses = [abs(change) for change in price_changes if change < 0]

        avg_gain = sum(gains) / min(period, len(gains)) if len(gains) > 0 else 0
        avg_loss = sum(losses) / min(period, len(losses)) if len(losses) > 0 else 0

        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        else:
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
    def get_rsi_results(rsi_data):
        rsi_market_dic = defaultdict(lambda: defaultdict(float))
        for data in rsi_data:
            rsi_market_dic[data['market']][data['log_dt']] = data['price']
        
        rsi_results = {}
        for market, price_data in rsi_market_dic.items():
            price_list = [price for log_dt, price in sorted(price_data.items())]
            rsi = calculate_rsi(price_list)
            if rsi is not None:
                rsi_results[market] = rsi
        return rsi_results
    
    #rsi 5분봉
    rsi_5_time_list = [get_current_time(current_time, -(1 + i * 5)) for i in range(14)]
    rsi_5_data = Market.objects.filter(log_dt__in=rsi_5_time_list).values('market', 'log_dt', 'price').order_by('log_dt')
    rsi_5_results = get_rsi_results(rsi_5_data)

    #rsi 15분봉
    rsi_15_time_list = [get_current_time(current_time, -(1 + i * 15)) for i in range(14)]
    rsi_15_data = Market.objects.filter(log_dt__in=rsi_15_time_list).values('market', 'log_dt', 'price').order_by('log_dt')
    rsi_15_results = get_rsi_results(rsi_15_data)

    #rsi 60분봉
    rsi_60_time_list = [get_current_time(current_time, -(1 + i * 60)) for i in range(14)]
    rsi_60_data = Market.objects.filter(log_dt__in=rsi_60_time_list).values('market', 'log_dt', 'price').order_by('log_dt')
    rsi_60_results = get_rsi_results(rsi_60_data)
    
    

    

    # #딕셔너리로처리 -> next방식과 큰차이 없어서 잠궈놈
    # price_data = Market.objects.filter(log_dt__in = [last_1_time, last_5_time, last_30_time, last_60_time, last_240_time]).values('market','log_dt','price')
    # price_market_dic = {}
    # for data in price_data:
    #     if data['market'] not in price_market_dic:
    #         price_market_dic[data['market']] = {}
    #     price_market_dic[data['market']][data['log_dt']] = data

    
    #고점데이터
    today_high_low_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0, price__gt = 0).values('market').annotate(max_price = Max('price'), min_price = Min('price'))
    
    #거래량,거래대금
    last_1_sum_data = Market.objects.filter(log_dt__gte= last_1_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_5_sum_data = Market.objects.filter(log_dt__gte= last_5_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_10_sum_data = Market.objects.filter(log_dt__gte= last_10_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_60_sum_data = Market.objects.filter(log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_today_sum_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))



    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    # last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')

    market_info_list = MarketInfo.objects.all().order_by('symbol')
    market_supply_list = MarketSupply.objects.all().order_by('symbol')
    
    # #딕셔너리로처리 -> next방식과 큰차이 없어서 잠궈놈
    # volume_market_dic = {}
    # for data in market_info_list:
    #     volume_market_dic[data.market] = {
    #         'count': {}, 
    #         'sum': {}
    #     }

    # for time_data, log_dt in zip([last_1_sum_data, last_5_sum_data, last_10_sum_data, last_60_sum_data, last_today_sum_data], [last_1_time, last_5_time, last_30_time, last_60_time, last_240_time]):
    #     for row in time_data:
    #         market = row['market']
    #         if volume_market_dic.get(market) == None:
    #             continue
    #         volume_market_dic[market]['count'][log_dt] = row['cnt']
    #         volume_market_dic[market]['sum'][log_dt] = row['total_amount']
        

    

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


            'kimchi_premium':next((round(((d.price/d.price_foreign)-1)*100,2) if d.price_foreign !=0 else 0 for d in last_1_data if d.market == item.market), None),

            
            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            # 'price_1m': price_market_dic[item.market][last_1_time]['price'],
            # 'price_5m': price_market_dic[item.market][last_5_time]['price'],
            # 'price_60m': price_market_dic[item.market][last_60_time]['price'],
            # 'price_240m': price_market_dic[item.market][last_240_time]['price'],

            'price_today_high': next((d['max_price'] for d in today_high_low_data if d['market'] == item.market), None),
            'price_today_low': next((d['min_price'] for d in today_high_low_data if d['market'] == item.market), None),
            
            # 'amount_1m': volume_market_dic[item.market]['sum'].get(last_1_time, None),
            # 'amount_5m': volume_market_dic[item.market]['sum'].get(last_5_time, None),
            # 'amount_10m': volume_market_dic[item.market]['sum'].get(last_10_time, None), 
            # 'amount_60m': volume_market_dic[item.market]['sum'].get(last_60_time, None),
            # 'amount_today': volume_market_dic[item.market]['sum'].get(utc_00_time, None),

            # 'count_1m': volume_market_dic[item.market]['count'].get(last_1_time, None),
            # 'count_5m': volume_market_dic[item.market]['count'].get(last_5_time, None),
            # 'count_10m': volume_market_dic[item.market]['count'].get(last_10_time, None),
            # 'count_60m': volume_market_dic[item.market]['count'].get(last_60_time, None),
            # 'count_today': volume_market_dic[item.market]['count'].get(utc_00_time, None)


            'amount_1m': next((d['total_amount'] for d in last_1_sum_data if d['market'] == item.market), None),
            'amount_5m': next((d['total_amount'] for d in last_5_sum_data if d['market'] == item.market), None),
            'amount_10m': next((d['total_amount'] for d in last_10_sum_data if d['market'] == item.market), None),
            'amount_60m': next((d['total_amount'] for d in last_60_sum_data if d['market'] == item.market), None),
            'amount_today': next((d['total_amount'] for d in last_today_sum_data if d['market'] == item.market), None),

            'count_1m': next((d['cnt'] for d in last_1_sum_data if d['market'] == item.market), None),
            'count_5m': next((d['cnt'] for d in last_5_sum_data if d['market'] == item.market), None),
            'count_10m': next((d['cnt'] for d in last_10_sum_data if d['market'] == item.market), None),
            'count_60m': next((d['cnt'] for d in last_60_sum_data if d['market'] == item.market), None),
            'count_today': next((d['cnt'] for d in last_today_sum_data if d['market'] == item.market), None),
            'rsi_5m': rsi_5_results[item.market] if rsi_5_results.get(item.market) != None else 0,
            'rsi_15m': rsi_15_results[item.market] if rsi_15_results.get(item.market) != None else 0,
            'rsi_60m': rsi_60_results[item.market] if rsi_60_results.get(item.market) != None else 0

        }
        for item in market_info_list if item.market != 'KRW-BTC'
        ]

    #print(market_list)
    context = {'trade_day_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'upbit/trade_day.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'upbit/trade_day.html', context)



def trade_swing(request):
   
    
    TEST_HOURS= 0
    #current_time = datetime(2025, 1, 22, 17, 0, 3, tzinfo = timezone.utc)
    current_time = datetime.now(tz = timezone.utc).replace(minute= 0, second = 0)
    current_hour = current_time.replace(minute =0, second= 0)
    
    last_1_time = get_current_time(current_time, -(1+TEST_HOURS))
    last_day_time = get_current_time(current_hour, -((24 * 1) + TEST_HOURS)*60)
    last_3days_time = get_current_time(current_hour, -((24 * 3) + TEST_HOURS)*60)
    last_week_time = get_current_time(current_hour, -((24 * 7) + TEST_HOURS)*60)
    last_month_time = get_current_time(current_hour, -((24 * 28) + TEST_HOURS)*60)
    
    #시점데이터
    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_day_data = MarketHour.objects.filter(log_dt = last_day_time)
    last_3days_data = MarketHour.objects.filter(log_dt = last_3days_time)
    last_week_data = MarketHour.objects.filter(log_dt = last_week_time)
    last_month_data = MarketHour.objects.filter(log_dt = last_month_time)

    #고점데이터
    high_low_data = MarketHour.objects.filter(log_dt__gte= last_month_time, volume__gt = 0, low_price__gt = 0).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))
    
    #거래량,거래대금
    
    last_day_sum_data = MarketHour.objects.filter(log_dt__gte= last_day_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_3days_sum_data = MarketHour.objects.filter(log_dt__gte= last_3days_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_week_sum_data = MarketHour.objects.filter(log_dt__gte= last_week_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    last_month_sum_data = MarketHour.objects.filter(log_dt__gte= last_month_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume'))
    market_info_list = MarketInfo.objects.all().order_by('symbol')
    market_supply_list = MarketSupply.objects.all().order_by('symbol')
    
    def calculate_rsi(price_list, period=14):
        if len(price_list) != 14:
            return None

        price_changes = [price_list[i] - price_list[i-1] for i in range(1, len(price_list))]
        gains = [change for change in price_changes if change > 0]
        losses = [abs(change) for change in price_changes if change < 0]

        avg_gain = sum(gains) / min(period, len(gains)) if len(gains) > 0 else 0
        avg_loss = sum(losses) / min(period, len(losses)) if len(losses) > 0 else 0

        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        else:
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
    def get_rsi_results(rsi_data):
        rsi_market_dic = defaultdict(lambda: defaultdict(float))
        for data in rsi_data:
            rsi_market_dic[data['market']][data['log_dt']] = data['trade_price']
        
        rsi_results = {}
        for market, price_data in rsi_market_dic.items():
            price_list = [price for log_dt, price in sorted(price_data.items())]
            rsi = calculate_rsi(price_list)
            if rsi is not None:
                rsi_results[market] = rsi
        return rsi_results
    
    #rsi 4시간봉
    rsi_240_time_list = [get_current_time(current_hour, -(i * 60)) for i in range(14)]
    rsi_240_data = MarketHour.objects.filter(log_dt__in=rsi_240_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_240_results = get_rsi_results(rsi_240_data)

    #rsi 1일봉
    rsi_day_time_list = [get_current_time(current_hour, -(i * 60 * 24)) for i in range(14)]
    rsi_day_data = MarketHour.objects.filter(log_dt__in=rsi_day_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_day_results = get_rsi_results(rsi_day_data)

    #rsi 3일봉
    rsi_3days_time_list = [get_current_time(current_hour, -(i * 60 * 72)) for i in range(14)]
    rsi_3days_data = MarketHour.objects.filter(log_dt__in=rsi_3days_time_list).values('market', 'log_dt', 'trade_price').order_by('log_dt')
    rsi_3days_results = get_rsi_results(rsi_3days_data)


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


            'kimchi_premium':next((round(((d.price/d.price_foreign)-1)*100,2) if d.price_foreign !=0 else 0 for d in last_1_data if d.market == item.market), None),

            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_day': next((d.trade_price for d in last_day_data if d.market == item.market), None),
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
        for item in market_info_list if item.market != 'KRW-BTC'
        ]

    #print(market_list)
    context = {'trade_swing_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'upbit/trade_swing.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'upbit/trade_swing.html', context)


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
            FROM upbit.tb_market_hour
            
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
        for item in market_info_list if item.market != 'KRW-BTC'
        ]
    context = {'trade_timetable_data': market_list
        # time trading 관련 데이터
    }
    
    
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'upbit/trade_timetable.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
            })
            
        return render(request, 'upbit/trade_timetable.html', context)
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)