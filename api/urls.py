from django.urls import path
from .views import save_fcm_token

urlpatterns = [
    path("save_fcm_token/", save_fcm_token, name="save_fcm_token"),
]
