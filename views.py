# coding=utf-8
from django.shortcuts import render
from student.models import *
import hashlib
from django.shortcuts import redirect
def login(request):
    if request.method == "GET":
        notice = "none"
    else:
        userName = request.POST["username"]
        passWord = request.POST["password"]
        m = hashlib.md5()
        m.update(passWord.encode("utf-8"))
        passWord = m.hexdigest()
        try:
            sqlData = User.objects.get(username=userName, password=passWord)
        except User.DoesNotExist:
            notice = "密码错误"
        else:
            notice = 'none'
            request.session['username'] = userName
            request.session['name'] = sqlData.name
            request.session['identity'] = sqlData.identity
            request.session['id'] = sqlData.id
            if request.session['identity'] == "学生":
                request.session['is_student'] = True
                return redirect('student/student_race.html')
            else:
                request.session['is_student'] = False
                return redirect('teacher/teacher_index.html')

    return render(request,'login.html',{'notice':notice})

def logout(request):
    request.session.clear()
    return redirect('/')

