from django.db import models

from base.models import Paper


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=25)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Article(Paper):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(
        upload_to='workshop/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles')
    is_draft = models.BooleanField(default=True)
    publisher = models.ForeignKey('accounts.EducationalInstitute', related_name='new_articles', on_delete=models.SET_NULL,
                                  null=True, blank=True)
