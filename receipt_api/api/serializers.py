from .models import (Category, Product, Currency, User,
                           Expense, ExpenseItem)
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "id"
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name",
            "id",
            "category"
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
            "id",
            "chat_id",
            "username",
            "first_name",
            "last_name",
            "default_currency",
        )


class ExpenseItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseItem
        fields = (
            "id",
            "expense",
            "product",
            "price",
        )


class ExpenseSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(read_only=True)
    items = ExpenseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "user",
            "items",
            "currency",
            "created_at",
        )
