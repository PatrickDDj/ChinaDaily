from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('news-list/', views.news_list, name='news-list'),
    path('news-import/', views.news_import, name='news-import'),
    path('news-download/', views.news_download, name='news-download'),
    path('news-trend/', views.news_trend, name='news-trend'),
    path('news-real-time-input/', views.news_real_time_input, name='news-real-time-input'),
    path('news-real-time-result/', views.news_real_time_result, name='news-real-time-result')
]
