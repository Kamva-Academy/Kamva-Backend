from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.auctionView import *
from .views.bidView import *

router = DefaultRouter()
# router.register('auction', OneTimeAuctionView)
# router.register('auction/<int:pk>', OneTimeAuctionView)
urlpatterns = [
    path('bid/', new_one_time_bid),
    path('create/', new_one_time_auction),
    path('lastAuction/', LastAuction.as_view()),
    path('result/', AuctionResult.as_view()),

    ]

urlpatterns += router.urls
