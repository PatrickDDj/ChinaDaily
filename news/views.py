from django.http import HttpResponse
from django.shortcuts import render, redirect
from .sparkTools.emotion_analysis import news_emotion_analysis_by_file, news_emotion_analysis_by_text
from .sparkTools.test_crawler import crawl
from .models import News
import os
from django.db.models import Avg
# Create your views here.


# 新闻首页（列表）：可通过date和type两个属性进行筛选
def news_list(request):
    date = request.GET.get('date')
    type = request.GET.get('type')
    news_list = News.objects.all().order_by('-add_time')
    if date != "" and date != None:
        news_list = news_list.filter(add_time=date)

    # 将某种情感占比大于40%的新闻定义为改种情感类型的新闻
    if type != "" and type != None:
        if type == 'positive':
            news_list = news_list.filter(positive__gte=40).order_by('-positive')
        if type == 'negative':
            news_list = news_list.filter(negative__gte=40).order_by('-negative')
        if type == 'neutral':
            news_list = news_list.filter(negative__gte=40).order_by('-neutral')
    context = {'news_list': news_list, 'date': date, 'type': type}
    return render(request, 'news/news-list.html', context)


# 导入新闻以及其情感分析结果至数据库中
def news_import(request):
    date = request.GET.get('date')
    dict_path = 'static/news/'+str(date)
    files = os.listdir(dict_path)

    # 分析当日所有新闻情感构成
    # 导入结果到数据库中
    for file in files:
        emotion_proportion, content = news_emotion_analysis_by_file(dict_path + '/' + file)

        news = News(title=file.replace('.txt', ''),
                    content = content,
                    positive = emotion_proportion['positive'],
                    negative = emotion_proportion['negative'],
                    neutral = emotion_proportion['neutral']
        )
        news.save()

    return redirect('news:news-list')


# 下载当日新闻到本地
def news_download(request):
    # 调用爬虫函数将当日新闻下载到本地指定文件夹中
    crawl()
    return HttpResponse('Success!')


# 分析近日新闻情感趋势
def news_trend(request):
    daily_proportion_list = News.objects.values('add_time').annotate(
        positive_score = Avg('positive'),
        neutral_score = Avg('neutral'),
        negative_score = Avg('negative')
    )
    # 获取数据库中所有新闻的日期,根据不同日期进行分组（group操作）
    time_list = list(daily_proportion_list.values_list('add_time', flat=True))
    time_list = [str(i).replace('&#39', '') for i in time_list]


    context = {'time_list': time_list,
               'positive_list': list(daily_proportion_list.values_list('positive_score', flat=True)),
               'neutral_list': list(daily_proportion_list.values_list('neutral_score', flat=True)),
               'negative_list': list(daily_proportion_list.values_list('negative_score', flat=True))}

    # 前端接受各个参数用于绘制情感构成直方图
    return render(request, 'news/news-trend.html', context)


# 导航至实时分析情感构成界面
def news_real_time_input(request):
    return render(request, 'news/news-real-time-input.html')


# 获取用户输入的英文文本，调用文本分析函数获取情感构成
def news_real_time_result(request):
    news = request.POST.get('news')

    emotion_proportion, _ = news_emotion_analysis_by_text(news)

    context = {'news': news, 'emotion_proportion': emotion_proportion}

    return render(request, 'news/news-real-time-result.html', context)
