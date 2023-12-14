#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/campers')
def all_campers():
    camp = Camper.query.all()
    
    return [c.to_dict(rules=('-signups', '-activities',)) for c in camp], 200

@app.get('/campers/<int:id>')
def camper_by_id(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return {"error": "Camper not found"}, 404
    return camper.to_dict(rules=('-activities',)), 200

@app.patch('/campers/<int:id>')
def patch_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return {"error": "Camper not found"}, 404
    try:
        data = request.json
        for key in data:
            setattr(camper, key, data[key])
        db.session.add(camper)
        db.session.commit()
        return camper.to_dict(rules=('-signups', '-activities')), 201
    except :
        return {'error': ['validation errors']}, 406
    
@app.post('/campers')
def post_camper():
    try:
        data = request.json
        camper = Camper(
            name = data['name'],
            age = data['age']
        )
        db.session.add(camper)
        db.session.commit()
        return camper.to_dict(rules=('-signups', '-activities')), 201
    except :
        return {'error': ['validation errors']}, 406
    
@app.get('/activities')
def all_activities():
    ac = Activity.query.all()
    return [a.to_dict(rules=('-signups', '-campers',)) for a in ac], 200

@app.delete('/activities/<int:id>')
def delete_activity(id):
    ac = db.session.get(Activity, id)
    if not ac:
        return {"error": "Activity not found"}, 404
    db.session.delete(ac)
    db.session.commit()
    return {}, 204

@app.post('/signups')
def post_signup():
    try:
        data = request.json
        sign = Signup(
            time = data['time'],
            camper_id = data['camper_id'],
            activity_id = data['activity_id']
        )
        db.session.add(sign)
        db.session.commit()
        return sign.to_dict(), 201
    except:
        return { "errors": ["validation errors"] }

if __name__ == '__main__':
    app.run(port=5555, debug=True)
