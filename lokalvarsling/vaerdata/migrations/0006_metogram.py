# Generated by Django 4.1 on 2024-02-23 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vaerdata', '0005_stasjon_altitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metogram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('navn', models.CharField(max_length=100)),
                ('url', models.TextField(blank=True)),
            ],
        ),
    ]