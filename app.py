from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import datetime
import jwt

from models.dao.accountDAO import AccountDAO
from models.dao.pollDAO import PollDAO
from models.dao.optionsDAO import OptionsDAO
from models.dao.voteDAO import VoteDAO
from models.dao.categoryDAO import CategoryDAO

from models.vo.exceptions import NoObjectFound, UnauthorizedAccess, ExceededVotes
from models.vo.account import Account
from models.vo.poll import Poll
from models.vo.options import Options
from models.vo.vote import Vote
from models.vo.category import Category

import psycopg2

app = Flask(__name__)

app.config['SECRET_KEY'] = "9u=brky[E?^MCVWZ7mtZj]PB?;|iP`"
app.config['DEBUG'] = True


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-api-key' in request.headers:
            token = request.headers['x-api-key']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            current_user = AccountDAO.verify_token(token, app.config['SECRET_KEY'])
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    
    return decorator




@app.route("/accounts/signup", methods=["POST"])
def create_account():
    data = request.get_json()

    try:
        data["username"] = data["username"].lower()
        account = Account(name=data["name"], email=data["email"], username=data["username"])
        account.set_password(data["password"])
        AccountDAO.create_account(account)
    except psycopg2.errors.UniqueViolation:
        return make_response(jsonify({'message' : 'Usuário ou email já utilizado'}), 409)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)

    return make_response(jsonify({'message' : 'Registrado com sucesso'}), 201)

@app.route('/accounts/signin')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    account_id = AccountDAO.login(auth.username.lower(), auth.password)

    if account_id:
        token = jwt.encode({'id' : account_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token' : token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@app.route('/accounts/edit', methods=["POST"])
@token_required
def edit_account(current_user):
    data = request.get_json()


    data["name"]
    data["username"]
    data["email"]
    try:
        account = Account(name=data["name"], email=data["email"], username=data["username"], id=current_user)
        print("aqiii")
        AccountDAO.update_account(account)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return jsonify({"message": 'updated successfully'})

@app.route('/accounts/<username>/polls')
def account_polls(username):
    try:
        polls_array = PollDAO.account_polls(username)
        return jsonify({"polls": polls_array})
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Usuário não encontrado'}), 404)

@app.route('/polls/create', methods=["POST"])
@token_required
def create_poll(current_user):
    data = request.get_json()

    try:
        poll = Poll(question=data["question"], isClosed=data["isClosed"], isPublicStatistics=data["isPublicStatistics"],
                    numChosenOptions=data["numChosenOptions"], timeLimit=data["timeLimit"], account_id=current_user,
                    limit_vote_per_user=data["limit_vote_per_user"], created_at=datetime.datetime.now()
                )

        if (len(data["options"]) < 2):
            return make_response(jsonify({'message' : 'As enquetes devem possuir pelos duas opções de resposta'}), 400)

        poll_id = PollDAO.create_poll(poll)
        for option in data["options"]:
            optionObject = Options(OptionText= option["text"], poll_id=poll_id)
            OptionsDAO.create_option(optionObject)

    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)

    return make_response(jsonify({'message' : 'registered successfully'}), 201)

@app.route('/polls/edit', methods=["POST"])
@token_required
def update_poll(current_user):
    data = request.get_json()

    try:
        poll = Poll(id=data["poll_id"], isClosed=data["isClosed"], isPublicStatistics=data["isPublicStatistics"], timeLimit=data["timeLimit"]
        , limit_vote_per_user=data["limit_vote_per_user"], account_id=current_user)
        PollDAO.update_poll(poll)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para alterar o recurso requisitado'}), 403)

    return jsonify({"message": 'updated successfully'})

@app.route("/polls/latest")
def latest():
    polls_array = PollDAO.latest()

    return jsonify({"polls": polls_array})

@app.route("/polls/<id>/result")
def polls_result(id):
    
    if 'x-api-key' in request.headers:
        token = request.headers['x-api-key']
        try:
            current_user = AccountDAO.verify_token(token, app.config['SECRET_KEY'])
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})

        user_id = current_user

    else:
        user_id = 0

    try:
        result = PollDAO.polls_result(id,user_id)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)
    except UnauthorizedAccess:
        return make_response(jsonify({'message' : 'Você não possui autorização para acessar o recurso requisitado'}), 403)

    return jsonify(result)

@app.route("/vote", methods=["POST"])
def vote():

    data = request.get_json()

    if 'x-api-key' in request.headers:
        token = request.headers['x-api-key']
        try:
            current_user = AccountDAO.verify_token(token, app.config['SECRET_KEY'])
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
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)

    return make_response(jsonify({'message' : 'voted successfully'}), 201)

@app.route("/category/")
def listAllCategories():
    try:
        names = CategoryDAO.listAll()
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)

    return jsonify(names)

@app.route("/category/<category_name>")
def category(category_name):

    try:
        polls = CategoryDAO.category(category_name)
    except KeyError:
        return make_response(jsonify({'message' : 'Os dados passados estão invalidos'}), 400)
    except NoObjectFound:
        return make_response(jsonify({'message' : 'Enquete não encontrada'}), 404)

    return jsonify(polls)

if __name__ == '__main__':
    app.run()
