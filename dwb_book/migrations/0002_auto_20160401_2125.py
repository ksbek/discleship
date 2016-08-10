# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dwb_book', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='congratulations_text',
            field=ckeditor.fields.RichTextField(null=True, blank=True),
        ),
    ]
