from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
import hashlib
import jwt
import os
from datetime import datetime, timedelta, timezone

JWT_KEY = os.getenv('JWT_SECRET_KEY', 'labai-slaptas-raktas-1')

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongo_conection_key (write)")
client = MongoClient(MONGO_URI)
db = client["mini_netflix"]

"""
Filmų sąrašas
    ~ Gaunamas visų duomenų duomenų bazėje esančių filmų sąrašas.
    ~ Atspausdinamas filmų json sąrašas.
"""

@app.route('/movies', methods=['GET'])
def get_movies():
    movies_cursor = db.movies.find({}, {'_id': 0})
    movies = []
    for movie in movies_cursor:
        movie['movie_id'] = str(movie['movie_id'])
        movies.append(movie)
    return jsonify(movies), 200

"""
Vartotojų registracija:
    ~ Pateikiamas vartotojo vardas, elektroninio pašto adresas ir slaptažodis. 
    ~ Kiekvienam vartotojui suteikiamas unikalus ID, pagal kurį veliau galimam bus gauti informaciją apie vartotoją.
    ~ KIekvienam vartotojui priskiriamas pigiausias įmanomas planas, vėliau jį galima pasikeisti. 
    ~ Jeigu vartotojas egzistuoja, tai gaunamas pranešimas, kad vartotojas egzistuoja.
"""

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    if db.users.find_one({"email": data['email']}):
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    user_data = {
        "user_id": ObjectId(),
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password
    }
    today = datetime.today()
    plans = [("basic", 9.99, 30), ("standard", 15.99, 90), ("premium", 19.99, 365)]
    cheapest_plan = min(plans, key = lambda p : p[1])

    subscription = ({
        "user_id": user_data["user_id"],
        "plan": cheapest_plan[0],
        "price": cheapest_plan[1],
        "valid_until": today + timedelta(days=cheapest_plan[2])
    })
    db.users.insert_one(user_data)
    db.subscriptions.insert_one(subscription)
    return jsonify({"message": "User registered successfully"}), 201

"""
Vartotojų prisijungimas:
    ~ Vartotojui prisijungiant prašoma elektroninio pašto adreso ir slaptažodžio.
    ~ Jeigu vartojas neegzistuoja pagal elektroninį pašto adresą arba slaptažodis neatitinka, gaunama klaida.
    ~ Prisijungusiam vartotojui suteikiamas token, kuris nebeveikia praėjus valandai. Po valandos vartotojas turi vėl prisijungti. 
"""

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400

    user = db.users.find_one({"email": data["email"]})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if hashlib.sha256(data["password"].encode()).hexdigest() != user["password"]:
        return jsonify({"error": "Incorrect password"}), 401

    token = jwt.encode({
        'user_id': str(user['user_id']),
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }, JWT_KEY, algorithm="HS256")

    return jsonify({"token": token}), 200

"""
Atsiliepimų apie filmus rodymas:
    ~ Pagal pateiktą filmo unikalų ID surandami atsiliepimai apie filmą.
    ~ Pateikiami visi atsiliepimai apie filmą.
"""

@app.route('/reviews/<string:movie_id>', methods=['GET'])
def get_reviews(movie_id):
    try:
        movie_oid = ObjectId(movie_id)
    except:
        return jsonify({"error": "Invalid movie_id"}), 400

    reviews_cursor = db.reviews.find({"movie_id": movie_oid}, {'_id': 0})
    reviews = []
    for r in reviews_cursor:
        r['user_id'] = str(r['user_id'])
        r['movie_id'] = str(r['movie_id'])
        reviews.append(r)
    return jsonify(reviews), 200

"""
Atsiliepimų kurimas:
    ~ Kievienas vartotojas turi galimybę parašyti atsiliepimą apie filmą.
    ~ Kad parašyti atsiliepimą būtinas prisijungimas, kadangi reikalaujama vartotojo sesijos token.
    ~ Atsiliepimas pridedamas prie duomenų bazės.
"""

@app.route('/reviews', methods=['POST'])
def create_review():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 403

    token = auth_header.strip()
    try:
        decoded_token = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 403

    user = db.users.find_one({"user_id": ObjectId(decoded_token.get("user_id"))})
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    comment = data.get("comment", "")

    if not movie_id or not rating:
        return jsonify({"error": "Missing 'movie_id' or 'rating'"}), 400

    try:
        movie_oid = ObjectId(movie_id)
    except:
        return jsonify({"error": "Invalid movie_id"}), 400

    db.reviews.insert_one({
        "user_id": user["user_id"],
        "movie_id": movie_oid,
        "rating": int(rating),
        "comment": comment
    })
    return jsonify({"message": "Review created successfully!"}), 201

"""
Filmų filtravimas su argumentais:
    ~ Jeigu vartotojas ieško filmo pagal žanrą arba metus, ši funkcija suteikai galimybę tai padaryti. 
    ~ Galima filtruoti pagal žanrą. Taip pat pagal metus. Arba visus kartu.
    ~ Pagal pasirenktus parametrus, gaunamas filmų sąrašas, pritaikius filtrą.
"""
@app.route('/movies/filter', methods=['GET'])
def filter_movies():
    genre = request.args.get('genre')
    min_year = request.args.get('min_year', type=int)
    max_year = request.args.get('max_year', type=int)

    query = {}
    if genre:
        query['genre'] = {'$in': [genre]}
    if min_year or max_year:
        query['release_year'] = {}
        if min_year:
            query['release_year']['$gte'] = min_year
        if max_year:
            query['release_year']['$lte'] = max_year

    movies_cursor = db.movies.find(query, {'_id': 0})
    movies = []
    for movie in movies_cursor:
        movie['movie_id'] = str(movie['movie_id'])
        movies.append(movie)
    return jsonify(movies), 200

"""
Filmų rušiavimas pagal metus:
    ~ Vartotojas gauna galimybę surūšiuoti filmus:
        ~ Nuo naujausio iki seniausio, 
        ~ Nuo seniausio iki naujausio.
    ~ Jeigu tvarkos argumentas nepateikiamas, tada filmai bus rūšiuojami nuo seniausio iki naujausio.
"""

@app.route('/movies/sorted', methods=['GET'])
def movies_sorted():
    sort_by = request.args.get('sort_by', 'release_year')
    order = request.args.get('order', 'asc')

    if order == 'asc':
        sort_order = ASCENDING
    elif order == 'desc':
        sort_order = DESCENDING
    else:
        return jsonify({"error" : "Non existent order picked"}), 400
    
    movies_cursor = db.movies.find({}, {'_id' : 0}).sort(sort_by, sort_order)
    movies = []
    for movie in movies_cursor:
        movie["movie_id"] = str(movie["movie_id"])
        movies.append(movie)

    return jsonify(movies), 200


# Agregavimo funkcijų naudojimas

"""
TOP 10 filmų radimas:
    ~ Vartotojas turi galimybę stebėti, kurie filmai turi geriausius reitingus.
    ~ Filmų populiarumas yra nusprendžiamas pagal filmo atsiliepimų įvertinimo vidurkį.
    ~ Taip pat susumuojama, kiek atsiliepimų filmas turi, taip pateikiant papildomą informaciją.
    ~ Filmai yra išrikiuojami mažėjimo tvarka.
    ~ Atspausdinami tik 10 geriausiai įvertinti filmai. 
"""

@app.route('/analytics/top_movies', methods=['GET'])
def top_movies():
    pipeline = [
        {"$group": {"_id": "$movie_id", "average_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}},
        {"$lookup": {"from": "movies", "localField": "_id", "foreignField": "movie_id", "as": "movie_info"}},
        {"$unwind": "$movie_info"},
        {"$project": {
            "_id": 0,
            "movie_id": {"$toString": "$_id"},
            "title": "$movie_info.title",
            "average_rating": {"$round": ["$average_rating", 2]},
            "review_count": 1
        }},
        {"$sort": {"average_rating": -1}},
        {"$limit": 10}
    ]
    results = list(db.reviews.aggregate(pipeline))
    return jsonify(results), 200

"""
Atsiliepimų skaičius pagal vartotojus:
    ~ Pagal kiekvieno vartotojo unikalų id suskaičiuojama, kiek atsiliepimų vartotojas yra parašęs.
    ~ Tada vartotojai surūšiuojami pagal atsiliepimų skaičių mažėjimo tvarka. 
    ~ Gaunamas vartotojų sąrašas sūrušiuotas pagal atsiliepimų skaičių.
"""

@app.route('/analytics/top_reviewers', methods=['GET'])
def top_reviewers():
    pipeline = [
        {"$group": {"_id": "$user_id", "review_count": {"$sum": 1}}},
        {"$lookup": {"from": "users", "localField": "_id", "foreignField": "user_id", "as": "user_info"}},
        {"$unwind": "$user_info"},
        {"$project": {
            "_id": 0,
            "name": "$user_info.name",
            "email": "$user_info.email",
            "review_count": 1
        }},
        {"$sort": {"review_count": -1}},
        {"$limit": 10}
    ]
    results = list(db.reviews.aggregate(pipeline))
    return jsonify(results), 200

"""
Vartotojų prenumerata:
    ~ Kiekvienas registruotas vartotojas gali sužinoti savo prenumeratos tipą. 
    ~ Tikrinamas varototjo prisijungimo token, taip apribojant, kad tik pat vartotojas gali gauti informaciją apie prenumeratą.
    ~ Randamas vartotojo Id ir galiausiai prenumeratos tipas.
"""

@app.route('/subscriptions', methods=['GET'])
def get_user_subscription():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 403

    token = auth_header.strip()
    try:
        decoded_token = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 403

    user = db.users.find_one({"user_id": ObjectId(decoded_token.get("user_id"))})
    if not user:
        return jsonify({"error": "User not found"}), 404

    subscription = db.subscriptions.find_one({"user_id": user["user_id"]}, {'_id': 0})
    if subscription:
        subscription['user_id'] = str(subscription['user_id'])
        return jsonify(subscription), 200
    return jsonify({"error": "Subscription not found"}), 404

"""
Prenumeratos tipo pakeitimas:
    ~ Kiekvienas vartotojas turi galimybę pakeisti savo prenumeratos tipą. 
    ~ Naudojamas token, kad tik pat vartotojas galėtų pakeisti savo informaciją, šiu atveju rpenumeratą. 
    ~ Reikalaujama pateikti į kokį planą vartotojas nori pasikeisti.
    ~ Pakeičiamas plano pavadinimas, kaina ir iki kada planas galioja.
"""

@app.route('/subscriptions', methods=['PUT'])
def update_subscription():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 403

    token = auth_header.strip()
    try:
        decoded_token = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 403

    user = db.users.find_one({"user_id": ObjectId(decoded_token.get("user_id"))})
    if not user:
        return jsonify({"error": "User not found"}), 404

    plan = request.get_json().get("plan")
    if not plan:
        return jsonify({"error": "Missing 'plan' field"}), 400
    
    plans = [("basic", 9.99, 30), ("standard", 15.99, 90), ("premium", 19.99, 365)]

    plan_info = next((p for p in plans if p[0] == plan), None)
    if not plan_info:
        return jsonify({"error" : "Invalid plan"}), 400
    
    plan_name, plan_price, plan_days = plan_info
    today = datetime.today()

    updated_data = {
        "plan" : plan_name,
        "price" : plan_price,
        "valid_until" : today + timedelta(days=plan_days)
    }

    result = db.subscriptions.update_one({"user_id": user["user_id"]}, {"$set": updated_data}, upsert=True)
    if result.matched_count == 0:
        return jsonify({"message": "New subscription created"}), 201
    return jsonify({"message": "Subscription updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
