from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def root_health(_request):
    return JsonResponse({'message': 'Auto API est en ligne.'})


urlpatterns = [
    path('', root_health, name='root_health'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/profile/', include('customers.urls')),
    path('api/products/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('payments.urls')),
    path('api/shipping/', include('shipping.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
