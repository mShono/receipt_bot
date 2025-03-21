from .models import (Category, Product, Currency, User,
                           Expense)
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name",
        )


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = (
            "code",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "chat_id",
            "username",
            "first_name",
            "last_name",
            "default_currency",
        )


class ExpenseSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = (
            "user",
            "category",
            "product",
            "amount",
            "currency",
            "created_at",
        )
