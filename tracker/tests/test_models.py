import pytest
from tracker.models import Transaction

#test to be each custome method: 1)Has alrady values  2)Its type is matching
@pytest.mark.django_db
def test_queryset_get_expenses(transactions):
    qs= Transaction.objects.get_expenses()
    assert qs.count() > 0
    assert all(
        [t.type =='expense' for t in qs]
    )
    
@pytest.mark.django_db
def test_queryset_get_income(transactions):
    qs= Transaction.objects.get_income()
    assert qs.count() > 0
    assert all(
        [t.type == 'income' for t in qs]
    )
    
@pytest.mark.django_db
def test_queryset_get_total_expenses(transactions):
    total_expenses= Transaction.objects.get_total_expenses()
    
    assert total_expenses == sum(
        [t.amount for t in transactions if t.type == 'expense']
    )
    
@pytest.mark.django_db
def test_queryset_get_total_income(transactions):
    total_income= Transaction.objects.get_total_income()
    
    assert total_income == sum(
        t.amount for t in transactions if t.type == 'income'
    )