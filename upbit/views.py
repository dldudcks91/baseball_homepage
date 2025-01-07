from django.shortcuts import render
from .models import Market
# Create your views here.
def index(request):
    context = {'index': 'Hello'}
    return render(request,'upbit/index.html',context)

def full_data(request):
    data_list = Market.objects.all()
    context = {'full_data':data_list}
    return render(request,'upbit/full_data.html', context)