from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """ User auth serializer """
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=32)


class RefillSerializer(serializers.Serializer):
    """ Refill serializer """
    username = serializers.CharField(max_length=32)
    amount = serializers.IntegerField


class TransactionsSerializer(serializers.Serializer):
    """ Transaction serializer """
    deposit_id = serializers.CharField(max_length=32)


class GameCreateSerializer(serializers.Serializer):
    """ Game creation serializer """
    name = serializers.CharField(max_length=32)
    title = serializers.CharField(max_length=32)


class GameBuySerializer(serializers.Serializer):
    """ Game buy serializer """
    game_id = serializers.CharField(max_length=32)
    username = serializers.CharField(max_length=32)
