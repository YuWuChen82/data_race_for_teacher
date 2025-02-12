from django.urls import path, re_path
from .views import get_ueditor_controller

urlpatterns = [
    re_path(r'^controller.html$', get_ueditor_controller),
]
