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
from models import db, User, People, Planet, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    results = [person.serialize() for person in people]
    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [user.serialize() for user in users]
    return jsonify(results), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Simulamos el usuario actual con ID 1

    # Buscamos todos los favoritos de ese usuario
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    # Serializamos cada favorito
    results = [fav.serialize() for fav in favorites]

    return jsonify(results), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Simulamos el usuario actual con ID 1

    # Comprobar si el planeta existe
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    # Crear el nuevo favorito
    new_favorite = Favorite(
        user_id=user_id, planet_id=planet_id, people_id=None)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": f"Planet {planet_id} added to favorites"}), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1  # Simulamos el usuario actual con ID 1

    # Comprobar si el personaje existe
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Character not found"}), 404

    # Crear el nuevo favorito
    new_favorite = Favorite(
        user_id=user_id, people_id=people_id, planet_id=None)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": f"Character {people_id} added to favorites"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  # Simulamos el usuario actual con ID 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite planet not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": f"Planet {planet_id} removed from favorites"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1  # Simulamos el usuario actual con ID 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite character not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": f"Character {people_id} removed from favorites"}), 200

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
