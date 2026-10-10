import random
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import User, Transaction, Category

class Command(BaseCommand):
    help= "Generates transaction for testing"
    
    def handle(self, *args, **options):
        fake= Faker()
        # Create categories
        categories= [
            "Bills",
            "Food",
            "Clothes",
            "Medical",
            "Housing",
            "Salary",
            "Social",
            "Transport",
            "Vacation",
        ]
        for category in categories:
            Category.objects.get_or_create(name= category)
            
        # Get user
        user= User.objects.filter(username= "joker").first()
        if not user:
            User.objects.create_superuser(username= "joker", password= "joker123")
            
        type= [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        categories= Category.objects.all()
        for i in range(20):
            Transaction.objects.create(
                user=user,
                category= random.choice(categories),
                type= random.choice(type),
                amount= random.uniform(1, 2500),
                date= fake.date_between(start_date= '-1y', end_date= 'today')
            )