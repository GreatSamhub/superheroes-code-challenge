from random import randint, choice
from flask import Flask
from models import db, Hero, Power, HeroPower
import os

#app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
#sys.path.append(app_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db/app.db')  # Update with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def seed_data():
    # Create and push an application context
    with app.app_context():
        print("🦸‍♀️ Seeding powers...")
        powers_data = [
            {"name": "super strength", "description": "gives the wielder super-human strengths"},
            {"name": "flight", "description": "gives the wielder the ability to fly through the skies at supersonic speed"},
            {"name": "super human senses", "description": "allows the wielder to use her senses at a super-human level"},
            {"name": "elasticity", "description": "can stretch the human body to extreme lengths"}
        ]

        for power_info in powers_data:
            power = Power(**power_info)
            db.session.add(power)

        print("🦸‍♀️ Seeding heroes...")
        heroes_data = [
            {"name": "Kamala Khan", "supername": "Ms. Marvel"},
            {"name": "Doreen Green", "supername": "Squirrel Girl"},
            {"name": "Gwen Stacy", "supername": "Spider-Gwen"},
            {"name": "Janet Van Dyne", "supername": "The Wasp"},
            {"name": "Wanda Maximoff", "supername": "Scarlet Witch"},
            {"name": "Carol Danvers", "supername": "Captain Marvel"},
            {"name": "Jean Grey", "supername": "Dark Phoenix"},
            {"name": "Ororo Munroe", "supername": "Storm"},
            {"name": "Kitty Pryde", "supername": "Shadowcat"},
            {"name": "Elektra Natchios", "supername": "Elektra"}
        ]

        for hero_info in heroes_data:
            hero = Hero(**hero_info)
            db.session.add(hero)

        print("🦸‍♀️ Adding powers to heroes...")

        strengths = ["Strong", "Weak", "Average"]
        for hero in Hero.query.all():
            for _ in range(randint(1, 4)):
                # get a random power
                power = Power.query.get(Power.query.with_entities(Power.id).order_by(db.func.random()).first())

                hero_power = HeroPower(hero_id=hero.id, power_id=power.id, strength=choice(strengths))
                db.session.add(hero_power)

        db.session.commit()

        print("🦸‍♀️ Done seeding!")

if __name__ == "__main__":
    seed_data()
