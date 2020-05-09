from django.db import models

# Create your models here.
class Product(models.Model):
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

    thumbnail = models.ImageField(
        verbose_name='サムネイル',
        upload_to='thumbnails/',
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=150,
        null=False,
        blank=False,
    )

    price = models.IntegerField(
        verbose_name='値段',
    )

    description = models.TextField(
        verbose_name='説明',
    )
