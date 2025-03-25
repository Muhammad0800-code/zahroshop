from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Product, Order, OrderItem, Bonus, Cart, Payment, UserFCMToken
from .serializers import ProductSerializer, OrderSerializer, BonusSerializer, CartSerializer, UserSerializer


# ===================== #
#      ПРОДУКТЫ        #
# ===================== #

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


# ===================== #
#       ЗАКАЗЫ         #
# ===================== #

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.get_final_price() * item.quantity for item in cart_items)
        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        cart_items.delete()
        return Response({"message": "Заказ оформлен!", "order_id": order.id}, status=status.HTTP_201_CREATED)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Не указан статус"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({"message": "Статус заказа обновлён!", "new_status": order.status}, status=status.HTTP_200_OK)


# ===================== #
#       КОРЗИНА        #
# ===================== #

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            quantity = serializer.validated_data.get('quantity', 1)

            product = get_object_or_404(Product, id=product_id)

            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            cart_item.quantity += quantity
            cart_item.save()

            return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart_item = Cart.objects.filter(user=request.user, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
            return Response({"message": "Товар удалён из корзины"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)


# ===================== #
#       ОПЛАТА         #
# ===================== #

class PaymentProcessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        payment_method = request.data.get("payment_method")

        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Проверяем, не была ли уже произведена оплата
        if Payment.objects.filter(order=order).exists():
            return Response({"error": "Этот заказ уже оплачен"}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(order=order, method=payment_method, status="paid")
        order.status = "Оплачено"
        order.save()

        return Response(
            {"message": "Оплата прошла успешно!", "order_id": order.id, "payment_method": payment.method},
            status=status.HTTP_200_OK
        )


# ===================== #
#      ПОЛЬЗОВАТЕЛИ    #
# ===================== #

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Ты авторизован! 🔥"})


class AdminCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            return Response({"is_admin": True, "message": "Ты администратор! 🔥"})
        return Response({"is_admin": False, "message": "Ты обычный пользователь."})


# ===================== #
#     PUSH-УВЕДОМЛЕНИЯ  #
# ===================== #

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    user = request.user
    fcm_token = request.data.get("fcm_token")

    if not fcm_token:
        return Response({"error": "FCM token is required"}, status=400)

    UserFCMToken.objects.update_or_create(user=user, defaults={"fcm_token": fcm_token})
    return Response({"message": "FCM token saved successfully"})


# ===================== #
#         URLS         #
# ===================== #

from django.urls import path

urlpatterns = [
    path("save_fcm_token/", save_fcm_token, name="save_fcm_token"),
]

class BonusViewSet(viewsets.ModelViewSet):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer