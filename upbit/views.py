from django.shortcuts import render
from .models import Market
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
# Create your views here.
def index(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/index.html',context)

def market_data(request):
    def get_current_time(current_time, modify_minutes):   
    
        rounded_minutes = (current_time.minute)
        rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) + modify_minutes
        formatted_time = rounded_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    
    last_1_time = get_current_time(datetime.now(), -timedelta(minutes = 1)-timedelta(minutes = 30))
    last_5_time = get_current_time(datetime.now(), -timedelta(minutes = 5)-timedelta(minutes = 30))
    last_30_time = get_current_time(datetime.now(), -timedelta(minutes = 30)-timedelta(minutes = 30))
    last_60_time = get_current_time(datetime.now(), -timedelta(minutes = 60)-timedelta(minutes = 30))
    last_240_time = get_current_time(datetime.now(), -timedelta(minutes = 240)-timedelta(minutes = 30))
    


    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)
    


    market_list = [
        {
            'market': item.market,
            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            'volume': item.volume,
            'amount': item.amount
        }
        for item in last_1_data
        ]
    context = {'market_data': market_list}


    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
           
            return JsonResponse(market_list, safe=False)
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'upbit/market_data.html', context)