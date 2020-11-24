from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

EMOTION_WORDS_PATH = 'static/emotionDict.txt'

import os
os.environ["PYSPARK_PYTHON"]="/Users/patrickdd/opt/anaconda3/envs/root_env/bin/python3"

conf = SparkConf().setAppName("ChinaDaily").setMaster("spark://localhost:7077")
sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")   # 设置日志级别
spark = SparkSession(sc)


def get_emotion_words():
    emotion_lines = open(EMOTION_WORDS_PATH, 'r').readlines()
    emotion_words = {}
    for line in emotion_lines:
        word, emotion = line.split('\t')
        emotion_words[word] = emotion.replace('\n', '')
    return emotion_words


def news_emotion_analysis_by_file(news_path):

    # emotion_words = get_emotion_words()
    news = open(news_path, 'r').read()

    emotion_proportion, news = news_emotion_analysis_by_text(news)
    # news_words = news.split(' ')
    # wordsRDD = sc.parallelize(news_words)
    # res = wordsRDD.filter(lambda word: word in emotion_words.keys()).map(lambda word: emotion_words[word]).map(lambda emotion: (emotion, 1)).reduceByKey(lambda e1, e2: e1+e2).sortBy(ascending=False, numPartitions=None, keyfunc=lambda x: x[0])
    #
    # res = res.take(3)
    #
    # emotion_propertion = {}
    #
    # cnt = 0
    #
    # for i in res:
    #     emotion_propertion[i[0]] = i[1]
    #     cnt += i[1]
    #
    # for i in emotion_propertion.keys():
    #     emotion_propertion[i] = int(emotion_propertion[i]*100/cnt)
    #
    return emotion_proportion, news


def news_emotion_analysis_by_text(news):
    emotion_words = get_emotion_words()

    # news = open(news_path, 'r').read()
    news_words = news.split(' ')
    wordsRDD = sc.parallelize(news_words)
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


# emotion_propertion = news_emotoio_analysis("20201117/14th Five-Year Plan showcases democratic policy-making - People's Daily Online.txt")
#
# print(emotion_propertion)
