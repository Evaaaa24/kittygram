from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from cats.views import AchievementViewSet, CatViewSet, UserViewSet
from events.views import EventViewSet, RegistrationViewSet

router = DefaultRouter()
# Kittygram (основной проект)
router.register('cats', CatViewSet)
router.register('achievements', AchievementViewSet)
router.register('users', UserViewSet)
# Кото-ивенты (расширение)
router.register('events', EventViewSet)
router.register('registrations', RegistrationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api-auth/', include('rest_framework.urls')),
    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
]
