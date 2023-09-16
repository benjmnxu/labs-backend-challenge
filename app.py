from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from extensions import db

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db.init_app(app)
app.app_context().push()

from models import *

@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route('/api/clubs')
def clubs():
    clubs = Club.query.all()
    content = {}
    for club in clubs:
        content[club.name] = {
            club.favorite,
            club.members,
            club.tags
        }
    return jsonify(content)

@app.route('/api/add_clubs')
def add():
    new_club = request.get_json()
    db.session.add(new_club)
    db.session.commit()
    return jsonify({"message": "new club added"})

@app.route('/api/favorite_club')
def favorites():
    new_club = request.get_json()
    club = new_club["club"]
    club = User.query.filter_by(name=club).first()
    club.favorite += 1
    db.session.commit()
    return jsonify({"message": "added new favorite club"})

@app.route('/api/tags')
def tags():
    # tags = request.get_json()
    tags = Tags.query.all()
    content = {}
    for tag in tags:
        club_list = tag.clubs
        content_list = []
        for club in club_list:
            content_list.append(club.name)
        content[tag.tag] = content_list
    return content

if __name__ == '__main__':
    app.run()
