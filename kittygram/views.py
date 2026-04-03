from django.contrib.auth import get_user_model
from django.shortcuts import render

from cats.models import Cat
from events.models import Event, Registration

User = get_user_model()


def index(request):
    context = {
        'cats_count': Cat.objects.count(),
        'users_count': User.objects.count(),
        'events_count': Event.objects.count(),
        'registrations_count': Registration.objects.filter(
            status='registered').count(),
    }
    return render(request, 'index.html', context)
