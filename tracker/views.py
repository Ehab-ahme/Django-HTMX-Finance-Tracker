from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings
from django_htmx.http import retarget
from .filters import TransactionFilter
from .models import Transaction
from .forms import TransactionForm
from .charting import plot_income_expenses_bar_char, plot_category_pie_chart
from .resources import TransactionResource
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'tracker/index.html')

@login_required
def transaction_list(request):
    transactions_filter= TransactionFilter(
        request.GET,
        queryset= Transaction.objects.filter(user= request.user).select_related('category')
    )
    paginator= Paginator(transactions_filter.qs, settings.PAGE_SIZE)
    transaction_page= paginator.page(1)
    
    total_income= transactions_filter.qs.get_total_income()
    total_expenses= transactions_filter.qs.get_total_expenses()
    context = { 
                "transactions": transaction_page,
                "filter": transactions_filter,
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_income": total_income - total_expenses}
    
    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)

    return render(request, 'tracker/transaction-list.html', context)

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form= TransactionForm(request.POST)
        if form.is_valid():
            transaction= form.save(commit=False)
            transaction.user= request.user
            transaction.save()
            context= {'message': 'Transaction was added successfully!'}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context= {'form': form}
            response= render(request, 'tracker/partials/create-transaction.html', context)
            return retarget(response, '#transaction-block')
    context= {'form': TransactionForm()}
    return render(request, 'tracker/partials/create-transaction.html', context)

@login_required
def update_transaction(request, pk):
    transaction= get_object_or_404(Transaction, pk= pk, user= request.user)
    if request.method== 'POST':
        form= TransactionForm(request.POST ,instance= transaction)
        if form.is_valid():
            transaction= form.save()
            context= {'message': 'Transaction was updated successfully!'}
            return render(request, 'tracker/partials/transaction-success.html', context)

        else:
            context= {
                'form': form,
                'transaction': transaction,
            }
            response= render(request, 'tracker/partials/update-transaction.html', context)
            return retarget(response, '#transaction-block')
    context= {
        'form': TransactionForm(instance= transaction),
        'transaction': transaction,
    }

    return render(request, 'tracker/partials/update-transaction.html', context)

@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request, pk):
    transaction= get_object_or_404(Transaction, pk= pk, user= request.user)
    transaction.delete()
    context= {
        "message": f"Transaction of {transaction.amount} on {transaction.date} was deleted successfully!"
    }
    return render(request, 'tracker/partials/transaction-success.html', context)

@login_required
def get_transactions(request):
    import time
    time.sleep(1)
    page= request.GET.get('page', 1)
    transactions_filter= TransactionFilter(
            request.GET,
            queryset= Transaction.objects.filter(user= request.user).select_related('category')
        )
    paginator= Paginator(transactions_filter.qs, settings.PAGE_SIZE)
    
    context= {
        'transactions': paginator.page(page)
    }
    return render(
                request,
                'tracker/partials/transactions-container.html#transaction_list',
                context
                )
    
@login_required
def transactions_charts(request):
    transactions_filter= TransactionFilter(
        request.GET,
        queryset= Transaction.objects.filter(user= request.user).select_related('category')
        )
    income_expenses_bar= plot_income_expenses_bar_char(transactions_filter.qs)
    
    category_income_pie = plot_category_pie_chart(
        transactions_filter.qs.filter(type="income")
    )
    category_expense_pie = plot_category_pie_chart(
        transactions_filter.qs.filter(type="expense")
    )
    
    context= {
        'filter': transactions_filter,
        'income_expense_barchar': income_expenses_bar.to_html(),
        'category_income_pie': category_income_pie.to_html(),
        'category_expense_pie': category_expense_pie.to_html(),
    }
    
    if request.htmx:
        return render(request, 'tracker/partials/charts-container.html', context)
    
    return render(request, 'tracker/charts.html', context)

@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={"HX-Redirect": request.get_full_path()})
    transactions_filter= TransactionFilter(
        request.GET,
        queryset= Transaction.objects.filter(user= request.user).select_related('category')
        )
    data= TransactionResource().export(transactions_filter.qs)
    response= HttpResponse(data.csv)
    response['Content-Disposition']= 'attachment; filename="transactions.csv"'
    return response