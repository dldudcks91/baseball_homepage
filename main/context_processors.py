from django.contrib.sessions.models import Session
from django.utils import timezone

def active_users(request):
    users = Session.objects.filter(expire_date__gte=timezone.now()).count()
    return {'active_users': users}