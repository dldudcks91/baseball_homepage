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
    def get_current_time(current_time):   
    
        rounded_minutes = (current_time.minute // 5) * 5 
        rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) - timedelta(minutes=5) - timedelta(hours = 6)
        formatted_time = rounded_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    current_time = get_current_time(datetime.now())
    market_data = Market.objects.filter(log_dt = current_time)


    context = {'market_data': market_data}
    return render(request,'upbit/market_data.html', context)

@csrf_exempt
def get_market_data(request):
    
    def get_current_time(current_time):   
    
        rounded_minutes = (current_time.minute // 5) * 5 
        rounded_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0) - timedelta(minutes=5) - timedelta(hours = 9)
        formatted_time = rounded_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    
    try:
        current_time = get_current_time(datetime.now())

        
        market_data = Market.objects.filter(log_dt = current_time)
        market_list = []
        
        for item in market_data:
            market_list.append({
                'market': item.market,
                'price': str(item.price),  # Decimal 타입을 문자열로 변환
                'volume': str(item.volume),
                'amount': str(item.amount)
            })
        print(current_time, len(market_data))
        return JsonResponse(market_list, safe=False)
    
    
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)