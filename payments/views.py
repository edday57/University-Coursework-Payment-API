from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.core import serializers
from django.shortcuts import get_object_or_404
from .models import Transaction, BillingAddress, CardDetails, Payment
import json
import random
# Create your views here.

def validateNewTransaction(obj):
    if "user_id" in obj and "order_id" in obj and "merchant_id" in obj and "delivery_email" in obj and "delivery_name" in obj and "amount" in obj:
        if type(obj['user_id']) != str:
            return False
        if type(obj['order_id']) != str:
            return False
        if type(obj['merchant_id']) != str:
            return False
        if type(obj['delivery_email']) != str:
            return False
        if type(obj['delivery_name']) != str:
            return False
        if type(obj['amount']) != float:
            return False
        return True
    return False

def validateBillingAddress(obj):
    if "fullname" in obj and "address_1" in obj and "address_2" in obj and "town_city" in obj and "postcode" in obj and "region" in obj and "country" in obj:
        for field in obj:
            if type(obj[field]) != str:
                return False
        return True
    return False

def validateCardDetails(obj):
    if "card_number" in obj and "cvv" in obj and "expiry_date" in obj:
        if type(obj['card_number']) != int:
            return False
        if type(obj['cvv']) != int:
            return False
        if type(obj['expiry_date']) != str:
            return False
        return True
    return False

def verifyCardDetails(obj):
    if len(str(obj["card_number"])) < 8 or len(str(obj["card_number"])) > 19:
        return 1
    if len(str(obj["cvv"])) != 3 and len(str(obj["cvv"])) != 4:
        return 2
    expiry = obj["expiry_date"]
    if len(expiry) != 5:
        return 3
    try:
        month = int(expiry[:2])
        year = int(expiry[-2:])
        if month < 0 or month > 12:
            return 3
        if year < 23 or year > 30:
            return 3
    except:
        return 3
    return 0
    
@csrf_exempt
def createTransaction(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        if not validateNewTransaction(body):
            return HttpResponse('Please ensure the request contains all required fields in the correct format.')
        else:
            #Valid body
            transaction = Transaction.objects.create(user_id=body['user_id'],
            order_id=body['order_id'],
            merchant_id=body['merchant_id'], 
            transaction_amount=body['amount'], 
            delivery_email=body['delivery_email'],
            delivery_name=body['delivery_name'],
            )
            return HttpResponse(transaction)
    else: 
        return HttpResponse('This API route only accepts POST requests')

@csrf_exempt
def getTransaction(request, id):
    if request.method == 'GET':
        try:
            transaction = Transaction.objects.get(transaction_id=id)
            data = serializers.serialize('json', [transaction,])
            struct = json.loads(data)
            data = addPK(struct[0])
            return HttpResponse(json.dumps(data))
        except:
            return HttpResponse('Transaction could not be found', status = 404) 
    else: 
        return HttpResponse('This API route only accepts GET requests')

@csrf_exempt
def getUserTransactions(request, id):
    if request.method == 'GET':
        transactions = Transaction.objects.filter(user_id=id).order_by('-date_created')
        data = serializers.serialize('json', transactions)
        transactions = []
        struct = json.loads(data)
        for item in struct:
            transactions.append(addPK(item))
        return HttpResponse(json.dumps(transactions))
    else: 
        return HttpResponse('This API route only accepts GET requests')

@csrf_exempt
def makePayment(request, id):
    if request.method == 'POST':
        body = json.loads(request.body)
        if "cardDetails" in body and "billingAddress" in body:
            if not validateBillingAddress(body['billingAddress']):
                return HttpResponse('Please ensure the request contains all required fields in the correct format.')
            elif not validateCardDetails(body['cardDetails']):
                return HttpResponse('Please ensure the request contains all required fields in the correct format.')
            else:
                #Valid body
                verify = verifyCardDetails(body['cardDetails'])
                if verify == 0:
                    rand = random.randint(0,20)
                    if rand == 20:
                        return HttpResponse("Payment authentication error", status=400)
                    try:
                        transaction = Transaction.objects.get(transaction_id=id)
                        #return HttpResponse(transaction.status, status=400)
                        if transaction.status != "New":
                            return HttpResponse("Payment has already been made.", status=400)
                        #Save billing and card details
                        billing = BillingAddress.objects.create(full_name=body['billingAddress']['fullname'],
                        address_1=body['billingAddress']['address_1'],
                        address_2=body['billingAddress']['address_2'],
                        town_city=body['billingAddress']['town_city'],
                        postcode=body['billingAddress']['postcode'],
                        region=body['billingAddress']['region'],
                        country=body['billingAddress']['country'])
                        card = CardDetails.objects.create(card_number=body['cardDetails']['card_number'],
                        cvv=body['cardDetails']['cvv'],
                        expiry_date=body['cardDetails']['expiry_date'],
                        billing_address=billing)
                        payment = Payment.objects.create(transaction=transaction,
                        last_4_card_digits = str(body['cardDetails']['card_number'])[-4:],
                        amount = transaction.transaction_amount)
                        #Update transaction
                        transaction.card_details=card
                        transaction.status="paid"
                        transaction.save()
                        return HttpResponse("Payment completed successfully")
                    except:
                        return HttpResponse('Transaction could not be found', status = 404) 
                elif verify == 1:
                    return HttpResponse("Card Details invalid", status=400)
                elif verify == 2:
                    return HttpResponse("CVV invalid", status=400)
                elif verify == 3:
                    return HttpResponse("Expiry Date invalid", status=400)
        else:
            return HttpResponse('Please ensure the request contains all required fields in the correct format.')
    else: 
        return HttpResponse('This API route only accepts POST requests')   

@csrf_exempt
def refundTransaction(request, id):
    if request.method == 'GET':
        try:
            transaction = Transaction.objects.get(transaction_id=id)
            if transaction.status == "Paid":
                payment = Payment.objects.create(transaction=transaction,
                            last_4_card_digits = str(transaction.card_details.card_number)[-4:],
                            amount = transaction.transaction_amount,
                            type="refund")
                transaction.status = "refunded"
                transaction.save()
                return HttpResponse('Payment refunded successfully')
            else:
                return HttpResponse('Payment could not be refunded', status = 400) 
        except:
            return HttpResponse('Transaction could not be found', status = 404) 
    else: 
        return HttpResponse('This API route only accepts GET requests')  

@csrf_exempt
def cancelTransaction(request, id):
    if request.method == 'GET':
        try:
            transaction = Transaction.objects.get(transaction_id=id)
            if transaction.status == "New":
                transaction.status = "cancelled"
                transaction.save()
                return HttpResponse('Transaction cancelled successfully')
            else:
                return HttpResponse('Payment has already been made or refunded.', status = 400)
        except:
            return HttpResponse('Transaction could not be found', status = 404) 
    else: 
        return HttpResponse('This API route only accepts GET requests')  

def makeJson(data):
    fields = data['fields']
    fields['transaction_id'] = data['pk']
    return json.dumps(fields)

def addPK(data):
    fields = data['fields']
    cardId = fields['card_details']
    if cardId != None:
        cardDetails = CardDetails.objects.get(id=cardId)
        fields['last_4_card_digits'] = str(cardDetails.card_number)[-4:]
    fields.pop('card_details')
    fields['transaction_id'] = data['pk']
    return fields