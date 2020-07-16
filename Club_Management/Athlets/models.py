from django.db import models

# Create your models here.

class Sports(models.Model):
    description=models.CharField(max_length=255)
