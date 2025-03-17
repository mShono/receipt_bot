from rest_framework.viewsets import ModelViewSet
from .models import (Category, Product, Currency, User,
                           Expense)
from .serializers import (CategorySerializer, ProductSerializer,
                          CurrencySerializer, UserSerializer,
                          ExpenseSerializer)

class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CurrencyViewSet(ModelViewSet):

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ExpenseViewSet(ModelViewSet):

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer