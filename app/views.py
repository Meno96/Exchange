from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
import random
import numpy as np
from datetime import datetime

from .market import Market
from .forms import OrderForm, MarketOrderForm
from .models import Order, Wallet, Profile, IpAddress

# Return actual IP
@csrf_exempt
def getActualIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Create IP object with actual date
@csrf_exempt
def addIp(actualIp):
    ipAddress = IpAddress(
        ipAddress=actualIp, pubDate=datetime.now())
    ipAddress.save()

# Return the nearest value
def closestValue(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

# Homepage's view
@login_required(login_url='user:login')
@csrf_exempt
def homePageView(request):
    data = Market()
    currency = data.updated_data()

    # Stores the last IP that have logged in to the platform as admin, shows a warning 
    # message when this is different from the previous one
    checkIp = None
    if request.user.is_staff:
        dbIp = IpAddress.objects.all().values().last()
        actualIp = getActualIP(request)

        if not dbIp:
            addIp(actualIp)
        else:
            if actualIp != dbIp['ipAddress']:
                addIp(actualIp)
                checkIp = True

    return render(request, "homepage.html", {"currency": currency, "checkIp": checkIp})

# Exchange page's view
@login_required(login_url='login')
@csrf_exempt
def orderView(request, id):

    # Get actual BTC price $
    data = Market()
    currency = data.updated_data()

    # Get the active limit orders from the db
    buyLimitOrderList = Order.objects.filter(
        status='open', type='buyLimit').order_by('-price')
    sellLimitOrderList = Order.objects.filter(
        status='open', type='sellLimit').order_by('price')
    sellLimitOrderList.reverse()

    # If actual BTC price went over the limit 
    # order's price automatically close the limit order
    for buyLimitOrder in buyLimitOrderList:
        if buyLimitOrder.price > currency:
            buyLimitOrder.status = 'close'
            buyLimitOrder.save()

    for sellLimitOrder in sellLimitOrderList:
        if sellLimitOrder.price < currency:
            sellLimitOrder.status = 'close'
            sellLimitOrder.save()

    # Instructions for building the DOM
    domValueSellList = []
    domValueBuyList = []
    domSellList = []
    domBuyList = []

    for i in range(1, 11):
        increment = 10
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

    for item in domSellList:
        item.update({'calc': ((maxQuantity * 20)/100)})
    for item in domBuyList:
        item.update({'calc': ((maxQuantity * 20)/100)})


    if request.user.is_staff == False:
        if request.method == 'POST':

            # Limit Orders
            if request.POST.get('buyLimit'):

                # Create buy limit order
                form = OrderForm(request.POST or None)
                if form.is_valid():
                    status = 'open'
                    type = 'buyLimit'
                    price = form.cleaned_data.get('price')
                    quantity = form.cleaned_data.get('quantity')
                    profileWallet = Wallet.objects.get(user=request.user)

                    # Manage invalid data
                    if price <= 0.0:
                        messages.error(
                            request, 'Cannot put a price lower then 0')
                        return redirect('app:order', id=id)
                    if quantity <= 0.0:
                        messages.error(
                            request, 'Cannot put a quantity lower then 0')
                        return redirect('app:order', id=id)
                    if price >= currency:
                        messages.error(
                            request, 'Cannot put a Buy Limit with price higher than the actual BTC price')
                        return redirect('app:order', id=id)
                    if price*quantity > profileWallet.usdWallet:
                        messages.error(
                            request, 'Insufficent funds to complete the order')
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

                # Create sell limit order
                form = OrderForm(request.POST or None)
                if form.is_valid():
                    status = 'open'
                    type = 'sellLimit'
                    price = form.cleaned_data.get('price')
                    quantity = form.cleaned_data.get('quantity')
                    profileWallet = Wallet.objects.get(user=request.user)

                    # Manage invalid data
                    if price <= 0.0:
                        messages.error(
                            request, 'Cannot put a price lower then 0')
                        return redirect('app:order', id=id)
                    if quantity <= 0.0:
                        messages.error(
                            request, 'Cannot put a quantity lower then 0')
                        return redirect('app:order', id=id)
                    if price <= currency:
                        messages.error(
                            request, 'Cannot put a Sell Limit with price higher than the actual BTC price')
                        return redirect('app:order', id=id)
                    if quantity > profileWallet.btcWallet:
                        messages.error(
                            request, 'Insufficent BTC to complete the order')
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

            # Market Orders
            if request.POST.get('buy'):

                # Create buy order
                form = MarketOrderForm(request.POST or None)
                if form.is_valid():
                    status = 'open'
                    type = 'buy'
                    price = currency
                    quantity = form.cleaned_data.get('quantity')
                    profileWallet = Wallet.objects.get(user=request.user)

                    # Manage invalid data
                    if quantity <= 0.0:
                        messages.error(
                            request, 'Cannot put a quantity lower then 0')
                        return redirect('app:order', id=id)
                    if price*quantity > profileWallet.usdWallet:
                        messages.error(
                            request, 'Insufficent funds to complete the order')
                        return redirect('app:order', id=id)

                    # Order matching
                    if sellLimitOrderList.exists():

                        quantityTot = 0
                        orderIndex = []

                        # Return only the sell limit orders create from other users
                        for i in range(len(sellLimitOrderList)):

                            if sellLimitOrderList[i].profile == profileWallet.user:
                                continue

                            orderIndex.append(i)
                            quantityTot += sellLimitOrderList[i].quantity
                            if quantityTot >= quantity:
                                break
                        
                        # Error if there aren't enought sell limit contract, otherwise it continues with the order's matching
                        if quantityTot < quantity:
                            messages.error(
                                request, f"There are not enough sell orders that match the request.")
                            return redirect('app:order', id=id)
                        else:
                            # Proceeds with the order's matching if the sell limit order has a price lower than 0.5% of the indicated price
                            if (100-(currency/sellLimitOrderList[i].price*100)) < 0.5:

                                newBuyOrder = Order.objects.create(
                                    profile=request.user,
                                    status=status,
                                    type=type,
                                    price=price,
                                    quantity=quantity,
                                    modified=timezone.now()
                                )

                                messages.info(request,
                                              f'Order created.')
                                messages.info(request,
                                              f'Slippage < 0.5%.')
                                messages.info(request,
                                              f'Start of the bitcoin exchange. ')


                                # Find the best combination of orders to ensure the best price
                                actualQuantity = newBuyOrder.quantity
                                actualBTC = profileWallet.btcWallet
                                for i in orderIndex:
                                    sellLimitOrder = Order.objects.get(
                                        _id=sellLimitOrderList[i]._id)
                                    profileSeller = Wallet.objects.get(
                                        user=sellLimitOrderList[i].profile)

                                    if actualQuantity > sellLimitOrderList[i].quantity:
                                        profileWallet.btcWallet += sellLimitOrderList[i].quantity
                                        profileWallet.usdWallet -= (sellLimitOrderList[i].price *
                                                                    sellLimitOrderList[i].quantity)

                                        profileSeller.usdWallet += sellLimitOrderList[i].price * \
                                            sellLimitOrderList[i].quantity
                                        profileSeller.btcWallet -= sellLimitOrderList[i].quantity
                                    else:
                                        profileWallet.btcWallet += actualQuantity
                                        profileWallet.usdWallet -= (sellLimitOrderList[i].price *
                                                                    actualQuantity)

                                        profileSeller.usdWallet += sellLimitOrderList[i].price * \
                                            actualQuantity
                                        profileSeller.btcWallet -= actualQuantity

                                    profileWallet.save()
                                    profileSeller.save()

                                    if actualQuantity < sellLimitOrderList[i].quantity:
                                        sellLimitOrder.quantity -= actualQuantity
                                    else:
                                        sellLimitOrder.status = 'close'

                                    sellLimitOrder.save()

                                    messages.success(
                                        request, f'Sell order id: {sellLimitOrderList[i]._id}. || Status: {sellLimitOrderList[i].status}.')
                                    if actualQuantity < sellLimitOrderList[i].quantity:
                                        messages.success(
                                            request, f'\nThe User who Sold has Received successfully {sellLimitOrderList[i].price}$ *{actualQuantity} .')
                                        actualQuantity = 0
                                    else:
                                        messages.success(
                                            request, f'\nThe User who Sold has Received successfully {sellLimitOrderList[i].price}$ *{sellLimitOrderList[i].quantity} .')
                                        actualQuantity -= sellLimitOrderList[i].quantity

                                newBuyOrder.status = 'close'
                                newBuyOrder.save()

                                messages.success(request,
                                                 f'Your Buy order id: {newBuyOrder._id}. || Status: {newBuyOrder.status}.')
                                messages.success(request,
                                                 f'\n|| BTC before exchange: {actualBTC}; || BTC after exchange: {profileWallet.btcWallet};')

                                messages.info(
                                    request, f'\nThe bitcoin exchange has been totally executed! Congratulations!')

                                return redirect('app:order', id=id)
                            else:
                                messages.error(
                                    request, 'Order canceled. Slippage > 0.5%. Wait for new sell limit order')
                                return redirect('app:order', id=id)
                    else:
                        messages.error(
                            request, 'Order book too thin. Wait for new sell limit order')
                        return redirect('app:order', id=id)



            if request.POST.get('sell'):

                # Create sell order
                form = MarketOrderForm(request.POST or None)
                if form.is_valid():
                    status = 'open'
                    type = 'sell'
                    price = currency
                    quantity = form.cleaned_data.get('quantity')
                    profileWallet = Wallet.objects.get(user=request.user)

                    # Manage invalid data
                    if quantity <= 0.0:
                        messages.error(
                            request, 'Cannot put a quantity lower then 0')
                        return redirect('app:order', id=id)
                    if quantity > profileWallet.btcWallet:
                        messages.error(
                            request, 'Insufficent BTC to complete the order')
                        return redirect('app:order', id=id)

                    # Order matching
                    if buyLimitOrderList.exists():

                        quantityTot = 0
                        orderIndex = []

                        # Return only the buy limit orders create from other users
                        for i in range(len(buyLimitOrderList)):
                            
                            if buyLimitOrderList[i].profile == profileWallet.user:
                                continue

                            orderIndex.append(i)
                            quantityTot += buyLimitOrderList[i].quantity
                            if quantityTot >= quantity:
                                break

                        # Error if there aren't enought sell limit contract, otherwise it continues with the order's matching
                        if quantityTot < quantity:
                            messages.error(
                                request, f"There are not enough buy orders that match the request.")
                            return redirect('app:order', id=id)
                        else:
                            # Proceeds with the order's matching if the sell limit order has a price lower than 0.5% of the indicated price
                            if (100-(buyLimitOrderList[i].price/currency*100)) < 0.5:

                                newSellOrder = Order.objects.create(
                                    profile=request.user,
                                    status=status,
                                    type=type,
                                    price=price,
                                    quantity=quantity,
                                    modified=timezone.now()
                                )

                                messages.info(request,
                                              f'Order created.')
                                messages.info(request,
                                              f'Slippage < 0.5%.')
                                messages.info(request,
                                              f'Start of the bitcoin exchange. ')


                                # Find the best combination of orders to ensure the best price
                                actualQuantity = newSellOrder.quantity
                                actualBTC = profileWallet.btcWallet
                                for i in orderIndex:

                                    buyLimitOrder = Order.objects.get(
                                        _id=buyLimitOrderList[i]._id)
                                    profileBuyer = Wallet.objects.get(
                                        user=buyLimitOrderList[i].profile)

                                    if actualQuantity > buyLimitOrderList[i].quantity:
                                        profileWallet.btcWallet -= buyLimitOrderList[i].quantity
                                        profileWallet.usdWallet += (buyLimitOrderList[i].price *
                                                                    buyLimitOrderList[i].quantity)

                                        profileBuyer.usdWallet -= buyLimitOrderList[i].price * \
                                            buyLimitOrderList[i].quantity
                                        profileBuyer.btcWallet += buyLimitOrderList[i].quantity
                                    else:
                                        profileWallet.btcWallet -= actualQuantity
                                        profileWallet.usdWallet += (buyLimitOrderList[i].price *
                                                                    actualQuantity)

                                        profileBuyer.usdWallet -= buyLimitOrderList[i].price * \
                                            actualQuantity
                                        profileBuyer.btcWallet += actualQuantity

                                    profileWallet.save()
                                    profileBuyer.save()

                                    if actualQuantity < buyLimitOrderList[i].quantity:
                                        buyLimitOrder.quantity -= actualQuantity
                                    else:
                                        buyLimitOrder.status = 'close'

                                    buyLimitOrder.save()

                                    messages.success(
                                        request, f'Buy order id: {buyLimitOrderList[i]._id}. || Status: {buyLimitOrderList[i].status}.')
                                    if actualQuantity < buyLimitOrderList[i].quantity:
                                        messages.success(
                                            request, f'\nThe User who bought has Received successfully {actualQuantity} BTC.')
                                        actualQuantity = 0
                                    else:
                                        messages.success(
                                            request, f'\nThe User who bought has Received successfully {buyLimitOrderList[i].quantity} BTC.')
                                        actualQuantity -= buyLimitOrderList[i].quantity

                                newSellOrder.status = 'close'
                                newSellOrder.save()

                                messages.success(request,
                                                 f'Your Sell order id: {newSellOrder._id}. || Status: {newSellOrder.status}.')
                                messages.success(request,
                                                 f'\n|| BTC before exchange: {actualBTC}; || BTC after exchange: {profileWallet.btcWallet};')

                                messages.info(
                                    request, f'\nThe bitcoin exchange has been totally executed! Congratulations!')

                                return redirect('app:order', id=id)
                            else:
                                messages.error(
                                    request, 'Order canceled. Slippage > 0.5%. Wait for new buy limit order')
                                return redirect('app:order', id=id)
                    else:
                        messages.error(
                            request, 'Order book too thin. Wait for new buy limit order')
                        return redirect('app:order', id=id)

    return render(request, 'app/order.html', {
        'currency': currency,
        'buyLimitOrderList': buyLimitOrderList,
        'sellLimitOrderList': sellLimitOrderList,
        'domSellList': domSellList,
        'domBuyList': domBuyList,
        'maxQuantity': maxQuantity,
    })
