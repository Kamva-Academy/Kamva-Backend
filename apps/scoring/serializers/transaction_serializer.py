from rest_framework import serializers
from apps.scoring.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['value', 'description', 'to']
