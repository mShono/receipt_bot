from django.urls import include, path
from rest_framework import routers

from .views import CategoryViewSet, ProductViewSet, CurrencyViewSet, UserViewSet, ExpenseViewSet


router = routers.DefaultRouter()
router.register("category", CategoryViewSet)
router.register("product", ProductViewSet)
router.register("currency", CurrencyViewSet)
router.register("users", UserViewSet)
router.register("expense", ExpenseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
