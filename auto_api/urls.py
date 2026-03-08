from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def root_health(_request):
    return JsonResponse({'message': 'Auto API est en ligne.'})


urlpatterns = [
    path('', root_health, name='root_health'),
    path('admin/', admin.site.urls),
]
