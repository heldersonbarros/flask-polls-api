from . import vote
from . model import Vote
from . dao import VoteDAO

from modules.account.dao import AccountDAO
from modules.exceptions import ExceededVotes, NoObjectFound, UnauthorizedAccess

from flask import request, make_response, jsonify


@vote.route("", methods=["POST"])
def vote():

    data = request.get_json()

    if 'x-api-key' in request.headers:
        token = request.headers['x-api-key']
        try:
            current_user = AccountDAO.verify_token(token)
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})

        user_id = current_user

    else:
        user_id = 0

    try:
        vote = Vote(poll_id=data["poll_id"], option_id=data["option_id"], account_id= user_id)
        VoteDAO.vote(vote)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except ExceededVotes:
        return make_response(jsonify({'message' : 'Você excedeu o limite de votos nessa enquete'}), 409)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada ou votação indisponível'}), 404)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return make_response(jsonify({'message' : 'voted successfully'}), 201)