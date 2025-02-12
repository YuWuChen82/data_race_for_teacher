from random import random

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from xlrd import Book

from djangoProject1.settings import MEDIA_ROOT
from student.models import *
# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Q
from teacher.views import sqlSelect, sqlWrite
import datetime, hashlib, tempfile, io, csv, chardet
import pytz
from django.utils import timezone


# Create your views here.
def index(request):
    articles = Article.objects.all().order_by('-pub_time')
    experts = Expert.objects.all()[0:2]
    paginator = Paginator(articles, 5)
    page = request.GET.get('page', '1')
    articles = paginator.page(page)
    return render(request, "index.html", {"articles": articles, "experts": experts})

def case(request):
    category = "案例"
    articles = Article.objects.filter(category=category)
    paginator = Paginator(articles, 5)
    page = request.GET.get('page', '1')
    articles = paginator.page(page)

    experts = Expert.objects.all()[0:2]
    return render(request, "index.html", {"articles": articles, "experts": experts, "category": category})

def kb(request):
    category = "知识"
    articles = Article.objects.filter(category=category)
    paginator = Paginator(articles, 5)
    page = request.GET.get('page', '1')
    articles = paginator.page(page)
    experts = Expert.objects.all()[0:2]
    return render(request, "index.html", {"articles": articles, "experts": experts, "category": category})

def video(request):
    category = "视频"
    articles = Article.objects.filter(category=category)
    paginator = Paginator(articles, 5)
    page = request.GET.get('page', '1')
    articles = paginator.page(page)
    experts = Expert.objects.all()[0:2]
    return render(request, "index.html", {"articles": articles, "experts": experts, "category": category})

def expert(request):
    experts = Expert.objects.all()[0:2]
    return render(request, "expert.html", {"experts": experts})

def article(request):
    article = Article.objects.filter(id=request.GET.get('id')).first()
    if article is None:
        return redirect('/blog')
    article.view_times += 1
    article.save()
    if request.method == 'POST':
        Comment.objects.create(
            user_id=request.session.get('id'),
            content=request.POST["comment"],
            article=request.GET["id"],
            time=str(timezone.make_aware(datetime.datetime.now(), pytz.UTC)),
        )
    comment = Comment.objects.filter(article=request.GET["id"]).order_by('time')
    paginator = Paginator(comment, 7)
    page = request.GET.get('page', 1)
    comment = paginator.get_page(page)
    return render(request, "article.html", {"article": article, "comment": comment})

def search(request):
    articles = Article.objects.all()
    if "tag" in request.GET:
        tag = request.GET["tag"]
        articles = Article.objects.filter(category=tag)
    if "q" in request.GET:
        q = request.GET["q"]
        articles = Article.objects.filter(Q(category__contains=q) | Q(content__contains=q) |Q(tags__contains=q) | Q(summary__contains=q))
    experts = Expert.objects.all()[0:2]
    paginator = Paginator(articles, 5)
    page = request.GET.get('page', '1')
    articles = paginator.page(page)

    return render(request, "index.html", {"articles": articles, "experts": experts, "category": "搜索"})

def dataShare(request):
    user_id = request.session.get('id')
    data = DataShare.objects.all().order_by('-id')
    paginator = Paginator(data, 10)
    page = request.GET.get('allpage', '1')
    c_obj = paginator.page(page)
    userdata = User.objects.filter(id=user_id).first()
    buyList = BuyRecord.objects.filter(buyer_id=user_id).values_list('data', flat=True)
    buyList = list(buyList)
    if request.method == "GET":
        webData = request.GET
        allpage = webData.get('allpage')
        mypage= webData.get('mypage')
        buypage = webData.get('buypage')
        buyrecord = webData.get('buyrecordpage')
        name = 'alldata'

        if allpage:
            page = request.GET.get('allpage', '1')
            paginator = Paginator(data, 10)
            c_obj = paginator.page(page)
            buyList = BuyRecord.objects.filter(buyer_id=user_id).values_list('data', flat=True)
            buyList = list(buyList)
            return render(request, 'dataShare.html',
                          {
                              'alldata': c_obj,
                              'user': userdata,
                              'buyList':buyList,
                          })
        elif mypage:
            name = 'mydata'
            page = request.GET.get('mypage', '1')
            data = DataShare.objects.filter(user_id=user_id).order_by('-id')
        elif buypage:
            name = 'buydata'
            page = request.GET.get('buypage', '1')
            data = BuyRecord.objects.filter(buyer_id=user_id).order_by('-id')
        elif buyrecord:
            name = 'buyrecord'
            page = request.GET.get('buyrecordpage', '1')
            data = BuyRecord.objects.filter(buyer_id=user_id).order_by('-id')
        paginator = Paginator(data, 10)
        c_obj = paginator.page(page)
        return render(request, 'dataShare.html',
                      {
                        name: c_obj,
                        'user': userdata,
                          'buyList': buyList,
                      })
    else:
        webdata = request.POST
        if "alldata" in webdata:
            return render(request, 'dataShare.html',
                          {
                              'alldata': c_obj,
                              'user': userdata,
                              'buyList': buyList,
                          })
        elif "mydata" in webdata:
            data = DataShare.objects.filter(user_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('mypage', '1')
            c_obj = paginator.page(page)
            userdata = User.objects.filter(id=user_id).first()
            if not data:
                flag = 1
            else:
                flag = 0
            return render(request, 'dataShare.html',
                          {
                              'mydata': c_obj,
                              'user': userdata,
                              'flag':flag
                          })
        elif "query_btn" in webdata:
            q = webdata.get('dataname')
            data = DataShare.objects.filter(brief__contains=q).order_by('-id')
            userdata = User.objects.filter(id=request.session.get('id')).first()
            buyList = BuyRecord.objects.filter(buyer_id=user_id).values_list('data', flat=True)
            buyList = list(buyList)

            if data:
                return render(request, 'dataShare.html',
                              {
                                  'alldata': data,
                                  'user': userdata,
                                  'buyList': buyList,
                              })
            else:
                data = DataShare.objects.all().order_by('-id')
                paginator = Paginator(data, 10)
                page = 1
                c_obj = paginator.page(page)
                return render(request, 'dataShare.html',
                              {
                                  'alldata': c_obj,
                                  'user': userdata,
                                  'buyList': buyList,
                                  'notice':"未查询到相关的数据"
                              })

        elif "buydata" in webdata:
            data = BuyRecord.objects.filter(buyer_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('buypage', '1')
            c_obj = paginator.page(page)
            userdata = User.objects.filter(id=user_id).first()
            return render(request, 'dataShare.html',
                          {
                              'buydata': c_obj,
                              'user': userdata,
                          })
        elif "buyrecord" in webdata:
            data = BuyRecord.objects.filter(buyer_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('buyrecordpage', '1')
            c_obj = paginator.page(page)
            userdata = User.objects.filter(id=user_id).first()
            return render(request, 'dataShare.html',
                          {
                              'buyrecord': c_obj,
                              'user': userdata,
                          })
        elif "updata" in webdata:
            brief = webdata.get('brief')
            points = webdata.get('points')
            data = DataShare.objects.filter(user_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('page', '1')
            c_obj = paginator.page(page)
            userdata = User.objects.filter(id=user_id).first()
            try:
                points = int(points)
            except:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "上传失败！积分输入有误"
                              })
            if points<0:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "上传失败！积分输入有误"
                              })
            if len(brief) > 20:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "上传失败！输入的字数超出限制。"
                              })
            else:
                try:
                    file = request.FILES['filedata']
                except:
                    return render(request, 'dataShare.html',
                                  {
                                      'mydata': c_obj,
                                      'user': userdata,
                                      'notice': "请上传文件。"
                                  })
                if not file.name.endswith('.zip'):
                    return render(request, 'dataShare.html',
                                  {
                                      'mydata': c_obj,
                                      'user': userdata,
                                      'notice': "上传失败！文件格式需为zip。"
                                  })
                else:
                    file_size = file.size  # 获取上传文件的大小，以字节为单位
                    if file_size > 1024 * 1024 * 500:  # 500 MB
                        return render(request, 'dataShare.html',
                                      {
                                          'mydata': c_obj,
                                          'user': userdata,
                                          'notice': "文件太大，请上传小于500MB的文件"
                                      })
                    else:
                        import uuid
                        fileName = str(uuid.uuid4())+".zip"
                        shareData = DataShare.objects.create(
                            brief=brief,
                            downloadTimes=0,
                            user_id=user_id,
                            file_name=fileName,
                            points=points,
                            size=file_size/1024/1024,
                        )
                        shareData.save()
                        fobj1 = open("media/dataShare/" + fileName, "wb")
                        for chunk in file.chunks():
                            fobj1.write(chunk)
                        fobj1.close()
                        data = DataShare.objects.filter(user_id=user_id).order_by('-id')
                        paginator = Paginator(data, 10)
                        page = request.GET.get('page', '1')
                        c_obj = paginator.page(page)
                        return render(request, 'dataShare.html',
                                      {
                                          'mydata': c_obj,
                                          'user': userdata,
                                          'notice': "数据资源上传成功！"
                                      })
        elif "changeData" in webdata:
            brief = webdata.get('brief')
            points = webdata.get('points')
            data = DataShare.objects.filter(user_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('page', '1')
            c_obj = paginator.page(page)
            userdata = User.objects.filter(id=user_id).first()
            try:
                points = int(points)
            except:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "修改失败！积分输入有误"
                              })
            if points < 0:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "修改失败！积分输入有误"
                              })
            if len(brief) > 20:
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "修改失败！输入的字数超出限制。"
                              })
            else:
                try:
                    file = request.FILES['filedata']
                    isFile = 1
                except:
                    isFile = 0
                dataId = int(webdata.get('dataId'))
                if isFile:
                    if not file.name.endswith('.zip'):
                        return render(request, 'dataShare.html',
                                      {
                                          'mydata': c_obj,
                                          'user': userdata,
                                          'notice': "上传失败！文件格式需为zip。"
                                      })
                    else:
                        file_size = file.size  # 获取上传文件的大小，以字节为单位
                        if file_size > 1024 * 1024 * 500:  # 500 MB
                            return render(request, 'dataShare.html',
                                          {
                                              'mydata': c_obj,
                                              'user': userdata,
                                              'notice': "文件太大，请上传小于500MB的文件"
                                          })
                        else:
                            fileName = DataShare.objects.get(id=dataId).file_name
                            fobj1 = open("media/dataShare/" + fileName, "wb")
                            for chunk in file.chunks():
                                fobj1.write(chunk)
                            fobj1.close()
                changeData = DataShare.objects.get(id=dataId)
                changeData.brief = brief
                changeData.points = points
                changeData.save()
                data = DataShare.objects.filter(user_id=user_id).order_by('-id')
                paginator = Paginator(data, 10)
                page = request.GET.get('page', '1')
                c_obj = paginator.page(page)
                return render(request, 'dataShare.html',
                              {
                                  'mydata': c_obj,
                                  'user': userdata,
                                  'notice': "修改成功！"
                              })
        elif "delData" in webdata:
            dataId = int(webdata.get('dataId'))
            DataShare.objects.get(id=dataId).delete()
            data = DataShare.objects.filter(user_id=user_id).order_by('-id')
            paginator = Paginator(data, 10)
            page = request.GET.get('page', '1')
            c_obj = paginator.page(page)
            return render(request, 'dataShare.html',
                          {
                              'mydata': c_obj,
                              'user': userdata,
                              'notice': "删除成功！"
                          })
        elif "purchaseData" in webdata:
            buyer = int(webdata.get('buyer'))
            seller = webdata.get('seller')
            buyer_data = User.objects.get(id=buyer)
            dataId = int(webdata.get("shareDataId"))
            shareData = DataShare.objects.get(id=dataId)
            if buyer_data.points < shareData.points:
                return render(request, 'dataShare.html',
                              {
                                  'alldata': c_obj,
                                  'user': userdata,
                                  'buyList': buyList,
                                  'notice': "购买失败！您的积分不足"
                              })
            else:
                buyer_data.points -= shareData.points
                buyer_data.save()
                record = BuyRecord.objects.create(
                    buyer_id=buyer,
                    data_id=dataId,
                )
                record.save()
                seller = User.objects.get(id=seller)
                seller.points += shareData.points
                seller.save()
                shareData.downloadTimes += 1
                shareData.save()
                buyList = BuyRecord.objects.filter(buyer_id=user_id).values_list('data', flat=True)
                buyList = list(buyList)
                userdata = User.objects.filter(id=user_id).first()
                return render(request, 'dataShare.html',
                              {
                                  'alldata': c_obj,
                                  'user': userdata,
                                  'buyList': buyList,
                                  'notice': "购买成功！"
                              })
        elif "recharge" in webdata:
            username = webdata.get('username')
            count = int(webdata.get('count'))
            userData = User.objects.filter(username=username).first()
            if userData:
                userData.points += count
                userData.save()
                notice = f"成功给用户{username}充值了{count}积分"
            else:
                notice = "充值失败！未找到该用户"
            userdata = User.objects.filter(id=user_id).first()
            return render(request, 'dataShare.html',
                          {
                              'alldata': c_obj,
                              'user': userdata,
                              'buyList': buyList,
                              'notice':notice,
                          })

#########################################教师端################################
def t_article(request):
    if request.method == 'POST':
        Article.objects.get(id=request.POST["id"]).delete()
    articles = Article.objects.exclude(category='视频').filter(user_id=request.session['id']).order_by('-id')
    page_num = request.GET.get('page', 1)
    paginator = Paginator(articles, 6)
    c_obj = paginator.get_page(page_num)
    return render(request, "Dashboard/article.html", {"articles": c_obj})


def t_article2(request):
    if request.method == 'GET':
        article = {}
        notice = ""
        if "id" in request.GET:
            article = Article.objects.filter(id=request.GET["id"]).first()
        if article is None:
            return redirect('article.html')
        return render(request, "Dashboard/article2.html", {"article": article, "notice": notice})

    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        category = request.POST["category"]
        summary = request.POST["summary"]
        tags = request.POST["tags"]
        time0 = request.POST["time"]
        view_times = 0
        if "id" not in request.GET:
            notice = "发布成功"
            article = Article.objects.create(
                view_times=view_times,
                zan_times=0,
                is_top=0,
                rank=0,
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                title=title,
                content=content,
                category=category,
                summary=summary,
                tags=tags,
                user_id=request.session["id"],
                pub_time=time0,
                img="default.jpg"
            )
        elif Article.objects.get(id=request.GET["id"]).user_id != request.session.get('id'):
            notice = "您只能修改自己发布的文章"
        else:
            notice = "修改成功"
            article = Article.objects.get(id=request.GET["id"])
            article.title = title
            article.content = content
            article.category = category
            article.summary = summary
            article.tags = tags
            article.pub_time = time0
            article.view_times = view_times
            article.save()
        if request.FILES:
            f = request.FILES['img']
            hz = "%s" % f.name
            hz = hz.split(".")[-1]
            fobj = open(MEDIA_ROOT + "/article/%s.%s" % (article.id, hz), 'wb')
            for chunk in f.chunks():
                fobj.write(chunk)
            fobj.close()
            article.img = "%s.%s" % (article.id, hz)
            article.save()
        if "id" not in request.GET:
            return HttpResponseRedirect("article.html")
        else:
            article = Article.objects.get(id=request.GET["id"])
            return render(request, "Dashboard/article2.html", {"article": article, "notice": notice})


def t_expert(request):
    if request.method == 'POST':
        Expert.objects.get(id=request.POST["id"]).delete()
    experts = Expert.objects.all()
    return render(request, "Dashboard/expert.html", {"experts": experts})


def t_expert2(request):
    if request.method == 'GET':
        expert = {}
        if "id" in request.GET:
            expert = Expert.objects.filter(id=request.GET["id"]).first()
        if expert is None:
            return redirect('expert.html')
        return render(request, "Dashboard/expert2.html", {"expert": expert})
    if request.method == 'POST':
        if "id" not in request.GET:
            m1 = hashlib.md5()
            phone = request.POST["phone"]
            m1.update(phone.encode('utf-8'))
            password = m1.hexdigest()
            expert = Expert.objects.create(
                name=request.POST["name"],
                domain=request.POST["domain"],
                introduction=request.POST["introduction"],
                phone=request.POST["phone"],
                wechat=request.POST["wechat"],
                qq=request.POST["qq"],
                price=request.POST["price"],
                avatar="default.jpg",
                password=password
            )
        else:
            expert = Expert.objects.get(id=request.GET["id"])
            expert.name = request.POST["name"]
            expert.domain = request.POST["domain"]
            expert.introduction = request.POST["introduction"]
            expert.phone = request.POST["phone"]
            expert.wechat = request.POST["wechat"]
            expert.qq = request.POST["qq"]
            expert.price = request.POST["price"]
            expert.save()
        if request.FILES:
            f = request.FILES['avatar']
            hz = "%s" % f.name
            hz = hz.split(".")[-1]
            fobj = open(MEDIA_ROOT + "/avatar/%s.%s" % (expert.id, hz), 'wb')
            for chunk in f.chunks():
                fobj.write(chunk)
            fobj.close()
            expert.avatar = "%s.%s" % (expert.id, hz)
            expert.save()
        if "id" not in request.GET:
            return HttpResponseRedirect("expert.html")
        else:
            expert = Expert.objects.all()
            return render(request, "Dashboard/expert.html", {"experts": expert})

