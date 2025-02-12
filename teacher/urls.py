from django.urls import path, re_path
from teacher.views import *  # 从自己的 app 目录引入 views

urlpatterns = [
    re_path('teacher_index.html',index),
    re_path('teacher_class.html',my_class),
    re_path('teacher_my_race.html',my_race),
    re_path('teacher_change_race.html',change_race),
    re_path('teacher_race_detail.html',race_detail),
    re_path('teacher_homepage.html',homepage),
    re_path('teacher_class_detail.html',class_detail),
    re_path('teacher_student_submit.html',student_submit),
    re_path('teacher_add_admin.html',add_admin),
]