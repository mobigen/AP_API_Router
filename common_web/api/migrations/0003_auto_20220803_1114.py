# Generated by Django 3.1.3 on 2022-08-03 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220802_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverinfo',
            name='domn_nm',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
