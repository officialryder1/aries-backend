# Generated by Django 5.0.7 on 2024-08-08 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='card',
            field=models.ManyToManyField(blank=True, null=True, related_name='player_cards', to='main.card'),
        ),
    ]
