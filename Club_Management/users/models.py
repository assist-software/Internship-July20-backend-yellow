from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from .serializers import UserSerializer
from django.core.files.storage import FileSystemStorage
from Athletes.models import Sports
fs = FileSystemStorage(location='photos/')


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, height, weight, age, role, gender,
                    primary_sport=None, secondary_sport=None, profile_image=None, password=None, commit=True):
        # Creates and saves an user
        serializer = UserSerializer(data={'email': email, 'first_name': first_name, 'last_name': last_name,
                                          'height': height, 'weight': weight, 'age': role, 'role': role,
                                          'gender': gender})
        serializer.is_valid()

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            height=height,
            weight=weight,
            age=age,
            role=role,
            gender=gender,
            primary_sport=primary_sport,
            secondary_sport=secondary_sport,
            profile_image=profile_image,
        )
        user.set_password(password)

        if commit:
            user.save()
        return user

    def create_superuser(self, email, first_name, last_name, height, weight, age, role, gender,
                         profile_image=None, password=None):
        # Creates and saves an superuser/admin
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            height=height,
            weight=weight,
            age=age,
            role=role,
            gender=gender,
            profile_image=profile_image,
            commit=False,
        )
        user.is_superuser = True
        user.save()
        return user

    def create_coach(self, email, first_name, last_name, height, weight, age, role, gender, profile_image=None,
                     password=None):
        # Creates and saves an coach
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            height=height,
            weight=weight,
            age=age,
            role=role,
            gender=gender,
            profile_image=profile_image,
            commit=False,
        )
        user.save()
        return user

    def create_athlete(self, email, first_name, last_name, height, weight, age, role, gender=None, profile_image=None,
                       password=None):
        # Creates and saves an athlete
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            height=height,
            weight=weight,
            age=age,
            role=role,
            gender=gender,
            profile_image=profile_image,
            commit=False,
        )
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # password from AbstractBaseUser

    ADMIN = 0
    COACH = 1
    ATHLETE = 2
    MALE = 0
    FEMALE = 1
    ROLES = [
        (ADMIN, 'Admin'),
        (COACH, 'Coach'),
        (ATHLETE, 'Athlete')
    ]

    GENDERS = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]
    first_name = models.CharField(_('First name'), max_length=50, blank=True)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True)
    email = models.EmailField(verbose_name=_('Email address'), max_length=255, unique=True)

    height = models.IntegerField(_('Height'), null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(400)])
    weight = models.FloatField(_('Weight'), null=True, blank=True,
                               validators=[MinValueValidator(0), MaxValueValidator(400)])
    age = models.PositiveIntegerField(_('Age'), validators=[MinValueValidator(0), MaxValueValidator(200)],
                                      blank=True, null=True, default=0)

    is_staff = models.BooleanField(_('Staff status'), default=True,
                                   help_text=_('Designates whether the user can log into this admin site.')
                                   )
    is_active = models.BooleanField(_('Active status'), default=True,
                                    help_text=_('Designates whether this user should be treated as active. '
                                                'Unselect this instead of deleting accounts.'),
                                    )
    primary_sport = models.ForeignKey('Athletes.Sports', blank=True, null=True, on_delete=models.CASCADE,
                                      related_name='Primary', help_text=_('Choose a primary sport.'))
    secondary_sport = models.ForeignKey('Athletes.Sports', blank=True, null=True, on_delete=models.CASCADE,
                                        related_name='Secondary', help_text=_('Choose a secondary sport.'))
    gender = models.IntegerField(_('Gender'), choices=GENDERS, default=MALE, blank=True)
    profile_image = models.TextField(blank=True, null=True)
    role = models.IntegerField(_('Role'), choices=ROLES, default=ADMIN)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'height', 'weight', 'age', 'role', 'gender']

    def get_full_name(self):
        # Return the first_name plus the last_name, with a space in between.
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}, height:{self.height}, weight:{self.weight}, age:{self.age}, " \
               f"role:{self.role}>"

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True
