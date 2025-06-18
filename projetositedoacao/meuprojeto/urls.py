from django.contrib import admin
from django.urls import path, include
from sndot import views  # ✅ agora sim, o nome da app está correto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),       # ✅ página inicial
    path('', include('setup.urls')),            # ✅ inclui rotas da app
]
