from typing import List, Tuple
from django.urls import reverse


from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from faker import Faker


SUBSCRIPTION_PLANS = (
    ("Basic", "Basic"),
    ("Premium", "Premium"),
    ("Enterprise", "Enterprise"),
)


# class Images
