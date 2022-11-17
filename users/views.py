from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime
from .forms import UserRegisterForm
from mail.models import Mail
from django.contrib.auth.models import User
from django.db.models import Count, Q, F,Sum, Avg

def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    CO2e_datewise, x=[], datetime.now()
    for i in range(5):
        y = x - timedelta(i)
        avg_estimate = Mail.objects.filter(date_sent__date=y).aggregate(Avg('mail_co2e'))
        estimate=Mail.objects.filter(sent_from=request.user, date_sent__date=y).aggregate(Sum('mail_co2e'))
        if(estimate['mail_co2e__sum'] is None):
            estimate['mail_co2e__sum'] = 0
        if(avg_estimate['mail_co2e__avg'] is None):
            avg_estimate['mail_co2e__avg'] = 0
        CO2e_datewise.append([y, estimate['mail_co2e__sum'], avg_estimate['mail_co2e__avg']])
    
    context={
        'user': request.user,
        'totalMails': Mail.objects.filter(Q(sent_to=request.user) | Q(sent_from=request.user)).count(),
        'totalInbox': Mail.objects.filter(sent_to=request.user).exclude(labels__label_name='Promotional').count(),
        'totalSent': Mail.objects.filter(sent_from=request.user).count(),
        'totalPromotion': Mail.objects.filter(sent_to=request.user, labels__label_name='Promotional').count(),
        'totalCO2e': Mail.objects.filter(sent_from=request.user).aggregate(Sum('mail_co2e')),
        'userCO2eG': CO2e_datewise,
    }
    return render(request, 'users/profile.html', context)