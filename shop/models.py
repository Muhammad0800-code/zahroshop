from django.contrib.auth.models import User
from django.db import models
from fcm_django.models import FCMDevice

# ======================= #
#        ТОВАРЫ          #
# ======================= #
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Скидочная цена")
    category = models.CharField(max_length=100, verbose_name="Категория")
    image = models.ImageField(upload_to="product_images/", blank=True, null=True, verbose_name="Фото товара")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price

    def __str__(self):
        return self.title


# ======================= #
#         ЗАКАЗЫ         #
# ======================= #
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменён"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Покупатель")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма", default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")

    def calculate_total_price(self):
        self.total_price = sum(item.get_total_price() for item in self.items.all())
        self.save()

    def complete_order(self):
        bonus = self.user.bonuses.first()
        if bonus:
            bonus.use_bonus(self.total_price // 10)
        for item in self.items.all():
            item.product.stock -= item.quantity
            item.product.save()
        Cart.objects.filter(user=self.user).delete()
        self.status = "shipped"
        self.save()

    def send_order_update_notification(self):
        """Отправка push-уведомлений при обновлении статуса заказа."""
        from .models import UserFCMToken  # Избегаем циклического импорта

        try:
            user_fcm = UserFCMToken.objects.get(user=self.user)
            if user_fcm.fcm_token:
                device, created = FCMDevice.objects.get_or_create(
                    registration_id=user_fcm.fcm_token,
                    defaults={"type": "android"}
                )
                device.send_message(
                    title="Обновление заказа",
                    body=f"Ваш заказ №{self.id} теперь в статусе: {self.get_status_display()}!"
                )
        except UserFCMToken.DoesNotExist:
            print(f"FCM-токен для пользователя {self.user.username} не найден")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")

    def save(self, *args, **kwargs):
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != self.status:
                self.send_order_update_notification()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    def get_total_price(self):
        return self.product.get_final_price() * self.quantity

    def __str__(self):
        return f"{self.product.title} ({self.quantity} шт.)"


# ======================= #
#        БОНУСЫ          #
# ======================= #
class Bonus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bonuses", verbose_name="Пользователь")
    total_bonus = models.PositiveIntegerField(default=0, verbose_name="Бонусный баланс")

    def add_bonus(self, amount):
        self.total_bonus += amount
        self.save()

    def use_bonus(self, amount):
        if self.total_bonus >= amount:
            self.total_bonus -= amount
            self.save()
        else:
            raise ValueError("Недостаточно бонусов")

    def __str__(self):
        return f"{self.user.username} - {self.total_bonus} бонусов"


# ======================= #
#        КОРЗИНА         #
# ======================= #
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def clear_cart(self):
        Cart.objects.filter(user=self.user).delete()

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity} шт.)"


# ======================= #
#        ОПЛАТА          #
# ======================= #
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment", verbose_name="Заказ")
    method = models.CharField(max_length=50, verbose_name="Способ оплаты")
    status = models.CharField(max_length=20, default="pending", verbose_name="Статус оплаты")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")

    def __str__(self):
        return f"Оплата заказа #{self.order.id} - {self.method} ({self.status})"


# ======================= #
#    FCM-Токены          #
# ======================= #
class UserFCMToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="fcm_token", verbose_name="Пользователь")
    fcm_token = models.CharField(max_length=255, verbose_name="FCM-токен")

    def __str__(self):
        return f"FCM-токен для {self.user.username}"
