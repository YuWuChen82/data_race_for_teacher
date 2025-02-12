from django.urls import path, re_path
from student.views import *  # 从自己的 app 目录引入 views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('student_race.html', race),
    path('student_index.html', index),
    path('student_race_detail.html', race_detail),
    path('student_homepage.html',homepage),
    path('student_submit_record.html',submit_record),
    path('student_my_course.html',my_course),
    path('student_dataAnalysis.html',dataAnalysis),
    path('rankData', rankData),
    path('raceData', raceData),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)