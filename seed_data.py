from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import random
import hashlib

client = MongoClient('mongodb+srv://justinaseil_db_user:Labas@cluster0.kkuyxfb.mongodb.net/mydb?retryWrites=true&w=majority&tls=true') # Prisijungiame prie MongoDB

try:
    client.admin.command('ping')
    print("Prisijungta prie MongoDB")
except Exception as e:
    print("Nepavyko prisijungti prie MongoDB", e)
    exit()

db = client["mini_netflix"]

db.movies.delete_many({})
db.users.delete_many({})
db.subscriptions.delete_many({})
db.reviews.delete_many({})

"""
Filmų pradiniai duomenys:
    ~ Kiekvienas filmas turi:
        ~ Unikalų ID
        ~ Pavadinimą
        ~ Sąrašą žanrų, kurie jam priskirti
        ~ Išleidimo metus
        ~ Reitingą
"""
movies = [
    {
        "movie_id": ObjectId(),
        "title": "Spider-Man: No Way Home",
        "genre": ["Action", "Adventure", "Sci-Fi"],
        "release_year": 2021,
        "rating": 8.2
    },
    {
        "movie_id": ObjectId(),
        "title": "Frozen",
        "genre": ["Animation", "Adventure", "Comedy", "Family", "Fantasy", "Musical"],
        "release_year": 2013,
        "rating": 7.5
    },
    {
        "movie_id": ObjectId(),
        "title": "The Last Samurai",
        "genre": ["Drama", "Action", "History"],
        "release_year": 2003,
        "rating": 7.7
    },
    {
        "movie_id": ObjectId(),
        "title": "Avengers: Endgame",
        "genre": ["Action", "Adventure", "Drama", "Sci-Fi"],
        "release_year": 2019,
        "rating": 8.4
    },
    {
        "movie_id": ObjectId(),
        "title": "Titanic",
        "genre": ["Drama", "Romance"],
        "release_year": 1997,
        "rating": 7.8
    },
    {
        "movie_id": ObjectId(),
        "title": "Inception",
        "genre": ["Action", "Adventure", "Sci-Fi", "Thriller"],
        "release_year": 2010,
        "rating": 8.8
    },
    {
        "movie_id": ObjectId(),
        "title": "The Dark Knight",
        "genre": ["Action", "Crime", "Drama"],
        "release_year": 2008,
        "rating": 9.0
    },
    {
        "movie_id": ObjectId(),
        "title": "The Lion King",
        "genre": ["Animation", "Adventure", "Drama", "Family"],
        "release_year": 1994,
        "rating": 8.5
    },
    {
        "movie_id": ObjectId(),
        "title": "Interstellar",
        "genre": ["Adventure", "Drama", "Sci-Fi"],
        "release_year": 2014,
        "rating": 8.6
    },
    {
        "movie_id": ObjectId(),
        "title": "The Godfather",
        "genre": ["Crime", "Drama"],
        "release_year": 1972,
        "rating": 9.2
    },
    {
        "movie_id": ObjectId(),
        "title": "Forrest Gump",
        "genre": ["Drama", "Romance"],
        "release_year": 1994,
        "rating": 8.8
    },
    {
        "movie_id": ObjectId(),
        "title": "The Matrix",
        "genre": ["Action", "Sci-Fi"],
        "release_year": 1999,
        "rating": 8.7
    }
]

try:
    db.movies.insert_many(movies)
except Exception as e:
    print("Klaida įkeliant filmą:", e)

"""
Vartotojų pradiniai duomenys:
    ~ Kiekvienas vartotojas turi:
        ~ Unikalų ID
        ~ Vardą
        ~ Elektroninį pašto adresą
        ~ Slaptažodį
    ~ Kiekvienas slaptašodis yra apsaugomas duomenų bazėje, naudojant maišos reikšmę.
"""

password_hash = hashlib.sha256("password123".encode()).hexdigest()

users = [
    {"user_id": ObjectId(), "name": "John Doe", "email": "john.doe@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Jane Smith", "email": "jane.smith@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Michael Johnson", "email": "michael.johnson@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Emily Davis", "email": "emily.davis@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "David Brown", "email": "david.brown@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Laura Wilson", "email": "laura.wilson@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Robert Taylor", "email": "robert.taylor@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Olivia Miller", "email": "olivia.miller@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "James Garcia", "email": "james.garcia@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Sophia Martinez", "email": "sophia.martinez@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Christopher Anderson", "email": "christopher.anderson@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Megan Thomas", "email": "megan.thomas@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Daniel Jackson", "email": "daniel.jackson@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Emma White", "email": "emma.white@gmail.com", "password": password_hash},
    {"user_id": ObjectId(), "name": "Andrew Harris", "email": "andrew.harris@gmail.com", "password": password_hash}
]
    
try:
    db.users.insert_many(users)
except Exception as e:
    print("Klaida įkeliant vartotoją:", e)


"""
Prenumeratų pradiniai duomenys:
    ~ Kiekviena prenumerata turi:
        ~ Unikalų vartotojo ID
        ~ Pavadinimą
        ~ Kainą
        ~ Galiojimo laiką
    ~ Kiekvienam naujam vartotojui yra priskiriamas pigiausias planas.
"""

today = datetime.today()
plans = [("basic", 9.99, 30), ("standard", 15.99, 90), ("premium", 19.99, 365)]
cheapest_plan = min(plans, key = lambda p : p[1])
subscriptions = []

for user in users:
    subscriptions.append({
        "user_id": user["user_id"],
        "plan": cheapest_plan[0],
        "price": cheapest_plan[1],
        "valid_until": today + timedelta(days=cheapest_plan[2])
    })

try:
    db.subscriptions.insert_many(subscriptions)
except Exception as e:
    print("Klaida įkeliant prenumerata:", e)



"""
Atsiliepimų pradiniai duomenys:
    ~ Kiekvienas atsiliepimas turi:
        ~ Unikalų vartotojo ID
        ~ Unikalų filmo ID
        ~ Filmo įvertinimą
        ~ Atsiliepimą
"""

reviews = [
    {
        "user_id": users[0]["user_id"],
        "movie_id": movies[0]["movie_id"],
        "rating": 9,
        "comment": "Fantastic action and nostalgia. Loved seeing all the Spider-Men together!"
    },
    {
        "user_id": users[5]["user_id"],
        "movie_id": movies[0]["movie_id"],
        "rating": 8,
        "comment": "A bit too long, but great fan service."
    },
    {
        "user_id": users[1]["user_id"],
        "movie_id": movies[1]["movie_id"],
        "rating": 8,
        "comment": "Let it go! Still a classic for kids and adults."
    },
    {
        "user_id": users[9]["user_id"],
        "movie_id": movies[1]["movie_id"],
        "rating": 7,
        "comment": "Good animation, but too many songs for me."
    },
    {
        "user_id": users[2]["user_id"],
        "movie_id": movies[2]["movie_id"],
        "rating": 8,
        "comment": "Powerful story and great visuals. Tom Cruise was impressive."
    },
    {
        "user_id": users[8]["user_id"],
        "movie_id": movies[2]["movie_id"],
        "rating": 7,
        "comment": "A bit slow, but deep and emotional."
    },
    {
        "user_id": users[3]["user_id"],
        "movie_id": movies[3]["movie_id"],
        "rating": 10,
        "comment": "The best superhero movie ever made. Perfect ending to a saga."
    },
    {
        "user_id": users[11]["user_id"],
        "movie_id": movies[3]["movie_id"],
        "rating": 9,
        "comment": "Emotional and epic. Loved every minute."
    },
    {
        "user_id": users[4]["user_id"],
        "movie_id": movies[4]["movie_id"],
        "rating": 9,
        "comment": "Beautiful and heartbreaking. Classic love story."
    },
    {
        "user_id": users[6]["user_id"],
        "movie_id": movies[4]["movie_id"],
        "rating": 8,
        "comment": "A timeless film, even after all these years."
    },
    {
        "user_id": users[7]["user_id"],
        "movie_id": movies[5]["movie_id"],
        "rating": 9,
        "comment": "Mind-blowing concept, amazing visuals."
    },
    {
        "user_id": users[13]["user_id"],
        "movie_id": movies[5]["movie_id"],
        "rating": 10,
        "comment": "Nolan at his best. Keeps you thinking long after it ends."
    },
    {
        "user_id": users[10]["user_id"],
        "movie_id": movies[6]["movie_id"],
        "rating": 10,
        "comment": "Heath Ledger as Joker was legendary."
    },
    {
        "user_id": users[12]["user_id"],
        "movie_id": movies[6]["movie_id"],
        "rating": 9,
        "comment": "Dark, deep, and unforgettable."
    },
    {
        "user_id": users[1]["user_id"],
        "movie_id": movies[7]["movie_id"],
        "rating": 9,
        "comment": "The best Disney movie ever. The music gives me chills."
    },
    {
        "user_id": users[8]["user_id"],
        "movie_id": movies[7]["movie_id"],
        "rating": 8,
        "comment": "Great animation and story. Timeless classic."
    },
    {
        "user_id": users[3]["user_id"],
        "movie_id": movies[8]["movie_id"],
        "rating": 9,
        "comment": "Beautiful visuals and emotional story. One of Nolan's finest."
    },
    {
        "user_id": users[14]["user_id"],
        "movie_id": movies[8]["movie_id"],
        "rating": 10,
        "comment": "Masterpiece. The music and plot are unforgettable."
    },
    {
        "user_id": users[2]["user_id"],
        "movie_id": movies[9]["movie_id"],
        "rating": 10,
        "comment": "The greatest film ever made. Every scene is iconic."
    },
    {
        "user_id": users[11]["user_id"],
        "movie_id": movies[9]["movie_id"],
        "rating": 9,
        "comment": "Classic masterpiece. Brilliant acting and direction."
    },
    {
        "user_id": users[5]["user_id"],
        "movie_id": movies[10]["movie_id"],
        "rating": 10,
        "comment": "Heartwarming and emotional. Tom Hanks at his best."
    },
    {
        "user_id": users[7]["user_id"],
        "movie_id": movies[10]["movie_id"],
        "rating": 9,
        "comment": "Such a touching story. Life really is like a box of chocolates."
    },
    {
        "user_id": users[0]["user_id"],
        "movie_id": movies[11]["movie_id"],
        "rating": 9,
        "comment": "Changed sci-fi forever. Amazing action and ideas."
    },
    {
        "user_id": users[9]["user_id"],
        "movie_id": movies[11]["movie_id"],
        "rating": 10,
        "comment": "Still holds up today. Neo is iconic."
    }
]

try:
    db.reviews.insert_many(reviews)
except Exception as e:
    print("Klaida įkeliant reviews:", e)

print("Duomenys įkelti į Mongo!")
