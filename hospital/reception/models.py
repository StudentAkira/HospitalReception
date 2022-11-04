from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from reception.managers import CustomUserManager


class CustomUser(AbstractUser):
    email = None
    first_name = None
    last_name = None
    username = models.CharField(max_length=127, unique=True)
    fio = models.CharField(max_length=127)
    role = models.CharField(max_length=25)
    objects = CustomUserManager()
