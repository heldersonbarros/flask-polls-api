from functools import wraps
from flask import request, jsonify
from modules.account.dao import AccountDAO

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-api-key' in request.headers:
            token = request.headers['x-api-key']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            current_user = AccountDAO.verify_token(token)
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    
    return decorator