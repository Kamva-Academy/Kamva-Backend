from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from kamva_backend.settings.base import get_environment_var
import sentry_sdk

schema_view = get_schema_view(
    openapi.Info(
        title="Kamva Backend APIs",
        default_version='v3',
        description="APIs list of Kamva Backend service",
    ),
    url=settings.SWAGGER_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

if not settings.DEBUG:
    sentry_sdk.init(
        get_environment_var('SENTRY_DNS'),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api/fsm/', include('apps.fsm.urls')),
    path('api/roadmap/', include('apps.roadmap.urls')),
    path('api/websiteappearance/', include('apps.websiteappearance.urls')),
    path('api/scoring/', include('apps.scoring.urls')),
    # https://pypi.org/project/django-link-shortener/
    path('s/', include('shortener.urls')),
]

urlpatterns += [path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
