from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api/fsm/', include('apps.fsm.urls')),
    # path('api/scoring/', include('apps.scoring.urls')),
    # path('api/base/', include('apps.base.urls')),
    # path('api/content/', include('apps.content_widget.urls')),
    # path('api/question/', include('apps.question_widget.urls')),
    path('api/websiteappearance/', include('apps.websiteappearance.urls')),
    path('s/', include('shortener.urls')), # https://pypi.org/project/django-link-shortener/
]

urlpatterns += [path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
