from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

EMOTION_WORDS_PATH = 'static/emotionDict.txt'

import os
os.environ["PYSPARK_PYTHON"]="/Users/patrickdd/opt/anaconda3/envs/root_env/bin/python3"

conf = SparkConf().setAppName("ChinaDaily").setMaster("spark://localhost:7077")
sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")   # 设置日志级别
spark = SparkSession(sc)


# 获取情感字典
def get_emotion_words():
    emotion_lines = open(EMOTION_WORDS_PATH, 'r').readlines()
    emotion_words = {}
    for line in emotion_lines:
        word, emotion = line.split('\t')
        emotion_words[word] = emotion.replace('\n', '')
    return emotion_words


# 通过txt文本文件分析情感构成
def news_emotion_analysis_by_file(news_path):

    news = open(news_path, 'r').read()

    emotion_proportion, news = news_emotion_analysis_by_text(news)

    return emotion_proportion, news


# 直接通过文本分析情感构成
def news_emotion_analysis_by_text(news):
    emotion_words = get_emotion_words()

    # 英文文本可以直接用空格' ' 分词
    news_words = news.split(' ')
    # 转化为RDD格式
    wordsRDD = sc.parallelize(news_words)

    # 1 - 过滤空（无效）单词
    # 2 - 过滤不在情感字典中的单词
    # 3 - 将单个word通过情感字典映射为positive neutral negative中的一种
    # 4 - 统计三类情感出现次数，转化为百分比作为返回值
    res = wordsRDD.filter(lambda word: word in emotion_words.keys()).map(lambda word: emotion_words[word]).map(
        lambda emotion: (emotion, 1)).reduceByKey(lambda e1, e2: e1 + e2).sortBy(ascending=False, numPartitions=None,
                                                                                 keyfunc=lambda x: x[0])

    res = res.take(3)

    emotion_proportion = {}

    cnt = 0

    for i in res:
        emotion_proportion[i[0]] = i[1]
        cnt += i[1]

    for i in emotion_proportion.keys():
        emotion_proportion[i] = int(emotion_proportion[i] * 100 / cnt)

    return emotion_proportion, news


