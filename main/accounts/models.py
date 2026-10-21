from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User profile extended for the Bihari wedding market."""

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    home_district = models.CharField(
        max_length=100,
        default="Patna",
        help_text="e.g., Patna, Darbhanga, Gaya, Bhojpur",
    )
    is_business_lead = models.BooleanField(
        default=False,
        help_text="Operator who captured this customer as a lead.",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username
