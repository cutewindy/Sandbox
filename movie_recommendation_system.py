
from collections import defaultdict
import sys
import numpy
from scipy import spatial
import re

class Movie(object):
    def __init__(self, movie_id, rating):
        self.movie_id = movie_id
        self.rating = rating


"""create file of input data"""
# def create_input_file():
#     my_file = open("test_data", "w")
#     my_file.write("Here is the date of movie recommendation system:\n")
#     my_file.write("1, 101, 5.0\n")
#     my_file.write("1, 102, 3.0\n")
#     my_file.write("1, 103, 2.5\n")
#     my_file.write("2, 101, 2.0\n")
#     my_file.write("2, 102, 2.5\n")
#     my_file.write("2, 103, 5.0\n")
#     my_file.write("2, 104, 2.0\n")
#     my_file.write("3, 101, 2.5\n")
#     my_file.write("3, 104, 4.0\n")
#     my_file.write("3, 105, 4.5\n")
#     my_file.write("3, 107, 5.0\n")
#     my_file.write("4, 101, 5.0\n")
#     my_file.write("4, 103, 3.0\n")
#     my_file.write("4, 104, 4.5\n")
#     my_file.write("4, 106, 4.0\n")
#     my_file.write("5, 101, 4.0\n")
#     my_file.write("5, 102, 3.0\n")
#     my_file.write("5, 103, 2.0\n")
#     my_file.write("5, 104, 4.0\n")
#     my_file.write("5, 105, 3.5\n")
#     my_file.write("5, 106, 4.0\n")
#     my_file.close()



"""Globla value: initialize data into user hash and movie hash"""
users = defaultdict(list)  # dict (key, value) = (user_id, list[(movie_id, rating)])
movies = defaultdict(list)  # dict (key, value) = (movie_id, list[user_id])
min_user_id = sys.maxsize
max_user_id = 0
users_count = 0
min_movie_id = sys.maxsize
max_movie_id = 0
movies_count = 0


def error(message):
    print message


"""check whether the input data is valid"""
def is_valid(data):
    # 1. check data length
    if len(data) != 3:
        error("Invalid data: expect 3 splited values, got: %s." % len(data))
        return False
    # 2. check user_id is integer
    if not data[0].isdigit():
        error("Invalid data: user_id '%s' is not an integer." % data[0])
        return False
    # try:
    #     user_id = int(data[0])
    #     if user_id < 0:
    #         error("Invalid data: user_id '%s' is out of range." % data[0])
    #         return False
    # except ValueError:
    #     print "Invalid data: user_id '%s' is not an integer." % data[0]
    #     return False
    # 3. check movie_id is integer
    if not data[1].isdigit():
        error("Invalid data: user_id '%s' is not an integer." % data[1])
        return False
    # try:
    #     movie_id = int(data[1])
    #     if movie_id < 0:
    #         error("Invalid data: movie_id '%s' is out of range." % data[1])
    #         return False
    # except ValueError:
    #     print "Invalid data: movie_id '%s' is not an integer." % data[1]
    #     return False
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

# test invalid data:
# line = "   11  , 22 , 3 ###21"
# matchObj = re.match("(.*?)#.*", line)
# if matchObj:
#     line = matchObj.group(1)
# data = [x.strip() for x in line.split(",")]
# print is_valid(data)



def init_data():
    global min_user_id
    global max_user_id
    global users_count
    global min_movie_id
    global max_movie_id
    global movies_count
    my_file = open("t12", "r")
    for line in my_file:
        orig_line = line
        matchObj = re.match("(.*?)#.*", line)  # using regex to remove comment
        if matchObj:
            line = matchObj.group(1)
        data = [x.strip() for x in line.split(",")]  # split string with ","
        if not is_valid(data):
            error("The invalid data is: %s" % orig_line)
            continue
        user_id = int(data[0])
        movie_id = int(data[1])
        rating = float(data[2])
        min_user_id = min(user_id, min_user_id)
        max_user_id = max(user_id, max_user_id)
        min_movie_id = min(movie_id, min_movie_id)
        max_movie_id = max(movie_id, max_movie_id)
        users[user_id].append(Movie(movie_id, rating))
        movies[movie_id].append(user_id)
    my_file.close()
    users_count = max_user_id - min_user_id + 1
    movies_count = max_movie_id - min_movie_id + 1
    # print data in two dict
    # for key in users:
    #     for l in users[key]:
    #         print key, l.movie_id, l.rating
    # print movies.items()
    # print "==========="


"""cooccurrence recommender algorithm"""
def cooccurrence_matrix():
    # step1: calculate cooccurrence matrix
    matrix = numpy.zeros((movies_count, movies_count))
    recommendation = [0] * users_count
    for user in users:
        movie = users[user]
        n = len(movie)
        for i in range(n):
            for j in range(i, n):
                if movie[i].movie_id == movie[j].movie_id:
                    matrix[movie[i].movie_id - min_movie_id][movie[j].movie_id - min_movie_id] += 1
                else:
                    matrix[movie[i].movie_id - min_movie_id][movie[j].movie_id - min_movie_id] += 1
                    matrix[movie[j].movie_id - min_movie_id][movie[i].movie_id - min_movie_id] += 1
    # step2: multiplying cooccurrence matrix with user's rating vector to produce a
    # weight vector that lead to recommendation, choose the weight user doesn't
    # have and with highest values in the weight vector
    for user in users:
        user_rating = [0.0] * movies_count
        movie_set = set()
        for movie in users[user]:
            user_rating[movie.movie_id - min_movie_id] = movie.rating
            movie_set.add(movie.movie_id)
        weights = matrix.dot(user_rating)
        max_weight = 0
        for i in range(movies_count):
            if (i + min_movie_id) not in movie_set and weights[i] > max_weight:
                max_weight = weights[i]
                recommendation[user - min_user_id] = i + min_movie_id
    print "co-occurrence: ", recommendation



"""User_based recommendation algorithm"""
def user_based():
    recommendation = [0] * users_count
    # step1: using cosine_similarity to calculate similar matrix
    similar_matrix = numpy.zeros((users_count, users_count))
    rating_matrix = numpy.zeros((users_count, movies_count))
    for user in users:
        for movie in users[user]:
            rating_matrix[user - min_user_id][movie.movie_id - min_movie_id] = movie.rating
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
    for user in users:
        movie_set = set()
        max_weight = 0
        for movie in users[user]:
            movie_set.add(movie.movie_id)
        for movie in movies:
            if movie not in movie_set:
                weight = 0
                count = 0
                for i in range(users_count):
                    if rating_matrix[i][movie - min_movie_id] != 0:
                        weight += rating_matrix[i][movie - min_movie_id] * similar_matrix[i][user - min_user_id]
                        count += 1
                average_weight = weight / count
                if average_weight > max_weight:
                    max_weight = average_weight
                    recommendation[user - min_user_id] = movie
    print "user-based: ", recommendation



def run():
    # create_input_file()
    init_data()
    cooccurrence_matrix()
    user_based()

    # for user in movies[206]:
    #     print user
    #     for movie in users[user]:
    #         if movie.movie_id == 206:
    #             print movie.movie_id, movie.rating


if __name__ == "__main__":
    run()














