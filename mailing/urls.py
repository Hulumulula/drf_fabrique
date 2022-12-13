from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import *


schema_view = get_schema_view(
    openapi.Info(
        title="Notification-service API",
        default_version='v1',
        description="Test description",
        terms_of_service="https:/www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

app = 'notification_service'
router = DefaultRouter()

router.register('mailing', viewset=MailingListView, basename='mailing')
router.register('client', viewset=ClientViewSet, basename='client')
router.register('message', viewset=MessageViewSet, basename='message')

urlpatterns = [
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^docs/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^docs/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
]
