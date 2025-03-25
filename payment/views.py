import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from orders.models import Order

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_payment(request):
    user = request.user
    order_id = request.data.get("order_id")
    payment_method = request.data.get("payment_method")

    if not order_id or not payment_method:
        return Response({"error": "Нужны order_id и payment_method"}, status=400)

    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=404)

    # Генерация ссылки на оплату
    payment_link = f"https://bank.com/pay?amount={order.total_price}&phone=+992927870019"

    # Здесь можно добавить логику обработки платежа через API банка

    return Response({
        "message": "Оплата успешно инициирована!",
        "order_id": order_id,
        "payment_link": payment_link
    }, status=200)
