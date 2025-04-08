from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import (Category, Product, Currency, User,
                           Expense, ExpenseItem)
from .serializers import (CategorySerializer, ProductSerializer,
                          CurrencySerializer, UserSerializer,
                          ExpenseSerializer, ExpenseItemSerializer)

class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',) 


    def list(self, request, *args, **kwargs):
        """Redefining the list function so that it returns status.HTTP_404_NOT_FOUND"""

        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CurrencyViewSet(ModelViewSet):

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',) 


class ExpenseViewSet(ModelViewSet):

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class ExpenseItemViewSet(ModelViewSet):

    queryset = ExpenseItem.objects.all()
    serializer_class = ExpenseItemSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=id',) 
