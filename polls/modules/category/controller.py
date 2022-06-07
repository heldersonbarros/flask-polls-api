from .dao import CategoryDAO as CategoryDAO
from . import category
from flask import jsonify, make_response
from modules.exceptions import NoObjectFound

@category.route("/")
def listAllCategories():
    try:
        names = CategoryDAO.list_all()
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)

    return jsonify(names)

@category.route("/<category_name>")
def category(category_name):
    try:
        polls = CategoryDAO.category(category_name)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)

    return jsonify(polls)
