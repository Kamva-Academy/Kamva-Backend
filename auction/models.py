from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    pass

class Account(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, unique=True, related_name='account')


class OneTimeBidder(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='oneTimeBidder')
    value = models.IntegerField()
    bid = models.IntegerField(default=0)
    
 
class BritishBidder(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='britishBidder')
    value = models.IntegerField()
    bid = models.IntegerField(default=0)
    
