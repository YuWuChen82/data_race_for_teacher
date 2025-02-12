from django.urls import path, re_path
from django.views.generic import TemplateView

from blog.views import *  # 从自己的 app 目录引入 views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index),
    path('index.html', index),
    path('case.html', case),
    path('kb.html', kb),
    path('video.html', video),
    path('expert.html', expert),
    path('article.html', article),
    path('search.html', search),
    path('teacher/article.html',t_article),
    path('teacher/article2.html',t_article2),
    path('teacher/expert.html',t_expert),
    path('teacher/expert2.html',t_expert2),
    path('dataShare.html',dataShare),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)