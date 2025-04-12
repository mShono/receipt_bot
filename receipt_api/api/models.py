from django.contrib.auth import get_user_model
from django.db import models

from receipt_api import constants


class Category(models.Model):

    name = models.CharField(
        "Category",
        max_length=constants.MAX_LEN_CATEGORY_NAME,
        unique=True
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        "Product",
        max_length=constants.MAX_LEN_PRODUCT_NAME,
        unique=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category",
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class Currency(models.Model):

    code = models.CharField(
        "Code",
        max_length=3,
        choices=constants.CURRENCY
        )

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.code

class User(models.Model):

    chat_id = models.IntegerField("Chat_id")
    username = models.CharField(
        "Username",
        max_length=constants.MAX_LEN_USER_INFO,
        unique=True,
        error_messages={
            "unique": "A user with such name already exists"
        },
    )
    first_name = models.CharField(
        "Name",
        max_length=constants.MAX_LEN_USER_INFO,
    )
    last_name = models.CharField(
        "Last name",
        max_length=constants.MAX_LEN_USER_INFO,
    )
    default_currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
        verbose_name="Default currency",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expence",
        verbose_name="User",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expence",
        verbose_name="Currency",
    )
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.currency is None and self.user.default_currency is not None:
            self.currency = self.user.default_currency
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} {self.user}"


class ExpenseItem(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Expense"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Product"
    )
    price = models.PositiveIntegerField(
        "Price",)

    def __str__(self):
        return f"{self.product} for {self.price}"