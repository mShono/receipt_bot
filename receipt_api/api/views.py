from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .filters import ExpenseItemFilter
from .mixins import NotFoundListMixin
from .models import (Category, Product, Currency, User,
                           Expense, ExpenseItem)
from .serializers import (CategorySerializer, ProductSerializer,
                          CurrencySerializer, UserSerializer,
                          ExpenseSerializer, ExpenseItemSerializer)


class CategoryViewSet(ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(NotFoundListMixin, ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',) 


class CurrencyViewSet(ModelViewSet):

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class UserViewSet(NotFoundListMixin, ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',) 


class ExpenseViewSet(ModelViewSet):

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_fields = {
        "user__chat_id": ["exact"],
        "created_at": ["exact", "range",],
    }
    search_fields = ('=user__chat_id', '=id',)


class ExpenseItemViewSet(NotFoundListMixin, ModelViewSet):

    queryset = ExpenseItem.objects.all()
    serializer_class = ExpenseItemSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = ExpenseItemFilter
    search_fields = ('=id',)

    @action(
        ["get"],
        detail=False,
        url_path="category_sums",
    )
    def category_sums(self, request):
        """Returns the sum of prices for each category"""
        queryset = self.filter_queryset(self.get_queryset())

        data = (
            queryset
            .values('product__category__name')
            .annotate(total_price=Sum('price'))
            .order_by('product__category__name')
        )

        result = []
        for row in data:
            result.append({'category': row['product__category__name'], 'total_price': row['total_price']})
        
        return Response(result)
