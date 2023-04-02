from django.db import models

# Create your models here.


class BillingAddress(models.Model):
    full_name = models.CharField(max_length=30)
    address_1 = models.CharField(max_length=30)
    address_2 = models.CharField(max_length=30)
    town_city = models.CharField(max_length=20)
    postcode = models.CharField(max_length=10)
    region = models.CharField(max_length=20)
    country = models.CharField(max_length=20)

class CardDetails(models.Model):
    card_number = models.BigIntegerField()
    cvv = models.SmallIntegerField()
    expiry_date = models.CharField(max_length=5)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.PROTECT)

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True, editable=False)
    order_id = models.CharField(max_length=30)
    user_id = models.CharField(max_length=30)
    merchant_id = models.CharField(max_length=30)
    transaction_amount = models.DecimalField(decimal_places=2, max_digits=8)
    delivery_email = models.CharField(max_length=30)
    delivery_name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    status_choices = [("new", "New"), ("paid", "Paid"), ("refunded", "Refunded"), ("cancelled", "Cancelled")]
    status = models.CharField(max_length=10, choices=status_choices, default="New")
    callback_url = models.CharField(max_length=60, null=True)
    card_details = models.ForeignKey(CardDetails, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return u'Transaction ID: %s User ID: %s' % (self.transaction_id, self.user_id)

class Payment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    last_4_card_digits = models.SmallIntegerField()
    type_choices = [("payment", "Paid"), ("refund", "Refund")]
    type = models.CharField(max_length=10, choices=type_choices, default= "payment")
    amount = models.DecimalField(decimal_places=2, max_digits=8)