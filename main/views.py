from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.sessions.models import Session


# ---------------------------------------------------------------------------------------- #

def to_main(request):
    return redirect('/main')
def index(request):
    # ---------------------------------------- [edit] ---------------------------------------- #
    '''
    메인화면
    '''
    num_list = [0,1,2]
    context = {'num_list': num_list}
    return render(request, 'main.html', context)
    
    # ---------------------------------------------------------------------------------------- #
