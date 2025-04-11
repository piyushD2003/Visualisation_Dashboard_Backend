from django.db import models

class Data(models.Model):
    end_year = models.CharField(max_length=10, blank=True, null=True)
    intensity = models.IntegerField(blank=True, null=True)
    sector = models.CharField(max_length=100,blank=True, null=True)
    topic = models.CharField(max_length=100,blank=True, null=True)
    insight = models.TextField(blank=True, null=True)
    url = models.CharField(blank=True, null=True)
    region = models.CharField(max_length=100,blank=True, null=True)
    start_year = models.CharField(max_length=10, blank=True, null=True)
    impact = models.TextField(blank=True, null=True)
    added = models.DateTimeField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    country = models.CharField(max_length=100,blank=True, null=True)
    relevance = models.IntegerField(blank=True, null=True)
    pestle = models.CharField(max_length=100,blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    likelihood = models.IntegerField(blank=True, null=True)

    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Created"
    )

    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Date Updated"
    )

    class Meta:
        db_table = "Data"
        verbose_name = "Data"
        verbose_name_plural = "Data"

    def __str__(self):
        return self.title