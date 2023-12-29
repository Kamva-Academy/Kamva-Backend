from django.db import models

class ContactMessage(models.Modal):
    subject = models.TextField()
    text = models.TextField()
    # phone = models.CharField(max_length=12)
    email = models.CharField(max_length=36)



# Create your models here.
