# Generated by Django 3.0.8 on 2020-07-21 12:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
                ('location', models.CharField(max_length=300)),
                ('date', models.DateTimeField(verbose_name='date events')),
                ('time', models.DateTimeField(verbose_name='time events')),
            ],
        ),
        migrations.CreateModel(
            name='Participants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_invited', models.BooleanField(default=False)),
                ('is_requested', models.BooleanField(default=False)),
                ('is_member', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
                ('latitude', models.IntegerField(validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ('longitude', models.IntegerField(validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('radius', models.IntegerField(default=0)),
                ('duration', models.IntegerField(default=0)),
                ('distance', models.IntegerField(default=0)),
                ('average_hr', models.IntegerField(default=0)),
                ('calories_burned', models.IntegerField(default=0)),
                ('average_speed', models.IntegerField(default=0)),
                ('workout_effectiveness', models.IntegerField(default=0)),
                ('heart_rate', models.IntegerField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Events.Events')),
            ],
        ),
    ]
