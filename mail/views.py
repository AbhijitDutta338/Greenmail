from django.shortcuts import render, redirect, get_object_or_404
from .models import Mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import NewMailForm
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
import requests, json

@login_required
def home(request,type):
    context=Mail.objects.all()
    if(type=='inbox'):
        context=Mail.objects.filter(sent_to=request.user).exclude(labels__label_name='Promotional').order_by('-date_sent')
    elif(type=='promotion'):
        context=Mail.objects.filter(labels__label_name='Promotional').order_by('-date_sent')
    elif(type=='sent'):
        context=Mail.objects.filter(sent_from=request.user).order_by('-date_sent')
    else:
        user=get_object_or_404(User, username=type)
        context=Mail.objects.filter(sent_from=user, labels__label_name='Promotional').order_by('-date_sent')
    
    pg=Paginator(context, 4)
    pgNum=request.GET.get('page')
    return render(request, 'mail/mail_home.html', {'mails': pg.get_page(pgNum)})

@login_required
def compose_mail(request):
    APIurl ='https://beta3.api.climatiq.io/estimate' 
    APIKey = {'Authorization': 'Bearer 1WJAWH7FD0MRNJHT1NFDC0JQF618'}
    APIrequestdata = {
        "emission_factor": "networking-provider_aws-region_ap_south_1",
        "parameters": {
			"data": 1,
			"data_unit": "GB"
        }
    }
    if request.method == 'POST':
        form = NewMailForm(request.POST)
        form.instance.sent_from=request.user
        if form.is_valid():
            response=requests.post(url=APIurl,data=json.dumps(APIrequestdata),headers=APIKey).json()
            form.instance.mail_co2e=(response['co2e'] * 1000000)
            messages.success(request, f'Mail sent successfully! Your mail generated {form.instance.mail_co2e} mg of CO2e.')
            form.save()
            return redirect('/mail/inbox/')
    else:
        form = NewMailForm()
    return render(request, 'mail/compose_mail.html', {'form': form})

@login_required
def read_mail(request, pk):
    mail=get_object_or_404(Mail,pk=pk)
    if(mail):
        mail.mail_read=True
        mail.save()
    return render(request, 'mail/read_mail.html', {'mail':mail})

@login_required
def theCorrectList(request):
    context=User.objects.annotate(
        TotalMails=Count('mail_from', filter=(Q(mail_from__sent_to = request.user) & Q(mail_from__labels__label_name='Promotional'))),
        UnreadMails=Count('mail_from', filter=(Q(mail_from__sent_to = request.user) & Q(mail_from__labels__label_name='Promotional') & Q(mail_from__mail_read=False))),
        Engagement=((F('TotalMails')-F('UnreadMails'))*100)/F('TotalMails')
    ).filter(TotalMails__gt=0).order_by('Engagement')
    
    pg=Paginator(context, 5)
    pgNum=request.GET.get('page')
    return render(request, 'mail/correct_list.html', {'prMailers': pg.get_page(pgNum)})
