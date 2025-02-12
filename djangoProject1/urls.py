"""
URL configuration for djangoProject1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.http import JsonResponse
from django.urls import path, include, re_path  # 从 django.urls 引入 include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
import views


def raceData(request):
    id = request.session.get('id')
    if request.method == "GET":
        return JsonResponse({
            'type': "      1",
        }, headers="11")


urlpatterns = [
    path('', views.login),
    path('logout', views.logout),
    path("student/", include("student.urls")),
    path("teacher/", include("teacher.urls")),
    path("blog/", include("blog.urls")),
    path('ueditor/', include('DjangoUeditor.urls')),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    re_path(r'^(?!.*media).*$', TemplateView.as_view(template_name='../templates/404.html'), name='404'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
