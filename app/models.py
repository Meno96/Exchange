from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Classe che attribuisce l'IP e la data di accesso
class IpAddress(models.Model):
    pubDate = models.DateTimeField('date published')
    ipAddress = models.GenericIPAddressField()

class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Wallet(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    btcWallet = models.FloatField(default=0)
    usdWallet = models.FloatField(default=0)
    startValue = models.FloatField(default=0)

    def __str__(self):
        text = f"Wallet n. {self._id}. User owner: {self.user}"
        return text

class Order(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=5)
    type = models.CharField(max_length=9)
    price = models.FloatField(default=None)
    quantity = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_id(self):
        return self._id