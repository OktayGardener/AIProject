# from pattern.vector import Document, NB
# from pattern.db import csv

# nb = NB()
# for review, rating in csv('reviews.csv'):
#     v = Document(review, type=int(rating), stopwords=True)
#     nb.train(v)

# print nb.classes
# print nb.classify(Document('A good movie!'))

from imdbpie import Imdb

imdb = Imdb()
imdb = Imdb(anonymize=True)  # to proxy requests


# Creating an instance with caching enabled
# Note that the cached responses expire every 2 hours or so.
# The API response itself dictates the expiry time)
# imdb = Imdb(cache=True)
# Specify optional cache directory, the default is '/tmp/imdbpiecache'
# imdb = Imdb(cache=True, cache_dir='/tmp/imdbpiecache/')

def getTitle(show_title):
    title_list = list(imdb.search_for_title(show_title))
    index = 0
    show_id = None

    while show_id is None:
        if title_list[index][u'title'] == show_title:
            show_id = title_list[index][u'imdb_id']
        index += 1

    return show_id


def searchShow(tvshow):
    title_id = getTitle(tvshow)
    print('title: ', title_id)
    print(imdb.get_title_reviews(title_id, max_results=15))

searchShow("The Walking Dead")
