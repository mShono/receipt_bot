from django.contrib import admin

from .models import (Category, Product, Currency, User,
                           Expense, ExpenseItem)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("pk", "code")
    list_display_links = ("code",)
    search_fields = ("code",)
    empty_value_display = "-пусто-"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "chat_id", "username", "first_name", "last_name", "default_currency")
    list_display_links = ("username",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "currency", "created_at")
    list_display_links = ("pk",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ("pk", "expense", "product", "price")
    list_display_links = ("pk",)
    search_fields = ("product",)
    empty_value_display = "-пусто-"