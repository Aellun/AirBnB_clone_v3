#!/usr/bin/python3
"""
module docstring: Manages the states view in the API
this modules handles the creation, retrieval,updating and deletion of records
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from api.v1.views import app_views
from models import storage
from models.state import State


ALLOWED_METHODS = ['GET', 'DELETE', 'POST', 'PUT']
"""HTTP methods supported by the states endpoint."""


@app_views.route('/states', methods=ALLOWED_METHODS)
@app_views.route('/states/<state_id>', methods=ALLOWED_METHODS)
def handle_states(state_id=None):
    """
    Dispatcher function for handling requests to the states endpoint.
    Based on the HTTP method of the incoming request,
    it calls the appropriate handler function.
    Raises a MethodNotAllowed exception
    if the request method is not in ALLOWED_METHODS.
    """
    handlers = {
        'GET': get_states,
        'DELETE': remove_state,
        'POST': add_state,
        'PUT': update_state,
    }
    if request.method in handlers:
        return handlers[request.method](state_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_states(state_id=None):
    """Retrieves all states or a specific state by ID.
    If an ID is provided, returns the state with that ID.
    Otherwise, returns all states.
    Raises a NotFound exception if the specified ID does not exist.
    """
    all_states = storage.all(State).values()
    if state_id:
        res = list(filter(lambda x: x.id == state_id, all_states))
        if res:
            return jsonify(res[0].to_dict())
        raise NotFound()
    all_states = list(map(lambda x: x.to_dict(), all_states))
    return jsonify(all_states)


def remove_state(state_id=None):
    """Removes a state with the specified id.
    """
    all_states = storage.all(State).values()
    res = list(filter(lambda x: x.id == state_id, all_states))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_state(state_id=None):
    '''Adds a new state with the data from the request body
    '''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    new_state = State(**data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


def update_state(state_id=None):
    """"Updates the state with the given id.
    Expects the request data to be in JSON format.
    Only updates fields not in the list of exclusion.
    Raises a BadRequest exception if the request data is not in JSON format.
    Raises a NotFound exception if the specified ID does not exist.
    """
    xkeys = ('id', 'created_at', 'updated_at')
    all_states = storage.all(State).values()
    res = list(filter(lambda x: x.id == state_id, all_states))
    if res:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        old_state = res[0]
        for key, value in data.items():
            if key not in xkeys:
                setattr(old_state, key, value)
        old_state.save()
        return jsonify(old_state.to_dict()), 200
    raise NotFound()
