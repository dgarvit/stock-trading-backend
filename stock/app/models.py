from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserExt(models.Model):
	userId = models.OneToOneField(User, on_delete=models.CASCADE)
	address = models.CharField(max_length=42)
	stockA = models.IntegerField()
	stockB = models.IntegerField()
	stockC = models.IntegerField()
	stockD = models.IntegerField()
	stockE = models.IntegerField()

class Stocks(models.Model):
	STOCKS = (
		('A','StockA'),
		('B','StockB'),
		('C','StockC'),
		('D','StockD'),
		('E','StockE')
	)
	name = models.CharField(max_length=1, choices = STOCKS, primary_key=True)
	price = models.IntegerField()
	quantity = models.IntegerField()
	available = models.IntegerField()

class TxnDB(models.Model):
	STOCKS = (
		('A','StockA'),
		('B','StockB'),
		('C','StockC'),
		('D','StockD'),
		('E','StockE')
	)
	txnID = models.CharField(max_length=32)
	user = models.ForeignKey(UserExt, on_delete=models.CASCADE)
	status = models.CharField(max_length=10)
	stock = models.CharField(max_length=1, choices = STOCKS)
	quantity = models.IntegerField()