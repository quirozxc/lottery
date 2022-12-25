# Generated by Django 4.1.3 on 2022-12-25 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BettingAgency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name of betting agency')),
                ('tax_id', models.CharField(max_length=15, verbose_name='Tax Identification Number')),
                ('description', models.CharField(blank=True, max_length=512, null=True, verbose_name='Betting agency description')),
                ('currency', models.CharField(choices=[('0', 'Bs.S'), ('1', 'USD'), ('2', 'COP')], max_length=2, verbose_name='Currency')),
                ('minimum_bet', models.PositiveIntegerField(verbose_name='Minimum bet')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Betting Agency',
                'db_table': 'betting_agency',
            },
        ),
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name of icon')),
                ('identifier', models.PositiveIntegerField(verbose_name='Numeric Identifier')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='icon', verbose_name='Logo')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'icon',
            },
        ),
        migrations.CreateModel(
            name='Lottery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name of lottery')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='lottery', verbose_name='Logo')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'lottery',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miercoles'), ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')], max_length=1, verbose_name='Day')),
                ('turn', models.TimeField(verbose_name='Draw schedule')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('lottery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery')),
            ],
            options={
                'db_table': 'schedule',
                'unique_together': {('lottery', 'day', 'turn')},
            },
        ),
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bet_multiplier', models.PositiveIntegerField(verbose_name='Bet multiplier')),
                ('minimum_bet', models.PositiveIntegerField(verbose_name='Minimum bet')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('betting_agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.bettingagency')),
                ('icon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.icon')),
                ('lottery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery')),
            ],
            options={
                'db_table': 'pattern',
                'unique_together': {('betting_agency', 'lottery', 'icon')},
            },
        ),
    ]
