# Generated by Django 3.0.8 on 2020-07-22 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MembersClub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_invited', models.BooleanField(default=False)),
                ('is_requested', models.BooleanField(default=False)),
                ('is_member', models.BooleanField(default=False)),
            ],
        ),
    ]
