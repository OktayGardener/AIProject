from imdb import ImdbClient
from pattern.vector import Document, NB
from pattern.db import csv
from imdbpie import Imdb
from pymongo import MongoClient
import sys


class NBModel:
    def __init__(self):
        self.nb = NB()
        self.stats = Statistics()
        try:
            self.nb = self.nb.load("./nb_training.p")
            self.new_nb_model = True
        except IOError:
            self.new_nb_model = False
            print("Creating new NB model")

    def naive_bayes_train(self, reviews):
        for review in reviews:
            if review.rating is not None:
                v = Document(review.text, type=int(review.rating), stopwords=True)
                self.nb.train(v)
        self.nb.save("./nb_training.p")
        print self.nb.classes

    def nb_test_imdb(self, reviews):
        arr = []
        for review in reviews:
            if review.rating is not None:
                v = Document(review.text, type=int(review.rating), stopwords=True)
                arr.append(v)
        print self.nb.test(arr, target=None)

    def nb_classify_tweets(self, tvshow, tweets):
        ratingSum = 0
        tweet_docs = [(self.nb.classify(Document(tweet)), tweet) for tweet in tweets]
        for tweet in tweet_docs:
            ratingSum += tweet[0]
            # print tweet
        # print("Doc[0] ", tweet_docs[0])
        print("num documents: ", len(tweet_docs))
        print("TV SHOW:::::::::::" + tvshow)
        Statistics().printStats(tvshow, ratingSum, len(tweet_docs))


class Statistics:
    def __init__(self):
        self.imdb = ImdbClient()

    def printStats(self, tvshow, sum, numItems):
        print("---------- Statistics -----------")
        print("Sum of the ratings from Twitter: ", sum)
        print("Number of classified ratings: ", numItems)
        print("Average value: ", float(sum) / numItems)
        print("Current IMDB rating: ", self.imdb.getCurrentImdbRating(tvshow))


def parse_show(show):
    lower_show = show.lower()
    print('Show: ', show)
    possible_shows = ['Walking Dead', \
                      'Arrow', \
                      'Family Guy', \
                      'Big bang Theory', \
                      'South Park', \
                      'American Horror Story', \
                      'Modern Family', \
                      'Heroes Reborn']
    if 'walking' in lower_show or 'dead' in lower_show:
        return possible_shows[0]
    elif lower_show == 'arrow':
        return possible_shows[1]
    elif lower_show == 'family guy' or 'guy' in lower_show:
        return possible_shows[2]
    elif 'big' in lower_show or 'bang' in lower_show or 'theory' in lower_show:
        return possible_shows[3]
    elif 'south' in lower_show or 'park' in lower_show:
        return possible_shows[4]
    elif 'american' in lower_show or 'horror' in lower_show or 'story' in lower_show:
        return possible_shows[5]
    elif 'modern' in lower_show:
        return possible_shows[6]
    elif 'heroes' in lower_show or 'reborn' in lower_show:
        return possible_shows[7]

    return 'undertermined'


class Classifier:
    def __init__(self, tvshow):
        self.tvshow = tvshow
        self.nb = NBModel()
        self.client = ImdbClient()

    def nbClassify(self):
        reviews = self.client.searchShow(self.tvshow)

        self.nb.naive_bayes_train(reviews)

        self.nb.nb_classify_tweets(self.tvshow, self.client.readFromMongo(parse_show(self.tvshow), 100))


def main(tvshow):
    classifier = Classifier(tvshow)
    classifier.nbClassify()


if __name__ == "__main__":
    main("The Walking Dead")
