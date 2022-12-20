from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from app.decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
import random
# From this app
from .forms import NewUserForm
# From other app
from app.models import Wallet, Profile
from app.market import Market

@unauthenticated_user
@csrf_exempt
def registerPageView(request):
    data = Market()
    currency = data.updated_data()

    form = NewUserForm()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        
        form = NewUserForm(request.POST)
        if form.is_valid():
            print('ok')
            user = form.save()

            # Profile creation
            newUserProfile = Profile(
                user=user,
            )
            newUserProfile.save()

            #Wallet Creation
            newUserWallet=Wallet(
                user=user,
                btcWallet = round(random.uniform(1, 10), 8),
                usdWallet = round(random.uniform(50000, 150000), 2),
            )
            
            newUserWallet.startValue = newUserWallet.usdWallet + (newUserWallet.btcWallet*currency)
            newUserWallet.save()

            return redirect('user:login')
        else:
            messages.info(request, 'Check that you have filled in all the required fields correctly.')

    return render(request, 'user/register.html', {"form": form})

@unauthenticated_user
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
            messages.info(request, 'Wrong username or password')

    return render(request, 'user/login.html', {"loginForm": form})

@login_required(login_url='login')
@csrf_exempt
def accountPageView(request, id):
    data = Market()
    currency = data.updated_data()

    username = request.user.username

    userWallet = get_object_or_404(Wallet, user_id=id)

    actualValue = userWallet.usdWallet + (userWallet.btcWallet * currency)
    startValue = userWallet.startValue
    
    delta = actualValue - startValue

    return render(request, 'user/account.html', {'username': username, 'delta': delta})

# View di logout
@csrf_exempt
def logoutUser(request):
    logout(request)
    return redirect('user:login')