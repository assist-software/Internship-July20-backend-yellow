# Generated by Django 3.0.8 on 2020-07-22 12:33

import django.core.files.storage
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Athletes', '0001_initial'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=50, verbose_name='Last name')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email address')),
                ('height', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(400)], verbose_name='Height')),
                ('weight', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(400)], verbose_name='Weight')),
                ('age', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(200)], verbose_name='Age')),
                ('is_staff', models.BooleanField(default=True, help_text='Designates whether the user can log into this admin site.', verbose_name='Staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='Active status')),
                ('gender', models.IntegerField(blank=True, choices=[(0, 'Male'), (1, 'Female')], default=0, verbose_name='Gender')),
                ('profile_image', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='photos/'), upload_to='')),
                ('role', models.IntegerField(choices=[(0, 'Admin'), (1, 'Coach'), (2, 'Athlete')], default=0, verbose_name='Role')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('primary_sport', models.ForeignKey(blank=True, help_text='Choose a primary sport.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Primary', to='Athletes.Sports')),
                ('secondary_sport', models.ForeignKey(blank=True, help_text='Choose a secondary sport.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Secondary', to='Athletes.Sports')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
