from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProductViewSet, OrderViewSet, BonusViewSet, 
    RegisterView, ProtectedView, AdminCheckView,
    ProductListCreateView, ProductDetailView, 
    CartView, AddToCartView, RemoveFromCartView,
    CreateOrderView, UpdateOrderStatusView,
    PaymentProcessView,
)

# Роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'bonuses', BonusViewSet)

# Общий список маршрутов
urlpatterns = [
    path('api/', include(router.urls)),  
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('admin-check/', AdminCheckView.as_view(), name='admin_check'),
    path('products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'),
    path('orders/update-status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('payment/process/', PaymentProcessView.as_view(), name='payment_process'),
]
