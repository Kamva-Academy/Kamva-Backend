from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    pass

class Account(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, unique=True, related_name='account')

class OneTimeAuction(models.Model):
    winner =  models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    max_bid = models.IntegerField(default=0)


class OneTimeBidder(models.Model):
    auction = models.ForeignKey(OneTimeAuction, on_delete=models.CASCADE, related_name='bidders')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='oneTimeBidders')
    value = models.IntegerField()
    bid = models.IntegerField(default=0)
    
 
class BritishAuction(models.Model):
    winner =  models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    max_bid = models.IntegerField(default=0)
    Increaseـrate = models.IntegerField(default=0)

class BritishBidder(models.Model):
    auction = models.ForeignKey(BritishAuction, on_delete=models.CASCADE, related_name='bidders')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='britishBidders')
    value = models.IntegerField()
    bid = models.IntegerField(default=0)
    
