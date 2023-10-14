from django.db import models


class Banner(models.Model):
    class BannerType(models.TextChoices):
        programs_page = "ProgramsPage"

    banner_type = models.CharField(
        max_length=30, default=BannerType.programs_page, choices=BannerType.choices)
    desktop_image = models.ImageField(upload_to='websiteappearance/')
    mobile_image = models.ImageField(upload_to='websiteappearance/')
    is_active = models.BooleanField(default=False)
    redirect_to = models.URLField()
