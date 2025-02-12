from django.http import JsonResponse
from django.shortcuts import render
from .models import *
import datetime, io, csv
import pytz
from django.utils import timezone
from django.db.models import Avg, Count
import hashlib
from django.core.paginator import Paginator
import pandas as pd
from sklearn.metrics import precision_score, recall_score, roc_auc_score, accuracy_score, \
    mean_squared_error, f1_score


def calculate_accuracy(student_file, answer_file):
    # 计算准确率
    right = (student_file == answer_file).all(axis=1).sum()
    accuracy = right / len(answer_file)
    return round(accuracy, 6)


def calculate_precision(student_file, answer_file):
    # 计算精确度
    true_positives = ((student_file.iloc[:, 1] == 1) & (answer_file.iloc[:, 1] == 1)).sum()
    false_positives = ((student_file.iloc[:, 1] == 1) & (answer_file.iloc[:, 1] != 1)).sum()
    precision = true_positives / (true_positives + false_positives)
    return round(precision, 6)


def calculate_recall(student_file, answer_file):
    # 计算召回率
    true_positives = ((student_file.iloc[:, 1] == 1) & (answer_file.iloc[:, 1] == 1)).sum()
    false_negatives = ((student_file.iloc[:, 1] != 1) & (answer_file.iloc[:, 1] == 1)).sum()
    recall = true_positives / (true_positives + false_negatives)
    return round(recall, 6)


def calculate_auc(student_file, answer_file):
    # 计算AUC
    true_labels = answer_file.iloc[:, 1].astype(float)
    probabilities = student_file.iloc[:, 1].astype(float)
    auc = roc_auc_score(true_labels, probabilities)
    return round(auc, 6)


def calculate_rmse(student_file, answer_file):
    # 计算RMSE
    true_labels = answer_file.iloc[:, 1].astype(float)
    predicted_labels = student_file.iloc[:, 1].astype(float)
    mse = mean_squared_error(true_labels, predicted_labels)
    rmse = mse ** 0.5
    return round(rmse, 6)


def calculate_f1(student_file, answer_file):
    # 计算F1分数
    true_labels = answer_file.iloc[:, 1].astype(float)
    predicted_labels = student_file.iloc[:, 1].astype(float)
    f1 = f1_score(true_labels, predicted_labels)
    return round(f1, 6)


def index(request):
    ss = request.session
    if request.method == "GET":
        data = ChooseClass.objects.filter(student_id=ss.get('id'))
        return render(request, 'student_index.html', {'data': data})


def my_course(request):
    ss = request.session
    if request.method == "GET":
        data = ChooseClass.objects.filter(student_id=ss.get('id'))
        return render(request, 'student_my_course.html', {'data': data})


def race(request):
    ss = request.session
    if request.method == "GET":
        class_id = list(ChooseClass.objects.filter(student_id=ss.get('id')).values_list('class_id', flat=True))
        race_data = Race.objects.filter(class_id__in=class_id).order_by('-time')
        join_race_id = list(RaceRecord.objects.filter(student_id=ss.get('id')).values_list('race_id', flat=True))
        page_num = request.GET.get('page', 1)
        paginator = Paginator(race_data, 6)
        c_obj = paginator.get_page(page_num)
        if join_race_id:
            pass
        else:
            join_race_id = []
        now_time = str(datetime.date.today())
        races = RaceRecord.objects.filter(student_id_id=ss.get('id')).order_by('-race_id__time')
        page_num1 = request.GET.get('page1', 1)
        paginator1 = Paginator(races, 6)
        c_obj1 = paginator1.get_page(page_num1)
        return render(request, 'student_race.html', {'race_data': c_obj, 'now_time': now_time,
                                                     'join_race_id': join_race_id,
                                                     'race_data1': c_obj1,
                                                     })


def race_detail(request):
    ss = request.session
    now_time = str(datetime.date.today())
    if request.method == "GET":
        race_id = request.GET.get('id')
        ss["race_id"] = race_id
        race_data = Race.objects.filter(id=race_id).first()
        if race_data is None:
            return race(request)
        class_id = race_data.class_id_id
        join_class_id = list(
            ChooseClass.objects.filter(student_id_id=ss.get('id')).values_list('class_id_id', flat=True))
        flag = 1
        for t in join_class_id:
            if t == class_id:
                flag = 0
        if flag:
            return race(request)
        join_race_id = list(RaceRecord.objects.filter(student_id=ss.get('id')).values_list('race_id', flat=True))
        if join_race_id:
            pass
        else:
            join_race_id = []
        if race_data.evaluate_type != "RMSE":
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('-score')
        else:
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('score')
        return render(request, 'student_race_detail.html',
                      {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                       'notice': '0', 'id': race_data.id})
    else:
        data = request.POST
        right_rate = 0
        race_id = data.get('race_id')
        path_answer = Race.objects.get(id=race_id).file_answer
        race_data = Race.objects.filter(id=race_id).first()
        evaluate = race_data.evaluate_type
        join_race_id = list(
            RaceRecord.objects.filter(student_id=ss.get('id')).values_list('race_id', flat=True))
        if join_race_id:
            pass
        else:
            join_race_id = []
        if race_data.evaluate_type != "RMSE":
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('-score')
        else:
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('score')
        if 'submit_answer_btn' in data:
            try:
                file_data = request.FILES['submit_answer']
                file_answer_name = "student_answer" + str(request.session.get('id')) + ".csv"
                student_file_path = "media/upload/" + file_answer_name
                fobj1 = open(student_file_path, "wb")
                for chunk in file_data.chunks():
                    fobj1.write(chunk)
                fobj1.close()
            except:
                return render(request, 'student_race_detail.html',
                              {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                               'notice': '1', 'id': race_data.id})
            if not file_data.name.endswith('.csv'):
                return render(request, 'student_race_detail.html',
                              {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                               'notice': '1', 'id': race_data.id})
            # a = file_data.file.read()
            # enList = ["utf-8", "gb2312", "gbk"]
            # for en in enList:
            #     try:
            #         fobj = io.StringIO(str(a, encoding=en))
            #         b = en
            #         if True:
            #             break
            #     except:
            #         pass
            # fobj.readline()
            # student_file = csv.reader(fobj)
            # fobj1 = open("./media/upload/" + path_answer, 'r', encoding=b)
            # fobj1.readline()
            # answer_file = csv.reader(fobj1)
            # student_file = list(student_file)
            # answer_file = list(answer_file)
            # answer_len = len(answer_file)
            # if len(student_file) != answer_len or answer_len == 1:
            #     return render(request, 'student_race_detail.html',
            #                   {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
            #                    'notice': '1', 'id': race_data.id})

            # 读取answer_file
            answer_file_path = './media/upload/' + path_answer  # 替换为实际的文件路径
            enList = ["utf-8", "gb2312", "gbk", 'latin1']
            for en in enList:
                try:
                    student_file = pd.read_csv(student_file_path, encoding=en)
                    answer_file = pd.read_csv(answer_file_path, encoding=en)
                    break
                except:
                    pass

            # 排序学生文件和答案文件
            student_file.sort_values(by=student_file.columns[0], inplace=True)
            answer_file.sort_values(by=answer_file.columns[0], inplace=True)
            if len(set(answer_file.iloc[:, 0]) - set(student_file.iloc[:, 0])) != 0:
                return render(request, 'student_race_detail.html',
                              {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                               'notice': '1', 'id': race_data.id})
            if evaluate == "ACC":
                right_rate = calculate_accuracy(student_file, answer_file)
            elif evaluate == "P":
                right_rate = calculate_precision(student_file, answer_file)
            elif evaluate == "R":
                right_rate = calculate_recall(student_file, answer_file)
            elif evaluate == "AUC":
                right_rate = calculate_auc(student_file, answer_file)
            elif evaluate == "RMSE":
                right_rate = calculate_rmse(student_file, answer_file)
            elif evaluate == "F1":
                right_rate = calculate_f1(student_file, answer_file)

            sub_record = SubmitRecord()
            sub_record.student_id_id = ss.get('id')
            sub_record.class_id_id = Race.objects.filter(id=race_id).first().class_id.id
            sub_record.race_id = Race.objects.get(id=race_id)
            sub_record.right_rate = right_rate
            current_time = timezone.make_aware(datetime.datetime.now(), pytz.timezone('Asia/Shanghai'))
            sub_record.time = str(current_time)
            sub_record.save()
            old_score = RaceRecord.objects.get(student_id_id=ss.get('id'), race_id_id=race_id).score
            if right_rate > old_score:
                obj1 = RaceRecord.objects.get(student_id_id=ss.get('id'), race_id_id=race_id)
                obj1.score = right_rate
                obj1.time = now_time
                obj1.save()
        else:
            isJoin = RaceRecord.objects.filter(race_id_id=race_id, student_id_id=ss.get('id')).first()
            if isJoin:
                pass
            else:
                RaceRecord.objects.create(race_id_id=race_id, student_id_id=ss.get('id'), time=now_time, score=0)
                race_data = Race.objects.filter(id=race_id).first()
                join_race_id = list(RaceRecord.objects.filter(student_id_id=ss.get('id')).values_list('race_id', flat=True))
                if join_race_id:
                    pass
                else:
                    join_race_id = []
                if race_data.evaluate_type != "RMSE":
                    rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('-score')
                else:
                    rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('score')
            return render(request, 'student_race_detail.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                           'notice': '3', 'id': race_data.id, 'score': right_rate})
        # 最终处理
        race_data = Race.objects.filter(id=race_id).first()
        join_race_id = list(RaceRecord.objects.filter(student_id_id=ss.get('id')).values_list('race_id', flat=True))
        if join_race_id:
            pass
        else:
            join_race_id = []
        if race_data.evaluate_type != "RMSE":
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('-score')
        else:
            rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('score')
        return render(request, 'student_race_detail.html',
                      {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id, 'rank': rank,
                       'notice': '2', 'id': race_data.id, 'score': right_rate})


def homepage(request):
    ss = request.session
    if request.method == 'GET':
        names = User.objects.get(id=ss.get('id'))
        information = User.objects.filter(id=ss.get('id')).aggregate(b=Count('racerecord__id'))
        return render(request, 'student_homepage.html', {'names': names, 'information': information, 'notice': '0'})
    else:
        webData = request.POST
        names = User.objects.get(id=ss.get('id'))
        information = User.objects.filter(id=ss.get('id')).aggregate(b=Count('racerecord__id'))
        if "change_btn" in webData:
            old = webData.get('old_password')
            new1 = webData.get('new_password')
            new2 = webData.get('repeat_password')
            if not new1 or new1.strip() == "":
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '4'})
            m = hashlib.md5()
            m.update(old.encode("utf-8"))
            old = m.hexdigest()
            password = User.objects.get(id=ss.get('id')).password
            if old != password:
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '1'})
            m = hashlib.md5()
            m.update(new1.encode("utf-8"))
            new1 = m.hexdigest()
            if new1 == password:
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '2'})
            m = hashlib.md5()
            m.update(new2.encode("utf-8"))
            new2 = m.hexdigest()
            if new1 != new2:
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '5'})
            User.objects.filter(id=ss.get('id')).update(password=new1)
            return render(request, 'student_homepage.html',
                          {'names': names, 'information': information, 'notice': '3'})
        elif "change_username" in webData:
            username = webData.get("new_username")
            existing_user = User.objects.filter(username=username).first()
            if existing_user and existing_user.id != ss.get('id'):
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '6'})
            elif username is None or username.strip() == "":
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '4'})
            import re
            pattern = r'^[a-zA-Z0-9]{1,20}$'
            if not re.match(pattern, username):
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '8'})
            else:
                User.objects.filter(id=ss.get('id')).update(username=webData.get("new_username"))
                names = User.objects.get(id=ss.get('id'))
                return render(request, 'student_homepage.html',
                              {'names': names, 'information': information, 'notice': '3'})


def submit_record(request):
    stu_id = request.session.get('id')
    ss = request.session
    now_time = str(datetime.date.today())
    race_id = request.session.get('race_id')
    race_data = Race.objects.filter(id=race_id).first()
    pageName = "page"
    if race_data is None:
        return race(request)
    class_id = race_data.class_id_id
    join_class_id = list(
        ChooseClass.objects.filter(student_id_id=ss.get('id')).values_list('class_id_id', flat=True))
    flag = 1
    for t in join_class_id:
        if t == class_id:
            flag = 0
    if flag:
        return race(request)
    join_race_id = list(RaceRecord.objects.filter(student_id=ss.get('id')).values_list('race_id', flat=True))
    if join_race_id:
        pass
    else:
        join_race_id = []
    data = SubmitRecord.objects.filter(student_id_id=stu_id, race_id_id=request.session.get('race_id')).order_by(
        '-time')
    page = request.GET.get('page', 1)
    paginator = Paginator(data, 15)
    c_data = paginator.get_page(page)
    notice = "当前记录"
    if request.method == "GET":
        if request.GET.get('page'):
            return render(request, 'student_submit_record.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                           'id': race_data.id, 'flag': 0, 'notice': notice, 'record': c_data, 'pageName': pageName})
        elif request.GET.get('allpage'):
            data = SubmitRecord.objects.filter(student_id_id=stu_id).order_by('-time')
            pageName = 'allpage'
            page = request.GET.get(pageName, 1)
            paginator = Paginator(data, 15)
            c_data = paginator.get_page(page)
            notice = "全部记录"
            return render(request, 'student_submit_record.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                           'id': race_data.id, 'flag': 0, 'notice': notice, 'record': c_data, 'pageName': pageName})
        elif request.GET.get('scorepage'):
            data = RaceRecord.objects.filter(student_id_id=stu_id).order_by('-time')
            pageName = 'scorepage'
            page = request.GET.get(pageName, 1)
            paginator = Paginator(data, 15)
            c_data = paginator.get_page(page)
            notice = "最高得分"
            return render(request, 'student_submit_record.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                           'id': race_data.id, 'flag': 1, 'notice': notice, 'record': c_data, 'pageName': pageName})
        return render(request, 'student_submit_record.html',
                      {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                       'id': race_data.id, 'flag': 0, 'notice': notice, 'record': c_data, 'pageName': pageName})

    else:
        webData = request.POST
        if "all_submit" in webData:
            data = SubmitRecord.objects.filter(student_id_id=stu_id).order_by('-time')
            pageName = 'allpage'
            page = request.GET.get(pageName, 1)
            paginator = Paginator(data, 15)
            c_data = paginator.get_page(page)
            notice = "全部记录"
            return render(request, 'student_submit_record.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                           'id': race_data.id, 'flag': 0, 'notice': notice, 'record': c_data, 'pageName': pageName})
        elif "score" in webData:
            data = RaceRecord.objects.filter(student_id_id=stu_id).order_by('-time')
            pageName = 'scorepage'
            page = request.GET.get(pageName, 1)
            paginator = Paginator(data, 15)
            c_data = paginator.get_page(page)
            notice = "最高得分"
            return render(request, 'student_submit_record.html',
                          {'race_data': race_data, 'now_time': now_time, 'join_race_id': join_race_id,
                           'id': race_data.id, 'flag': 1, 'notice': notice, 'record': c_data, 'pageName': pageName})


def dataAnalysis(request):
    id = request.session.get('id')
    if request.method == "GET":
        race = RaceRecord.objects.filter(student_id_id=id)
        return render(request, 'dataAnalysis.html',
                      {
                          'race':race
                      })


def rankData(request):
    id = request.session.get('id')
    if request.method == "GET":
        rank = RaceRecord.objects.filter(student_id_id=id)
        rankX = []
        rankY = []
        for t in rank:
            rankX.append(t.race_id.name)
            rankY.append([float(t.score), t.race_id.evaluate_type])
        return JsonResponse({'rankX':rankX,
                'rankY':rankY,
                })
def raceData(request):
    id = request.session.get('id')
    if request.method == "GET":
        race_id = request.GET.get('id')
        rank = SubmitRecord.objects.filter(student_id_id=id, race_id_id=race_id)
        rankX = []
        rankY = []
        for t in rank:
            rankX.append(t.time)
            rankY.append([float(t.right_rate), t.race_id.evaluate_type])
            type = t.race_id.evaluate_type
        return JsonResponse({
            'rankX':rankX,
            'rankY':rankY,
            'type':type,
                })