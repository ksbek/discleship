# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dwb_group', '0001_initial'),
        ('dwb_book', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invoice_number', models.CharField(unique=True, max_length=36)),
                ('uuid', models.CharField(unique=True, max_length=36)),
                ('status', models.CharField(default=b'pending', max_length=16, choices=[(b'pending', 'Pending'), (b'payed', 'Payed'), (b'canceled', 'Canceled'), (b'failed', 'Failed')])),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('buyer_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('recipient_name', models.CharField(max_length=255, null=True, blank=True)),
                ('recipient_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=18, decimal_places=2)),
                ('total_charge', models.DecimalField(max_digits=18, decimal_places=2)),
                ('gift_code', models.CharField(max_length=255, null=True, blank=True)),
                ('api_log', models.TextField(blank=True)),
                ('api_data', models.TextField(default=b'{}')),
                ('church_name', models.CharField(max_length=255, null=True, blank=True)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
                ('buyer_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('group', models.ForeignKey(related_name='+', blank=True, to='dwb_group.Group', help_text='Group to join.', null=True)),
            ],
            options={
                'db_table': 'dwb_purchase',
            },
        ),
        migrations.CreateModel(
            name='PurchaseClaim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(unique=True, max_length=36)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('copy', models.ForeignKey(to='dwb_book.Copy')),
                ('purchase', models.ForeignKey(related_name='claims', to='dwb_store.Purchase')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dwb_purchase_claim',
            },
        ),
    ]
