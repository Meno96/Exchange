from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import random
# From this app
from .forms import NewUserForm
# From other app
from app.models import Wallet
from app.market import Market

@csrf_exempt
def registerPageView(request):
    data = Market()
    currency = data.updated_data()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            #Wallet Creation
            newUserWallet=Wallet(
                user=user,
                btcWallet = round(random.uniform(1, 10), 8)
            )
            newUserWallet.usd_wallet = newUserWallet.btcWallet * currency

            # Wallet balance (USD and BTC)
            newUserWallet.usdBalance = newUserWallet.usdWallet
            newUserWallet.btcBalance = newUserWallet.btcWallet
            newUserWallet.save()
            

            jsonUser = {
                'username': username,
                'email': email,
                'USD Balance': newUserWallet.usdBalance,
                'BTC Balance': newUserWallet.btcBalance
                }

            return JsonResponse(jsonUser, safe=False)

    return JsonResponse('', safe=False)

def loginPageView(request):
    context = {}
    return render(request, 'app/login.html', context)