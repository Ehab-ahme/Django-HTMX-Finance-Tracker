from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from tracker.models import Category, Transaction
from pytest_django.asserts import assertTemplateUsed

@pytest.mark.django_db
def test_total_values_appears_on_user_page(user_transactions, client):
    user= user_transactions[0].user
    client.force_login(user)
    
    income_total= sum(t.amount for t in user_transactions if t.type =='income') 
    expense_total= sum(t.amount for t in user_transactions if t.type =='expense' )
    net= income_total - expense_total
    
    response= client.get(reverse('transactions-list'))
    
    assert response.context["total_income"] == income_total
    assert response.context["total_expenses"] == expense_total
    assert response.context["net_income"] == net

@pytest.mark.django_db    
def test_transaction_type_filter(user_transactions, client):
    user= user_transactions[0].user
    client.force_login(user)
    
    # Simulate some data comes from the user (Front-end)
    # Income check:
    GET_params= {'transaction_type': 'income'}
    response= client.get(reverse('transactions-list'), GET_params)

    qs= response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.type == 'income'
        
    # Check if the transaction it's actually True
    
    GET_params= {'transaction_type': 'expense'}
    response= client.get(reverse('transactions-list'), GET_params)
    
    qs= response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.type == 'expense'

# 1)[WHAT] Test that, if the user choose start_end date, is the result would be within these two date ??
# 2) How the date will be sent ??
# 3) what will i inspect 
@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    user= user_transactions[0].user
    client.force_login(user)

# We will simulate the case the user choose satrt_end date & we will generate START_END date using python's module
    #start_date_cutoff= datetime(year=2026, month=7, day=14).date() - timedelta(days= 120)
    start_date_cutoff= datetime(year= 2026, month=3, day= 1).date()
    GET_params= {'start_date': start_date_cutoff}

    response= client.get(reverse('transactions-list'), GET_params)
    qs= response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.date >= start_date_cutoff

    end_date_cutoff= datetime(year= 2026, month=6, day= 1).date()
    GET_params= {'end_date': end_date_cutoff}

    response= client.get(reverse('transactions-list'), GET_params)
    qs= response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.date <= end_date_cutoff
@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    user= user_transactions[0].user
    client.force_login(user)
    # Get first two categories' pks
    category_pks= Category.objects.all()[:2].values_list('pk', flat=True)
    GET_params= {'category': category_pks}


    response= client.get(reverse('transactions-list'), GET_params)
    qs= response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.category.pk in category_pks
        
@pytest.mark.django_db
def test_add_transaction_request(user, transaction_dict_params, client):
    client.force_login(user) 
    user_transaction_count= Transaction.objects.filter(user= user).count()
# Sen a request with transaction data    
    headers= {"HTTP_Hx_Request": "true"}
    response= client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
        )
# Assert the count has increased after the POST request
    assert Transaction.objects.filter(user= user).count() == user_transaction_count + 1
    assertTemplateUsed(response, 'tracker/partials/transaction-success.html')

@pytest.mark.django_db  
def test_transaction_with_negative_value(user, transaction_dict_params, client):
    client.force_login(user) 
    user_transaction_count= Transaction.objects.filter(user= user).count()

    # headers= {"HTTP_Hx_Request": "true"}
    transaction_dict_params['amount']= -50

    response= client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        # **headers
        )
    assert Transaction.objects.filter(user= user).count() == user_transaction_count
    assertTemplateUsed(response, 'tracker/partials/create-transaction.html')
    assert 'Hx-Retarget' in response.headers

@pytest.mark.django_db  
def test_updating_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    assert Transaction.objects.filter(user= user).count() == 1
    
    transaction= Transaction.objects.first()
    transaction_dict_params['amount'] = 98
    transaction_dict_params['date'] = datetime.now().date()
    
    client.post(
        reverse('update-transaction', kwargs={"pk": transaction.pk}),
        transaction_dict_params,)
    assert Transaction.objects.filter(user= user).count() == 1
    
    transaction= Transaction.objects.first()
    assert transaction_dict_params['amount'] == 98
    assert transaction_dict_params['date'] == datetime.now().date()


@pytest.mark.django_db  
def test_deleting_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    assert Transaction.objects.filter(user= user).count() == 1
    
    transaction= Transaction.objects.first()
    
    client.delete(
        reverse('delete-transaction', kwargs={'pk': transaction.pk}),
                transaction_dict_params,)
    assert Transaction.objects.filter(user= user).count() == 0
