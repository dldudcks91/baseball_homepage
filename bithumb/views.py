from django.shortcuts import render
from .models import Market, MarketHour, MarketDay, MarketInfo, MADays, MA60Minutes, MarketBitget, MA60MinutesBitget, MarketHourBitget, UserMemo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

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


def trade_bithumb(request):
    
    
    TEST_SECONDS= 0
    #current_time = datetime(2025, 2, 11, 23, 14, 41, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_SECONDS)
    current_time = datetime.now(tz = timezone.utc) - timedelta(seconds = 10)
    #current_time = datetime(2025, 2, 12, 8, 1, 33, tzinfo = timezone.utc)
    last_time = get_current_time(current_time, -(TEST_SECONDS))
    last_temp_time = get_current_time(current_time, -(10 + TEST_SECONDS))
    last_1_time = get_current_time(current_time, -(60 + TEST_SECONDS))
    last_5_time = get_current_time(current_time, -(300 + TEST_SECONDS))
    last_10_time = get_current_time(current_time, -(600 + TEST_SECONDS))
    last_30_time = get_current_time(current_time, -(1800 + TEST_SECONDS))
    last_60_time = get_current_time(current_time, -(3600 + TEST_SECONDS))
    last_240_time = get_current_time(current_time, -(14400 + TEST_SECONDS))
    
    
    last_1d_time = get_current_time(current_time, -(60 * 60 * 24 +TEST_SECONDS))
    last_7d_time = get_current_time(current_time, -(60 * 60 * 24 * 7 +TEST_SECONDS))
    
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0),0)
    
    #시점데이터
    last_data = Market.objects.filter(log_dt = last_time)
    if len(last_data)== 0:
        last_data = MarketBitget.objects.filter(log_dt = last_temp_time)        
    last_1_data = Market.objects.filter(log_dt = last_1_time)
    last_5_data = Market.objects.filter(log_dt = last_5_time)
    last_30_data = Market.objects.filter(log_dt = last_30_time)
    last_60_data = Market.objects.filter(log_dt = last_60_time)
    last_240_data = Market.objects.filter(log_dt = last_240_time)
    last_1d_data = Market.objects.filter(log_dt = last_1d_time)
    last_7d_data = Market.objects.filter(log_dt = last_7d_time)


    market_info_data = MarketInfo.objects.all().order_by('market')
    
    #고점데이터
    today_high_low_data = Market.objects.filter(log_dt__gte= last_1d_time).values('market').annotate(max_price = Max('price'), min_price = Min('price'))
    
    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    # last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    
    
    last_hour = (last_time.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1))
    last_day = (last_time- timedelta(days=1)).date()
    
    ma_60_data = MA60Minutes.objects.filter(log_dt = last_hour).order_by('market')
    ma_day_data = MADays.objects.filter(date = last_day).order_by('market')


    print('last_time:', last_time, len(last_data))
    print('last_hour:', last_hour, len(ma_60_data))
    print('last_day:', last_day, len(ma_day_data))
    


    
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
            'capitalization': next((d.capitalization for d in market_info_data if d.market == item.market), None),
            'price_last': next((d.price for d in last_data if d.market == item.market), None),
            'price_1m': next((d.price for d in last_1_data if d.market == item.market), None),
            'price_5m': next((d.price for d in last_5_data if d.market == item.market), None),
            'price_30m': next((d.price for d in last_30_data if d.market == item.market), None),
            'price_60m': next((d.price for d in last_60_data if d.market == item.market), None),
            'price_240m': next((d.price for d in last_240_data if d.market == item.market), None),
            'price_1d': next((d.price for d in last_1d_data if d.market == item.market), None),
            'price_7d': next((d.price for d in last_7d_data if d.market == item.market), None),
            

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
        for item in market_info_data
        ]

    print(market_list[0])
    context = {'trade_day_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_list.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'bithumb/trade_list.html', context)

def trade_bitget(request):
    
    
    TEST_SECONDS= 0
    #current_time = datetime(2025, 2, 11, 23, 14, 41, tzinfo = timezone.utc)#datetime.now(tzinfo = timezone.utc) #- timedelta(minutes = TEST_SECONDS)
    current_time = datetime.now(tz = timezone.utc) - timedelta(seconds = 10)
    #current_time = datetime(2025, 2, 12, 8, 1, 33, tzinfo = timezone.utc)
    last_time = get_current_time(current_time, -(TEST_SECONDS))
    last_temp_time = get_current_time(current_time, -(10 + TEST_SECONDS))
    last_1m_time = get_current_time(current_time, -(60 + TEST_SECONDS))
    last_3m_time = get_current_time(current_time, -(60 * 3 + TEST_SECONDS))
    last_5m_time = get_current_time(current_time, -(60 * 5 + TEST_SECONDS))
    last_15m_time = get_current_time(current_time, -(60 * 15 + TEST_SECONDS))
    last_30m_time = get_current_time(current_time, -(60 * 30 + TEST_SECONDS))
    last_1h_time = get_current_time(current_time, -(60 * 60 + TEST_SECONDS))
    last_2h_time = get_current_time(current_time, -(60 * 60 * 2+ TEST_SECONDS))
    last_4h_time = get_current_time(current_time, -(60 * 60 * 4 + TEST_SECONDS))
    last_8h_time = get_current_time(current_time, -(60 * 60 * 8 + TEST_SECONDS))
    
    last_1d_time = get_current_time(current_time, -(60 * 60 * 24 + TEST_SECONDS))
    last_3d_time = get_current_time(current_time, -(60 * 60 * 24 * 3+TEST_SECONDS))
    last_7d_time = get_current_time(current_time, -(60 * 60 * 24 * 7 +TEST_SECONDS))
    last_14d_time = get_current_time(current_time, -(60 * 60 * 24 * 14 +TEST_SECONDS))
    
    utc_00_time = get_current_time(current_time.replace(hour= 0, minute = 0, second = 0 ,microsecond = 0),0)
    
    #시점데이터
    last_data = MarketBitget.objects.filter(log_dt = last_time)
    if len(last_data)== 0:
        last_data = MarketBitget.objects.filter(log_dt = last_temp_time)        
    #last_1m_data = MarketBitget.objects.filter(log_dt = last_1m_time)
    #last_3m_data = MarketBitget.objects.filter(log_dt = last_3m_time)
    last_5m_data = MarketBitget.objects.filter(log_dt = last_5m_time)
    last_15m_data = MarketBitget.objects.filter(log_dt = last_15m_time)
    #last_30m_data = MarketBitget.objects.filter(log_dt = last_30m_time)
    last_1h_data = MarketBitget.objects.filter(log_dt = last_1h_time)
    #last_2h_data = MarketBitget.objects.filter(log_dt = last_2h_time)
    last_4h_data = MarketBitget.objects.filter(log_dt = last_4h_time)
    last_8h_data = MarketBitget.objects.filter(log_dt = last_8h_time)
    last_1d_data = MarketBitget.objects.filter(log_dt = last_1d_time)
    last_3d_data = MarketBitget.objects.filter(log_dt = last_3d_time)
    last_7d_data = MarketBitget.objects.filter(log_dt = last_7d_time)
    last_14d_data = MarketBitget.objects.filter(log_dt = last_14d_time)

    market_info_data = MarketBitget.objects.values('market').distinct()
    
    
    #고점데이터
    #today_high_low_data = Market.objects.filter(log_dt__gte= last_1d_time).values('market').annotate(max_price = Max('price'), min_price = Min('price'))
    
    #print(last_3_sum_data)
    # 직전 n~60분 데이터 -> 나중에 수정해보자 좋은값찾아서
    # last_1_60_sum_data = Market.objects.filter(log_dt__lt= last_1_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_3_60_sum_data = Market.objects.filter(log_dt__lt= last_3_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_5_60_sum_data = Market.objects.filter(log_dt__lt= last_5_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    # last_10_60_sum_data = Market.objects.filter(log_dt__lt= last_10_time, log_dt__gte= last_60_time, volume__gt = 0).values('market').annotate(total_volume=Sum('volume'), total_amount = Sum('amount'), cnt = Count('volume')).order_by('market')
    
    last_hour = (last_time.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1))
    last_day = (last_time- timedelta(days=1)).date()
    last_3_day = (last_time- timedelta(days=3)).date()
    last_7_day = (last_time- timedelta(days=7)).date()
    
    ma_60_data = MA60MinutesBitget.objects.filter(log_dt = last_hour).order_by('market')

    hour1_high_low_data = MarketBitget.objects.filter(log_dt__gte= last_1h_time).values('market').annotate(max_price = Max('price'), min_price = Min('price'))
    hour4_high_low_data = MarketBitget.objects.filter(log_dt__gte= last_4h_time).values('market').annotate(max_price = Max('price'), min_price = Min('price'))

    today_high_low_data = MarketHourBitget.objects.filter(log_dt__gte= last_day).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))
    day3_high_low_data = MarketHourBitget.objects.filter(log_dt__gte= last_3_day).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))
    #today_high_low_data = MarketHourBitget.objects.filter(log_dt__gte= last_day).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))
    week_high_low_data = MarketHourBitget.objects.filter(log_dt__gte= last_7_day).values('market').annotate(max_price = Max('high_price'), min_price = Min('low_price'))

    print("hour1_high_low_data:", hour1_high_low_data)
    market_list = [
        {
            'market': item['market'][:-4],
            
            'volume': next((d.volume for d in last_data if d.market == item['market']), None),
            'funding_rate':next((d.funding_rate for d in last_data if d.market == item['market']), None),
            'price_last': next((d.price for d in last_data if d.market == item['market']), None),
            #'price_1m': next((d.price for d in last_1m_data if d.market == item['market']), None),
            #'price_3m': next((d.price for d in last_3m_data if d.market == item['market']), None),
            'price_5m': next((d.price for d in last_5m_data if d.market == item['market']), None),
            'price_15m': next((d.price for d in last_15m_data if d.market == item['market']), None),
            #'price_30m': next((d.price for d in last_30m_data if d.market == item['market']), None),
            'price_1h': next((d.price for d in last_1h_data if d.market == item['market']), None),
            #'price_2h': next((d.price for d in last_2h_data if d.market == item['market']), None),
            'price_4h': next((d.price for d in last_4h_data if d.market == item['market']), None),
            'price_8h': next((d.price for d in last_8h_data if d.market == item['market']), None),
            'price_1d': next((d.price for d in last_1d_data if d.market == item['market']), None),
            'price_3d': next((d.price for d in last_3d_data if d.market == item['market']), None),
            'price_7d': next((d.price for d in last_7d_data if d.market == item['market']), None),
            'price_14d': next((d.price for d in last_14d_data if d.market == item['market']), None),
            'ma_60_10': next((d.ma_10 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_20': next((d.ma_20 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_34': next((d.ma_34 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_50': next((d.ma_50 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_100': next((d.ma_100 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_200': next((d.ma_200 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_400': next((d.ma_400 for d in ma_60_data if d.market == item['market']), None),
            'ma_60_800': next((d.ma_800 for d in ma_60_data if d.market == item['market']), None),
            



            'price_1h_high': next((d['max_price'] for d in hour1_high_low_data if d['market'] == item['market']), None),
            'price_1h_low': next((d['min_price'] for d in hour1_high_low_data if d['market'] == item['market']), None),
            'price_4h_high': next((d['max_price'] for d in hour4_high_low_data if d['market'] == item['market']), None),
            'price_4h_low': next((d['min_price'] for d in hour4_high_low_data if d['market'] == item['market']), None),


            'price_today_high': next((d['max_price'] for d in today_high_low_data if d['market'] == item['market']), None),
            'price_today_low': next((d['min_price'] for d in today_high_low_data if d['market'] == item['market']), None),

            'price_3d_high': next((d['max_price'] for d in day3_high_low_data if d['market'] == item['market']), None),
            'price_3d_low': next((d['min_price'] for d in day3_high_low_data if d['market'] == item['market']), None),

            'price_week_high': next((d['max_price'] for d in week_high_low_data if d['market'] == item['market']), None),
            'price_week_low': next((d['min_price'] for d in week_high_low_data if d['market'] == item['market']), None),
            
       
        }
        for item in market_info_data
        ]

    print(market_list[0])
    context = {'trade_day_data': market_list}
    

    #추가로 요청받았을때
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, 'bithumb/trade_list.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'data': market_list
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

    
    return render(request,'bithumb/trade_list.html', context)

@require_http_methods(["GET", "POST", "DELETE"])
    
@require_http_methods(["GET"])
def get_user_memos(request):
    """모든 사용자 메모 조회"""
    memos = UserMemo.objects.all()
    data = {
        'favorites': list(memos.filter(favorite=True).values_list('market', flat=True)),
        'memos': {m.market: m.memo for m in memos if m.memo},
        'last_visited_at': {m.market: m.last_visited_at for m in memos if m.last_visited_at}
    }
    print("get_user_memos: ", data)
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def update_user_memo(request):
    """즐겨찾기/메모/마지막 방문 시간 통합 업데이트"""
    market = request.POST.get('market')
    
    if not market:
        return JsonResponse({'error': 'market is required'}, status=400)
    
    # 레코드 가져오기 또는 생성
    memo_obj, created = UserMemo.objects.get_or_create(market=market)
    
    # 1. favorite 토글 또는 업데이트
    if 'favorite' in request.POST:
        favorite_value = request.POST.get('favorite').lower() == 'true'
        memo_obj.favorite = favorite_value
        
        # favorite이 True가 되면 날짜 기록, False가 되면 날짜 삭제
        if favorite_value:
            if not memo_obj.favorite_date:  # 처음 등록하는 경우만
                memo_obj.favorite_date = datetime.now(tz=timezone.utc) + timedelta(hours=9)
        else:
            memo_obj.favorite_date = None
    
    # 2. memo 업데이트
    if 'memo' in request.POST:
        memo_obj.memo = request.POST.get('memo', '')

    # 3. last_visited_at 업데이트 (서버 시간 저장으로 수정됨)
    if 'last_visited_at' in request.POST:
        # 클라이언트에서 보낸 문자열 값은 무시하고, 서버의 현재 시간(UTC)을 저장
        memo_obj.last_visited_at = datetime.now(tz=timezone.utc) + timedelta(hours=9)
    
    memo_obj.save()
    
    return JsonResponse({
        'status': 'success',
        'market': market,
        'favorite': memo_obj.favorite,
        'favorite_date': memo_obj.favorite_date.isoformat() if memo_obj.favorite_date else None,
        'memo': memo_obj.memo,
        # 프론트엔드 표시 형식에 맞춰 문자열로 포맷팅하여 반환 ('25.02.12 14:30')
        'last_visited_at': memo_obj.last_visited_at.strftime('%y.%m.%d %H:%M') if memo_obj.last_visited_at else None
    })