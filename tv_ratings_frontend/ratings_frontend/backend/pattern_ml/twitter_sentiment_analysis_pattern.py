from imdb import ImdbClient
from pattern.vector import Document, NB
from pattern.db import csv
from imdbpie import Imdb
from pymongo import MongoClient
import sys
import os


# TODO:
# 1 Train model with ALL imdb data possible for all shows and classify tweets from one show based on this (predicting overall imdb score?)
# 2 Train model with specific show + episode specific data and classify tweets for one show, try to predict next episode's imdb score (all tweets)!
# 3 Train model with specific show + episode specific data in order to classify tweets from one week back


class NBModel:
    def __init__(self):
        self.nb = NB()
        self.stats = Statistics()
        try:
            print("dir: " + os.getcwd())
            if os.getcwd().endswith("tv_ratings_frontend"):
                print("Working in django")
                self.nb = self.nb.load("ratings_frontend/backend/pattern_ml/nb_training.p")
            else:
                print("Not working in django")
                self.nb = self.nb.load("./nb_training.p")
            self.new_nb_model = True
            print("Using existing pickled model")
        except IOError:
            self.new_nb_model = False
            print("Creating new NB model")

    def nb_train_text(self, reviews):
        for review in reviews:
            if review.rating is not None and review.rating < 10 and review.rating > 1:
                v = Document(review.text, type=int(review.rating), stopwords=True)
                self.nb.train(v)
                # self.nb.save("./nb_training.p")
                #   print self.nb.classes

    def nb_train_summary(self, reviews):
        for review in reviews:
            if review.rating is not None:# and review.rating < 10 and review.rating > 1:
                v = Document(review.summary, type=int(review.rating), stopwords=True)
                self.nb.train(v)

    def nb_train_all_text(self, review_set):
        for review_list in review_set:
            self.nb_train_text(review_list)
        self.nb.save_model()

    def save_model(self):
        self.nb.save('./nb_training.p')

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
        self.nb_stats()
        Statistics().printStats(tvshow, ratingSum, len(tweet_docs))
        print self.nb.distribution

        return Statistics().get_stats(tvshow, ratingSum, len(tweet_docs))

    def nb_stats(self):
        print('----------- Classifier stats -----------')
        #  print("Features: ", self.nb.features)
        print("Classes: ", self.nb.classes)
        print("Skewness: ", self.nb.skewness)
        print("Distribution: ", self.nb.distribution)
        print("Majority: ", self.nb.majority)
        print("Minority: ", self.nb.minority)


class Statistics:
    def __init__(self):
        self.imdb = ImdbClient()

    # returns tuple: (sum, num_items, predicted rating, current IMDB rating, percent error)
    def get_stats(self, tvshow, sum, num_items):
        current_imdb_rating = self.imdb.getCurrentImdbRating(tvshow)
        predicted_value = float(sum) / num_items
        return sum, num_items, predicted_value, current_imdb_rating, \
               float(current_imdb_rating - predicted_value) / float(current_imdb_rating)

    def printStats(self, tvshow, sum, numItems):
        currentImdbRating = self.imdb.getCurrentImdbRating(tvshow)
        predictedValue = float(sum) / numItems
        print("---------- Statistics -----------")
        print("Sum of the ratings from Twitter: ", sum)
        print("Number of classified ratings: ", numItems)
        print("Average value: ", predictedValue)
        print("Current IMDB rating: ", currentImdbRating)
        print("Current error: ", float(currentImdbRating - predictedValue) / float(currentImdbRating))


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

    def classifyAll(self):
        possible_shows = ['Walking Dead', \
                          'Arrow', \
                          'Family Guy', \
                          'Big bang Theory', \
                          'South Park', \
                          'American Horror Story', \
                          'Modern Family', \
                          'Heroes Reborn']

        reviews = []
        for show in possible_shows:
            reviews.append(self.client.searchShow(show))
        self.nb.nb_train_text(reviews)
        self.nb.nb_classify_tweets(self.tvshow, self.client.readFromMongo(parse_show(self.tvshow), sys.maxint))

    def nb_train(self):
        shows = ['The Walking Dead',
                 'The Big Bang Theory',
                 'Arrow',
                 'Family Guy',
                 'South Park',
                 'American Horror Story',
                 'Modern Family',
                 'Heroes Reborn']
        for show in shows:
            reviews = self.client.searchShow(show)
            self.nb.nb_train_text(reviews)
            self.nb.save_model()

    def nbClassify(self):
        return self.nb.nb_classify_tweets(self.tvshow,
                                          self.client.readFromMongo(parse_show(self.tvshow), 10000))

def main(tvshow):
    classifier = Classifier(tvshow)
    classifier.nb_train()
    classifier.nbClassify()


if __name__ == "__main__":
    main("The Walking Dead")
