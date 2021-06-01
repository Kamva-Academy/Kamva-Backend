from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
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
      default_version='v2',
      # description="Test description",

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # path('api/auction/', include('auction.urls')),
    path('chat/', include('workshop.api.urls', namespace='workshop')),
    # for auth
    # path('api-auth/', include('rest_framework.urls')),
    # path('rest-auth/', include('rest_auth.urls')),
    # path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('api/fsm/', include('fsm.urls')),
    path('api/notifications/', include('notifications_jwt.urls', namespace='notifications')),
    path('api/notice/', include('notice.urls')),
    path('api/scoring/', include('scoring.urls')),

    # path('api(?P<format>\.json|\.yaml)/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += i18n_patterns(
#     url(r'^/{}'.format(ADMIN_URL), admin.site.urls)
# )
