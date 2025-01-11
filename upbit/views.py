from django.shortcuts import render
from .models import Market, MarketInfo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Count, Max

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
    
    TEST_MINUTES= 20
    current_time = datetime.now() #- timedelta(minutes = TEST_MINUTES)
    last_1_time = get_current_time(current_time, -(1+TEST_MINUTES))
    last_3_time = get_current_time(current_time, -(3+TEST_MINUTES))
    last_5_time = get_current_time(current_time, -(5+TEST_MINUTES))
    last_10_time = get_current_time(current_time, -(10+TEST_MINUTES))
    last_30_time = get_current_time(current_time, -(30+TEST_MINUTES))
    last_60_time = get_current_time(current_time, -(60+TEST_MINUTES))
    last_240_time = get_current_time(current_time, -(240+TEST_MINUTES))
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0),0)
    


    #고점데이터
    today_high_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0).values('market').annotate(max_price = Max('price')).order_by('market')
    #거래량,거래대금
    last_1_sum_data = Market.objects.filter(log_dt__gte= last_1_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_3_sum_data = Market.objects.filter(log_dt__gte= last_3_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_5_sum_data = Market.objects.filter(log_dt__gte= last_5_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_10_sum_data = Market.objects.filter(log_dt__gte= last_10_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_60_sum_data = Market.objects.filter(log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    last_today_sum_data = Market.objects.filter(log_dt__gte= utc_00_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')

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
            return (nu_mean / de_mean) -1

    last_1_data = Market.objects.filter(log_dt = last_1_time).order_by('market')
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)
    
    for a,b in zip(last_1_data, last_1_60_sum_data):
        print(a.market, a.volume,b)
        #print(a,b)

    market_info_list = MarketInfo.objects.all()
    
    
    market_list = [
        {
            'market': item.market,
            'korean_name':item.korean_name,
            'english_name':item.english_name,
            'capitalization':item.capitalization,
            'kimchi_premium':next((round(((d.price/d.price_foreign)-1)*100,2) if d.price_foreign !=0 else 0 for d in last_1_data if d.market == item.market), None),

            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            'price_today_high': next((d['max_price'] for d in today_high_data if d['market'] == item.market), None),
            'ratio_1m_60m':next((get_volume_ratio(nu, de) for nu, de in zip(last_1_sum_data, last_1_60_sum_data) if de['market'] == item.market),None),
            'ratio_3m_60m':next((get_volume_ratio(nu, de) for nu, de in zip(last_3_sum_data, last_3_60_sum_data) if de['market'] == item.market),None),
            'ratio_5m_60m':next((get_volume_ratio(nu, de) for nu, de in zip(last_5_sum_data, last_5_60_sum_data) if de['market'] == item.market),None),
            'ratio_10m_60m':next((get_volume_ratio(nu, de) for nu, de in zip(last_10_sum_data, last_10_60_sum_data) if de['market'] == item.market),None),
            
            'amount_1m': next((d.amount for d in last_1_data if d.market == item.market), None),
            
            'amount_5m': next((d['total_amount'] for d in last_5_sum_data if d['market'] == item.market), None),
            'amount_60m': next((d['total_amount'] for d in last_60_sum_data if d['market'] == item.market), None),
            'amount_today': next((d['total_amount'] for d in last_today_sum_data if d['market'] == item.market), None)



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