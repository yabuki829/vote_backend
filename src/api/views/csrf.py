from django.middleware.csrf import get_token
from django.http import JsonResponse

def csrf(request):
  print("csrfトークンを作成します")
  return JsonResponse({'csrfToken': get_token(request)})
