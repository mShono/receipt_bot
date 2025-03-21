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
        verbose_name="User",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Category",
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Product",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Currency",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.currency is None and self.user.default_currency is not None:
            self.currency = self.user.default_currency
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Expense {self.created_at}'