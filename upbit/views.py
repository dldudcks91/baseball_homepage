from django.shortcuts import render
from .models import Market, MarketInfo, MarketSupply
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Count, Max, Min

from datetime import datetime, timedelta, timezone
# Create your views here.
def index(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/index.html',context)
def trade_list(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/trade_list.html',context)

def trade_day(request):
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
    
    TEST_MINUTES= 0
    current_time = datetime(2025, 1, 23, 7, 36, 0, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_MINUTES)
    #current_time = datetime.now()
    last_1_time = get_current_time(current_time, -(1+TEST_MINUTES))
    last_3_time = get_current_time(current_time, -(3+TEST_MINUTES))
    last_5_time = get_current_time(current_time, -(5+TEST_MINUTES))
    last_10_time = get_current_time(current_time, -(10+TEST_MINUTES))
    last_30_time = get_current_time(current_time, -(30+TEST_MINUTES))
    last_60_time = get_current_time(current_time, -(60+TEST_MINUTES))
    last_240_time = get_current_time(current_time, -(240+TEST_MINUTES))
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0) - timedelta(hours=9),0)
    
    #시점데이터
    last_1_data = Market.objects.filter(log_dt = last_1_time).order_by('market')
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)

    #고점데이터
    today_high_low_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0, price__gt = 0).values('market').annotate(max_price = Max('price'), min_price = Min('price')).order_by('market')
    
    #거래량,거래대금
    last_1_sum_data = Market.objects.filter(log_dt__gte= last_1_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_5_sum_data = Market.objects.filter(log_dt__gte= last_5_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_10_sum_data = Market.objects.filter(log_dt__gte= last_10_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_60_sum_data = Market.objects.filter(log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_today_sum_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')

    # last_1_dict = {item['market']: item for item in last_1_sum_data}
    # last_5_dict = {item['market']: item for item in last_5_sum_data}
    # last_10_dict = {item['market']: item for item in last_10_sum_data}
    # last_60_dict = {item['market']: item for item in last_60_sum_data}


    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    # last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')

    
    
    

    # def get_volume_ratio(nu: dict, de: dict) -> float:
    #     if nu['cnt'] == 0:
    #         nu_mean = 0
    #     else:
    #         nu_mean = nu['total_volume'] / nu['cnt']

    #     if de['cnt'] ==0:
    #         de_mean = 0
    #     else:
    #         de_mean = de['total_volume'] / de['cnt']

        
    #     if de_mean == 0:
    #         return 0
    #     else:
    #         return (nu_mean / de_mean) -1

    
    
            



    

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


            'kimchi_premium':next((round(((d.price/d.price_foreign)-1)*100,2) if d.price_foreign !=0 else 0 for d in last_1_data if d.market == item.market), None),

            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            'price_today_high': next((d['max_price'] for d in today_high_low_data if d['market'] == item.market), None),
            'price_today_low': next((d['min_price'] for d in today_high_low_data if d['market'] == item.market), None),
            # 'ratio_1m_60m':get_volume_ratio(last_1_dict.get(item.market), last_60_dict.get(item.market)) if item.market in last_1_dict and item.market in last_60_dict else None,
            # 'ratio_5m_60m':get_volume_ratio(last_5_dict.get(item.market), last_60_dict.get(item.market)) if item.market in last_1_dict and item.market in last_60_dict else None,
            # 'ratio_10m_60m':get_volume_ratio(last_10_dict.get(item.market), last_60_dict.get(item.market)) if item.market in last_1_dict and item.market in last_60_dict else None,
            #next((get_volume_ratio(nu, de) for nu, de in zip(last_10_sum_data, last_60_sum_data) if de['market'] == item.market),None),
            
            'amount_1m': next((d['total_amount'] for d in last_1_sum_data if d['market'] == item.market), None),
            'amount_5m': next((d['total_amount'] for d in last_5_sum_data if d['market'] == item.market), None),
            'amount_10m': next((d['total_amount'] for d in last_10_sum_data if d['market'] == item.market), None),
            'amount_60m': next((d['total_amount'] for d in last_60_sum_data if d['market'] == item.market), None),
            'amount_today': next((d['total_amount'] for d in last_today_sum_data if d['market'] == item.market), None),

            'count_1m': next((d['cnt'] for d in last_1_sum_data if d['market'] == item.market), None),
            'count_5m': next((d['cnt'] for d in last_5_sum_data if d['market'] == item.market), None),
            'count_10m': next((d['cnt'] for d in last_10_sum_data if d['market'] == item.market), None),
            'count_60m': next((d['cnt'] for d in last_60_sum_data if d['market'] == item.market), None),
            'count_today': next((d['cnt'] for d in last_today_sum_data if d['market'] == item.market), None)

        }
        for item in market_info_list
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
    context = {
    # swing trading 관련 데이터
    }
    return render(request, 'upbit/trade_swing.html', context)

def trade_time(request):
    context = {
        # time trading 관련 데이터
    }
    return render(request, 'upbit/trade_time.html', context)