import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import render
from sklearn.metrics import roc_auc_score, mean_squared_error, f1_score
import random
from student.models import *
import datetime, io, csv
import pytz
from django.utils import timezone
from django.db.models import Avg, Count, Max
import hashlib
from django.db.models import Q
import pymysql


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


def sqlSelect(sql):
    conn = pymysql.connect(host='localhost', port=3306, user='root1', passwd='123456', db='data_race')
    cur = conn.cursor()
    cur.execute(sql)
    sqlData = cur.fetchall()
    cur.close()
    conn.close()
    return sqlData


def sqlWrite(sql):
    conn = pymysql.connect(host='localhost', port=3306, user='root1', passwd='123456', db='data_race')
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return


def index(request):
    ss = request.session
    if request.method == 'GET':
        class_data = Class.objects.filter(teacher_id=ss.get('id'))
        return render(request, 'teacher_index.html', {'notice': '0', 'class_data': class_data})
    else:
        class_data = Class.objects.filter(teacher_id=ss.get('id'))
        rp = request.POST
        try:
            file_data = request.FILES['file_data']
            file_answer = request.FILES['file_answer']
        except:
            return render(request, 'teacher_index.html', {'notice': '1', 'class_data': class_data})
        race_type = rp.get('race_type')
        begin_time = rp.get('begin_time')
        over_time = rp.get('over_time')
        race_name = rp.get('race_name')
        class_id = rp.getlist('class_name')
        race_data = rp.get('question_introduce')
        evaluate_type = rp.get('evaluate_type')
        if not file_data.name.endswith('.zip') or not file_answer.name.endswith('.csv') \
                or not race_name or not begin_time or not over_time or not race_type or not class_id or not class_data or not evaluate_type:
            return render(request, 'teacher_index.html', {'notice': '1', 'class_data': class_data})
        id = Race.objects.aggregate(max_id=Max('id'))['max_id'] or 0
        id += 1

        #  图片列表
        picture_list = ["apple", "banana", "grape", "dragonFruit", "kiwifruit", "peach", "strawberry", "watermelon"]
        for t in class_id:
            file_data_name = "race_data_" + str(id) + ".zip"
            file_answer_name = "race_answer" + str(id) + ".csv"
            fobj1 = open("media/upload/" + file_data_name, "wb")
            for chunk in file_data.chunks():
                fobj1.write(chunk)
            fobj1.close()
            fobj2 = open("media/upload/" + file_answer_name, "wb")
            for chunk in file_answer.chunks():
                fobj2.write(chunk)
            fobj2.close()
            current_time = timezone.make_aware(datetime.datetime.now(), pytz.UTC)
            # 随机抽取图片
            random_picture = random.choice(picture_list)
            race = Race.objects.create(
                id=id,
                name=race_name,
                type=race_type,
                begin_time=begin_time,
                over_time=over_time,
                content=race_data,
                teacher_id_id=ss.get('id'),
                file_data=file_data_name,
                file_answer=file_answer_name,
                class_id_id=t,
                time=str(current_time),
                evaluate_type=evaluate_type,
                picture=random_picture + ".png",
            )
            id += 1
        return render(request, 'teacher_index.html', {'notice': '2', 'class_data': class_data})


def my_class(request):
    ss = request.session
    if request.method == 'GET':
        class_data = Class.objects.filter(teacher_id_id=ss.get('id')).annotate(num=Count('chooseclass')).order_by('-id')
        if not class_data:
            notice = '1'
        else:
            notice = '0'
        paginator = Paginator(class_data, 5)
        page = request.GET.get('page', 1)
        c_data = paginator.get_page(page)
        return render(request, 'teacher_class.html', {'notice': notice, 'data': c_data})
    else:
        webData = request.POST
        if "add_btn" in webData:
            name = webData.get("class_name")
            brief = webData.get("class_brief")
            class_time = webData.get("class_time")
            class_address = webData.get("class_address")
            current_time = timezone.make_aware(datetime.datetime.now(), pytz.UTC)
            Class.objects.create(
                name=name,
                teacher_id_id=ss.get('id'),
                brief=brief,
                class_time=class_time,
                address=class_address,
                create_time=str(current_time)
            )
        elif "delete_btn" in webData:
            class_id = webData.get("class_id")
            Class.objects.get(id=class_id).delete()
        class_data = Class.objects.filter(teacher_id_id=ss.get('id')).annotate(num=Count('chooseclass')).order_by('-id')
        if not class_data:
            notice = '1'
        else:
            notice = '0'
            paginator = Paginator(class_data, 5)
            page = request.GET.get('page', 1)
            c_data = paginator.get_page(page)
        return render(request, 'teacher_class.html', {'notice': notice, 'data': c_data})


def class_detail(request):
    class_id = request.GET.get('id', 1)
    data = Class.objects.filter(id=class_id).first()
    teacher_id = request.session.get('id')
    if data is None or data.teacher_id_id != teacher_id:
        return my_class(request)
    if request.method == "GET":
        sql = "SELECT u.id AS student_id, u.name AS student_name, u.username, " \
              "IFNULL(num_of_races, 0) AS num_of_races " \
              "FROM user u " \
              "INNER JOIN choose_class cc ON u.id = cc.student_id " \
              "LEFT JOIN " \
              "(SELECT rr.student_id, COUNT(DISTINCT rr.id) AS num_of_races " \
              "FROM race_record rr " \
              "INNER JOIN race r ON rr.race_id = r.id AND r.class_id = '%s' " \
              "GROUP BY rr.student_id) AS race_stats " \
              "ON u.id = race_stats.student_id " \
              "WHERE cc.class_id = '%s' AND u.identity = '学生';" % (class_id, class_id)
        data = sqlSelect(sql)
        with open("./media/class/class" + str(class_id) + ".csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["编号", "姓名", "账号", "参加的比赛数量"])  # 写入表头
            for row in data:
                writer.writerow(row)  # 写入数据行
        return render(request, 'teacher_class_detail.html', {'data': data, 'class_id': class_id})
    else:
        webData = request.POST
        class_id = request.GET.get('id', 1)
        notice = ''
        if "add_btn" in webData:
            name = webData.get("add_name")
            username = webData.get("add_username")
            password = webData.get("add_password") or "123456"
            m = hashlib.md5()
            m.update(password.encode("utf-8"))
            password = m.hexdigest()
            sql = "SELECT id FROM user where username = '%s'" % username
            stu_id = sqlSelect(sql)
            if stu_id == ():
                sql = "insert into user(name, username, password, identity) " \
                      "values ('%s', '%s', '%s', '学生')" \
                      % (name, username, password)
                sqlWrite(sql)
                sql = "SELECT id FROM user where username = '%s'" % username
                stu_id = sqlSelect(sql)
                sql = "insert into choose_class(student_id,class_id) values ('%s','%s')" % (stu_id[0][0], class_id)
                sqlWrite(sql)
                notice = f"学生‘{username}’已添加成功"
            else:
                sql = "select class_id from choose_class where student_id = '%s' and class_id = '%s'" % (
                    stu_id[0][0], class_id)
                if sqlSelect(sql) != ():
                    notice = f"添加失败！学生‘{username}’已经在本课程"
                    pass
                else:
                    notice = f"学生‘{username}’已添加成功"
                    sql = "insert into choose_class(student_id,class_id) values ('%s','%s')" % (stu_id[0][0], class_id)
                    sqlWrite(sql)
        if "race_number_sort" in webData:
            sql = "SELECT u.id AS student_id, u.name AS student_name, u.username, " \
                  "IFNULL(num_of_races, 0) AS num_of_races " \
                  "FROM user u " \
                  "INNER JOIN choose_class cc ON u.id = cc.student_id " \
                  "LEFT JOIN " \
                  "(SELECT rr.student_id, COUNT(DISTINCT rr.id) AS num_of_races " \
                  "FROM race_record rr " \
                  "INNER JOIN race r ON rr.race_id = r.id AND r.class_id = '%s' " \
                  "GROUP BY rr.student_id) AS race_stats " \
                  "ON u.id = race_stats.student_id " \
                  "WHERE cc.class_id = '%s' AND u.identity = '学生' order by num_of_races desc;" % (class_id, class_id)
            data = sqlSelect(sql)
            with open("./media/class/class" + str(class_id) + ".csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["编号", "姓名", "账号", "参加的比赛数量", ])  # 写入表头
                for row in data:
                    writer.writerow(row)  # 写入数据行
            return render(request, 'teacher_class_detail.html', {'data': data, 'class_id': class_id})
        if "change_btn" in webData:
            student_id = int(webData.get("change_stu_id"))
            name = webData.get("change_name")
            username = webData.get("change_username")
            existing_user = User.objects.filter(username=username).first()
            if existing_user and existing_user.id != student_id:
                notice = "用户名已存在，请重新输入其他用户名"
            elif username is None or username.strip() == "" or name is None or name.strip() == "":
                notice = "姓名或用户名不能为空"
            else:
                sql = "update user set name = '%s', username = '%s' where id = '%s'" % (name, username, student_id)
                sqlWrite(sql)
                notice = "学生信息修改成功"
        if "delete_btn" in webData:
            student_id = webData.get("student_id")
            sql = "delete from choose_class where student_id = '%s' and class_id = '%s'" % (student_id, class_id)
            sqlWrite(sql)
            notice = "学生已被移除"
        if "submit_file" in webData:
            if not request.FILES["myFile"].name.endswith('.csv'):
                notice = "文件格式错误"
            else:
                csv_file = request.FILES['myFile']
                a = csv_file.read()
                try:
                    csv_reader = csv.reader(a.decode('utf-8').splitlines())
                except:
                    csv_reader = csv.reader(a.decode('gbk').splitlines())
                data = list(csv_reader)
                if len(data) > 0:
                    column_count = len(data[0])
                else:
                    column_count = 0
                data = data[1:]
                for t in data:
                    if t[0] is None or t[1] is None or t[0] == "" or t[1] == "":
                        continue
                    sql = "SELECT id FROM user where username = '%s'" % t[1]
                    stu_id = sqlSelect(sql)
                    if not stu_id:
                        sql = "insert into user(name, username, password, identity) " \
                              "values ('%s', '%s', '%s', '学生')" \
                              % (t[0], t[1], "e10adc3949ba59abbe56e057f20f883e")
                        sqlWrite(sql)
                        sql = "SELECT id FROM user where username = '%s'" % t[1]
                        stu_id = sqlSelect(sql)
                        sql = "insert into choose_class(student_id,class_id) values ('%s','%s')" % (
                            stu_id[0][0], class_id)
                        sqlWrite(sql)
                    else:
                        sql = "select class_id from choose_class where student_id = '%s' and class_id = '%s'" % (
                            stu_id[0][0], class_id)
                        if sqlSelect(sql):
                            pass
                        else:
                            sql = "insert into choose_class(student_id,class_id) values ('%s','%s')" % (
                                stu_id[0][0], class_id)
                            sqlWrite(sql)
                notice = "学生导入成功"
        if 'reset_btn' in webData:
            student_id = webData.get('student_id_reset', 1)
            User.objects.filter(id=student_id).update(password='e10adc3949ba59abbe56e057f20f883e')
            notice = "学生密码重置成功"
        sql = "SELECT u.id AS student_id, u.name AS student_name, u.username, " \
              "IFNULL(num_of_races, 0) AS num_of_races " \
              "FROM user u " \
              "INNER JOIN choose_class cc ON u.id = cc.student_id " \
              "LEFT JOIN " \
              "(SELECT rr.student_id, COUNT(DISTINCT rr.id) AS num_of_races " \
              "FROM race_record rr " \
              "INNER JOIN race r ON rr.race_id = r.id AND r.class_id = '%s' " \
              "GROUP BY rr.student_id) AS race_stats " \
              "ON u.id = race_stats.student_id " \
              "WHERE cc.class_id = '%s' AND u.identity = '学生';" % (class_id, class_id)
        data = sqlSelect(sql)
        with open("./media/class/class" + str(class_id) + ".csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["编号", "姓名", "账号", "参加的比赛数量"])  # 写入表头
            for row in data:
                writer.writerow(row)  # 写入数据行
        return render(request, 'teacher_class_detail.html', {'data': data, 'class_id': class_id, 'notice': notice})


def my_race(request):
    data = Race.objects.filter(teacher_id_id=request.session.get('id')).order_by('-id')
    c_class = Class.objects.filter(teacher_id_id=request.session.get('id'))
    now_time = str(datetime.date.today())
    if request.method == 'GET':
        paginator = Paginator(data, 7)
        page = request.GET.get('page', 1)
        c_data = paginator.get_page(page)
        return render(request, 'teacher_my_race.html', {'data': c_data, 'class': c_class, 'now_time': now_time})
    else:
        webData = request.POST
        if "delete_btn" in webData:
            race_id = webData.get("race_id")
            Race.objects.get(id=race_id).delete()
            data = Race.objects.filter(teacher_id_id=request.session.get('id')).order_by('-id')
            paginator = Paginator(data, 7)
            page = request.GET.get('page', 1)
            c_data = paginator.get_page(page)
            return render(request, 'teacher_my_race.html',
                          {'data': c_data, 'class': c_class, 'now_time': now_time, })
        elif "query_btn" in webData:
            class_id = webData.get("class_id")
            race_type = webData.get("race_type")
            race_state = webData.get("race_state")
            query = Q()
            # 根据班级进行过滤
            if class_id != "全部":
                query &= Q(class_id_id=class_id)
            # 根据比赛类型进行过滤
            if race_type != "全部":
                query &= Q(type=race_type)
            # 根据比赛状态进行过滤
            if race_state == "未开始":
                query &= Q(begin_time__gt=now_time)
            elif race_state == "已结束":
                query &= Q(over_time__lt=now_time)
            elif race_state == "进行中":
                query &= Q(begin_time__lte=now_time, over_time__gte=now_time)
            # 应用筛选条件
            if class_id != "全部":
                class_id = int(class_id)
            data = data.filter(query).all()
            paginator = Paginator(data, 7)
            page = request.GET.get('page', 1)
            c_data = paginator.get_page(page)
            return render(request, 'teacher_my_race.html',
                          {'data': c_data, 'class': c_class, 'now_time': now_time,
                           'race_state': race_state, 'race_type': race_type, 'class_id': class_id})


def change_race(request):
    if request.method == "GET":
        race_id = request.GET.get('id', 1)
        data = Race.objects.filter(id=race_id).first()
        teacher_id = request.session.get('id')
        if data is None or data.teacher_id_id != teacher_id:
            return my_race(request)
        else:
            class_data = Class.objects.filter(teacher_id_id=request.session.get('id'))
            return render(request, 'teacher_change_race.html', {'data': data, 'class_data': class_data})
    else:
        ss = request.session
        class_data = Class.objects.filter(teacher_id=ss.get('id'))
        rp = request.POST
        try:
            file_data = request.FILES['file_data']
            isData = 1
        except:
            isData = 0
        try:
            file_answer = request.FILES['file_answer']
            isAnswer = 1
        except:
            isAnswer = 0
        race_type = rp.get('race_type')
        begin_time = rp.get('begin_time')
        over_time = rp.get('over_time')
        race_name = rp.get('race_name')
        class_id = rp.get('class_name')
        race_data = rp.get('question_introduce')
        race_id = rp.get('race_id')
        evaluate = rp.get('evaluate_type')
        data = Race.objects.get(id=race_id)
        if not race_name or not begin_time or not over_time or not race_type or not class_id or not class_data:
            return render(request, 'teacher_change_race.html',
                          {'notice': '1', 'class_data': class_data, 'data': data})
        if isAnswer:
            if not file_answer.name.endswith('.csv'):
                return render(request, 'teacher_change_race.html',
                              {'notice': '1', 'class_data': class_data, 'data': data})
            else:
                fobj2 = open("media/upload/" + data.file_answer, "wb")
                for chunk in file_answer.chunks():
                    fobj2.write(chunk)
                fobj2.close()
        if isData:
            if not file_data.name.endswith('.zip'):
                return render(request, 'teacher_change_race.html',
                              {'notice': '1', 'class_data': class_data, 'data': data})
            else:
                fobj1 = open("media/upload/" + data.file_data, "wb")
                for chunk in file_data.chunks():
                    fobj1.write(chunk)
            fobj1.close()

        current_time = timezone.make_aware(datetime.datetime.now(), pytz.UTC)
        race = Race.objects.filter(id=race_id).update(
            name=race_name,
            type=race_type,
            begin_time=begin_time,
            over_time=over_time,
            content=race_data,
            class_id_id=class_id,
            time=str(current_time),
            evaluate_type=evaluate,
        )
        data = Race.objects.get(id=race_id)
        return render(request, 'teacher_change_race.html', {'notice': '2', 'class_data': class_data, 'data': data})


def race_detail(request):
    race_id = request.GET.get('id', 1)
    race_data = Race.objects.filter(id=int(race_id)).first()
    if race_data is None or race_data.teacher_id_id != request.session.get('id'):
        return my_race(request)
    evaluate = race_data.evaluate_type
    rankList = []
    if race_data.evaluate_type != "RMSE":
        rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('-score')
    else:
        rank = RaceRecord.objects.filter(race_id_id=race_id, score__gt=0).order_by('score')
    count = 1
    for t in rank:
        rankList.append(
            [count, t.student_id.username, t.student_id.name, t.student_id.organization, t.score, t.time])
        count += 1

    if request.method == "GET":
        with open("media/rank/" + "race_rank" + str(race_id) + ".csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["排名", "账号", "姓名", "组织", evaluate, "最优成绩提交日"])  # 写入表头
            count = 0
            for row in rank:
                count += 1
                writer.writerow(
                    [count, row.student_id.username, row.student_id.name, row.student_id.organization, f"{row.score}",
                     row.time])  # 写入数据行
        return render(request, 'teacher_race_detail.html', {'race_data': race_data, 'notice': '0', 'rank': rank})
    else:
        webInput = request.POST
        if "sortByScore" in webInput:
            return render(request, 'teacher_race_detail.html',
                          {'race_data': race_data, 'notice': '0', 'rank': rank})
        elif "sortByUsername" in webInput:
            rankList.sort(key=lambda x: x[1])
            return render(request, 'teacher_race_detail.html',
                          {'race_data': race_data, 'notice': '0', 'rank': rank, 'rankList': rankList})
        else:
            path_answer = Race.objects.get(id=race_id).file_answer
            try:
                file_data = request.FILES['submit_answer']
                file_answer_name = "student_answer" + str(request.session.get('id')) + ".csv"
                student_file_path = "media/upload/" + file_answer_name
                fobj1 = open(student_file_path, "wb")
                for chunk in file_data.chunks():
                    fobj1.write(chunk)
                fobj1.close()
            except:
                return render(request, 'teacher_race_detail.html',
                              {'race_data': race_data, 'notice': '1', 'rank': rank})
            if not file_data.name.endswith('.csv'):
                return render(request, 'teacher_race_detail.html',
                              {'race_data': race_data, 'notice': '1', 'rank': rank})
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
            #     return render(request, 'teacher_race_detail.html', {'race_data': race_data, 'notice': '1', 'rank': rank})
            student_file = pd.read_csv(student_file_path)

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
                return render(request, 'teacher_race_detail.html',
                              {'race_data': race_data, 'rank': rank,
                               'notice': '1', })
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
            # if evaluate == "ACC":
            #     right = 0
            #     for s1, a1 in zip(student_file, answer_file):
            #         if s1 == a1:
            #             right += 1
            #     right_rate = round(right / answer_len, 6)
            # elif evaluate == "P":
            #     # 精准率计算逻辑
            #     true_positives = 0  # 初始化真正例数
            #     false_positives = 0  # 初始化假正例数
            #
            #     # 假设 student_file 和 answer_file 是二维列表，每行包含多个数据，且第二列是预测的标签
            #     for s1, a1 in zip(student_file, answer_file):
            #         if s1[1] == 1 and a1[1] == 1:
            #             true_positives += 1  # 预测为正且实际为正
            #         elif s1[1] == 1 and a1[1] != 1:
            #             false_positives += 1  # 预测为正但实际为负
            #
            #     # 计算精准率
            #     if true_positives + false_positives == 0:
            #         precision = 0  # 避免除以零错误
            #     else:
            #         precision = round(true_positives / (true_positives + false_positives), 6)
            #     right_rate = precision
            # elif evaluate == "R":
            #     # 召回率计算逻辑
            #     true_positives = 0  # 初始化真正例数
            #     false_negatives = 0  # 初始化假负例数
            #
            #     # 假设 student_file 和 answer_file 是二维列表，每行包含多个数据，且第二列是预测的标签
            #     for s1, a1 in zip(student_file, answer_file):
            #         if s1[1] == 1 and a1[1] == 1:
            #             true_positives += 1  # 预测为正且实际为正
            #         elif s1[1] != 1 and a1[1] == 1:
            #             false_negatives += 1  # 预测为负但实际为正
            #
            #     # 计算召回率
            #     if true_positives + false_negatives == 0:
            #         recall = 0  # 避免除以零错误
            #     else:
            #         recall = round(true_positives / (true_positives + false_negatives), 6)
            #     right_rate = recall
            # elif evaluate == "AUC":
            #     from sklearn.metrics import roc_auc_score
            #     true_labels = [float(t[1]) for t in answer_file]
            #     probabilities = [float(t[1]) for t in student_file]
            #     auc = roc_auc_score(true_labels, probabilities)
            #     # 将AUC格式化为百分比形式，保留六位小数
            #     formatted_auc = round(auc, 6)
            #     right_rate = formatted_auc
            # elif evaluate == "RMSE":
            #     from sklearn.metrics import mean_squared_error
            #     true_values = [float(t[1]) for t in answer_file]
            #     predicted_values = [float(t[1]) for t in student_file]
            #     mse = mean_squared_error(true_values, predicted_values)
            #     right_rate = round(mse ** 0.5, 6)
            return render(request, 'teacher_race_detail.html',
                          {'race_data': race_data, 'notice': '2', 'rank': rank, 'score': right_rate})


def homepage(request):
    if request.method == "GET":
        id = request.session.get('id')
        data = User.objects.filter(id=id).first()
        return render(request, 'teacher_homepage.html', {'data': data, 'notice': 0})
    else:
        webData = request.POST
        ss = request.session
        id = request.session.get('id')
        data = User.objects.filter(id=id).first()
        old = webData.get('old_password')
        new1 = webData.get('new_password')
        new2 = webData.get('repeat_password')
        if not old or not new1 or not new2:
            return render(request, 'teacher_homepage.html',
                          {'data': data, 'notice': '4'})
        m = hashlib.md5()
        m.update(old.encode("utf-8"))
        old = m.hexdigest()
        password = User.objects.get(id=ss.get('id')).password
        if old != password:
            return render(request, 'teacher_homepage.html',
                          {'data': data, 'notice': '1'})
        m = hashlib.md5()
        m.update(new1.encode("utf-8"))
        new1 = m.hexdigest()
        if new1 == password:
            return render(request, 'teacher_homepage.html',
                          {'data': data, 'notice': '2'})
        m = hashlib.md5()
        m.update(new2.encode("utf-8"))
        new2 = m.hexdigest()
        if new1 != new2:
            return render(request, 'teacher_homepage.html',
                          {'data': data, 'notice': '5'})
        User.objects.filter(id=ss.get('id')).update(password=new1)
        return render(request, 'teacher_homepage.html',
                      {'data': data, 'notice': '3'})


def student_submit(request):
    if request.method == "GET":
        class_id = request.GET.get('id', 0)
        class_id = int(class_id)
        if class_id == 0:
            data = SubmitRecord.objects.filter(class_id__teacher_id_id=request.session.get('id')).order_by('-time')
        else:
            data = SubmitRecord.objects.filter(class_id__teacher_id_id=request.session.get('id'),
                                               class_id_id=class_id).order_by(
                '-time')
        page = request.GET.get('page', 1)
        paginator = Paginator(data, 16)
        c_data = paginator.get_page(page)
        class_data = Class.objects.filter(teacher_id_id=request.session.get('id'))
        return render(request, 'teacher_student_submit.html',
                      {'data': c_data, 'class_data': class_data, 'class_id': class_id})
    else:
        class_id = request.GET.get('id', 0)
        webData = request.POST
        name = webData.get('stu_name')
        data = SubmitRecord.objects.filter(Q(student_id__name__contains=name) | Q(student_id__username__contains=name),
                                           class_id__teacher_id_id=request.session.get('id'), ).order_by('-time')
        page = request.GET.get('page', 1)
        paginator = Paginator(data, 16)
        c_data = paginator.get_page(page)
        class_data = Class.objects.filter(teacher_id_id=request.session.get('id'))
        return render(request, 'teacher_student_submit.html',
                      {'data': c_data, 'class_data': class_data, 'class_id': class_id})


def add_admin(request):
    if request.method == "GET":
        notice = ""
        return render(request, 'teacher_add_admin.html', {'notice': notice})
    else:
        webData = request.POST
        if 'add_btn' in webData:
            name = webData.get('add_name')
            username = webData.get('add_username')
            password = webData.get('add_password')
            a = User.objects.filter(username=username)
            if not (name and username and password):
                notice = "不能提交空内容。"
                return render(request, 'teacher_add_admin.html', {'notice': notice})
            if a:
                notice = "添加失败！该用户名已经存在。"
            else:
                m = hashlib.md5()
                m.update(password.encode("utf-8"))
                password = m.hexdigest()
                User.objects.create(
                    name=name,
                    username=username,
                    password=password,
                    identity='教师',
                )
                notice = f"{username}添加成功！"
            return render(request, 'teacher_add_admin.html', {'notice': notice})
        elif 'query_btn' in webData:
            name = webData.get('stu_name')
            information = User.objects.filter(Q(name__contains=name) | Q(username__contains=name),
                                              identity="学生").annotate(b=Count('racerecord__id'))
            return render(request, 'teacher_add_admin.html', {'student_data': information})
