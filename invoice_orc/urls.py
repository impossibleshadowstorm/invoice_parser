from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse


def home(request):
    HELLO = """
    <div>
    <h1 style="display:flex; justify-content:center; align-item:center">Welcome to XpressoGroup</h1>
    <a style="display:flex; justify-content:center; align-item:center" href="/admin/"> Goto Admin</a>
    </div>
    """
    return HttpResponse(HELLO)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/invoice/", include("invoice.urls")),
    path("", home, name="home"),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
