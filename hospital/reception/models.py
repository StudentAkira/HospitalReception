import datedelta as datedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from reception.managers import CustomUserManager
from datetime import datetime, timedelta


class Ticket(models.Model):

    owner = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="ticket_owner")
    target = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="ticket_target")
    receipt_time = models.DateTimeField(default=datetime.now())
    objects = models.Manager()


class Disease(models.Model):
    DoesNotExist = None

    class StateChoices(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Critical'
        BAD_STABLE = 'BAD STABLE', 'Bad stable'
        GOOD_STABLE = 'GOOD STABLE', 'Good stable'
        REMISSION = 'REMISSION', 'Remission'
        FULL_REMISSION = 'FULL REMISSION', 'Full remission'

    name = models.CharField(max_length=127, null=False)
    description = models.CharField(max_length=511, null=False)
    drugs = models.CharField(max_length=1023)
    recommendations = models.CharField(max_length=1023, null=False)
    status = models.CharField(max_length=255, choices=StateChoices.choices, null=False)
    discovered_at = models.DateTimeField(default=datetime.now(), null=False)
    card = models.ForeignKey("MedicalCard", on_delete=models.CASCADE, related_name="medical_card", null=False)
    objects = models.Manager()


class MedicalCard(models.Model):
    DoesNotExist = None

    owner = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="card_owner")
    objects = models


class CustomUser(AbstractUser):
    DoesNotExist = None

    class RoleChoices(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        DOCTOR = 'doctor', 'Doctor'

    email = None
    first_name = None
    last_name = None
    username = models.CharField(max_length=127, unique=True)
    fio = models.CharField(max_length=127)
    role = models.CharField(max_length=25, choices=RoleChoices.choices)

    objects = CustomUserManager()
