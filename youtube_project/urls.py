from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esto le dice a Django: "Para cualquier ruta, mira dentro de videos/urls.py"
    path('', include('videos.urls')), 
]