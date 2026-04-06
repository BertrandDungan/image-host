"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from backend.views.react_view import ReactView
from rest_framework.routers import DefaultRouter
from backend.views import user_view, image_view
from drf_spectacular.views import SpectacularSwaggerView

router = DefaultRouter()
router.register(r"users", user_view.UserViewSet)

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/", include((router.urls))),
    path("api/images/", image_view.ImageView.as_view(), name="images"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("", ReactView.as_view(), name="index"),
    path(r"<path:path>", ReactView.as_view(), name="index_with_path"),
]
