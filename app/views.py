from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
import random
import numpy as np

from .market import Market
from .forms import OrderForm
from .models import Order, Wallet, Profile


def closestValue(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]


@csrf_exempt
def homePageView(request):
    data = Market()
    currency = data.updated_data()
    return render(request, "homepage.html", {"currency": currency})


@login_required
@csrf_exempt
def orderView(request, id):
    data = Market()
    currency = data.updated_data()
    domValueSellList = []
    domValueBuyList = []
    domSellList = []
    domBuyList = []

    for i in range(1, 11):
        increment = 50
        if i == 1:
            domValueSellList.append(currency+increment)
            domValueBuyList.append(currency-increment)
            domSellList.append({'value': currency+increment, 'quantity': 0})
            domBuyList.append({'value': currency-increment, 'quantity': 0})
        else:
            domValueSellList.append(domValueSellList[i-2]+increment)
            domValueBuyList.append(domValueBuyList[i-2]-increment)
            domSellList.append(
                {'value': domSellList[i-2]['value']+increment, 'quantity': 0})
            domBuyList.append(
                {'value': domBuyList[i-2]['value']-increment, 'quantity': 0})

    buyLimitOrderList = Order.objects.filter(
        status='open', type='buyLimit').order_by('-price')
    sellLimitOrderList = Order.objects.filter(
        status='open', type='sellLimit').order_by('-price')
    buyOrderList = Order.objects.filter(
        status='open', type='buy').order_by('-price')
    sellOrderList = Order.objects.filter(
        status='open', type='sell').order_by('-price')

    for buyLimitOrder in buyLimitOrderList:
        if buyLimitOrder.price >= domValueBuyList[len(domValueBuyList)-1] and buyLimitOrder.price <= domValueBuyList[0]:
            closestNum = closestValue(domValueBuyList, buyLimitOrder.price)
            for item in domBuyList:
                if item['value'] == closestNum:
                    item['quantity'] += buyLimitOrder.quantity

    for sellLimitOrder in sellLimitOrderList:
        if sellLimitOrder.price >= domValueSellList[0] and sellLimitOrder.price <= domValueSellList[len(domValueSellList)-1]:
            closestNum = closestValue(domValueSellList, sellLimitOrder.price)
            for item in domSellList:
                if item['value'] == closestNum:
                    item['quantity'] += sellLimitOrder.quantity

    domSellList.reverse()

    maxSellQuantity = sorted(domSellList, key=lambda i: i['quantity'])[
        len(domSellList)-1]['quantity']
    maxBuyQuantity = sorted(domBuyList, key=lambda i: i['quantity'])[
        len(domSellList)-1]['quantity']

    if maxSellQuantity > maxBuyQuantity:
        maxQuantity = maxSellQuantity
    else:
        maxQuantity = maxBuyQuantity

    wallet = get_object_or_404(Wallet, user_id=id)
    userProfile = get_object_or_404(Profile, user_id=id)

    if request.method == 'POST':

        # Limit Order
        if request.POST.get('buyLimit'):

            form = OrderForm(request.POST or None)
            if form.is_valid():
                status = 'open'
                type = 'buyLimit'
                price = form.cleaned_data.get('price')
                quantity = form.cleaned_data.get('quantity')
                profileWallet = Wallet.objects.get(user=request.user)

                if price <= 0.0:
                    messages.error(request, 'Cannot put a price lower then 0')
                    return redirect('app:order', id=id)
                if quantity <= 0.0:
                    messages.error(
                        request, 'Cannot put a quantity lower then 0')
                    return redirect('app:order', id=id)
                if price >= currency:
                    messages.error(
                        request, 'Cannot put a Buy Limit with price higher than the actual BTC price')
                    print(
                        'Cannot put a Buy Limit with price higher than the actual BTC price')
                    return redirect('app:order', id=id)

                newBuyLimitOrder = Order.objects.create(
                    profile=request.user,
                    status=status,
                    type=type,
                    price=price,
                    quantity=quantity,
                    modified=timezone.now()
                )

                messages.success(
                    request, f'Your buy order (id: {newBuyLimitOrder._id}) of {newBuyLimitOrder.quantity} BTC for {newBuyLimitOrder.price} $ is succesfully added to the Order Book! \n || Status: {newBuyLimitOrder.status}.')

            return redirect('app:order', id=id)

        if request.POST.get('sellLimit'):

            form = OrderForm(request.POST or None)
            if form.is_valid():
                status = 'open'
                type = 'sellLimit'
                price = form.cleaned_data.get('price')
                quantity = form.cleaned_data.get('quantity')
                profileWallet = Wallet.objects.get(user=request.user)

                if price <= 0.0:
                    messages.error(request, 'Cannot put a price lower then 0')
                    return redirect('app:order', id=id)
                if quantity <= 0.0:
                    messages.error(
                        request, 'Cannot put a quantity lower then 0')
                    return redirect('app:order', id=id)
                if price <= currency:
                    messages.error(
                        request, 'Cannot put a Buy Limit with price higher than the actual BTC price')
                    return redirect('app:order', id=id)

                newSellLimitOrder = Order.objects.create(
                    profile=request.user,
                    status=status,
                    type=type,
                    price=price,
                    quantity=quantity,
                    modified=timezone.now()
                )

                messages.success(
                    request, f'Your sell order (id: {newSellLimitOrder._id}) of {newSellLimitOrder.quantity} BTC for {newSellLimitOrder.price} $ is succesfully added to the Order Book! \n || Status: {newSellLimitOrder.status}.')

            return redirect('app:order', id=id)
            
        # Market Order
        if request.POST.get('buy'):
            form = OrderForm(request.POST or None)
            if form.is_valid:
                status = 'open'
                type = 'buy'
                price = currency
                quantity = form.cleaned_data.get('quantity')
                profileWallet = Wallet.objects.get(user=request.user)

                if quantity <= 0.0:
                    messages.error(
                        request, 'Cannot put a quantity lower then 0')
                    return redirect('app:order', id=id)

                newBuyOrder = Order.objects.create(
                    profile=request.user,
                    status=status,
                    type=type,
                    price=price,
                    quantity=quantity,
                    modified=timezone.now()
                )

    # return JsonResponse('', safe=False)
    return render(request, 'app/order.html', {
        'currency': currency,
        'buyLimitOrderList': buyLimitOrderList,
        'sellLimitOrderList': sellLimitOrderList,
        'domSellList': domSellList,
        'domBuyList': domBuyList,
        'maxQuantity': maxQuantity,
    })
