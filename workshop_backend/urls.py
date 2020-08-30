from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('chat/', include('workshop.api.urls', namespace='workshop')),
    # for auth
    # path('api-auth/', include('rest_framework.urls')),
    # path('rest-auth/', include('rest_auth.urls')),
    # path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('accounts.urls', 'accounts'), namespace='accounts'))
    path('api/fsm/', include('fsm.urls') ),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
