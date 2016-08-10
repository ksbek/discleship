# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import ckeditor.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'en', max_length=8, choices=[(b'en', 'English'), (b'es', 'Spanish')])),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('date_available', models.DateTimeField(help_text='When book became available', null=True, blank=True)),
                ('status', models.CharField(default=b'draft', max_length=255, choices=[(b'active', 'Active'), (b'hidden', 'Hidden'), (b'draft', 'Draft'), (b'deleted', 'Deleted')])),
                ('cover_image', models.ImageField(upload_to=b'workbook-cover')),
                ('style_css', models.TextField(help_text="Use class 'book-display'", null=True, blank=True)),
                ('price', models.DecimalField(max_digits=18, decimal_places=2)),
                ('priest_price', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('congratulations_text', ckeditor.fields.RichTextField()),
                ('certificate_background', models.ImageField(height_field=b'certificate_background_height', width_field=b'certificate_background_width', upload_to=b'workbook-certificate')),
                ('certificate_background_width', models.IntegerField()),
                ('certificate_background_height', models.IntegerField()),
                ('certificate_name_top', models.FloatField(help_text='Position of name from top in %', verbose_name=b'Name top-offset')),
                ('sort_order', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'workbook_book',
            },
        ),
        migrations.CreateModel(
            name='Copy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255, choices=[(b'preview', 'Preview'), (b'progress', 'In Progress'), (b'completed', 'Completed')])),
                ('overall_progress', models.FloatField(default=0)),
                ('completed_date', models.DateField(default=datetime.datetime.now, null=True, blank=True)),
                ('certificate_number', models.IntegerField(default=0)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
            ],
            options={
                'db_table': 'workbook_copy',
                'verbose_name_plural': 'Copies',
            },
        ),
        migrations.CreateModel(
            name='FileForDownload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=b'files-for-download')),
                ('book', models.ForeignKey(related_name='+', to='dwb_book.Book')),
            ],
            options={
                'db_table': 'workbook_file_for_download',
                'verbose_name_plural': 'Files For Download',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_type', models.CharField(blank=True, max_length=255, db_column=b'type', choices=[(b'h1', 'Heading 1'), (b'h2', 'Heading 2'), (b'h3', 'Heading 3'), (b'text', 'Text'), (b'textarea', 'Type-in Question'), (b'boolean', 'Yes/No Question'), (b'radio', 'Choose One Question')])),
                ('intro', models.TextField(null=True, blank=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('content', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('footnotes', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('data', models.TextField(null=True, blank=True)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
            ],
            options={
                'db_table': 'workbook_item',
            },
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('placeholder', models.CharField(max_length=255)),
                ('replacement', models.TextField()),
                ('style_css', models.TextField(null=True, blank=True)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
            ],
            options={
                'db_table': 'workbook_marker',
            },
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_quantity', models.IntegerField(help_text='Minimum quantity for this pricing')),
                ('price', models.DecimalField(max_digits=18, decimal_places=2)),
                ('book', models.ForeignKey(to='dwb_book.Book')),
            ],
            options={
                'ordering': ['book', 'min_quantity'],
                'db_table': 'workbook_price',
                'verbose_name_plural': 'pricing',
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('copy', models.ForeignKey(to='dwb_book.Copy')),
                ('item', models.ForeignKey(to='dwb_book.Item')),
            ],
            options={
                'db_table': 'workbook_response',
            },
        ),
        migrations.AddField(
            model_name='copy',
            name='current_item',
            field=models.ForeignKey(blank=True, to='dwb_book.Item', null=True),
        ),
        migrations.AddField(
            model_name='copy',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='first_appendix_heading',
            field=models.ForeignKey(related_name='+', blank=True, to='dwb_book.Item', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='first_payed_heading',
            field=models.ForeignKey(related_name='+', blank=True, to='dwb_book.Item', null=True),
        ),
        migrations.AlterOrderWithRespectTo(
            name='item',
            order_with_respect_to='book',
        ),
    ]
