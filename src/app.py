"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorites
#from models import Person
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "secret-key"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# START endpoints
@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#get_all_users
@app.route('/users', methods=['GET'])
def get_all_users():

    #consulta a la tabla user
    user_query = User.query.all()
    #mapear i serialize toda la tabla de user
    result = list(map(lambda item: item.serialize(), user_query))
 
    response_body = {
        "msg": "Get all users",
        "results": result
    }

    return jsonify(response_body), 200

# create one user
@app.route('/users', methods=['POST'])
def create_user():
    
    request_body = request.get_json(force=True)
    # creacion de un registro en la tabla de user
    user = User(email=request_body["email"])
    db.session.add(user)
    db.session.commit()
    
    response_body = {
        "msg": "user created",
    }
    
    return jsonify(response_body), 200

#CHARACTERS
#get_all_charaters
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters_query = Characters.query.all()
    results = list(map(lambda item: item.serialize(), characters_query))

    response_body = {
        "msg": "ok characters",
        "results": results
    }

    return jsonify(response_body), 200

#get_one_charater
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_one_character(character_id):

    character_query = Characters.query.filter_by(id=character_id).first()

    # Manejo de errores para cuando se busca una id que no está
    if character_query is None:
        return jsonify({"msg": "Character not found"}), 404

    response_body = {
        "msg": "ok one character",
        "result": character_query.serialize()
    }
    
    return jsonify(response_body), 200

# create one character
@app.route('/characters', methods=['POST'])
def create_character():
    
    request_body = request.get_json(force=True)
    if "name" or "gender" or "birth_year" not in request_body:
        # raise es para levantar una excepcion de error en la API
        raise APIException("Faltan datos", status_code=400)
    # creacion de un registro en la tabla de user
    character = Characters(name=request_body["name"], birth_year=request_body["birth_year"], gender=request_body["gender"], height=request_body["height"], skin_color=request_body["skin_color"], eye_color=request_body["eye_color"])
    db.session.add(character)
    db.session.commit()
    
    response_body = {
        "msg": "Character created",
    }
    
    return jsonify(response_body), 200

#PLANETS
#get_all_planets
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets_query = Planets.query.all()
    results = list(map(lambda item: item.serialize(), planets_query))

    print(results)

    response_body = {
        "msg": "ok planets",
        "results": results
    }

    return jsonify(response_body), 200

#get_one_planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet_query = Planets.query.filter_by(id=planet_id).first()

    # Manejo de errores para cuando se busca una id que no está
    if planet_query is None:
        return jsonify({"msg":"Planet not found"}),404

    response_body = {
        "msg": "ok one planet",
        "result": planet_query.serialize()
    }
    
    return jsonify(response_body), 200

# create one planet
@app.route('/planets', methods=['POST'])
def create_planet():
    
    request_body = request.get_json(force=True)

    #planet_exists = Planets.query.filter_by(name=request_body["name"])
    #if planet_exists is None :
        #return jsonify({"msg": "Name information is missing."}), 400

    planet = Planets(name=request_body["name"], climate=request_body["climate"], population=request_body["population"], orbital_period=request_body["orbital_period"], rotation_period=request_body["rotation_period"], diameter=request_body["diameter"])
    db.session.add(planet)
    db.session.commit()
    
    response_body = {
        "msg": "Planet created",
        "planet": planet.serialize()
    }
    
    return jsonify(response_body), 200

#get_all_favorites
@app.route('/favorites', methods=['GET'])
def get_all_favorites():
    favorites_query = Favorites.query.all()
    results = list(map(lambda item: item.serialize(), favorites_query))

    print(results)

    response_body = {
        "msg": "ok favorites",
        "results": results
    }

    return jsonify(response_body), 200

#get_one_favorite
@app.route('/favorites/<int:favorite_id>', methods=['GET'])
def get_one_favorite(favorite_id):

    favorite_query = Favorites.query.filter_by(id=favorite_id).first()

    response_body = {
        "msg": "ok one favorite",
        "result": favorite_query.serialize()
    }
    
    return jsonify(response_body), 200

#create_one_favorite
@app.route('/favorites/', methods=['POST'])
def create_one_favorite():
    request_body = request.get_json(force=True)
    # creacion de un registro en la tabla de user
    exists = Favorites.query.filter_by(users_id=request_body["users_id"],characters_id=request_body["characters_id"],planets_id=request_body["planets_id"]).first()
    if exists != None:
        return jsonify({"msg":"Already exists this favortie"}), 400
    
    favorite = Favorites(users_id=request_body["users_id"], characters_id=request_body["characters_id"], planets_id=request_body["planets_id"])
    db.session.add(favorite)
    db.session.commit()
    
    response_body = {
        "msg": "Favorite created",
        
    }
    
    return jsonify(response_body), 200

#delete_one_favorite
@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_one_favorite(favorite_id):

    favorite_delete = Favorites.query.filter_by(id=favorite_id).first()

    db.session.delete(favorite_delete)
    db.session.commit()
    
    response_body = {
        "msg": "Favorite deleted",
    }
    
    return jsonify(response_body), 200

# SING UP 
@app.route("/signup", methods=["POST"])
def signup():  
    request_body = request.get_json(force=True)
    #creacion de un registro en la tabla de user   
    if "email" not in request_body:
        return jsonify({"msg": "You have to put an email"}), 404
    
    email_query = User.query.filter_by(email=request_body["email"]).first()
    
    if email_query != None:
        return jsonify({"msg": "User already exists"}), 400
        
    if "password" not in request_body:
        return jsonify({"msg": "You have to put a password"}), 404
    
    user = User(email=request_body["email"], password=request_body["password"])

    db.session.add(user)
    db.session.commit()

    response_body = {
        "msg": "User created"
    }
    
    return jsonify(response_body), 200


# Login
# # Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email == None or password == None:
        return jsonify({"msg": "Missing data"}), 404

    user = User.query.filter_by(email=email).first()
    print(user) 

    if user == None:
         return jsonify({"msg": "User dosen't exist"}), 404   

    if password != user.password:
        return jsonify({"msg": "Bad password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

#Profile
# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    return jsonify(logged_in_as=user.serialize()), 200

# END endpoints

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)