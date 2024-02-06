#!/usr/bin/python3
'''Index view for the API that provides basic ino about the system's state'''
from flask import jsonify

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


@app_views.route('/status')
def get_status():
    '''
    Endpoint route to check the API's operational status.
    Returns a simple JSON response indicating the status
    '''
    return jsonify(status='OK')


@app_views.route('/stats')
def get_stats():
    '''Endpoint route to retrieve statistics
      about the number of instances
      for each entity in the database.
      Returns a JSON object with counts for each entity
    '''
    objects = {
        'amenities': Amenity,
        'cities': City,
        'places': Place,
        'reviews': Review,
        'states': State,
        'users': User
    }
    for key, value in objects.items():
        objects[key] = storage.count(value)
    return jsonify(objects)
