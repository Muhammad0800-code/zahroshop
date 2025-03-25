from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from orders.views import update_order_status  # ✅ Исправленный импорт

# Главная страница API
def home(request):
    return JsonResponse({"message": "Добро пожаловать в API!"})

urlpatterns = [
    path("", home),  # Главная страница API
    path("admin/", admin.site.urls),  # Админ-панель Django
    path("api/", include("shop.urls")),  # Основные API эндпоинты магазина
    path("api/payment/", include("payment.urls")),  # Подключаем платежный модуль
    path("api/order/update_status/", update_order_status, name="update_order_status"),  # ✅ Исправленный путь
    path("api/", include("api.urls")),  # Подключаем маршруты API
]
