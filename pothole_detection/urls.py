# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from api.views import officer_dashboard, detect

# urlpatterns = [
#     path('', include('api.urls')),
#     path('admin/', admin.site.urls),
#     path('dashboard/', officer_dashboard, name='officer_dashboard'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)










from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]