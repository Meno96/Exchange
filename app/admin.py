from django.contrib import admin
from .models import Wallet, Order, Profile


class AdminWallet(admin.ModelAdmin):
    list_display = ("user", "_id", "btcWallet", "usdWallet", "btcBalance", "usdBalance")

class AdminOrder(admin.ModelAdmin):
    list_display = ("_id", "profile", "created", "status", "type")

class AdminProfile(admin.ModelAdmin):
    list_display = ["user", "_id"]


admin.site.register(Wallet, AdminWallet)
admin.site.register(Order, AdminOrder)
admin.site.register(Profile, AdminProfile)
