from django.db import models
from django.contrib.auth.models import User
from accounts.models import *
class OneTimeAuction(models.Model):
    team =  models.ForeignKey(Team, null=True, on_delete=models.CASCADE, related_name='oneTimeAuction')
    auction_pay_type = models.IntegerField(default=1)
    winner =  models.ForeignKey('OneTimeBidder', null=True, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

class OneTimeBidder(models.Model):
    auction = models.ForeignKey(OneTimeAuction, on_delete=models.CASCADE, related_name='bidders')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='oneTimeBidders')
    value = models.IntegerField(default=50)
    bid = models.IntegerField(default=0)
    
'''
class BritishAuction(models.Model):
    winner =  models.ForeignKey('BritishBidder', null=True, on_delete=models.CASCADE)
    Increaseـrate = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

class BritishBidder(models.Model):
    auction = models.ForeignKey(BritishAuction, on_delete=models.CASCADE, related_name='bidders')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='britishBidders')
    value = models.IntegerField()
    bid = models.IntegerField(default=0)
    
'''