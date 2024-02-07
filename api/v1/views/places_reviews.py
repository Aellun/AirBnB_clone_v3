#!/usr/bin/python3
"""
Module docstring: Manages the creation, retrieval, and modification
of Review objects via RESTful endpoints.
This module implements routes for handling review-related operations
such as listing reviews for a place, creating a new review, retrieving
a review by ID, updating a review, and deleting a review.
"""
from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.review import Review


@app_views.route("/places/<place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def reviews_by_place(place_id):
    """
    '''Endpoint for retrieving all reviews
    associated with a specified place.
    Returns a JSON array of all reviews for the specified place.
    If the place is not found, a  404 error is returned.
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
    '''Endpoint method for creating a new review for a given place.
    Accepts a JSON payload with the review details,
    including the user_id and text.
    If the place or user is not found,
    or the required fields are missing,
    a  400 or  404 error is returned."""

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
    Endpoint method for retrieving
    a single review by its unique identifier
    Returns the requested review as a JSON object.
    If the review is not found, a  404 error is returned.
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
    Endpoint method for updating an existing
    review by its unique identifier.
    Accepts a JSON payload with the updated review details.
    If the review is not found, or the JSON is malformed,
    a  400 or  404 error is returned.
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
    Endpoint method for deleting an existing review
    by its unique identifier.
    Deletes the specified review from the data store.
        :param : Review object id
        :return: empty dict with 200 or 404 if not found
    """

    fetched_obj = storage.get("Review", str(review_id))

    if fetched_obj is None:
        abort(404)

    storage.delete(fetched_obj)
    storage.save()

    return jsonify({})
