#!/usr/bin/python3
"""
Module doctstring: This module provides the implementation for the review
in the AirBnB clone API
The module also allows for the management of Review objects,
including operations such as listing reviews for a place,
creating new reviews, retrieving a review by ID,
updating a review, and deleting a review.
'''

"""
from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.review import Review


@app_views.route("/places/<place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def reviews_by_place(place_id):
    """
    Handler method for retrieving all reviews associated with a specific place.
    Returns a JSON array of all reviews for the specified place ID
    If the place does not exist, a  404 error is returned.
    """
    review_list = []
    place_obj = storage.get("Place", str(place_id))

    if place_obj is None:
        abort(404)

    for obj in place_obj.reviews:
        review_list.append(obj.to_json())

    return jsonify(review_list)


@app_views.route("/places/<place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def review_create(place_id):
    """
    Handler function for creating a new review for a specific place.
    Requires a JSON payload with 'user_id' and 'text' fields.
    If the place or user does not exist, or if the JSON payload is missing
    required fields, a  400 or  404 error is returned.
    On successful creation, returns the newly created review JSON object
    with a  201 status code.
    """
    review_json = request.get_json(silent=True)
    if review_json is None:
        abort(400, 'Not a JSON')
    if not storage.get("Place", place_id):
        abort(404)
    if not storage.get("User", review_json["user_id"]):
        abort(404)
    if "user_id" not in review_json:
        abort(400, 'Missing user_id')
    if "text" not in review_json:
        abort(400, 'Missing text')

    review_json["place_id"] = place_id

    new_review = Review(**review_json)
    new_review.save()
    resp = jsonify(new_review.to_json())
    resp.status_code = 201

    return resp


@app_views.route("/reviews/<review_id>",  methods=["GET"],
                 strict_slashes=False)
def review_by_id(review_id):
    """
    handler method that gets a specific Review object by ID
        :param review_id: place object id
        :return: review obj with the specified id or error
    """

    fetched_obj = storage.get("Review", str(review_id))

    if fetched_obj is None:
        abort(404)

    return jsonify(fetched_obj.to_json())


@app_views.route("/reviews/<review_id>",  methods=["PUT"],
                 strict_slashes=False)
def review_put(review_id):
    """
    handler method that updates specific Review object by ID
        :param review_id: Review object ID
        :return: Review object and 200 on success, or 400 or 404 on failure
    """
    place_json = request.get_json(silent=True)

    if place_json is None:
        abort(400, 'Not a JSON')

    fetched_obj = storage.get("Review", str(review_id))

    if fetched_obj is None:
        abort(404)

    for key, val in place_json.items():
        if key not in ["id", "created_at", "updated_at", "user_id",
                       "place_id"]:
            setattr(fetched_obj, key, val)

    fetched_obj.save()

    return jsonify(fetched_obj.to_json())


@app_views.route("/reviews/<review_id>",  methods=["DELETE"],
                 strict_slashes=False)
def review_delete_by_id(review_id):
    """
    deletes Review by id
    :param : Review object id
    :return: empty dict with 200 or 404 if not found
    """

    fetched_obj = storage.get("Review", str(review_id))

    if fetched_obj is None:
        abort(404)

    storage.delete(fetched_obj)
    storage.save()

    return jsonify({})
