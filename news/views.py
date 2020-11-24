from django.http import HttpResponse
from django.shortcuts import render, redirect
from .sparkTools.emotion_analysis import news_emotion_analysis_by_file, news_emotion_analysis_by_text
from .sparkTools.test_crawler import crawl
from .models import News
import os
from django.db.models import Avg
# Create your views here.


def news_list(request):
    date = request.GET.get('date')
    type = request.GET.get('type')
    news_list = News.objects.all().order_by('-add_time')
    if date != "" and date != None:
        news_list = news_list.filter(add_time=date)
    if type != "" and type != None:
        if type == 'positive':
            news_list = news_list.filter(positive__gte=40).order_by('-positive')
        if type == 'negative':
            news_list = news_list.filter(negative__gte=40).order_by('-negative')
        if type == 'neutral':
            news_list = news_list.filter(negative__gte=40).order_by('-neutral')
    context = {'news_list': news_list, 'date': date, 'type': type}
    return render(request, 'news/news-list.html', context)


def news_import(request):
    date = request.GET.get('date')
    dict_path = 'static/news/'+str(date)
    files = os.listdir(dict_path)

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


def news_download(request):
    crawl()
    return HttpResponse('Success!')


def news_trend(request):
    daily_proportion_list = News.objects.values('add_time').annotate(
        positive_score = Avg('positive'),
        neutral_score = Avg('neutral'),
        negative_score = Avg('negative')
    )

    time_list = list(daily_proportion_list.values_list('add_time', flat=True))
    time_list = [str(i).replace('&#39', '') for i in time_list]


    context = {'time_list': time_list,
               'positive_list': list(daily_proportion_list.values_list('positive_score', flat=True)),
               'neutral_list': list(daily_proportion_list.values_list('neutral_score', flat=True)),
               'negative_list': list(daily_proportion_list.values_list('negative_score', flat=True))}

    return render(request, 'news/news-trend.html', context)


def news_real_time_input(request):
    return render(request, 'news/news-real-time-input.html')


def news_real_time_result(request):
    news = request.POST.get('news')

    emotion_proportion, _ = news_emotion_analysis_by_text(news)

    context = {'news': news, 'emotion_proportion': emotion_proportion}

    return render(request, 'news/news-real-time-result.html', context)
