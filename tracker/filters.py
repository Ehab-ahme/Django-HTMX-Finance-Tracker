import django_filters
from django import forms
from .models import Transaction, Category

class TransactionFilter(django_filters.FilterSet):
    transaction_type= django_filters.ChoiceFilter(
        choices= Transaction.TRANSACTION_TYPE_CHOICES,
        field_name= "type",
        lookup_expr= "iexact",
        empty_label= "any"
    )
    transaction_category= django_filters.CharFilter(
        field_name= 'category',
        lookup_expr='iexact',
        label='category')
    
    start_date= django_filters.DateFilter(
        field_name= 'date',
        lookup_expr= 'gte',
        label= 'Dste From',
        widget= forms.DateInput(attrs={'type': 'date'})
    )
    
    end_date= django_filters.DateFilter(
            field_name= 'date',
            lookup_expr= 'lte',
            label= 'Date To',
            widget= forms.DateInput(attrs={'type':'date'})
        )
    
    category= django_filters.ModelMultipleChoiceFilter(queryset= Category.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple())
    
    class Meta:
        model= Transaction
        fields= ('transaction_type', 'start_date', 'end_date', 'category')