from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from SolarTrackingSystem import solarTrackingApp

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("solarTrackingApp.urls")),
]
# Add static files serving for development only
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Catch-all pattern for 404 page
urlpatterns += [
    path("<path:unknown_path>", solarTrackingApp.views.custom_404, name="custom_404"),
]
