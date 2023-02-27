import uuid
from django.db import models

# Create your models here.
# User model is included by default in Django from the django.contrib.auth system


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    lastUser = models.ForeignKey(models.User, on_delete=models.SET('Deleted User'), null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    filesize = models.IntegerField()
    file = models.FileField(upload_to='files/')
