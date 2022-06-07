from flask import request, jsonify, make_response, current_app
import psycopg2
import datetime
import jwt
from . import account
from .dao import AccountDAO
from .model import Account

from modules.decorators import token_required
from modules.exceptions import NoObjectFound, UnauthorizedAccess
from modules.poll.dao import PollDAO
from modules.option.dao import OptionsDAO

@account.route("/signup", methods=["POST"])
def create_account():
    data = request.get_json()

    try:
        data["username"] = data["username"].lower()
        account = Account(**data)
        account.set_password(data["password"])
        AccountDAO.create_account(account)
    except psycopg2.errors.UniqueViolation:
        return make_response(jsonify({'message' : 'Usuário ou email já utilizado'}), 409)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)

    return make_response(jsonify({'message' : 'Registrado com sucesso'}), 201)

@account.route('/signin/')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    account_id = AccountDAO.login(auth.username.lower(), auth.password)

    if account_id:
        token = jwt.encode({'id' : account_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token' : token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@account.route('/edit', methods=["PUT"])
@token_required
def edit_account(current_user):
    data = request.get_json()
    data["id"] = current_user

    try:
        account = Account(**data)
        AccountDAO.update_account(account)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)
        
    return jsonify({"message": 'updated successfully'})

@account.route('/<id>/delete', methods=["DELETE"])
@token_required
def delete_account(current_user, id):
    
    try:
        AccountDAO.delete_account(id,current_user)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return jsonify({"message": 'deleted successfully'})

@account.route('/<username>/polls')
def account_polls(username):
    try:
        polls_array = PollDAO.account_polls(username)
        for poll in polls_array:
            poll["options"] = OptionsDAO.getOptionsByPollId(poll["id"])
        return jsonify({"polls": polls_array})
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Usuário não encontrado'}), 404)