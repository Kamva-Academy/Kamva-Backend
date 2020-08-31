from django.contrib import admin

# Register your models here.
from auction.models import OneTimeAuction, OneTimeBidder

admin.site.register(OneTimeAuction)
admin.site.register(OneTimeBidder)

