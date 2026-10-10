from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQeurySet

class User(AbstractUser):
    pass

# Transaction can be eather Income or Expense
# Has an amount
# Has a CATEGORY (FK)
# Is tied to User (FK)
# Has a DATE

class Category(models.Model):
    name= models.CharField(max_length=50, unique=True)
    class Meta():
        verbose_name_plural= 'categories'
    
    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES= (
        ("income", "Income"),
        ("expense", "Expense"),
    )
    
    user= models.ForeignKey(User, on_delete=models.CASCADE )
    category= models.ForeignKey(Category, on_delete=models.CASCADE)
    type= models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    date= models.DateField()
    objects= TransactionQeurySet().as_manager()
    
    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date} by {self.user}"
    
    class Meta():
        ordering = ['-date']