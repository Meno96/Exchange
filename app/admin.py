from django.contrib import admin
from .models import Wallet

class AdminWallet(admin.ModelAdmin):
    list_display = ("user",
                    "_id",
                    "btc_wallet",
                    "usd_wallet",
                    "btc_balance",
                    "usd_balance")

admin.site.register(Wallet, AdminWallet)