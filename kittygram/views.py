from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render

from cats.models import Cat
from wishlist.models import Contribution, Need

User = get_user_model()


def index(request):
    context = {
        'cats_count': Cat.objects.count(),
        'users_count': User.objects.count(),
        'needs_count': Need.objects.count(),
        'closed_count': Need.objects.filter(status='closed').count(),
    }
    return render(request, 'index.html', context)


def needs_list(request):
    needs = Need.objects.all()

    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')

    if status_filter:
        needs = needs.filter(status=status_filter)
    if priority_filter:
        needs = needs.filter(priority=priority_filter)

    for need in needs:
        fulfilled = need.contributions.aggregate(
            total=Sum('quantity'))['total'] or 0
        need.fulfilled = fulfilled
        if need.quantity_required > 0:
            need.progress = min(
                round(fulfilled / need.quantity_required * 100, 1), 100)
        else:
            need.progress = 100

    context = {
        'needs': needs,
        'current_filter': status_filter,
        'current_priority': priority_filter,
    }
    return render(request, 'needs_list.html', context)
