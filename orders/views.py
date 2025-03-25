from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shop.models import Order

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request):
    order_id = request.data.get("order_id")
    new_status = request.data.get("status")

    if not order_id or not new_status:
        return Response({"error": "Нужно передать order_id и status"}, status=400)

    try:
        order = Order.objects.get(id=order_id)

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Некорректный статус заказа"}, status=400)

        order.status = new_status
        order.save()
        return Response({"message": f"Статус заказа {order_id} обновлён на {new_status}"})
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    address = request.data.get("address")
    total_price = request.data.get("total_price")

    if not address or not total_price:
        return Response({"error": "Адрес и сумма обязательны"}, status=400)

    try:
        total_price = float(total_price)
        if total_price <= 0:
            return Response({"error": "Сумма должна быть положительной"}, status=400)
    except ValueError:
        return Response({"error": "Некорректная сумма"}, status=400)

    order = Order.objects.create(
        user=user,
        address=address,
        total_price=total_price,
        status="pending"  # Начальный статус заказа
    )

    return Response({"message": "Заказ оформлен!", "order_id": order.id}, status=201)


