from django.contrib import admin
from .models import Wallet, Order


class AdminWallet(admin.ModelAdmin):
    list_display = ("user", "_id", "btcWallet", "usdWallet", "btcBalance", "usdBalance")

class AdminOrder(admin.ModelAdmin):
    list_display = ("_id", "user", "created", "status", "type")


admin.site.register(Wallet, AdminWallet)
admin.site.register(Order, AdminOrder)
