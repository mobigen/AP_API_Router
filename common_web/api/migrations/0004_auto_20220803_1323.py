# Generated by Django 3.1.3 on 2022-08-03 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20220803_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiinfo',
            name='cmd',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
