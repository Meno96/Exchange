from djongo.models.fields import ObjectIdField, Field
from django.contrib.auth.models import User
from django.db import models

class Wallet(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    btc_wallet = models.FloatField(default=0)
    usd_wallet = models.FloatField(default=0)
    btc_balance = models.FloatField(default=0)
    usd_balance = models.FloatField(default=0)

    def __str__(self):
        text = f"Wallet n. {self._id}. User owner: {self.user}"
        return text