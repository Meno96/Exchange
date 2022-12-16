from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
import random
# From this app
from .forms import NewUserForm
# From other app
from app.models import Wallet, Profile
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

            # Profile creation
            newUserProfile = Profile(
                user=user,
            )
            newUserProfile.save()

            #Wallet Creation
            newUserWallet=Wallet(
                user=user,
                btcWallet = round(random.uniform(1, 10), 8)
            )
            newUserWallet.usdWallet = newUserWallet.btcWallet * currency

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

@csrf_exempt
def loginPageView(request):
    form = AuthenticationForm(request, data=request.POST)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('app:homepage')
        else:
            messages.info(request, 'Username o Password sono sbagliati')

    return render(request, 'user/login.html', {"login_form": form})