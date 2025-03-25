# Generated by Django 5.1.7 on 2025-03-21 17:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_payment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'В ожидании'), ('processing', 'В обработке'), ('shipped', 'Отправлен'), ('delivered', 'Доставлен'), ('cancelled', 'Отменён')], default='pending', max_length=20, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(max_length=50, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='shop.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default='pending', max_length=20, verbose_name='Статус оплаты'),
        ),
        migrations.CreateModel(
            name='UserFCMToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(max_length=255, verbose_name='FCM-токен')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fcm_token', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
