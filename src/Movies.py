import time
import random
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = 'http://www.metacritic.com/'
SLEEP_TIME = 1

class Movie:
    def __init__(self, url_id):
        self.url_id = url_id
        self.details_url = BASE_URL + 'movie/' + url_id + '/details'
        self.critics_url = BASE_URL + 'movie/' + url_id + '/critic-reviews'
        self.users_url = BASE_URL + 'movie/' + url_id + '/user-reviews'
        self.soup = self.make_soup_from_url(self.details_url)
        self.critics_soup = self.make_soup_from_url(self.critics_url)
        self.users_soup = self.make_soup_from_url(self.users_url)
        self.title = self.soup.find('h1').text
        self.metascore = self.soup.select('span.metascore_w.header_size')[0].text
        self.user_score = self.soup.select('span.metascore_w.user')[0].text
        self.release_date = self.soup.find('div', {'class': 'product_info'}).find('span', {'class': 'release_date'}).text.strip().split('\n')[1]
        self.runtime = self.get_tr('runtime')
        self.movie_rating = self.get_tr('movie_rating')
        self.company = self.get_tr('company')
        self.languages = self.get_tr('languages')
        self.countries = self.get_tr('countries')
        self.genres = self.get_tr('genres')
        self.cast = None
        self.director = None
        self.producer = None
        self.writer = None
        self.reviews = [] # [(score, pub, critic)]
        self.user_reviews = None  # [(positive, mixed, negative)]
        self.update_people()
        self.update_reviews()
        self.update_users()

    def make_soup_from_url(self, url, attempt=0):
        attempt = attempt + 1
        time.sleep(SLEEP_TIME + attempt*int(random.random()))
        if attempt > 10:
            return None
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'chrome'})
            html = urllib.request.urlopen(req).read()
            return BeautifulSoup(html, "lxml")
        except:
            self.make_soup_from_url(attempt)

    def get_tr(self, search_string):
        try:
            tr = self.soup.find('tr', {'class': search_string}).find('td', {'class': 'data'}).text
            return clean_span_array(tr.split(','))
        except:
            return

    def get_people_from_category(self, category):
        people = []
        try:
            for role in category.parent.parent.parent.find_all('td', {'class': 'role'}):
                name = role.previous_sibling.previous_sibling.text.strip()
                role = role.text.strip()
                if ('Producer' in role) and (role != 'Producer'):
                    pass
                else:
                    people.append(name)
            if len(people) == 1:
                return people[0]
            else:
                return people
        except:
            return people

    def update_people(self):
        principal_cast_flag = False
        for category in self.soup.find_all('th', {'class': 'person'}):
            category_name = category.text.strip()

            if category_name == 'Principal Cast':
                principal_cast_flag = True
                self.cast = self.get_people_from_category(category)
            elif category_name == 'Cast' and principal_cast_flag:
                pass
            elif category_name == 'Cast':
                self.cast = self.get_people_from_category(category)
            elif category_name == 'Director':
                self.director = self.get_people_from_category(category)
            elif category_name == 'Producer':
                self.producer = self.get_people_from_category(category)
            elif category_name == 'Writer':
                self.writer = self.get_people_from_category(category)

    def update_reviews(self):
        for review in self.critics_soup.find_all('div', {'class': 'review'}):
            try:
                score = review.find('div', {'class': 'movie'}).text
                publication = review.find('span', {'class': 'source'}).text
                author = review.find('span', {'class': 'author'}).text
                self.reviews.append((score, publication, author))
            except:
                pass

    def update_users(self):
        try:
            sentiments = ('Positive:', 'Mixed:', 'Negative:')
            result = [] 
            for sentiment in sentiments:
                result.append(self.users_soup.find(text=sentiment).parent.parent.find('div', {'class': 'count'}).text)

            self.user_reviews = tuple(result)
        except:
            self.user_reviews = (0, 0, 0)
            

def clean_span_array(array):
    if type(array) == list:
        if len(array)==1:
            return array[0].strip()
        else:
            return [a.strip() for a in array]
    else:
        return array
