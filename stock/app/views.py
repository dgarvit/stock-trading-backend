from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import UserExt, Stocks

from web3.contract import ConciseContract

import web3
import json
import datetime
import hashlib

abi = "XXX"
contract_address="XXX"

node_url = "http://localhost:8545"

@login_required(login_url='/login/')
def index(request):
	return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            
            w3 = web3.Web3(web3.HTTPProvider(node_url))
            address = w3.personal.newAccount(raw_password)

            var = UserExt(userId=user, address = address)
            var.save()

            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def home(request):
    
    user = UserExt.objects.get(userId=request.user)
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    d={}
    d["Balance"] = w3.toEther((w3.eth.getBalance(user.address)))
    d["StockA"]  = user.StockA
    d["StockB"]  = user.StockB
    d["StockC"]  = user.StockC
    d["StockD"]  = user.StockD
    d["StockE"]  = user.StockE
    d["address"] = user.address

    d[""]

    return render(request, 'home.html', d)

def buy_stock(request):

    pass

def sell_stock(request):
    pass


