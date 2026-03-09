from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal

from decimal import Decimal
from django.core.exceptions import ValidationError

class Account(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    def __str__(self):
        return self.name

    def deposit(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += amount
        self.save()

        Transaction.objects.create(
            account=self,
            amount=float(amount),
            action="deposit"
        )

    def withdraw(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValidationError("Insufficient funds")
        self.balance -= amount
        self.save()

        Transaction.objects.create(
            account=self,
            amount=float(amount),
            action="withdraw"
        )

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    amount = models.FloatField()
    action = models.CharField(max_length=10, choices=[("deposit", "Deposit"), ("withdraw", "Withdraw")])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.amount} for {self.account.name} on {self.date}"