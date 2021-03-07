# from datetime import datetime
#
# from django.db import models
# from django.contrib.auth.models import User
# from accounts.models import *
#
# class OneTimeAuction(models.Model):
#     auction_pay_type = models.IntegerField(default=1)
#     winner =  models.ForeignKey('OneTimeBidder', null=True, on_delete=models.CASCADE)
#     start_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#
#     # end_time = models.DateTimeField(null=True, blank=True, default=timezone.localtime()+timedelta(minutes=3))
#
#     def end_time(self):
#         return self.start_time + timedelta(minutes=3)
#
#
# class OneTimeBidder(models.Model):
#     auction = models.ForeignKey(OneTimeAuction, on_delete=models.CASCADE, related_name='bidders')
#     # participant = models.ForeignKey(accounts.Participant, on_delete=models.CASCADE, related_name='oneTimeBidders')
#     value = models.IntegerField(default=50)
#     bid = models.IntegerField(default=0)
#
