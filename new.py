#!/opt/python-3.4/linux/bin/python3

import re
import sys
from collections import defaultdict

import numpy
from scipy import spatial


def error(message):
    print(message)


class User(object):

    def __init__(self, id):
        self.id = id
        self.ratings = dict() # {movie_id : rating}
        self.recommend_movie_ids = dict() # {'algorithm' : [recommend_movie_id]}
        self.recommend_movie_ids['cooccurrence'] = list()
        self.recommend_movie_ids['user_based_cos_similarity'] = list()

    def watch_movie(self, movie_id, rating):
        self.ratings[movie_id] = rating


class Movie(object):

    def __init__(self, id):
        self.id = id
        self.ratings = dict() # {user_id: rating}

    def watched_by_user(self, user_id, rating):
        self.ratings[user_id] = rating


class MovieRecommendationProgram(object):
    users = dict() # {user_id : <User Object>}
    movies = dict() # {movie_id : <Movie Object>}
    users_list = None # [user_id] used for mapping matrix index and user_id
    movies_list = None # [movie_id] used for mapping matrix index and movie_id

    def __init__(self):
        self.run()

    def run(self):
        self.read_data()
        self.do_cooccurrence_algorithm()
        self.do_user_based_cos_similarity_algorithm()
        self.show_result()

    def read_data(self):
        users = self.users
        movies = self.movies
        for line in sys.stdin:
            orig_line = line
            matchObj = re.match("(.*?)#.*", line)  # using regex to remove comment
            if matchObj:
                line = matchObj.group(1)
            data = [x.strip() for x in line.split(",")]  # split string with ","
            if not self.is_valid(data):
                error(" " * 8 + "The invalid data is: %s" % orig_line)
                continue
            user_id = int(data[0])
            movie_id = int(data[1])
            rating = float(data[2])

            if user_id not in users:
                users[user_id] = User(user_id)
            if movie_id not in movies:
                movies[movie_id] = Movie(movie_id)
            users[user_id].watch_movie(movie_id, rating)
            movies[movie_id].watched_by_user(user_id, rating)
        self.users_list = list(users.keys())
        self.movies_list = list(movies.keys())

    def is_valid(self, data):
        """check whether the input data is valid"""
        # 1. check data length
        if len(data) != 3:
            error("Invalid data: expect 3 splited values, got: %s." % len(data))
            return False
        # 2. check user_id is integer
        if not data[0].isdigit():
            error("Invalid data: user_id '%s' is not an integer." % data[0])
            return False
        # 3. check movie_id is integer
        if not data[1].isdigit():
            error("Invalid data: user_id '%s' is not an integer." % data[1])
            return False
        # 4. check rating is floating and in range[0.0, 5.0]
        try:
            rating = float(data[2])
            if rating < 0 or rating > 5:
                error("Invalid data: rating '%s' is out of range." % data[2])
                return False
        except ValueError:
            error("Invalid data: rating '%s' is not a floating." % data[2])
            return False
        return True

    def do_cooccurrence_algorithm(self):
        """cooccurrence recommender algorithm"""
        users = self.users
        movies = self.movies
        users_list = self.users_list
        movies_list = self.movies_list
        users_count = len(self.users)
        movies_count = len(self.movies)

        # step1: calculate cooccurrence matrix
        matrix = numpy.zeros((movies_count, movies_count))
        for user_id in users_list:
            seen = set()
            for movie_id1 in users[user_id].ratings:
                for movie_id2 in users[user_id].ratings:
                    if movie_id2 in seen:
                        continue
                    m_i = movies_list.index(movie_id1)
                    m_j = movies_list.index(movie_id2)
                    if m_i == m_j:
                        matrix[m_i][m_j] += 1
                    else:
                        matrix[m_i][m_j] += 1
                        matrix[m_j][m_i] += 1
                seen.add(movie_id1)

        # step2: multiplying cooccurrence matrix with user's rating vector to produce a
        # weight vector that lead to recommendation, choose the weight user doesn't
        # have and with highest values in the weight vector
        for user_id, user in users.items():
            user_ratings_list = [0] * movies_count
            for movie_id, rating in user.ratings.items():
                m_i = movies_list.index(movie_id)
                user_ratings_list[m_i] = rating
            weights = list(matrix.dot(user_ratings_list))
            recommend_movie_ids = []
            max_weight = 0
            for i, weight in enumerate(weights):
                if movies_list[i] in user.ratings:
                    continue
                if weight > max_weight:
                    max_weight = weight
                    recommend_movie_ids = [movies_list[i]]
                elif weight == max_weight:
                    recommend_movie_ids.append(movies_list[i])
            user.recommend_movie_ids['cooccurrence'] = sorted(recommend_movie_ids)

    def do_user_based_cos_similarity_algorithm(self):
        """User based cos similarity recommendation algorithm"""
        users = self.users
        movies = self.movies
        users_list = self.users_list
        movies_list = self.movies_list
        users_count = len(self.users)
        movies_count = len(self.movies)

        # step1: using cosine_similarity to calculate similar matrix
        rating_matrix = numpy.zeros((users_count, movies_count))
        for user_id in users_list:
            for movie_id in users[user_id].ratings:
                m_i = users_list.index(user_id)
                m_j = movies_list.index(movie_id)
                rating_matrix[m_i][m_j] = users[user_id].ratings[movie_id]

        similar_matrix = numpy.zeros((users_count, users_count))
        for i in range(users_count):
            for j in range(i, users_count):
                if sum(rating_matrix[i]) == 0.0 or sum(rating_matrix[j]) == 0.0:
                    continue
                elif i == j:
                    similar_matrix[i][j] = 1
                else:
                    curr = 1 - spatial.distance.cosine(rating_matrix[i], rating_matrix[j])
                    similar_matrix[i][j] = curr
                    similar_matrix[j][i] = curr

        # step2: naive and slow algorithm
        for user_id in users_list:
            recommend_movie_ids = []
            max_avg_weight = -1
            for movie_id in movies_list:
                if movie_id in users[user_id].ratings:
                    continue
                weight = 0
                count = 0
                m_j = movies_list.index(movie_id)
                for m_i in range(len(rating_matrix)):
                    v = rating_matrix[m_i][m_j]
                    if v == 0:
                        continue
                    weight += v * similar_matrix[users_list.index(user_id)][m_i]
                    count += 1
                avg_weight = weight / count if count != 0 else \
                             0
                if avg_weight > max_avg_weight:
                    max_avg_weight = avg_weight
                    recommend_movie_ids = [movie_id]
                elif avg_weight == max_avg_weight:
                    recommend_movie_ids.append(movie_id)
            users[user_id].recommend_movie_ids['user_based_cos_similarity'] = sorted(recommend_movie_ids)

    def show_result(self):
        print("=" * 50)
        print("1. Coocurrence recommender algorithm: ")
        for user_id, user in self.users.items():
            print(" " * 8 + "User: %-3s =>  Movies: %s" % (user_id, user.recommend_movie_ids['cooccurrence']))
        print("=" * 50)
        print("2. User-based cos similarity recommendation: ")
        for user_id, user in self.users.items():
            print(" " * 8 + "User: %-3s =>  Movies: %s" % (user_id, user.recommend_movie_ids['user_based_cos_similarity']))

main = MovieRecommendationProgram

if __name__ == '__main__':
    print("\n" * 2 + "*" * 50)
    print(" " * 12 + "Movie recommendation System")
    print(" " * 14 + "Program 1, Wendi Weng")
    print("*" * 50 + "\n")
    main()
    print("\n" + "*" * 50)
    print(" " * 22 + "Done")
    print("*" * 50 + "\n")
