from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import random
from .forms import NewUserForm
from .models import Wallet
from .market import Market

@csrf_exempt
def registerPage(request):
    data = Market()
    currency = data.updated_data()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            #Wallet Creation
            new_user_wallet=Wallet(
                user=user,
                btc_wallet = round(random.uniform(1, 10), 8)
            )
            new_user_wallet.usd_wallet = new_user_wallet.btc_wallet * currency

            # Wallet balance (USD and BTC)
            new_user_wallet.usd_balance = new_user_wallet.usd_wallet
            new_user_wallet.btc_balance = new_user_wallet.btc_wallet
            new_user_wallet.save()
            

            jsonUser = {
                'username': username,
                'email': email,
                'USD Balance': new_user_wallet.usd_balance,
                'BTC Balance': new_user_wallet.btc_balance
                }

            return JsonResponse(jsonUser, safe=False)

    return JsonResponse('', safe=False)

def loginPage(request):
    context = {}
    return render(request, 'app/login.html', context)

def homePage(request):
    context = {}
    return render(request, 'app/home.html', context)