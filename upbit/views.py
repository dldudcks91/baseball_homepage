from django.shortcuts import render
from .models import Market, MarketInfo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Count

from datetime import datetime, timedelta
# Create your views here.
def index(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/index.html',context)

def market_data(request):
    def get_current_time(current_time: datetime, modify_minutes: int) -> str:   
        '''
        현재시간 포맷에맞춰서 변화해주는 함수
        '''
        rounded_minutes = (current_time.minute)
        if modify_minutes < 0:
            rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) - timedelta(minutes = abs(modify_minutes))
        else:
            rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) + timedelta(minutes = abs(modify_minutes))
        formatted_time = rounded_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    
    last_1_time = get_current_time(datetime.now(), -1)
    last_3_time = get_current_time(datetime.now(), -3)
    last_5_time = get_current_time(datetime.now(), -5)
    last_10_time = get_current_time(datetime.now(), -10)
    last_30_time = get_current_time(datetime.now(), -30)
    last_60_time = get_current_time(datetime.now(), -60)
    last_240_time = get_current_time(datetime.now(), -240)
    
    last_1_sum_data = Market.objects.filter(log_dt__gte= last_1_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_3_sum_data = Market.objects.filter(log_dt__gte= last_3_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_5_sum_data = Market.objects.filter(log_dt__gte= last_5_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_10_sum_data = Market.objects.filter(log_dt__gte= last_10_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_60_sum_data = Market.objects.filter(log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')

    def get_volume_ratio(nu: dict, de: dict) -> float:
        if nu['cnt'] == 0:
            nu_mean = 0
        else:
            nu_mean = nu['total_volume'] / nu['cnt']

        if de['cnt'] ==0:
            de_mean = 0
        else:
            de_mean = de['total_volume'] / de['cnt']

        if de_mean == 0:
            return 0
        else:
            return nu_mean / de_mean

    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)
    

    market_info_list = MarketInfo.objects.all()
    
    
    market_list = [
        {
            'market': item.market,
            'korean_name':item.korean_name,
            'english_name':item.english_name,
            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            'ratio_1m_60m':next((get_volume_ratio(de, nu) for de, nu in zip(last_1_sum_data, last_1_60_sum_data) if de['market'] == item.market),None),
            'ratio_3m_60m':next((get_volume_ratio(de, nu) for de, nu in zip(last_3_sum_data, last_3_60_sum_data) if de['market'] == item.market),None),
            'ratio_5m_60m':next((get_volume_ratio(de, nu) for de, nu in zip(last_5_sum_data, last_5_60_sum_data) if de['market'] == item.market),None),
            'ratio_10m_60m':next((get_volume_ratio(de, nu) for de, nu in zip(last_10_sum_data, last_10_60_sum_data) if de['market'] == item.market),None),
            'volume_1m': next((d.volume for d in last_1_data if d.market == item.market), None),
            'amount_1m': next((d.amount for d in last_1_data if d.market == item.market), None),
            'volume_60m': next((d['total_volume'] for d in last_60_sum_data if d['market'] == item.market), None),
            'amount_60m': next((d['total_amount'] for d in last_60_sum_data if d['market'] == item.market), None)



        }
        for item in market_info_list if item.market !='KRW-BTC'
        ]

    #print(market_list)
    context = {'market_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
           
            return JsonResponse(market_list, safe=False)
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'upbit/market_data.html', context)