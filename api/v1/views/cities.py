#!/usr/bin/python3
'''Module docstring: Manages the cities view for the API,
including CRUD operations for city resources.'''
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from api.v1.views import app_views
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(state_id=None, city_id=None):
    '''Dispatcher The method handler for the cities http endpoint.
    supports GET,DELETE,POST and PUT as methods allowed
    '''
    handlers = {
        'GET': get_cities,
        'DELETE': remove_city,
        'POST': add_city,
        'PUT': update_city,
    }
    if request.method in handlers:
        return handlers[request.method](state_id, city_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_cities(state_id=None, city_id=None):
    '''Gets the city with the specified id or all cities in
    the state with the specified id.
    '''
    if state_id:
        state = storage.get(State, state_id)
        if state:
            cities = list(map(lambda x: x.to_dict(), state.cities))
            return jsonify(cities)
    elif city_id:
        city = storage.get(City, city_id)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def remove_city(state_id=None, city_id=None):
    '''Removes a city with the specified id
    Also deletes associated places and reviews
    if the storage type is not a database.
    Raises a NotFound exception if the city ID does not exist.
    '''
    if city_id:
        city = storage.get(City, city_id)
        if city:
            storage.delete(city)
            if storage_t != "db":
                for place in storage.all(Place).values():
                    if place.city_id == city_id:
                        for review in storage.all(Review).values():
                            if review.place_id == place.id:
                                storage.delete(review)
                        storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_city(state_id=None, city_id=None):
    '''Adds a new city with the data from the requested body
    Expects the request data to be in JSON format
    with at least a 'name' field and a 'state_id'.
    Raises a BadRequest exception if the request data is invalid
    or the state does not exist.
    '''
    state = storage.get(State, state_id)
    if not state:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    data['state_id'] = state_id
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


def update_city(state_id=None, city_id=None):
    '''Updates the city with the given id.
    expects the request data to be in json format
    updates the fields except those in list of exclusion
    rasies 404 error when the city ID does not exist
    '''
    xkeys = ('id', 'state_id', 'created_at', 'updated_at')
    if city_id:
        city = storage.get(City, city_id)
        if city:
            data = request.get_json()
            if type(data) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in data.items():
                if key not in xkeys:
                    setattr(city, key, value)
            city.save()
            return jsonify(city.to_dict()), 200
    raise NotFound()
