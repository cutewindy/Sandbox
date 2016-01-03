# Making a Connection with MongoClient
from pymongo import MongoClient
wendyClient = MongoClient()
# Or:
# import pymongo
# wendyClient = pymongo.MongoClient()


# Databases
wendyDb = wendyClient.test_database # Getting a Database


# Collections
wendyCollection = wendyDb.test_collection # Getting a Collection


# Documents
import datetime
post1 = {"author": "Mike",
        "text": "My first blog posst!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}
wendyDb.posts.drop() # clean collection: posts
posts = wendyDb.posts # getting a collection: posts


# insert()
post1 = posts.insert_one(post1) # insert a document in the collection of posts: post1
# Or post = WendyDb.posts.insert_one(post)
post2 = {"name": "Wendi"}
post2 = posts.insert_one(post2)


# find_one(): returns a single document(first matching) matching a query
print "********************************1"
print posts.find_one() # find_one()
print posts.find_one({"name": "Wendi"})
print posts.find_one({"name": "Xiao"}) # (None if there are no matches)


# find a post by its _id
post2_id = post2.inserted_id # get the document's id
print "********************************2"
print posts.find_one({"_id": post2_id})
post2_id_as_str = str(post2_id) # an ObjectId is not the same as its string representation
print posts.find_one({"_id": post2_id_as_str}) # No result


# A common task in web applications is to get an ObjectId from the request URL
#  and find the matching document. It's necessary in this case to convert the
#  ObjectId from a string before passing it to find_one.
from bson.objectid import ObjectId
def get(post_id):
    document = wendyClient.wendyDb.posts.find_one({"_id": ObjectId(post_id)}) # convert from string to ObjectId
    return document
print "********************************3"
print get("5688417b67ccc10fb1a5b7e0")


# insert_many(): Bulk Insert
new_post1 = [{"author": "Mike",
              "text": "Another post!",
              "tags": ["bulk", "insert"],
              "date": datetime.datetime(2016, 1, 2, 13, 39)},
              {"author": "Eliot",
              "title": "MongoDB is fun",
              "text": "and pretty easy too!",
              "date": datetime.datetime(2016, 1, 2, 13, 41)}
            ]
# new_post1[1] has a different "shape" than the other posts - there is no "tags"
#  field and we've added a new field, "title", This is what we mean when we say that
#  MongoDB is schema-free.
wendyDb.new_posts.drop()
new_posts = wendyDb.new_posts # getting a collection: new_posts
new_post1 = new_posts.insert_many(new_post1) # insert a document: new_post1
print "********************************4"
print new_posts.find_one() # find the first matching document
print new_post1.inserted_ids # find the document new_post1's Id


# find(): find() returns a Cursor instance, which allows us to iterate over all matching documents.
print "********************************5"
for post in new_posts.find():
    print post
# can pass a document to find() to limit the returned results
for post in new_posts.find({"author": "Eliot"}): # get only those documents whose author is "Eliot"
    print post


# count(): If we just want to know how many documents match a query
#  we can perform a count() operation instead of a full query.
print "********************************6"
print new_posts.count() # get a count of all of the documents in a collection
print new_posts.find({"author": "Mike"}).count() # just of those documents that match a specific query


# Range Queries:
# MongoDB supports many different types of advanced queries. As an example,
#  lets perform a query where we limit results to posts older than a certain date,
#  but also sort the results by author.
d = datetime.datetime(2016, 1, 2, 16, 18)
print "********************************7"
for post in new_posts.find({"date":{"$lt": d}}).sort("author"):
#use the special "$lt" operator to do a range query, and also call sort() to sort the results by author
    print post


# Indexing
wendyDb.profiles.drop()
from pymongo import ASCENDING # recommanded
result = wendyDb.profiles.create_index([("user_id", ASCENDING)],
                                        unique = True)
# or
# import pymongo
# result = wendyDb.profiles.create_index([("user_id", pymongo.ASCENDING)],
#                                         unique = True)
print "********************************8"
print list(wendyDb.profiles.index_information())
# we have two indexes now: one is the index on _id that MongoDB creates automatically,
#  and the other is the index on user_id we just created.

user_profiles = [
    {"user_id": 211, "name": "Luke"},
    {"user_id": 212, "name": "Ziltoid"}]
result = wendyDb.profiles.insert_many(user_profiles)
for user_profile in wendyDb.profiles.find():
    print user_profile
# The index prevents us from inserting a document whose user_id is already in the collection:
new_profile = {"user_id": 210, "name": "Drew"}
duplicate_profile = {"user_id": 212, "name": "Tommy"}
result = wendyDb.profiles.insert_one(new_profile)  # This is fine
# result = wendyDb.profiles.insert_one(duplicate_profile)
print "********************************9"
for user_profile in wendyDb.profiles.find():
    print user_profile
# print dir(result)
# help(result)



# show result:
# ********************************1
# {u'date': datetime.datetime(2016, 1, 3, 1, 1, 52, 197000), u'text': u'My first blog posst!', u'_id': ObjectId('5688730067ccc128adb95c7d'), u'author': u'Mike', u'tags': [u'mongodb', u'python', u'pymongo']}
# {u'_id': ObjectId('5688730067ccc128adb95c7e'), u'name': u'Wendi'}
# None
# ********************************2
# {u'_id': ObjectId('5688730067ccc128adb95c7e'), u'name': u'Wendi'}
# None
# ********************************3
# None
# ********************************4
# {u'date': datetime.datetime(2016, 1, 2, 13, 39), u'text': u'Another post!', u'_id': ObjectId('5688730067ccc128adb95c7f'), u'author': u'Mike', u'tags': [u'bulk', u'insert']}
# [ObjectId('5688730067ccc128adb95c7f'), ObjectId('5688730067ccc128adb95c80')]
# ********************************5
# {u'date': datetime.datetime(2016, 1, 2, 13, 39), u'text': u'Another post!', u'_id': ObjectId('5688730067ccc128adb95c7f'), u'author': u'Mike', u'tags': [u'bulk', u'insert']}
# {u'date': datetime.datetime(2016, 1, 2, 13, 41), u'text': u'and pretty easy too!', u'_id': ObjectId('5688730067ccc128adb95c80'), u'author': u'Eliot', u'title': u'MongoDB is fun'}
# {u'date': datetime.datetime(2016, 1, 2, 13, 41), u'text': u'and pretty easy too!', u'_id': ObjectId('5688730067ccc128adb95c80'), u'author': u'Eliot', u'title': u'MongoDB is fun'}
# ********************************6
# 2
# 1
# ********************************7
# {u'date': datetime.datetime(2016, 1, 2, 13, 41), u'text': u'and pretty easy too!', u'_id': ObjectId('5688730067ccc128adb95c80'), u'author': u'Eliot', u'title': u'MongoDB is fun'}
# {u'date': datetime.datetime(2016, 1, 2, 13, 39), u'text': u'Another post!', u'_id': ObjectId('5688730067ccc128adb95c7f'), u'author': u'Mike', u'tags': [u'bulk', u'insert']}
# ********************************8
# [u'user_id_1', u'_id_']
# {u'_id': ObjectId('5688730067ccc128adb95c81'), u'user_id': 211, u'name': u'Luke'}
# {u'_id': ObjectId('5688730067ccc128adb95c82'), u'user_id': 212, u'name': u'Ziltoid'}
# ********************************9
# {u'_id': ObjectId('5688730067ccc128adb95c81'), u'user_id': 211, u'name': u'Luke'}
# {u'_id': ObjectId('5688730067ccc128adb95c82'), u'user_id': 212, u'name': u'Ziltoid'}
# {u'_id': ObjectId('5688730067ccc128adb95c83'), u'user_id': 210, u'name': u'Drew'}
# [Finished in 0.7s]
































