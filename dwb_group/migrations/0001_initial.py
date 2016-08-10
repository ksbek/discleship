# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dwb_book', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('date_started', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dwb_group',
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'pending', max_length=16, choices=[(b'pending', 'Pending'), (b'accepted', 'Accepted')])),
                ('recipient_email', models.EmailField(max_length=255, null=True, verbose_name="Recipient's email", blank=True)),
                ('recipient_name', models.CharField(max_length=255, null=True, verbose_name="Recipient's name", blank=True)),
                ('code', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_accepted', models.DateTimeField(null=True, blank=True)),
                ('group', models.ForeignKey(related_name='+', to='dwb_group.Group')),
                ('recipient_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sender_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dwb_invite',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='dwb_group.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dwb_member',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'draft', max_length=16, choices=[(b'draft', 'Draft'), (b'sent', 'Sent'), (b'failed', 'Failed')])),
                ('recipient_email', models.CharField(max_length=255, null=True, blank=True)),
                ('text', models.TextField()),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('recipient_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sender_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dwb_message',
            },
        ),
    ]
