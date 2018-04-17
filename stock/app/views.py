from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

import time

from .models import UserExt, Stocks, txnDB

from web3.contract import ConciseContract

import web3
import json
import datetime
import hashlib

abi = open("Trade.json")["abi"]
contract_address="XXX"

node_url = "http://localhost:8545"

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

            var = UserExt(userId=user, address = address,stockA=0,stockB=0, stockC=0,stockD=0, stockE=0)
            var.save()

            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required(login_url='/login/')
def index(request):
    user = UserExt.objects.get(userId=request.user)
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    d={}
    d["balance"] = w3.toEther((w3.eth.getBalance(user.address)))
    d["StockA"]  = user.StockA
    d["StockB"]  = user.StockB
    d["StockC"]  = user.StockC
    d["StockD"]  = user.StockD
    d["StockE"]  = user.StockE
    d["address"] = user.address

    d["OtherUsers"] = UserExt.objects.exclude(userId=request.user)

    d2 = {
        "A":Stocks.objects.get(name="A").price,
        "B":Stocks.objects.get(name="B").price,
        "C":Stocks.objects.get(name="C").price,
        "D":Stocks.objects.get(name="D").price,
        "E":Stocks.objects.get(name="E").price
    }

    return render(request, 'index.html', {
        'userdict': d,
        'stockdict': d2,
        })

@login_required(login_url='/login/')
def buy_stock(request):
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    cI = w3.eth.contract(abi,contract_address,ContractFactoryClass=ConciseContract) 
    if request.method == "POST":
        user = UserExt.objects.get(userId = request.user)

        raw_password = request.POST.get("password1",'')
        stock = request.POST.get("stock",'')
        quantity = request.POST.get("quantity",'')
        seller_address = request.POST.get("seller_address",'')
        seller = UserExt.objects.get(address = seller_address)
        stockObj = Stocks.objects.get(name = stock)
        tmp = {
            "A":seller.StockA,
            "B":seller.StockB,
            "C":seller.StockC,
            "D":seller.StockD,
            "E":seller.StockE
        }

        messages = []
        if (tmp[stock] <= quantity and quantity*stockObj.price <= w3.eth.getBalance(user.address)):
            w3.personal.unlockAccount(user.address,raw_password)
            txnID = hashlib.md5(request.user.address+user_address+os.urandom(4)).hexdigest()
            cI.createNewTrade.sendTransaction(txnID,user.address,user_address,{"from":user.address,"value":quantity*stockObj.price})
            cI.accept(txnID,transact={"from":user.address})
            w3.personal.unlockAccount(seller_address,raw_password)
            cI.accept(txnID,transact={"from":seller_address})
            tmp[stock] -= quantity
            tmp[stock].save()
            var = txnDB(txnID=txnID,status="pending",user=request.user,stock=stock,quantity=quantity)
            var.save()
            messages.append("Transaction " + txnID + " was successful!")

        else:
            messages.append("Error in the fields!")

        return render(request, {'messages': messages})
    else:
        render(request, 'buy.html')

@login_required(login_url='/login/')
def sell_stock(request):
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    cI = w3.eth.contract(abi,contract_address,ContractFactoryClass=ConciseContract) 
    user = UserExt.objects.get(userId = request.user)
    tmp = {
        "A":user.StockA,
        "B":user.StockB,
        "C":user.StockC,
        "D":user.StockD,
        "E":user.StockE
    }

    messages = []
    if request.method == "POST":
        
        stock = request.POST.get("stock",'')
        quantity = request.POST.get("quantity",'')
        tmp[stock] += quantity
        user.save()
        messages.append("Stock added for listing successfully!")
    
    return render(request, 'sell.html', {
        'messages': messages,
        'stocks': temp,
        })


@login_required(login_url='/login/')
def view_txns(request):
    txnList=[]  
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    cI = w3.eth.contract(abi,contract_address,ContractFactoryClass=ConciseContract) 

    tmp = txnDB.objects.all()
    head = "ALL TRANSACTIONS"
    for i in tmp:
        buyer,seller,balance=cI.getTxn(i.txnID)
        t={
            "id":i.txnID,
            "buyer":buyer,
            "seller":seller,
            "balance":balance,
            "stock":i.stock,
            "quantity":i.quantity
        }
        txnList.append(t)
    return render(request, 'transactions.html', {
        'head': head,
        'transactions': txnList,
        })


@login_required(login_url='/login/')
def view_txns_user(request):
    txnList=[]
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    cI = w3.eth.contract(abi,contract_address,ContractFactoryClass=ConciseContract) 

    tmp = txnDB.objects.filter(userId=request.user)
    for i in tmp:
        buyer,seller,balance=cI.getTxn(i.txnID)
        t={
            "id":i.txnID,
            "buyer":buyer,
            "seller":seller,
            "balance":balance,
            "stock":i.stock,
            "quantity":i.quantity
        }
        txnList.append(t)

    head = "MY TRANSACTIONS"
    return render(request, 'transactions.html', {
        'head': head,
        'transactions': txnList,
        })
