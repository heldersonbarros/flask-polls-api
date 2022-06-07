from . import poll
from . model import Poll
from . dao import PollDAO
from modules.account.dao import AccountDAO
from modules.option.dao import OptionsDAO
from modules.option.model import Options
from modules.decorators import token_required
from modules.exceptions import UnauthorizedAccess, NoObjectFound

import datetime
from flask import request, jsonify, make_response

@poll.route('/create', methods=["POST"])
@token_required
def create_poll(current_user):
    data = request.get_json()
    data["account_id"] = current_user
    data["created_at"] = datetime.datetime.now()
    options = data.pop("options")

    try:
        poll = Poll(**data)

        if (len(options) < 2):
            return make_response(jsonify({'message' : 'As enquetes devem possuir pelos duas opções de resposta'}), 400)

        poll_id = PollDAO.create_poll(poll)
        for option in options:
            optionObject = Options(OptionText= option["text"], poll_id=poll_id)
            OptionsDAO.create_option(optionObject)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)

    return make_response(jsonify({'message' : 'registered successfully'}), 201)

@poll.route('/edit', methods=["PUT"])
@token_required
def update_poll(current_user):
    data = request.get_json()
    data['account_id'] = current_user

    try:
        poll = Poll(**data)
        PollDAO.update_poll(poll)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return jsonify({"message": 'updated successfully'})

@poll.route('/<id>/delete', methods=["DELETE"])
@token_required
def delete_poll(current_user, id):
    
    try:
        PollDAO.delete_poll(id,current_user)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return jsonify({"message": 'deleted successfully'})

@poll.route("/latest")
def latest():
    polls_array = PollDAO.latest()
    for poll in polls_array:
        poll["options"] = OptionsDAO.getOptionsByPollId(poll["id"])

    return jsonify({"polls": polls_array})

@poll.route("/<id>/result")
def polls_result(id):
    
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
        check_poll = PollDAO.checkResultAuthorization(id, user_id)
        if check_poll:
            result = OptionsDAO.getOptionsVotesResult(id)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para acessar o recurso requisitado'}), 403)

    return jsonify(result)