from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Rasta Workshop API",
        default_version='v3',
        # description="Test description",
    ),
    url=settings.SWAGGER_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('api/fsm/', include('fsm.urls')),
    path('api/scoring/', include('scoring.urls')),
    path('api/event_metadata/', include('event_metadata.urls')),
]


urlpatterns += [path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
