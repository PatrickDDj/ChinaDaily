from django.db import models

# Create your models here.
from django.utils import timezone


class News(models.Model):
    title = models.TextField()
    content = models.TextField()

    add_time = models.DateField(default=timezone.now)

    positive = models.IntegerField()
    neutral = models.IntegerField()
    negative = models.IntegerField()
