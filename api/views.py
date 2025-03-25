from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def save_fcm_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("fcm_token")
            if not token:
                return JsonResponse({"error": "FCM-токен отсутствует"}, status=400)

            # Здесь можешь сохранить токен в БД, например, к пользователю
            return JsonResponse({"message": "FCM-токен сохранен успешно!"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON"}, status=400)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)
