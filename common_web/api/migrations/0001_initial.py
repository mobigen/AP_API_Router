# Generated by Django 4.0.6 on 2022-09-29 05:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ServerInfo',
            fields=[
                ('srvr_nm', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('ip_adr', models.CharField(max_length=128)),
                ('domn_nm', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'db_table': 'sitemng"."api_item_server_dtl',
            },
        ),
        migrations.CreateModel(
            name='ApiInfo',
            fields=[
                ('api_nm', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('route_url', models.CharField(max_length=256, unique=True)),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('mthd', models.CharField(blank=True, max_length=64, null=True)),
                ('cmd', models.CharField(blank=True, max_length=512, null=True)),
                ('mode', models.CharField(max_length=32)),
                ('srvr_nm', models.ForeignKey(db_column='srvr_nm', on_delete=django.db.models.deletion.PROTECT, to='api.serverinfo')),
            ],
            options={
                'db_table': 'sitemng"."api_item_bas',
            },
        ),
        migrations.CreateModel(
            name='ApiParamInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nm', models.CharField(max_length=64)),
                ('data_type', models.CharField(max_length=16)),
                ('deflt_val', models.CharField(max_length=128)),
                ('api_nm', models.ForeignKey(db_column='api_nm', on_delete=django.db.models.deletion.CASCADE, to='api.apiinfo')),
            ],
            options={
                'db_table': 'sitemng"."api_item_param_dtl',
                'unique_together': {('api_nm', 'nm')},
            },
        ),
    ]
