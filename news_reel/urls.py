"""news_reel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework_simplejwt.authentication import JWTAuthentication


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path("", include("users.api.v1.urls"), name="users-v1"),
        path("", include("posts.api.v1.urls"), name="posts-v1"),
        path("", include("reviews.api.v1.urls"), name="reviews-v1"),
        path("", include("reports.api.v1.urls"), name="reports-v1"),
        path("", include("followers.api.v1.urls"), name="followers-v1"),
    ]))
]

# swagger
schema_view = get_schema_view(
    openapi.Info(
        title="News Reel API",
        default_version="v1",
        description="API documentation for News Reel App",
    ),
    public=True,
    permission_classes=(AllowAny, ),
    authentication_classes=(JWTAuthentication, )
)

urlpatterns += [
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs")
]


admin.site.site_header = "News Reel"
admin.site.site_title = "News Reel Admin Portal"
admin.site.index_title = "News Reel Admin"
