# Generated by Django 3.0.5 on 2020-05-11 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0002_shoppingcart_shoppingcartitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='ユーザ'),
        ),
        migrations.AlterField(
            model_name='shoppingcartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='amazon.ShoppingCart', verbose_name='ショッピングカート'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0, verbose_name='評価')),
                ('title', models.CharField(max_length=255, verbose_name='タイトル')),
                ('comment', models.TextField(verbose_name='コメント')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.Product', verbose_name='商品')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザ')),
            ],
        ),
    ]
