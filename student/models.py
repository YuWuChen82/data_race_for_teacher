from django.db import models
from DjangoUeditor.models import UEditorField
import datetime
from django.utils import timezone

class DataShare(models.Model):
    brief = models.CharField(max_length=255)
    time = models.DateTimeField(default=timezone.now)  # 需要导入 timezone 模块
    downloadTimes = models.IntegerField(null=True, default=None)
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user', null=True)
    file_name = models.CharField(max_length=255)
    points = models.IntegerField(null=True, default=0)
    size = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'dataShare'  # 指定数据库表名

class BuyRecord(models.Model):
    buyer = models.ForeignKey('User', on_delete=models.CASCADE, db_column='buyer', null=True,related_name='selling_records')
    time = models.DateTimeField(default=timezone.now)  # 需要导入 timezone 模块
    data = models.ForeignKey('DataShare',on_delete=models.CASCADE, db_column='data', null=True)
    class Meta:
        db_table = 'buy_record'  # 指定数据库表名



class Article(models.Model):
    title = models.CharField(max_length=100)
    img = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    view_times = models.IntegerField()
    zan_times = models.IntegerField()
    is_top = models.IntegerField()
    rank = models.IntegerField()
    pub_time = models.DateField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    category = models.CharField(max_length=200)
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='user')
    tags = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["-pub_time"]
        db_table = 'article'


class Comment(models.Model):
    time = models.DateTimeField(default=datetime.datetime.now())
    content = models.CharField(max_length=255, blank=True, null=True)
    article = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='user')

    class Meta:
        db_table = 'comment'


class Expert(models.Model):
    time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=20, blank=True, null=True)
    avatar = models.CharField(max_length=100, blank=True, null=True)
    introduction = models.TextField()
    domain = models.CharField(max_length=200, blank=True, null=True)
    price = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    qq = models.CharField(max_length=30, blank=True, null=True)
    wechat = models.CharField(max_length=100)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'expert'


class ChooseClass(models.Model):
    student_id = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True,to_field='id',db_column='student_id')
    class_id = models.ForeignKey('Class', models.DO_NOTHING,db_column='class_id')

    class Meta:
        managed = False
        db_table = 'choose_class'
        unique_together = (('id', 'class_id'),)


class Class(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    teacher_id = models.ForeignKey('User', models.DO_NOTHING,blank=True, null=True,db_column='teacher_id',)
    create_time = models.DateTimeField(blank=True, null=True)
    brief = models.CharField(max_length=100, blank=True, null=True)
    #class_time = models.CharField(max_length=100, blank=True, null=True, db_comment='上课时间')
    class_time = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'class'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Race(models.Model):
    name = models.CharField(max_length=2000, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    begin_time = models.CharField(max_length=20, blank=True, null=True)
    over_time = models.CharField(max_length=20, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    teacher_id = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True,db_column='teacher_id')
    time = models.DateTimeField(blank=True, null=True)
    file_data = models.CharField(max_length=100, blank=True, null=True)
    file_answer = models.CharField(max_length=100, blank=True, null=True)
    evaluate_type = models.CharField(max_length=100, blank=True, null=True)
    picture = models.CharField(max_length=100, blank=True, null=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE,
                                    db_column='class_id')  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'race'
        unique_together = (('id', 'class_id'),)


class RaceRecord(models.Model):
    race_id = models.ForeignKey(Race, models.DO_NOTHING, blank=True, null=True,db_column='race_id')
    student_id = models.ForeignKey('User', blank=True, null=True, db_column='student_id',on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    time = models.CharField(max_length=26, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'race_record'


class SubmitRecord(models.Model):
    student_id = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, to_field='id',db_column='student_id')
    class_id = models.ForeignKey('Class', models.DO_NOTHING, db_column='class_id')
    race_id = models.ForeignKey(Race, models.DO_NOTHING, blank=True, null=True, db_column='race_id')
    right_rate = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'submit_record'


class User(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    identity = models.CharField(max_length=20)
    organization = models.CharField(max_length=100)
    points = models.IntegerField(default=100,)
    class Meta:
        managed = False
        db_table = 'user'