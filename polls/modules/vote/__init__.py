from flask import Blueprint

vote = Blueprint('vote', __name__, url_prefix='/vote')

from . import controller