# Generated by Django 4.1.7 on 2023-03-31 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=30)),
                ('address_1', models.CharField(max_length=30)),
                ('address_2', models.CharField(max_length=30)),
                ('town_city', models.CharField(max_length=20)),
                ('postcode', models.CharField(max_length=10)),
                ('region', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CardDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.BigIntegerField()),
                ('cvv', models.SmallIntegerField()),
                ('expiry_date', models.DateField()),
                ('billing_address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payments.billingaddress')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=30)),
                ('user_id', models.CharField(max_length=30)),
                ('merchant_id', models.CharField(max_length=30)),
                ('transaction_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date_created', models.DateField()),
                ('status', models.CharField(choices=[('new', 'New'), ('paid', 'Paid'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], default='New', max_length=10)),
                ('callback_url', models.CharField(max_length=60)),
                ('card_details', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payments.carddetails')),
                ('delivery_info', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payments.deliveryinfo')),
            ],
        ),
    ]