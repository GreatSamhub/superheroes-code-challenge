#!/usr/bin/env python3

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from marshmallow import fields
import os

from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db/app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)


class PowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Power
        load_instance = True
        sqla_session = db.session

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "powerbyid",
                values=dict(power_id="<id>")),
            "powers": ma.URLFor("powers"),
        }
    )

class HeroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hero
        load_instance = True
        sqla_session = db.session

    id = ma.auto_field()
    name = ma.auto_field()
    supername = ma.auto_field()
    powers = fields.Nested("PowerSchema", many=True)

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "herobyid",
                values=dict(hero_id="<id>")),
            "heroes": ma.URLFor("heroes"),
        }
    )

class HeroPowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HeroPower
        load_instance = True
        sqla_session = db.session

    hero_id = ma.auto_field()
    power_id = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "heropowerbyid",
                values=dict(heropower_id="<heropower_id>")),
            "heropowers": ma.URLFor("heropowers"),
        }
    )

hero_schema = HeroSchema()
heroes_schema = HeroSchema(many=True)

power_schema = PowerSchema()
powers_schema = PowerSchema(many=True)

heroPower_schema = HeroPowerSchema()
heroPowers_schema = HeroPowerSchema(many=True)

# ... rest of your code




class Index(Resource):

    def get(self):

        response_dict = {
            "index": "Welcome to the Heroes RESTful API",
        }

        response = make_response(
            jsonify(response_dict),
            200,
        )

        return response

api.add_resource(Index, '/')

class HeroResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return heroes_schema.dump(heroes), 200

api.add_resource(HeroResource, '/heroes', endpoint='heroes')

class HeroByIDResource(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if hero:
            return hero_schema.dump(hero), 200
        else:
            return {"message": "Hero not found"}, 404
api.add_resource(HeroByIDResource, '/heroes/<int:hero_id>', endpoint='herobyid')
        
class PowerResource(Resource):
    def get(self):
        powers = Power.query.all()
        return powers_schema.dump(powers), 200

api.add_resource(PowerResource, '/powers', endpoint='powers')

class PowerByIDResource(Resource):
    def get(self, power_id):
        power = Power.query.get(power_id)
        if power:
            return power_schema.dump(power), 200
        else:
            return {"message": "Power not found"}, 404
    
    def patch(self, power_id):
        power = Power.query.get(power_id)
        if not power:
            return {"error": "Power not found"}, 404

        try:
            # Update the power description
            power.description = request.json["description"]

            # Commit the changes to the database
            db.session.commit()

            # Return the updated power
            return power_schema.dump(power), 200
        except ValueError as e:
            return {"errors": [str(e)]}, 400
api.add_resource(PowerByIDResource, '/powers/<int:power_id>', endpoint='powerbyid')

class HeroPowersResource(Resource):
    def post(self):
        try:
            # Extract data from the request body
            data = request.json
            strength = data["strength"]
            power_id = data["power_id"]
            hero_id = data["hero_id"]

            # Check if the hero and power exist
            hero = Hero.query.get(hero_id)
            power = Power.query.get(power_id)
            if not hero or not power:
                return {"error": "Hero or Power not found"}, 404

            # Create a new HeroPower instance
            hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)

            # Add the new HeroPower to the database
            db.session.add(hero_power)
            db.session.commit()

            # Return the data related to the hero
            return hero_schema.dump(hero), 201
        except ValueError as e:
            return {"errors": [str(e)]}, 400

api.add_resource(HeroPowersResource, '/hero_powers', endpoint='hero_powers')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
