from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

import time

from .models import UserExt, Stocks, TxnDB

from web3.contract import ConciseContract

import web3
import json
import datetime
import hashlib
import os

abi = json.load(open("./Trade.json"))["abi"]
contract_address="0x2063c81d7a8c1a3be3ad92b8fae6c24f5186c946"

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
    d["balance"] = w3.eth.getBalance(user.address)
    d["StockA"]  = user.stockA
    d["StockB"]  = user.stockB
    d["StockC"]  = user.stockC
    d["StockD"]  = user.stockD
    d["StockE"]  = user.stockE
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
        quantity = int(request.POST.get("quantity",''))
        seller_address = request.POST.get("seller_address",'')
        seller = UserExt.objects.get(address = seller_address)
        stockObj = Stocks.objects.get(name = stock)
        tmp = {
            "A":seller.stockA,
            "B":seller.stockB,
            "C":seller.stockC,
            "D":seller.stockD,
            "E":seller.stockE
        }

        messages = []
        print (tmp[stock],quantity,quantity*stockObj.price,w3.eth.getBalance(user.address))
        if (tmp[stock] >= int(quantity) and quantity*stockObj.price <= w3.eth.getBalance(user.address)):
            w3.personal.unlockAccount(user.address,raw_password)
            txnID = hashlib.md5(bytes(user.address+seller_address,"utf-8")+os.urandom(4)).hexdigest()
            print(cI.__dict__)
            
            cI.createNewTrade(txnID,user.address,seller_address,transact={"from":user.address,"value":quantity*stockObj.price})
            cI.accept(txnID,transact={"from":user.address})
            w3.personal.unlockAccount(seller_address,raw_password)
            cI.accept(txnID,transact={"from":seller_address})
            tmp[stock] -= int(quantity)
            if stock=="A":
                seller.stockA-=int(quantity)
            if stock=="B":
                seller.stockB-=int(quantity)
            if stock=="C":
                seller.stockC-=int(quantity)
            if stock=="D":
                seller.stockD-=int(quantity)
            if stock=="E":
                seller.stockE-=int(quantity)
            seller.save()
            if stock=="A":
                user.stockA+=int(quantity)
            if stock=="B":
                user.stockB+=int(quantity)
            if stock=="C":
                user.stockC+=int(quantity)
            if stock=="D":
                user.stockD+=int(quantity)
            if stock=="E":
                user.stockE+=int(quantity)

            user.save()
            var = TxnDB(txnID=txnID,status="pending",user=user,stock=stock,quantity=quantity)
            var.save()
            messages.append("Transaction " + txnID + " was successful!")

        else:
            messages.append("Error in the fields!")

        return render(request, 'buy.html', {'messages': messages})
    else:
        return render(request, 'buy.html')

@login_required(login_url='/login/')
def sell_stock(request):
    w3 = web3.Web3(web3.HTTPProvider(node_url))
    cI = w3.eth.contract(abi=abi,address=w3.toChecksumAddress(contract_address)) 
    user = UserExt.objects.get(userId = request.user)
    tmp = {
        "A":user.stockA,
        "B":user.stockB,
        "C":user.stockC,
        "D":user.stockD,
        "E":user.stockE
    }

    messages = []
    if request.method == "POST":
        
        stock = request.POST.get("stock",'')
        quantity = request.POST.get("quantity",'')
        
        tmp[stock] += int(quantity)
        if stock=="A":
            user.stockA+=int(quantity)
        if stock=="B":
            user.stockB+=int(quantity)
        if stock=="C":
            user.stockC+=int(quantity)
        if stock=="D":
            user.stockD+=int(quantity)
        if stock=="E":
            user.stockE+=int(quantity)

        user.save()
        messages.append("Stock added for listing successfully!")
    
    return render(request, 'sell.html', {
        'messages': messages,
        'stocks': tmp,
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
