from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.
class Settings(models.Model):
    USD = "USD"
    PLN = "PLN"
    EUR = "EUR"
    MAIN_CURRENCY_CHOICES = [
        (USD, "United States Dollar"),
        (PLN, "Polish Złoty"),
        (EUR, "Euro")
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="settings"
    )
    main_currency = models.CharField(
        max_length=3,
        choices=MAIN_CURRENCY_CHOICES,
        default=USD
    )
    
    def __str__(self) -> str:
        return f"Main currency: {self.main_currency}"


class Category(models.Model):
    INCOME = "I"
    EXPENSE = "E"
    CATEGORY_TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense")
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    name = models.CharField(
        max_length=50
    )
    category_type = models.CharField(
        max_length=1,
        choices=CATEGORY_TYPE_CHOICES,
        default=EXPENSE
    )
    total = models.DecimalField(
        max_digits=22,
        decimal_places=2
    )
    
    def __str__(self) -> str:
        return f"{self.name} - {self.total}"
    
    
class Currency(models.Model):
    code = models.CharField(
        max_length=3,
        unique=True
    )
    name = models.CharField(
        max_length=40,
        unique=True
    )
    exchange_rates = models.JSONField()
    
    def __str__(self) -> str:
        return f"{self.code}    {self.name}"


class Account(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="accounts"
    )
    name = models.CharField(
        max_length=50
    )
    balance = models.DecimalField(
        max_digits=22,
        decimal_places=2
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="accounts"
    )
    description = models.CharField(
        max_length=100
    )
    
    def __str__(self) -> str:
        return f"{self.name} - {self.balance} {self.currency.code}"
    
    
class Transaction(models.Model):
    INCOME = "I"
    EXPENSE = "E"
    TRANSFER = "T"
    TRANSACTION_TYPE_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
        (TRANSFER, "Transfer")
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=1,
        choices=TRANSACTION_TYPE_CHOICES,
        default=EXPENSE
    )
    amount = models.DecimalField(
        max_digits=22,
        decimal_places=2
    )
    date = models.DateField(
        default=datetime.date.today
    )
    description = models.CharField(
        max_length=100
    )
    
    def __str__(self) -> str:
        amount_sign = "-"
        if self.transaction_type == self.INCOME:
            amount_sign = "+"
        elif self.transaction_type == self.TRANSFER:
            amount_sign = ""
            
        return f"{self.category.name} {self.account.name} \
{amount_sign + self.amount} {self.description}"
